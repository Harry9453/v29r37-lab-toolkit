from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .death_score import DeathScoreReport
from .odds import implied_probability
from .feature_gates import GateSignal

GRADE_ORDER = ["No Bet", "C", "B-", "B", "B+", "A"]


def _grade_index(grade: str) -> int:
    return GRADE_ORDER.index(grade)


def _downgrade(grade: str, steps: int = 1) -> str:
    return GRADE_ORDER[max(0, _grade_index(grade) - steps)]


def _cap_grade(grade: str, cap: str) -> str:
    return GRADE_ORDER[min(_grade_index(grade), _grade_index(cap))]


def _norm_market(bet_type: str) -> str:
    return bet_type.lower().replace(" ", "").replace("_", "")


def _is_under_market(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return "under" in b or "小" in b


def _is_over_market(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return "over" in b or "大" in b


def _is_under_25(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return any(k in b for k in ["under2.5", "u2.5", "小2.5"])


def _is_under_35(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return any(k in b for k in ["under3.5", "u3.5", "小3.5"])


def _is_over_25_or_35(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return any(k in b for k in ["over2.5", "o2.5", "大2.5", "over3.5", "o3.5", "大3.5"])


def _is_btts_market(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return "btts" in b or "兩隊進球" in bet_type or "双方进球" in bet_type


def _is_btts_no(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return _is_btts_market(bet_type) and any(k in b for k in ["no", "否", "不是"])


def _is_btts_yes(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return _is_btts_market(bet_type) and any(k in b for k in ["yes", "是"])


def _is_team_total_under(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return ("team" in b or "進球" in bet_type or "进球" in bet_type) and _is_under_market(bet_type)


def _is_handicap_market(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return any(k in b for k in ["handicap", "讓", "让", "+", "-"])


def _is_win_market(bet_type: str) -> bool:
    b = _norm_market(bet_type)
    return any(k in b for k in ["win", "勝", "胜", "moneyline", "ml"])


def base_grade_from_ev(expected_roi: float) -> str:
    if expected_roi <= 0:
        return "No Bet"
    if expected_roi >= 0.10:
        return "A"
    if expected_roi >= 0.06:
        return "B+"
    if expected_roi >= 0.04:
        return "B"
    if expected_roi >= 0.025:
        return "B-"
    return "C"


def stake_for_grade(grade: str) -> int:
    return {
        "A": 250,
        "B+": 150,
        "B": 100,
        "B-": 50,
        "C": 0,
        "No Bet": 0,
    }[grade]


@dataclass(frozen=True)
class PickGrade:
    bet_type: str
    odds: float
    model_probability: float
    implied_probability: float
    expected_roi: float
    base_grade: str
    final_grade: str
    recommended_stake: int
    reasons: List[str]


def _apply_death_score_rules(
    grade: str,
    bet_type: str,
    death_report: DeathScoreReport,
    reasons: List[str],
) -> str:
    is_under = _is_under_market(bet_type)
    is_u25 = _is_under_25(bet_type)
    is_u35 = _is_under_35(bet_type)

    if death_report.death_probability_top_n >= 0.45:
        reasons.append("Top10死亡比分機率≥45%，No Bet")
        return "No Bet"
    if death_report.death_probability_top_n >= 0.35:
        grade = _downgrade(grade, 2)
        reasons.append("Top10死亡比分機率≥35%，降2級")
    elif death_report.top1_is_death:
        grade = _downgrade(grade, 2)
        reasons.append("Top1是死亡比分，降2級")
    elif death_report.top3_death_count >= 1:
        grade = _downgrade(grade, 1)
        reasons.append("Top3含死亡比分，降1級")
    elif death_report.top10_death_count >= 3:
        grade = _downgrade(grade, 1)
        reasons.append("Top10死亡比分≥3個，降1級")

    # V29-R3.7a / V29-R3.7a-1 / V29-R3.7a-2: under markets cannot be A when death-score concentration is meaningful.
    if is_under and grade != "No Bet":
        if death_report.death_probability_top_n >= 0.12:
            before = grade
            grade = _cap_grade(grade, "B+")
            if before != grade:
                reasons.append("小球死亡比分集中度≥12%，小球不可A，封頂B+")
        if is_u35 and death_report.top10_death_count >= 3:
            before = grade
            grade = _cap_grade(_downgrade(grade, 1), "B")
            if before != grade:
                reasons.append("小3.5遇Top10右尾死亡比分≥3個，額外降級且最高B")
        if is_u25 and death_report.top10_death_count >= 2:
            before = grade
            grade = _downgrade(grade, 1)
            if before != grade:
                reasons.append("小2.5死亡比分過多，額外降1級")

    return grade


def _apply_deep_right_tail_split(
    grade: str,
    bet_type: str,
    sig: GateSignal,
    reasons: List[str],
) -> str:
    is_under = _is_under_market(bet_type)
    is_u25 = _is_under_25(bet_type)
    is_u35 = _is_under_35(bet_type)
    is_btts_no = _is_btts_no(bet_type)
    is_btts_yes = _is_btts_yes(bet_type)
    is_team_under = _is_team_total_under(bet_type)
    is_over = _is_over_market(bet_type) or _is_over_25_or_35(bet_type)

    if sig.code == "DEEP_RIGHT_TAIL_CLEAN_SHEET":
        # Spain 4-0 / Japan 4-0 / Brazil 3-0 archetype.
        if is_u35 or is_u25:
            if sig.score >= 5:
                reasons.append(f"{sig.code}: {sig.message}；小球在零封型右尾中不買")
                return "No Bet"
            before = grade
            grade = _downgrade(grade, 1)
            if before != grade:
                reasons.append(f"{sig.code}: {sig.message}；小球降1級")
            return grade

        if is_btts_no or is_team_under:
            # Clean-sheet right tail supports BTTS No / weak-team under, but do not upgrade in grading engine.
            reasons.append(f"{sig.code}: {sig.message}；BTTS否/弱隊小不被右尾硬殺")
            return grade

        reasons.append(f"{sig.code}: {sig.message}")
        return grade

    if sig.code == "DEEP_RIGHT_TAIL_BTTS":
        # Netherlands 5-1 / England 4-2 archetype.
        if is_u35 or is_u25:
            reasons.append(f"{sig.code}: {sig.message}；BTTS型深右尾下小球不買")
            return "No Bet"

        if is_btts_no or is_team_under:
            if sig.score >= 6:
                reasons.append(f"{sig.code}: {sig.message}；BTTS否/弱隊小在BTTS型深右尾不買")
                return "No Bet"
            before = grade
            grade = _downgrade(grade, 2)
            if before != grade:
                reasons.append(f"{sig.code}: {sig.message}；BTTS否/弱隊小降2級")
            return grade

        if is_btts_yes or is_over:
            # Positive signal only; do not upgrade automatically.
            reasons.append(f"{sig.code}: {sig.message}；大球/BTTS是可觀察，但仍需EV")
            return grade

        reasons.append(f"{sig.code}: {sig.message}")
        return grade

    if sig.code == "DEEP_RIGHT_TAIL_MIXED":
        if is_under:
            before = grade
            grade = _downgrade(grade, 1)
            if before != grade:
                reasons.append(f"{sig.code}: {sig.message}；混合右尾下小球降1級")
        else:
            reasons.append(f"{sig.code}: {sig.message}")
        return grade

    return grade


def _apply_market_specific_gate(
    grade: str,
    bet_type: str,
    sig: GateSignal,
    reasons: List[str],
) -> str:
    """
    V29-R3.7a-1 + V29-R3.7a-2 Market-Specific Gate.

    Right Tail / Low Block / Early Burst are hard filters mainly for:
    - Under 2.5 / Under 3.5
    - handicap / weak-side handicap safety

    Deep Right Tail Split further separates:
    - DEEP_RIGHT_TAIL_CLEAN_SHEET
    - DEEP_RIGHT_TAIL_BTTS
    - DEEP_RIGHT_TAIL_MIXED
    """
    is_u25 = _is_under_25(bet_type)
    is_u35 = _is_under_35(bet_type)
    is_btts = _is_btts_market(bet_type)
    is_team_under = _is_team_total_under(bet_type)
    is_handicap = _is_handicap_market(bet_type)
    is_win = _is_win_market(bet_type)

    if sig.code in {"DEEP_RIGHT_TAIL_CLEAN_SHEET", "DEEP_RIGHT_TAIL_BTTS", "DEEP_RIGHT_TAIL_MIXED"}:
        return _apply_deep_right_tail_split(grade, bet_type, sig, reasons)

    hard_under_codes = {
        "RIGHT_TAIL_SCORE",
        "LOW_BLOCK_FRAGILITY",
        "EARLY_FAVORITE_BURST",
        "CREATIVE_REPLACEMENT_CHAIN",
        "MANAGER_SHOCK_NOT_RESET",
    }

    # Right-tail family: only hard-kill under / handicap safety. Do not auto-kill BTTS No.
    if sig.code in hard_under_codes:
        if is_u35:
            if sig.score >= 5:
                reasons.append(f"{sig.code}: 分數≥5，小3.5在強右尾/低位破局局面不買")
                return "No Bet"
            if sig.score >= 4:
                before = grade
                grade = _cap_grade(_downgrade(grade, 1), "B")
                if before != grade:
                    reasons.append(f"{sig.code}: 分數≥4，小3.5額外降級且最高B")
            elif sig.level in {"downgrade", "reset"}:
                grade = _downgrade(grade, 1)
                reasons.append(f"{sig.code}: {sig.message}，小3.5降1級")
            else:
                reasons.append(f"{sig.code}: {sig.message}")
            return grade

        if is_u25:
            if sig.score >= 4:
                before = grade
                grade = _downgrade(grade, 1)
                if before != grade:
                    reasons.append(f"{sig.code}: 分數≥4，小2.5額外降級")
            elif sig.level in {"downgrade", "reset"}:
                grade = _downgrade(grade, 1)
                reasons.append(f"{sig.code}: {sig.message}，小2.5降1級")
            else:
                reasons.append(f"{sig.code}: {sig.message}")
            return grade

        if is_handicap:
            if sig.score >= 5:
                before = grade
                grade = _downgrade(grade, 2)
                if before != grade:
                    reasons.append(f"{sig.code}: 分數≥5，讓分/受讓右尾安全性不足，降2級")
            elif sig.score >= 4:
                before = grade
                grade = _downgrade(grade, 1)
                if before != grade:
                    reasons.append(f"{sig.code}: 分數≥4，讓分/受讓降1級")
            else:
                reasons.append(f"{sig.code}: {sig.message}")
            return grade

        # BTTS No / team under / win markets: record caution, but do not direct no_bet.
        reasons.append(f"{sig.code}: {sig.message}；本市場不套用Right Tail硬性No Bet")
        return grade

    # Weak-side transition is the correct hard gate for BTTS No and weak-team under.
    if sig.code == "WEAK_SIDE_TRANSITION_CHAIN":
        if is_btts or is_team_under:
            if sig.level == "no_bet":
                reasons.append(f"{sig.code}: {sig.message}")
                return "No Bet"
            if sig.level in {"downgrade", "reset"}:
                before = grade
                grade = _downgrade(grade, 1)
                if before != grade:
                    reasons.append(f"{sig.code}: {sig.message}，BTTS/單隊小降1級")
            elif sig.level == "caution":
                reasons.append(f"{sig.code}: {sig.message}")
            else:
                reasons.append(f"{sig.code}: {sig.message}")
            return grade

        if sig.level in {"downgrade", "reset"} and is_win:
            grade = _downgrade(grade, 1)
            reasons.append(f"{sig.code}: {sig.message}，勝負盤降1級")
        else:
            reasons.append(f"{sig.code}: {sig.message}")
        return grade

    # Dominance conversion still applies broadly to favorite win / handicap / team-over markets.
    if sig.code == "DOMINANCE_CONVERSION_RISK":
        if sig.level == "no_bet":
            reasons.append(f"{sig.code}: {sig.message}")
            return "No Bet"
        if sig.level in {"downgrade", "reset"}:
            before = grade
            grade = _downgrade(grade, 1)
            if before != grade:
                reasons.append(f"{sig.code}: {sig.message}，降1級")
        elif sig.level == "caution":
            reasons.append(f"{sig.code}: {sig.message}")
        return grade

    # Fallback for unknown gates.
    if sig.level == "no_bet":
        reasons.append(f"{sig.code}: {sig.message}")
        return "No Bet"
    if sig.level in {"reset", "downgrade"}:
        grade = _downgrade(grade, 1)
        reasons.append(f"{sig.code}: {sig.message}，降1級")
    elif sig.level == "caution":
        reasons.append(f"{sig.code}: {sig.message}")
    return grade


def grade_pick(
    bet_type: str,
    odds: float,
    model_probability: float,
    death_report: Optional[DeathScoreReport] = None,
    gate_signals: Optional[List[GateSignal]] = None,
) -> PickGrade:
    implied = implied_probability(odds)
    ev = model_probability * odds - 1.0
    grade = base_grade_from_ev(ev)
    base = grade
    reasons: List[str] = [f"EV={ev:.2%}, model={model_probability:.2%}, implied={implied:.2%}"]

    if death_report is not None and grade != "No Bet":
        grade = _apply_death_score_rules(grade, bet_type, death_report, reasons)

    for sig in gate_signals or []:
        if grade == "No Bet":
            break
        grade = _apply_market_specific_gate(grade, bet_type, sig, reasons)

    return PickGrade(
        bet_type=bet_type,
        odds=odds,
        model_probability=model_probability,
        implied_probability=implied,
        expected_roi=ev,
        base_grade=base,
        final_grade=grade,
        recommended_stake=stake_for_grade(grade),
        reasons=reasons,
    )
