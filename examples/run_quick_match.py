from v29r3 import build_score_model, scenario_to_stake

home_team = "主隊"
away_team = "客隊"
mu_home = 1.45
mu_away = 1.15
bet_type = "BTTS_YES"

model = build_score_model(mu_home, mu_away, rho=0.0, max_goals=10)

print("Match:", home_team, "vs", away_team)
print("\nTop scores:")
for score, p in model.top_scores:
    print(score, f"{p:.2%}")

print("\nMarket probabilities:")
for k in ["home_win", "draw", "away_win", "under_2_5", "over_2_5", "btts_yes", "btts_no"]:
    print(k, f"{model.markets[k]:.2%}")

print("\nScenario-to-Stake:")
print(scenario_to_stake(bet_type, model.top_scores, base_stake=200))
