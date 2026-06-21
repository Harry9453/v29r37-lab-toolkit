from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class TeamMatchStats:
    shots_on_target: Optional[float] = None
    shots_off_target: Optional[float] = None
    corners: Optional[float] = None
    possession: Optional[float] = None
    attacks: Optional[float] = None
    dangerous_attacks: Optional[float] = None
    yellow_cards: Optional[float] = None
    red_cards: Optional[float] = None
    penalties: Optional[float] = None


@dataclass(frozen=True)
class DataGateSignal:
    level: str  # ok / caution / downgrade / no_bet / reset
    code: str
    message: str


def _safe_ratio(a: Optional[float], b: Optional[float]) -> Optional[float]:
    if a is None or b is None or b == 0:
        return None
    return a / b


def evaluate_data_gates(
    home: TeamMatchStats,
    away: TeamMatchStats,
    home_name: str = "Home",
    away_name: str = "Away",
) -> List[DataGateSignal]:
    signals: List[DataGateSignal] = []

    if home.shots_on_target is not None and home.shots_on_target >= 7:
        signals.append(DataGateSignal("reset", "HOME_SOT_RIGHT_TAIL", f"{home_name} 射正≥7，強隊3+右尾上修"))

    if away.shots_on_target is not None and away.shots_on_target >= 4:
        signals.append(DataGateSignal("caution", "AWAY_GOAL_RISK", f"{away_name} 射正≥4，不能輕買 {away_name} 小0.5"))

    if (
        away.shots_on_target is not None
        and away.possession is not None
        and away.shots_on_target <= 2
        and away.possession >= 55
    ):
        signals.append(DataGateSignal("downgrade", "POSSESSION_NO_CONVERSION", f"{away_name} 控球高但射正≤2，BTTS是降級"))

    ratio = _safe_ratio(home.dangerous_attacks, away.dangerous_attacks)
    if ratio is not None:
        if ratio >= 3:
            signals.append(DataGateSignal("no_bet", "DANGEROUS_ATTACK_GAP_3X", f"{home_name} 危險進攻是 {away_name} 3倍以上，{away_name} 受讓高危"))
        elif ratio >= 2:
            signals.append(DataGateSignal("downgrade", "DANGEROUS_ATTACK_GAP_2X", f"{home_name} 危險進攻明顯領先，{away_name} 受讓降級"))

    conditions = 0
    if home.shots_on_target is not None and away.shots_on_target is not None and home.shots_on_target - away.shots_on_target >= 5:
        conditions += 1
    if home.corners is not None and away.corners is not None and home.corners - away.corners >= 8:
        conditions += 1
    if home.possession is not None and home.possession >= 65:
        conditions += 1
    if ratio is not None and ratio >= 3:
        conditions += 1
    if away.red_cards is not None and away.red_cards >= 1:
        conditions += 1
    if away.shots_on_target is not None and away.shots_on_target <= 1:
        conditions += 1

    if conditions >= 3:
        signals.append(DataGateSignal("reset", "EXTREME_DOMINATION_RESET", f"極端壓制觸發{conditions}項，比分分布重置，強隊大勝右尾上修"))

    if away.red_cards is not None and away.red_cards >= 1:
        pressure = 0
        if away.yellow_cards is not None and away.yellow_cards >= 2:
            pressure += 1
        if ratio is not None and ratio >= 2:
            pressure += 1
        if home.corners is not None and away.corners is not None and home.corners > away.corners:
            pressure += 1
        if pressure >= 2:
            signals.append(DataGateSignal("reset", "PRESSURE_INDUCED_RED_CARD", f"{away_name} 紅牌可能是長時間承壓結果，不當純偶發"))

    return signals
