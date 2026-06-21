from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple


def poisson_probs(mu: float, max_goals: int) -> List[float]:
    if mu < 0:
        raise ValueError("mu must be non-negative")
    probs = []
    p = math.exp(-mu)
    probs.append(p)
    for k in range(1, max_goals + 1):
        p = p * mu / k
        probs.append(p)
    return probs


def normalize_grid(grid: List[List[float]]) -> List[List[float]]:
    total = sum(sum(row) for row in grid)
    if total <= 0:
        raise ValueError("grid mass must be positive")
    return [[v / total for v in row] for row in grid]


def poisson_score_grid(mu_home: float, mu_away: float, max_goals: int = 10) -> List[List[float]]:
    hp = poisson_probs(mu_home, max_goals)
    ap = poisson_probs(mu_away, max_goals)
    grid = [[hp[h] * ap[a] for a in range(max_goals + 1)] for h in range(max_goals + 1)]
    return normalize_grid(grid)


def apply_low_score_adjustment(
    grid: List[List[float]],
    mu_home: float,
    mu_away: float,
    rho: float = 0.0,
) -> List[List[float]]:
    # 輕量 Dixon-Coles 低比分修正，只當輔助，不是正式 fitted DC。
    out = [row[:] for row in grid]
    if rho == 0 or len(out) <= 1 or len(out[0]) <= 1:
        return out

    out[0][0] *= max(0.0, 1.0 - mu_home * mu_away * rho)
    out[1][0] *= max(0.0, 1.0 + mu_away * rho)
    out[0][1] *= max(0.0, 1.0 + mu_home * rho)
    out[1][1] *= max(0.0, 1.0 - rho)
    return normalize_grid(out)


def market_probabilities(grid: List[List[float]]) -> Dict[str, float]:
    n = len(grid)
    out = {
        "home_win": 0.0,
        "draw": 0.0,
        "away_win": 0.0,
        "over_2_5": 0.0,
        "under_2_5": 0.0,
        "over_3_5": 0.0,
        "under_3_5": 0.0,
        "btts_yes": 0.0,
        "btts_no": 0.0,
        "home_under_0_5": 0.0,
        "away_under_0_5": 0.0,
        "home_under_1_5": 0.0,
        "away_under_1_5": 0.0,
        "home_over_1_5": 0.0,
        "away_over_1_5": 0.0,
        "home_win_by_2_plus": 0.0,
        "away_win_by_2_plus": 0.0,
        "away_plus_2_three_way_like": 0.0,
        "home_exactly_win_by_2": 0.0,
        "home_win_by_3_plus": 0.0,
    }

    for h in range(n):
        for a in range(n):
            p = grid[h][a]
            if h > a:
                out["home_win"] += p
            elif h == a:
                out["draw"] += p
            else:
                out["away_win"] += p

            total = h + a
            if total >= 3:
                out["over_2_5"] += p
            else:
                out["under_2_5"] += p

            if total >= 4:
                out["over_3_5"] += p
            else:
                out["under_3_5"] += p

            if h >= 1 and a >= 1:
                out["btts_yes"] += p
            else:
                out["btts_no"] += p

            if h == 0:
                out["home_under_0_5"] += p
            if a == 0:
                out["away_under_0_5"] += p
            if h <= 1:
                out["home_under_1_5"] += p
            if a <= 1:
                out["away_under_1_5"] += p
            if h >= 2:
                out["home_over_1_5"] += p
            if a >= 2:
                out["away_over_1_5"] += p

            margin = h - a
            if margin >= 2:
                out["home_win_by_2_plus"] += p
            if margin <= -2:
                out["away_win_by_2_plus"] += p

            # 台灣運彩三項讓分盤近似：客隊 +2 過 = 主隊沒有贏 2 球以上。
            # 主隊剛好贏 2 球屬於讓分和局，要獨立看。
            if margin <= 1:
                out["away_plus_2_three_way_like"] += p
            if margin == 2:
                out["home_exactly_win_by_2"] += p
            if margin >= 3:
                out["home_win_by_3_plus"] += p

    return out


def top_scores(grid: List[List[float]], top_n: int = 10) -> List[Tuple[str, float]]:
    scores = []
    for h in range(len(grid)):
        for a in range(len(grid[h])):
            scores.append((f"{h}-{a}", grid[h][a]))
    return sorted(scores, key=lambda x: x[1], reverse=True)[:top_n]


@dataclass(frozen=True)
class ScoreModelResult:
    mu_home: float
    mu_away: float
    rho: float
    markets: Dict[str, float]
    top_scores: List[Tuple[str, float]]
    grid: List[List[float]]


def build_score_model(mu_home: float, mu_away: float, rho: float = 0.0, max_goals: int = 10) -> ScoreModelResult:
    grid = poisson_score_grid(mu_home, mu_away, max_goals=max_goals)
    grid = apply_low_score_adjustment(grid, mu_home, mu_away, rho=rho)
    return ScoreModelResult(
        mu_home=mu_home,
        mu_away=mu_away,
        rho=rho,
        markets=market_probabilities(grid),
        top_scores=top_scores(grid, top_n=10),
        grid=grid,
    )
