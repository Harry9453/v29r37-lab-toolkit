from v29r3 import (
    TailIntensityFactors,
    evaluate_tail_intensity,
    grade_pick,
)

controlled_3_0 = evaluate_tail_intensity(TailIntensityFactors(
    clean_sheet_tail=True,
    favorite_can_stop_at_three=True,
    favorite_game_management_after_lead=True,
    opponent_low_shot_volume=True,
    explosive_goal_difference_need=False,
    weak_side_chase_opens_space=False,
    late_sub_firepower=False,
))

explosive_4_0 = evaluate_tail_intensity(TailIntensityFactors(
    clean_sheet_tail=True,
    favorite_can_stop_at_three=False,
    favorite_game_management_after_lead=False,
    opponent_low_shot_volume=True,
    explosive_goal_difference_need=True,
    weak_side_chase_opens_space=True,
    late_sub_firepower=True,
))

btts_positive = evaluate_tail_intensity(TailIntensityFactors(
    btts_tail=True,
    weak_side_goal_chain_high=True,
    top10_has_btts_scores=True,
    btts_yes_model_prob_ge_55=True,
    btts_yes_price_playable=True,
))

markets = [
    ("Under 3.5", 1.45, 0.72),
    ("BTTS No", 1.65, 0.70),
    ("BTTS Yes", 1.95, 0.55),
    ("Over 2.5", 1.85, 0.58),
]

for label, sig in [
    ("Controlled 3-0 clean-sheet tail", controlled_3_0),
    ("Explosive 4-0/5-0 clean-sheet tail", explosive_4_0),
    ("BTTS positive tail", btts_positive),
]:
    print("\n===", label, "===")
    print(sig)
    for bet_type, odds, prob in markets:
        pick = grade_pick(bet_type, odds, prob, gate_signals=[sig])
        print(bet_type, "=>", pick.base_grade, "->", pick.final_grade, "stake", pick.recommended_stake)
        for r in pick.reasons:
            print("  -", r)
