from v29r3 import (
    DeepRightTailFactors,
    evaluate_deep_right_tail,
    grade_pick,
)

clean_sheet_tail = evaluate_deep_right_tail(DeepRightTailFactors(
    favorite_multi_point_attack=True,
    favorite_late_push_or_sub_firepower=True,
    favorite_can_score_after_lead=True,
    weak_side_low_block_or_fragile_backline=True,
    favorite_defensive_control=True,
    favorite_press_suppresses_counters=True,
    weak_side_transition_chain=False,
    weak_side_set_piece_threat=False,
    weak_side_projected_sot_two_plus=False,
    match_can_open_both_ways=False,
))

btts_tail = evaluate_deep_right_tail(DeepRightTailFactors(
    favorite_multi_point_attack=True,
    favorite_late_push_or_sub_firepower=True,
    favorite_can_score_after_lead=True,
    weak_side_low_block_or_fragile_backline=True,
    weak_side_transition_chain=True,
    weak_side_set_piece_threat=True,
    weak_side_projected_sot_two_plus=True,
    match_can_open_both_ways=True,
    favorite_defensive_control=False,
    favorite_press_suppresses_counters=False,
))

print("Clean-sheet right tail signal")
print(clean_sheet_tail)
print("\nBTTS right tail signal")
print(btts_tail)

markets = [
    ("Under 3.5", 1.45, 0.72),
    ("BTTS No", 1.65, 0.70),
    ("BTTS Yes", 1.95, 0.55),
    ("Over 2.5", 1.85, 0.58),
]

print("\n--- Clean-sheet tail market behavior ---")
for bet_type, odds, prob in markets:
    pick = grade_pick(bet_type, odds, prob, gate_signals=[clean_sheet_tail])
    print(bet_type, "=>", pick.base_grade, "->", pick.final_grade, "stake", pick.recommended_stake)
    for r in pick.reasons:
        print("  -", r)

print("\n--- BTTS tail market behavior ---")
for bet_type, odds, prob in markets:
    pick = grade_pick(bet_type, odds, prob, gate_signals=[btts_tail])
    print(bet_type, "=>", pick.base_grade, "->", pick.final_grade, "stake", pick.recommended_stake)
    for r in pick.reasons:
        print("  -", r)
