from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


DEATH_SCORE_MAP: Dict[str, List[str]] = {
    "BTTS_YES": ["1-0", "2-0", "3-0", "0-1", "0-2", "0-3", "0-0"],
    "UNDER_2_5": ["2-1", "1-2", "3-0", "0-3", "2-2", "3-1", "1-3"],
    "AWAY_UNDER_0_5": ["1-1", "2-1", "0-1", "1-2", "2-2", "0-2"],
    "AWAY_UNDER_1_5": ["1-2", "2-2", "0-2", "1-3", "2-3", "0-3"],
    "HOME_UNDER_1_5": ["2-1", "2-0", "2-2", "3-1", "3-0"],
    "AWAY_PLUS_2": ["3-0", "3-1", "4-1", "4-0", "5-1", "5-0"],
    "HOME_WIN": ["0-0", "1-1", "0-1", "1-2", "0-2"],
}


@dataclass(frozen=True)
class StakeDecision:
    recommended_stake: int
    status: str  # keep / downgrade / test_only / no_bet
    reason: str
    death_count_top5: int
    death_probability_top5: float


def scenario_to_stake(
    bet_type: str,
    top_scores: List[Tuple[str, float]],
    base_stake: int = 200,
    low_odds: bool = False,
) -> StakeDecision:
    deaths = set(DEATH_SCORE_MAP.get(bet_type, []))
    death_count = 0
    death_prob = 0.0

    for score, prob in top_scores[:5]:
        if score in deaths:
            death_count += 1
            death_prob += prob

    if death_count >= 3 or death_prob >= 0.30:
        return StakeDecision(0, "no_bet", "死亡比分過多或前五死亡比分機率≥30%", death_count, death_prob)

    if death_count == 2 or death_prob >= 0.20:
        return StakeDecision(min(100, base_stake), "test_only", "死亡比分風險偏高，只允許100以下測試", death_count, death_prob)

    if death_count == 1:
        return StakeDecision(min(base_stake // 2, 100), "downgrade", "前五有死亡比分，金額降一級", death_count, death_prob)

    if low_odds:
        return StakeDecision(min(100, base_stake), "downgrade", "低賠薄價值，最多小測試", death_count, death_prob)

    return StakeDecision(base_stake, "keep", "未觸發死亡比分降級，但仍需過 Betting Filter", death_count, death_prob)


def combine_filter_decisions(base_stake: int, scenario: StakeDecision, data_gate_levels: List[str]) -> StakeDecision:
    if "no_bet" in data_gate_levels:
        return StakeDecision(0, "no_bet", scenario.reason + "；Data Gate 出現 no_bet", scenario.death_count_top5, scenario.death_probability_top5)
    if "reset" in data_gate_levels:
        return StakeDecision(min(scenario.recommended_stake, 100), "test_only", scenario.reason + "；Data Gate 觸發重置，只能測試", scenario.death_count_top5, scenario.death_probability_top5)
    if "downgrade" in data_gate_levels:
        return StakeDecision(min(scenario.recommended_stake, 100), "downgrade", scenario.reason + "；Data Gate 降級", scenario.death_count_top5, scenario.death_probability_top5)
    return scenario
