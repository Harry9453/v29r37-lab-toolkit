from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class GateSignal:
    level: str  # ok / caution / downgrade / no_bet / reset
    code: str
    score: float
    message: str


@dataclass(frozen=True)
class RightTailFactors:
    elite_midfield_return: bool = False
    multi_point_attack: bool = False
    opponent_defensive_instability: bool = False
    opponent_attacks_but_leaves_space: bool = False
    home_or_morale_edge: bool = False
    goal_difference_need: bool = False
    substitute_firepower: bool = False
    early_goal_pressure: bool = False
    opponent_wide_protection_weak: bool = False


def evaluate_right_tail(f: RightTailFactors) -> GateSignal:
    score = 0.0
    if f.elite_midfield_return:
        score += 1.0
    if f.multi_point_attack:
        score += 1.0
    if f.opponent_defensive_instability:
        score += 1.0
    if f.opponent_attacks_but_leaves_space:
        score += 0.5
    if f.home_or_morale_edge:
        score += 0.5
    if f.goal_difference_need:
        score += 0.5
    if f.substitute_firepower:
        score += 0.5
    if f.early_goal_pressure:
        score += 0.5
    if f.opponent_wide_protection_weak:
        score += 1.0

    if score >= 5.0:
        level = "no_bet"
        msg = "Right Tail 極高：小3.5與弱隊受讓需嚴格降級或不買"
    elif score >= 3.5:
        level = "downgrade"
        msg = "Right Tail 高：小2.5降級，小3.5至少降半級"
    elif score >= 2.0:
        level = "caution"
        msg = "Right Tail 中：3-0/3-1/4-1分支上修"
    else:
        level = "ok"
        msg = "Right Tail 低或中低"
    return GateSignal(level, "RIGHT_TAIL_SCORE", score, msg)


@dataclass(frozen=True)
class WeakSideTransitionFactors:
    pace_wide_player: bool = False
    shot_creating_winger_or_ten: bool = False
    late_arriving_midfielder: bool = False
    set_piece_height: bool = False
    opponent_fullbacks_high: bool = False
    projected_sot_at_least_two: bool = False


def evaluate_weak_side_transition(f: WeakSideTransitionFactors) -> GateSignal:
    score = sum([
        f.pace_wide_player,
        f.shot_creating_winger_or_ten,
        f.late_arriving_midfielder,
        f.set_piece_height,
        f.opponent_fullbacks_high,
        f.projected_sot_at_least_two,
    ])
    if score >= 4:
        return GateSignal("downgrade", "WEAK_SIDE_TRANSITION_CHAIN", float(score), "弱隊進球鏈完整：弱隊小0.5與BTTS否降級")
    if score >= 3:
        return GateSignal("caution", "WEAK_SIDE_TRANSITION_CHAIN", float(score), "弱隊有明顯偷球鏈：單隊小0.5最多B-/C")
    return GateSignal("ok", "WEAK_SIDE_TRANSITION_CHAIN", float(score), "弱隊進球鏈不足")


@dataclass(frozen=True)
class DominanceConversionFactors:
    high_possession: bool = False
    many_shots_low_sot_rate: bool = False
    many_corners_low_header_quality: bool = False
    relies_on_crosses_or_long_shots: bool = False
    opponent_deep_low_block: bool = False
    lacks_box_finisher: bool = False


def evaluate_dominance_conversion(f: DominanceConversionFactors) -> GateSignal:
    score = sum([
        f.high_possession,
        f.many_shots_low_sot_rate,
        f.many_corners_low_header_quality,
        f.relies_on_crosses_or_long_shots,
        f.opponent_deep_low_block,
        f.lacks_box_finisher,
    ])
    if score >= 4:
        return GateSignal("downgrade", "DOMINANCE_CONVERSION_RISK", float(score), "壓制不等於轉化：熱門勝/讓分/單隊大降級")
    if score >= 3:
        return GateSignal("caution", "DOMINANCE_CONVERSION_RISK", float(score), "轉化風險偏高：不能只看控球與角球")
    return GateSignal("ok", "DOMINANCE_CONVERSION_RISK", float(score), "轉化風險未明顯觸發")


def worst_gate_level(signals: List[GateSignal]) -> str:
    order = {"ok": 0, "caution": 1, "downgrade": 2, "reset": 3, "no_bet": 4}
    if not signals:
        return "ok"
    return max((s.level for s in signals), key=lambda x: order.get(x, 0))
