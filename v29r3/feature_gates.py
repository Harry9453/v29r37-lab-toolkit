from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class GateSignal:
    level: str  # ok / caution / downgrade / no_bet / reset
    code: str
    score: float
    message: str


# ---------------------------------------------------------------------------
# Existing V29-R3.7 Gates
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# V29-R3.7a Right-Tail Calibration Patch
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LowBlockFragilityFactors:
    weak_team_back_five_or_low_block: bool = False
    early_goal_concession_risk: bool = False
    poor_escape_ball_or_buildout: bool = False
    favorite_has_wide_overload: bool = False
    favorite_has_box_finisher: bool = False
    favorite_needs_goal_difference: bool = False


def evaluate_low_block_fragility(f: LowBlockFragilityFactors) -> GateSignal:
    """
    Low Block ≠ Stable Under.
    If a weak side's low block can be broken early, Under 2.5 / 3.5 must be downgraded.
    """
    score = sum([
        f.weak_team_back_five_or_low_block,
        f.early_goal_concession_risk,
        f.poor_escape_ball_or_buildout,
        f.favorite_has_wide_overload,
        f.favorite_has_box_finisher,
        f.favorite_needs_goal_difference,
    ])
    if score >= 5:
        return GateSignal(
            "no_bet",
            "LOW_BLOCK_FRAGILITY",
            float(score),
            "低位防守脆弱且早球後易崩：Under 3.5 不得升A，Under 2.5嚴格不買",
        )
    if score >= 4:
        return GateSignal(
            "downgrade",
            "LOW_BLOCK_FRAGILITY",
            float(score),
            "低位防守不等於穩定小球：小球降級",
        )
    if score >= 3:
        return GateSignal(
            "caution",
            "LOW_BLOCK_FRAGILITY",
            float(score),
            "低位防守有破局風險：需檢查3-0/4-0/3-1",
        )
    return GateSignal("ok", "LOW_BLOCK_FRAGILITY", float(score), "低位破局風險未明顯觸發")


@dataclass(frozen=True)
class EarlyFavoriteBurstFactors:
    early_goal_path: bool = False
    favorite_multi_point_attack: bool = False
    weak_side_cannot_chase_game: bool = False
    favorite_pressing_after_lead: bool = False
    weak_side_defensive_confidence_low: bool = False


def evaluate_early_favorite_burst(f: EarlyFavoriteBurstFactors) -> GateSignal:
    """
    Early Favorite Burst Rule.
    Strong favorite early goal path creates 3-0 / 4-0 right-tail branch.
    """
    score = sum([
        f.early_goal_path,
        f.favorite_multi_point_attack,
        f.weak_side_cannot_chase_game,
        f.favorite_pressing_after_lead,
        f.weak_side_defensive_confidence_low,
    ])
    if score >= 4:
        return GateSignal(
            "downgrade",
            "EARLY_FAVORITE_BURST",
            float(score),
            "強隊早球爆發條件完整：3-0/4-0/5-0分支上修，小3.5降級",
        )
    if score >= 3:
        return GateSignal(
            "caution",
            "EARLY_FAVORITE_BURST",
            float(score),
            "強隊有早球後連續進球條件：右尾需上修",
        )
    return GateSignal("ok", "EARLY_FAVORITE_BURST", float(score), "早球爆發條件未明顯觸發")


@dataclass(frozen=True)
class CreativeReplacementFactors:
    star_creator_absent: bool = False
    central_link_player_available: bool = False
    wide_breaker_available: bool = False
    box_finisher_available: bool = False
    second_ball_midfield_cover: bool = False


def evaluate_creative_replacement(f: CreativeReplacementFactors) -> GateSignal:
    """
    Creative Absence Replacement Chain.
    A missing creator does not automatically mean under if the replacement chain is complete.
    """
    replacement_score = sum([
        f.central_link_player_available,
        f.wide_breaker_available,
        f.box_finisher_available,
        f.second_ball_midfield_cover,
    ])

    if not f.star_creator_absent:
        return GateSignal("ok", "CREATIVE_REPLACEMENT_CHAIN", float(replacement_score), "未觸發主創缺陣修正")

    if replacement_score >= 4:
        return GateSignal(
            "downgrade",
            "CREATIVE_REPLACEMENT_CHAIN",
            float(replacement_score),
            "主創缺陣但替代進攻鏈完整：不得因缺陣自動壓低總進球，強隊右尾保留",
        )
    if replacement_score >= 2:
        return GateSignal(
            "caution",
            "CREATIVE_REPLACEMENT_CHAIN",
            float(replacement_score),
            "主創缺陣但仍有部分替代鏈：進攻下修幅度需保守",
        )
    return GateSignal(
        "ok",
        "CREATIVE_REPLACEMENT_CHAIN",
        float(replacement_score),
        "主創缺陣且替代鏈不足：可下修進攻",
    )


