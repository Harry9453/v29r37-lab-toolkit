from v29r3 import (
    build_score_model,
    TeamMatchStats,
    evaluate_data_gates,
    scenario_to_stake,
    combine_filter_decisions,
    Ledger,
    BetRecord,
)

# 賽前設定：這是當時盲模擬的大概均值，不用賽後比分回頭改。
model = build_score_model(mu_home=1.75, mu_away=0.85, rho=0.0, max_goals=10)

print("Top scores:")
for score, p in model.top_scores[:10]:
    print(score, round(p, 4))

print("\nMarkets:")
for k in ["home_win", "draw", "away_win", "under_2_5", "over_2_5", "away_under_1_5"]:
    print(k, round(model.markets[k], 4))

# 賽後數據 gate：用來復盤，不回頭改賽前下注。
home = TeamMatchStats(shots_on_target=10, corners=19, possession=77, attacks=165, dangerous_attacks=154, yellow_cards=1, red_cards=0)
away = TeamMatchStats(shots_on_target=0, corners=1, possession=23, attacks=35, dangerous_attacks=3, yellow_cards=1, red_cards=2)

signals = evaluate_data_gates(home, away, home_name="加拿大", away_name="卡達")
print("\nData Gate signals:")
for s in signals:
    print(s.level, s.code, s.message)

stake_decision = scenario_to_stake("AWAY_UNDER_1_5", model.top_scores, base_stake=200)
final_decision = combine_filter_decisions(200, stake_decision, [s.level for s in signals])
print("\nStake decision:", final_decision)

ledger = Ledger()
record = BetRecord(
    bet_id="CAN-QAT-001",
    match="加拿大 vs 卡達",
    bet_type="卡達進球小1.5",
    stake=200,
    odds=1.35,
    book="simulation",
    model_version="V29-R3",
    notes="賽前盲模擬，賽後用數據閘門復盤",
)
record.settle("win")
record.error_tags = ["方向正確", "比分分布右尾低估", "極端壓制重置"]
ledger.add(record)
print("\nLedger summary:", ledger.summary(include_books=["simulation"]))
