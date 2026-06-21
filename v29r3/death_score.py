from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

Score = Tuple[int, int]


def _parse_score(score: str) -> Score:
    h, a = score.split("-")
    return int(h), int(a)


def success_predicate(bet_type: str) -> Callable[[int, int], bool]:
    key = bet_type.upper()
    table: Dict[str, Callable[[int, int], bool]] = {
        "UNDER_2_5": lambda h, a: h + a <= 2,
        "OVER_2_5": lambda h, a: h + a >= 3,
        "UNDER_3_5": lambda h, a: h + a <= 3,
        "OVER_3_5": lambda h, a: h + a >= 4,
        "BTTS_YES": lambda h, a: h >= 1 and a >= 1,
        "BTTS_NO": lambda h, a: h == 0 or a == 0,
        "HOME_UNDER_0_5": lambda h, a: h == 0,
        "AWAY_UNDER_0_5": lambda h, a: a == 0,
        "HOME_UNDER_1_5": lambda h, a: h <= 1,
        "AWAY_UNDER_1_5": lambda h, a: a <= 1,
        "HOME_OVER_1_5": lambda h, a: h >= 2,
        "AWAY_OVER_1_5": lambda h, a: a >= 2,
        "HOME_WIN": lambda h, a: h > a,
        "AWAY_WIN": lambda h, a: a > h,
        "DRAW": lambda h, a: h == a,
        "HOME_WIN_BY_2_PLUS": lambda h, a: h - a >= 2,
        "AWAY_WIN_BY_2_PLUS": lambda h, a: a - h >= 2,
        "AWAY_PLUS_2_THREE_WAY_LIKE": lambda h, a: h - a <= 1,
        "HOME_EXACTLY_WIN_BY_2": lambda h, a: h - a == 2,
        "HOME_WIN_BY_3_PLUS": lambda h, a: h - a >= 3,
        "TOTAL_GOALS_2_3": lambda h, a: 2 <= h + a <= 3,
    }
    if key not in table:
        raise ValueError(f"unsupported bet_type for death score analysis: {bet_type}")
    return table[key]


@dataclass(frozen=True)
class DeathScoreReport:
    bet_type: str
    top_n: int
    death_count_top_n: int
    death_probability_top_n: float
    death_probability_total: float
    top_death_scores: List[Tuple[str, float]]
    top_safe_scores: List[Tuple[str, float]]
    top1_is_death: bool
    top3_death_count: int
    top5_death_count: int
    top10_death_count: int


def analyse_death_scores(
    grid: List[List[float]],
    bet_type: str,
    *,
    top_n: int = 10,
) -> DeathScoreReport:
    predicate = success_predicate(bet_type)
    all_scores: List[Tuple[str, float, bool]] = []
    death_probability_total = 0.0
    for h, row in enumerate(grid):
        for a, p in enumerate(row):
            is_death = not predicate(h, a)
            all_scores.append((f"{h}-{a}", p, is_death))
            if is_death:
                death_probability_total += p

    ranked = sorted(all_scores, key=lambda x: x[1], reverse=True)
    top = ranked[:top_n]
    top_deaths = [(score, p) for score, p, is_death in top if is_death]
    top_safe = [(score, p) for score, p, is_death in top if not is_death]

    def death_count(k: int) -> int:
        return sum(1 for _, _, is_death in ranked[:k] if is_death)

    return DeathScoreReport(
        bet_type=bet_type.upper(),
        top_n=top_n,
        death_count_top_n=len(top_deaths),
        death_probability_top_n=sum(p for _, p in top_deaths),
        death_probability_total=death_probability_total,
        top_death_scores=top_deaths,
        top_safe_scores=top_safe,
        top1_is_death=ranked[0][2] if ranked else False,
        top3_death_count=death_count(3),
        top5_death_count=death_count(5),
        top10_death_count=death_count(10),
    )
