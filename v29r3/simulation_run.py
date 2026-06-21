from __future__ import annotations

import csv
import json
import random
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .score_model import market_probabilities, top_scores


@dataclass(frozen=True)
class Scenario:
    name: str
    weight: float
    mu_home: float
    mu_away: float
    rho: float = 0.0  # reserved for future analytical scenario support
    tags: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.name:
            raise ValueError("scenario name is required")
        if self.weight <= 0:
            raise ValueError(f"scenario {self.name}: weight must be > 0")
        if self.mu_home < 0 or self.mu_away < 0:
            raise ValueError(f"scenario {self.name}: mu values must be non-negative")


@dataclass(frozen=True)
class SimulationMeta:
    run_id: str
    model_version: str
    match_name: str
    seed: int
    n: int
    max_goals: int
    data_status: str  # clean / live / result_exposed / proxy / audit
    ledger_type: str  # official / test / simulation / live / user_override / audit
    created_at_unix: float


@dataclass(frozen=True)
class SimulationRunResult:
    meta: SimulationMeta
    scenarios: List[Scenario]
    scenario_counts: Dict[str, int]
    markets: Dict[str, float]
    top_scores: List[Tuple[str, float]]
    grid: List[List[float]]
    score_counts: Dict[str, int]

    def to_json_dict(self) -> Dict[str, object]:
        return {
            "meta": asdict(self.meta),
            "scenarios": [asdict(s) for s in self.scenarios],
            "scenario_counts": self.scenario_counts,
            "markets": self.markets,
            "top_scores": self.top_scores,
            "score_counts": self.score_counts,
        }

    def write_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_json_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def write_top_scores_csv(self, path: str | Path) -> None:
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["rank", "score", "probability"])
            for i, (score, prob) in enumerate(self.top_scores, start=1):
                w.writerow([i, score, prob])

    def write_markets_csv(self, path: str | Path) -> None:
        with Path(path).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["market", "probability"])
            for k in sorted(self.markets):
                w.writerow([k, self.markets[k]])


def _normalise_scenarios(scenarios: List[Scenario]) -> List[Scenario]:
    if not scenarios:
        raise ValueError("at least one scenario is required")
    for s in scenarios:
        s.validate()
    total = sum(s.weight for s in scenarios)
    return [Scenario(s.name, s.weight / total, s.mu_home, s.mu_away, s.rho, list(s.tags)) for s in scenarios]


def _sample_scenario(rng: random.Random, scenarios: List[Scenario]) -> Scenario:
    x = rng.random()
    cumulative = 0.0
    for s in scenarios:
        cumulative += s.weight
        if x <= cumulative:
            return s
    return scenarios[-1]


def _sample_poisson_knuth(rng: random.Random, mu: float) -> int:
    # Pure-Python Poisson sampler. Efficient enough for football lambdas and reproducible with random.Random.
    # For large mu, switch to normal approximation later if needed; current football use is usually < 5.
    if mu < 0:
        raise ValueError("mu must be non-negative")
    if mu == 0:
        return 0
    # Avoid importing math in hot path repeatedly.
    import math

    limit = math.exp(-mu)
    k = 0
    p = 1.0
    while p > limit:
        k += 1
        p *= rng.random()
    return k - 1


def run_monte_carlo_mixture(
    match_name: str,
    scenarios: List[Scenario],
    *,
    n: int = 300_000,
    seed: int = 20260621,
    max_goals: int = 10,
    model_version: str = "V29-R3.7-Lab",
    data_status: str = "clean",
    ledger_type: str = "simulation",
    run_id: Optional[str] = None,
) -> SimulationRunResult:
    if n <= 0:
        raise ValueError("n must be > 0")
    if max_goals < 3:
        raise ValueError("max_goals should be at least 3")

    scenarios = _normalise_scenarios(scenarios)
    rng = random.Random(seed)
    run_id = run_id or f"sim_{uuid.uuid4().hex[:10]}"

    grid_counts = [[0 for _ in range(max_goals + 1)] for _ in range(max_goals + 1)]
    scenario_counts: Dict[str, int] = {s.name: 0 for s in scenarios}
    score_counts: Dict[str, int] = {}

    for _ in range(n):
        s = _sample_scenario(rng, scenarios)
        scenario_counts[s.name] += 1
        h = _sample_poisson_knuth(rng, s.mu_home)
        a = _sample_poisson_knuth(rng, s.mu_away)
        # Keep all tail mass inside the grid instead of dropping it.
        h = min(h, max_goals)
        a = min(a, max_goals)
        grid_counts[h][a] += 1
        key = f"{h}-{a}"
        score_counts[key] = score_counts.get(key, 0) + 1

    grid = [[c / n for c in row] for row in grid_counts]
    meta = SimulationMeta(
        run_id=run_id,
        model_version=model_version,
        match_name=match_name,
        seed=seed,
        n=n,
        max_goals=max_goals,
        data_status=data_status,
        ledger_type=ledger_type,
        created_at_unix=time.time(),
    )
    return SimulationRunResult(
        meta=meta,
        scenarios=scenarios,
        scenario_counts=scenario_counts,
        markets=market_probabilities(grid),
        top_scores=top_scores(grid, top_n=10),
        grid=grid,
        score_counts=score_counts,
    )
