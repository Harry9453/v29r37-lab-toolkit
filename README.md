# V29-R3 Growth Toolkit

這是 World Cup Model V29-R3 的第一版可執行工具包。

定位：**輔助模型成長，不取代主模型。**

它把我們目前的規則做成固定流程：

1. 賠率與公平機率
2. Poisson 比分分布
3. Data Gate：射正、危險進攻、控球轉化、紅牌壓力
4. Scenario-to-Stake：死亡比分與金額降級
5. Ledger：正式單 / 測試單 / 模擬金 / 真錢 / 串關分離
6. Review：賽後復盤分類

## 快速執行

```bash
cd v29r3_growth_toolkit
python examples/canada_qatar_review.py
python examples/run_quick_match.py
```

## 核心原則

- 外部工具、Poisson、Dixon-Coles、物理層都只是輔助。
- 主模型仍是球隊近況、球員狀態、戰術對位、比賽分類、Betting Filter、帳本。
- 沒有回測，不算正式吸收。
- 贏單也要復盤，不能因為贏就說模型正確。
- 死亡比分在前五主分支，下注必須降級、減碼或 No Bet。
