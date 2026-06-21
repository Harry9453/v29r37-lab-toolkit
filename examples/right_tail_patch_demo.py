from v29r3 import (
    GateSignal,
    LowBlockFragilityFactors,
    EarlyFavoriteBurstFactors,
    CreativeReplacementFactors,
    ManagerShockFactors,
    RightTailFactors,
    evaluate_low_block_fragility,
    evaluate_early_favorite_burst,
    evaluate_creative_replacement,
    evaluate_manager_shock,
    evaluate_right_tail,
    grade_pick,
)


def show(label, signal):
    print(f"{label}: {signal.level} | score={signal.score} | {signal.message}")


# Demo case: strong favorite vs low block, learned from Japan 4-0 Tunisia and Spain 4-0 Saudi.
signals = [
    evaluate_right_tail(RightTailFactors(
        multi_point_attack=True,
        opponent_defensive_instability=True,
        substitute_firepower=True,
        early_goal_pressure=True,
        opponent_wide_protection_weak=True,
        goal_difference_need=True,
    )),
    evaluate_low_block_fragility(LowBlockFragilityFactors(
        weak_team_back_five_or_low_block=True,
        early_goal_concession_risk=True,
        poor_escape_ball_or_buildout=True,
        favorite_has_wide_overload=True,
        favorite_has_box_finisher=True,
    )),
    evaluate_early_favorite_burst(EarlyFavoriteBurstFactors(
        early_goal_path=True,
        favorite_multi_point_attack=True,
        weak_side_cannot_chase_game=True,
        favorite_pressing_after_lead=True,
    )),
    evaluate_creative_replacement(CreativeReplacementFactors(
        star_creator_absent=True,
        central_link_player_available=True,
        wide_breaker_available=True,
        box_finisher_available=True,
        second_ball_midfield_cover=True,
    )),
    evaluate_manager_shock(ManagerShockFactors(
        recent_heavy_loss=True,
        interim_or_new_manager=True,
        short_preparation_days=True,
        opponent_high_control_favorite=True,
    )),
]

for i, s in enumerate(signals, 1):
    show(f"Gate {i}", s)

# No death_report in this demo; this checks market-specific gate behavior.
pick = grade_pick(
    bet_type="Under 3.5",
    odds=1.45,
    model_probability=0.7161,
    death_report=None,
    gate_signals=signals,
)

print("\nPick result")
print("base_grade:", pick.base_grade)
print("final_grade:", pick.final_grade)
print("recommended_stake:", pick.recommended_stake)
print("reasons:")
for r in pick.reasons:
    print("-", r)
