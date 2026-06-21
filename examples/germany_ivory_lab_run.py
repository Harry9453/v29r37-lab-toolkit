from v29r3 import (
    Scenario,
    run_monte_carlo_mixture,
    analyse_death_scores,
    grade_pick,
    RightTailFactors,
    WeakSideTransitionFactors,
    evaluate_right_tail,
    evaluate_weak_side_transition,
)

scenarios = [
    Scenario("Germany control", 0.50, 2.15, 0.55, tags=["favorite_control"]),
    Scenario("Ivory Coast low block", 0.25, 1.55, 0.45, tags=["low_block"]),
    Scenario("Germany right tail", 0.15, 3.35, 0.65, tags=["right_tail"]),
    Scenario("Ivory Coast transition", 0.10, 1.75, 1.05, tags=["weak_transition"]),
]

result = run_monte_carlo_mixture(
    "Germany vs Ivory Coast",
    scenarios,
    n=300_000,
    seed=20260621,
    data_status="live",
    ledger_type="live",
    run_id="GER_CIV_R37_DEMO",
)

print(result.meta)
print("\nTop10")
for score, p in result.top_scores:
    print(score, f"{p:.2%}")

print("\nMarkets")
for k in ["home_win", "under_2_5", "under_3_5", "btts_no", "away_under_0_5"]:
    print(k, f"{result.markets[k]:.2%}")

right_tail = evaluate_right_tail(RightTailFactors(multi_point_attack=True, substitute_firepower=True, early_goal_pressure=True))
weak_chain = evaluate_weak_side_transition(WeakSideTransitionFactors(
    pace_wide_player=True,
    shot_creating_winger_or_ten=True,
    late_arriving_midfielder=True,
    opponent_fullbacks_high=True,
))

death = analyse_death_scores(result.grid, "UNDER_3_5")
grade = grade_pick("UNDER_3_5", 1.58, result.markets["under_3_5"], death, [right_tail, weak_chain])
print("\nDeath", death)
print("\nGrade", grade)
