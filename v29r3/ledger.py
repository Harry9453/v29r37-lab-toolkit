from __future__ import annotations

import csv
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional


VALID_BOOKS = {"official", "test", "simulation", "real_money", "parlay", "pending"}
VALID_RESULTS = {"pending", "win", "loss", "push", "void", "half_win", "half_loss"}


@dataclass
class BetRecord:
    bet_id: str
    match: str
    bet_type: str
    stake: float
    odds: Optional[float]
    result: str = "pending"
    book: str = "simulation"
    profit: Optional[float] = None
    model_version: str = "V29-R3"
    notes: str = ""
    error_tags: List[str] = field(default_factory=list)

    def settle(self, result: str, odds: Optional[float] = None) -> "BetRecord":
        if result not in VALID_RESULTS:
            raise ValueError(f"invalid result: {result}")
        if odds is not None:
            self.odds = odds
        self.result = result

        if result == "win":
            self.profit = None if self.odds is None else self.stake * (self.odds - 1)
        elif result == "loss":
            self.profit = -self.stake
        elif result in {"push", "void"}:
            self.profit = 0.0
        elif result == "half_win":
            self.profit = None if self.odds is None else self.stake * 0.5 * (self.odds - 1)
        elif result == "half_loss":
            self.profit = -self.stake * 0.5
        return self

    def to_row(self) -> Dict[str, str]:
        row = asdict(self)
        row["error_tags"] = "|".join(self.error_tags)
        return row


class Ledger:
    def __init__(self) -> None:
        self.records: List[BetRecord] = []

    def add(self, record: BetRecord) -> None:
        if record.book not in VALID_BOOKS:
            raise ValueError(f"invalid book: {record.book}")
        if record.result not in VALID_RESULTS:
            raise ValueError(f"invalid result: {record.result}")
        self.records.append(record)

    def summary(self, include_books: Optional[List[str]] = None) -> Dict[str, float]:
        rows = self.records
        if include_books is not None:
            rows = [r for r in rows if r.book in include_books]
        settled = [r for r in rows if r.result != "pending" and r.profit is not None]
        stake = sum(r.stake for r in settled)
        profit = sum(r.profit or 0.0 for r in settled)
        roi = profit / stake if stake else 0.0
        return {"count": len(settled), "stake": stake, "profit": profit, "roi": roi}

    def to_csv(self, path: str | Path) -> None:
        path = Path(path)
        if not self.records:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.records[0].to_row().keys()))
            writer.writeheader()
            for r in self.records:
                writer.writerow(r.to_row())