@dataclass(frozen=True)
class ManagerShockFactors:
    recent_heavy_loss: bool = False
    interim_or_new_manager: bool = False
    short_preparation_days: bool = False
    opponent_high_control_favorite: bool = False
    defensive_confidence_low: bool = False


def evaluate_manager_shock(f: ManagerShockFactors) -> GateSignal:
    """
    Manager Shock ≠ Defensive Reset.
    A new manager after a heavy loss is not automatically a defensive upgrade.
    """
    score = sum([
        f.recent_heavy_loss,
        f.interim_or_new_manager,
        f.short_preparation_days,
        f.opponent_high_control_favorite,
        f.defensive_confidence_low,
    ])
    if score >= 4:
        return GateSignal(
            "downgrade",
            "MANAGER_SHOCK_NOT_RESET",
            float(score),
            "換帥不等於防守修復：強隊3+機率上修，小球降級",
        )
    if score >= 3:
        return GateSignal(
            "caution",
            "MANAGER_SHOCK_NOT_RESET",
            float(score),
            "換帥修復效果不明：不得自動上修防守穩定",
        )
    return GateSignal("ok", "MANAGER_SHOCK_NOT_RESET", float(score), "換帥風險未明顯觸發")


# ---------------------------------------------------------------------------
# V29-R3.7a-2 Deep Right Tail Split Patch
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DeepRightTailFactors:
    """
    Split right-tail risk into clean-sheet and BTTS-tail forms.

    clean_sheet_tail:
        3-0 / 4-0 / 5-0 pattern. Under 3.5 dangerous, BTTS No can remain playable.

    btts_tail:
        3-1 / 4-1 / 4-2 / 5-1 / 5-2 pattern.
        Under 3.5 dangerous and BTTS No should be downgraded or killed.
    """
    favorite_multi_point_attack: bool = False
    favorite_late_push_or_sub_firepower: bool = False
    favorite_can_score_after_lead: bool = False
    weak_side_low_block_or_fragile_backline: bool = False

    weak_side_transition_chain: bool = False
    weak_side_set_piece_threat: bool = False
    weak_side_projected_sot_two_plus: bool = False
    match_can_open_both_ways: bool = False

    favorite_defensive_control: bool = False
    favorite_press_suppresses_counters: bool = False


def evaluate_deep_right_tail(f: DeepRightTailFactors) -> GateSignal:
    clean_score = sum([
        f.favorite_multi_point_attack,
        f.favorite_late_push_or_sub_firepower,
        f.favorite_can_score_after_lead,
        f.weak_side_low_block_or_fragile_backline,
        f.favorite_defensive_control,
        f.favorite_press_suppresses_counters,
    ])

    btts_score = sum([
        f.favorite_multi_point_attack,
        f.favorite_late_push_or_sub_firepower,
        f.favorite_can_score_after_lead,
        f.weak_side_transition_chain,
        f.weak_side_set_piece_threat,
        f.weak_side_projected_sot_two_plus,
        f.match_can_open_both_ways,
    ])

    if btts_score >= 5 and btts_score >= clean_score:
        level = "no_bet" if btts_score >= 6 else "downgrade"
        return GateSignal(
            level,
            "DEEP_RIGHT_TAIL_BTTS",
            float(btts_score),
            f"BTTS型深右尾：4-1/5-1/4-2分支上修；BTTS否與小3.5降級或不買；clean_score={clean_score}",
        )

    if clean_score >= 5 and clean_score > btts_score:
        level = "downgrade"
        return GateSignal(
            level,
            "DEEP_RIGHT_TAIL_CLEAN_SHEET",
            float(clean_score),
            f"零封型深右尾：3-0/4-0/5-0分支上修；小3.5降級，但BTTS否不被右尾硬殺；btts_score={btts_score}",
        )

    if max(clean_score, btts_score) >= 4:
        return GateSignal(
            "caution",
            "DEEP_RIGHT_TAIL_MIXED",
            float(max(clean_score, btts_score)),
            f"混合型右尾：需同時檢查3-0/4-0與3-1/4-1；clean_score={clean_score}, btts_score={btts_score}",
        )

    return GateSignal(
        "ok",
        "DEEP_RIGHT_TAIL_NONE",
        float(max(clean_score, btts_score)),
        f"深右尾未明顯觸發；clean_score={clean_score}, btts_score={btts_score}",
    )


def scoreline_in(scoreline: str, candidates: Iterable[str]) -> bool:
    return scoreline.replace(" ", "") in {c.replace(" ", "") for c in candidates}


def worst_gate_level(signals: List[GateSignal]) -> str:
    order = {"ok": 0, "caution": 1, "downgrade": 2, "reset": 3, "no_bet": 4}
    if not signals:
        return "ok"
    return max((s.level for s in signals), key=lambda x: order.get(x, 0))
