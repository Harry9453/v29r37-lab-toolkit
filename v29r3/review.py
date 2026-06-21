from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class MatchReview:
    match: str
    score: str
    model_hits: List[str]
    model_misses: List[str]
    error_tags: List[str]
    ledger_update: str
    rule_updates: List[str]

    def to_markdown(self) -> str:
        lines = [f"# {self.match} 復盤", "", f"終場：**{self.score}**", ""]
        lines.append("## 命中項")
        lines += [f"- {x}" for x in self.model_hits]
        lines.append("")
        lines.append("## 錯誤項")
        lines += [f"- {x}" for x in self.model_misses]
        lines.append("")
        lines.append("## 錯誤標籤")
        lines += [f"- {x}" for x in self.error_tags]
        lines.append("")
        lines.append("## 帳本更新")
        lines.append(self.ledger_update)
        lines.append("")
        lines.append("## 規則更新")
        lines += [f"- {x}" for x in self.rule_updates]
        return "\n".join(lines)


def classify_from_stats(
    home_goals: int,
    away_goals: int,
    home_sot: int,
    away_sot: int,
    home_dangerous: int,
    away_dangerous: int,
    away_red: int = 0,
) -> List[str]:
    tags: List[str] = []
    if home_goals >= 4:
        tags.append("強隊右尾低估")
    if away_goals == 0 and away_sot <= 1:
        tags.append("弱隊進球上限判斷正確")
    if home_sot - away_sot >= 5:
        tags.append("射正差距導致比分重置")
    if away_dangerous > 0 and home_dangerous / away_dangerous >= 3:
        tags.append("危險進攻極端差距")
    if away_red >= 1:
        tags.append("紅牌後比分分布重置")
    return tags
