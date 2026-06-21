from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


def implied_probability(decimal_odds: float) -> float:
    if decimal_odds <= 1.0:
        raise ValueError("decimal_odds must be > 1.0")
    return 1.0 / decimal_odds


def fair_odds(probability: float) -> float:
    if probability <= 0:
        return float("inf")
    return 1.0 / probability


def remove_overround(probs: Iterable[float]) -> List[float]:
    probs = list(probs)
    total = sum(probs)
    if total <= 0:
        raise ValueError("probabilities must sum to a positive number")
    return [p / total for p in probs]


def no_vig_from_decimal_odds(odds: Iterable[float]) -> List[float]:
    implied = [implied_probability(o) for o in odds]
    return remove_overround(implied)


@dataclass(frozen=True)
class MarketPrice:
    name: str
    odds: Optional[float]
    model_probability: Optional[float] = None

    @property
    def break_even_probability(self) -> Optional[float]:
        if self.odds is None:
            return None
        return implied_probability(self.odds)

    @property
    def edge(self) -> Optional[float]:
        if self.model_probability is None or self.odds is None:
            return None
        return self.model_probability - implied_probability(self.odds)

    @property
    def expected_roi(self) -> Optional[float]:
        if self.model_probability is None or self.odds is None:
            return None
        p = self.model_probability
        return p * (self.odds - 1.0) - (1.0 - p)
