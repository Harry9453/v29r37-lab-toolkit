# V29-R3.7 Lab Upgrade Notes

這版不是 V29-R4。定位是把 V29-R3.6 Actionable Edge Bridge 的人工判斷，逐步搬進可驗證代碼。

## 新增模組

- `simulation_run.py`: 真正 Monte Carlo 多情境模擬，輸出 run_id / seed / N / data_status / ledger_type。
- `death_score.py`: 動態死亡比分分析，不再只靠固定字典。
- `feature_gates.py`: Right Tail、Weak-side Transition Chain、Dominance Conversion 的分數 Gate。
- `ev_grader.py`: EV + death score + gates 自動給 A/B/C/No Bet 與建議金額。
- `ledger_v2.py`: 增加 live、user_override、proxy_backtest、result_exposed、audit 等帳本分類，且可記 run_id / EV / grade。

## 使用原則

凡是輸出「300,000 次模擬」，必須有：

```text
run_id
model_version
seed
N
data_status
scenario_weights
top10_scores
market_probabilities
EV/grade output
```

沒有這些，只能叫模型估算。
