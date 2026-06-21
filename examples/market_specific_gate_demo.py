from v29r3 import (
    RightTailFactors,
    WeakSideTransitionFactors,
    evaluate_right_tail,
    evaluate_weak_side_transition,
    grade_pick,
)

signals = [
    evaluate_right_tail(RightTailFactors(
        multi_point_attack=True,
        opponent_defensive_instability=True,
        substitute_firepower=True,
        early_goal_pressure=True,
        opponent_wide_protection_weak=True,
        goal_difference_need=True,
    )),
    evaluate_weak_side_transition(WeakSideTransitionFactors(
        pace_wide_player=True,
        shot_creating_winger_or_ten=False,
        late_arriving_midfielder=False,
        set_piece_height=True,
        opponent_fullbacks_high=True,
        projected_sot_at_least_two=False,
    )),
]

print("Gate signals:")
for s in signals:
    print(f"- {s.code}: {s.level} | score={s.score} | {s.message}")

under35 = grade_pick(
    bet_type="Under 3.5",
    odds=1.45,
    model_probability=0.7161,
    death_report=None,
    gate_signals=signals,
)

btts_no = grade_pick(
    bet_type="BTTS No",
    odds=1.65,
    model_probability=0.6951,
    death_report=None,
    gate_signals=signals,
)

print("\nUnder 3.5 result")
print("base:", under35.base_grade)
print("final:", under35.final_grade)
print("stake:", under35.recommended_stake)
for r in under35.reasons:
    print("-", r)

print("\nBTTS No result")
print("base:", btts_no.base_grade)
print("final:", btts_no.final_grade)
print("stake:", btts_no.recommended_stake)
for r in btts_no.reasons:
    print("-", r)
