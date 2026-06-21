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

## V29-R3.7a Right-Tail Calibration Patch

這不是 V29-R4。這是 V29-R3.7 的小型校正 patch，目標是把近期復盤得到的右尾、早球、低位破局與替代進攻鏈規則寫進 Gate 層。

### 觸發背景

#### Japan 4-0 Tunisia
- 賽前模型抓到日本勝、BTTS 否、突尼西亞小 0.5。
- 但小 3.5 原始機率過高，實際 4-0 打穿。
- 成長點：強隊替代進攻鏈完整時，不能因主創缺陣就自動壓小球。
- 成長點：換帥不等於防守修復。

#### Spain 4-0 Saudi Arabia
- 賽前模型 Right Tail 極高判斷正確，實際比分 4-0 且在 Top5。
- 小 3.5 原始機率偏高，但 Gate 成功避開下注。
- 成長點：低位 5-4-1 不等於穩定小球；早失球後低位防守會轉成右尾風險。

### 新增 Gate

`feature_gates.py` 新增：

```text
LowBlockFragilityFactors / evaluate_low_block_fragility
EarlyFavoriteBurstFactors / evaluate_early_favorite_burst
CreativeReplacementFactors / evaluate_creative_replacement
ManagerShockFactors / evaluate_manager_shock
```

用途：

```text
Low Block ≠ Stable Under
Early Favorite Burst
Creative Absence Replacement Chain
Manager Shock ≠ Defensive Reset
```

### EV Grader 修正

`ev_grader.py` 新增小球市場硬性降級：

```text
若 Under 市場死亡比分集中度 >= 12%，小球不可 A。
若小 3.5 遇到 RIGHT_TAIL / LOW_BLOCK_FRAGILITY / EARLY_FAVORITE_BURST 分數 >= 4，額外降級且最高 B。
若分數 >= 5，Under 3.5 直接 No Bet。
若小 2.5 遇到右尾或低位破局分數 >= 4，額外降級。
```

### 原則

- 這些 Gate 必須在盲模擬後、看盤口前先產生。
- 盤口只能用於 EV 與分級，不得反向修改模型機率。
- 不得因單場結果直接升級為 V29-R4。
