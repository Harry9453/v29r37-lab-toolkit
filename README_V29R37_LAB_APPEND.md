## V29-R3.7a-3 Tail Intensity Patch

這不是 V29-R4。這是 V29-R3.7a-2 後的小修正。

### 修正原因

V29-R3.7a-2 已能分辨：

```text
Clean-sheet Right Tail：4-0 型
BTTS Right Tail：5-1 / 4-2 型
```

但 proxy backtest 顯示仍有兩個問題：

```text
1. Brazil 3-0 Haiti 類型，小3.5 被打得太死。
2. Netherlands 5-1 Sweden / England 4-2 Croatia 類型，BTTS Yes / 大球還太保守。
```

### 新增內容

`feature_gates.py` 新增：

```text
TailIntensityFactors
evaluate_tail_intensity
```

輸出：

```text
CONTROLLED_CLEAN_SHEET_TAIL
EXPLOSIVE_CLEAN_SHEET_TAIL
BTTS_TAIL_POSITIVE
TAIL_INTENSITY_NONE
```

### 市場影響

Controlled Clean-sheet Tail：

```text
偏 3-0 型。
小3.5 降級但不直接 No Bet。
BTTS否可保留。
```

Explosive Clean-sheet Tail：

```text
偏 4-0 / 5-0 型。
小3.5 No Bet。
BTTS否不被硬殺。
```

BTTS Tail Positive：

```text
偏 5-1 / 4-2 型。
BTTS否降級。
BTTS是 / 大球可進 B- / B 觀察，但仍要 EV。
```

### 測試檔

```text
examples/tail_intensity_demo.py
```
