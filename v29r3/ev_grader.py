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


def _is_under_market(bet_type: str) -> bool:
    b = bet_type.lower().replace(" ", "")
    return "under" in b or "小" in b


def _is_under_25(bet_type: str) -> bool:
    b = bet_type.lower().replace(" ", "")
    return any(k in b for k in ["under2.5", "u2.5", "小2.5"])


def _is_under_35(bet_type: str) -> bool:
    b = bet_type.lower().replace(" ", "")
    return any(k in b for k in ["under3.5", "u3.5", "小3.5"])


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

    is_under = _is_under_market(bet_type)
    is_u25 = _is_under_25(bet_type)
    is_u35 = _is_under_35(bet_type)

    if death_report is not None and grade != "No Bet":
        if death_report.death_probability_top_n >= 0.45:
            grade = "No Bet"
            reasons.append("Top10死亡比分機率≥45%，No Bet")
        elif death_report.death_probability_top_n >= 0.35:
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

        # V29-R3.7a: under markets cannot be A when death-score concentration is meaningful.
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

    for sig in gate_signals or []:
        if grade == "No Bet":
            break

        # General gate behavior from V29-R3.7
        if sig.level == "no_bet":
            grade = "No Bet"
            reasons.append(f"{sig.code}: {sig.message}")
            break
        elif sig.level in {"reset", "downgrade"}:
            grade = _downgrade(grade, 1)
            reasons.append(f"{sig.code}: {sig.message}，降1級")
        elif sig.level == "caution":
            reasons.append(f"{sig.code}: {sig.message}")

        # V29-R3.7a market-specific hard filters.
        if grade == "No Bet":
            break

        if is_u35 and sig.code in {
            "RIGHT_TAIL_SCORE",
            "LOW_BLOCK_FRAGILITY",
            "EARLY_FAVORITE_BURST",
            "CREATIVE_REPLACEMENT_CHAIN",
            "MANAGER_SHOCK_NOT_RESET",
        }:
            if sig.score >= 5:
                grade = "No Bet"
                reasons.append(f"{sig.code}: 分數≥5，小3.5在強右尾/低位破局局面不買")
                break
            if sig.score >= 4:
                before = grade
                grade = _cap_grade(_downgrade(grade, 1), "B")
                if before != grade:
                    reasons.append(f"{sig.code}: 分數≥4，小3.5額外降級且最高B")

        if is_u25 and sig.code in {"RIGHT_TAIL_SCORE", "LOW_BLOCK_FRAGILITY", "EARLY_FAVORITE_BURST"}:
            if sig.score >= 4:
                before = grade
                grade = _downgrade(grade, 1)
                if before != grade:
                    reasons.append(f"{sig.code}: 分數≥4，小2.5額外降級")

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
