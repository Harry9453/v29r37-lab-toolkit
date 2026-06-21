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

    for sig in gate_signals or []:
        if grade == "No Bet":
            break
        if sig.level == "no_bet":
            grade = "No Bet"
            reasons.append(f"{sig.code}: {sig.message}")
        elif sig.level in {"reset", "downgrade"}:
            grade = _downgrade(grade, 1)
            reasons.append(f"{sig.code}: {sig.message}，降1級")
        elif sig.level == "caution":
            reasons.append(f"{sig.code}: {sig.message}")

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
