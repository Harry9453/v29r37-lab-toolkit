## V29-R3.7a-2 Deep Right Tail Split Patch

這不是 V29-R4。這是 V29-R3.7a-1 後的小型右尾分型修正。

### 修正原因

V29-R3.7a-1 已經修正：

```text
Right Tail 不再全市場誤殺 BTTS No。
小3.5 遇到強右尾會降級或 No Bet。
```

但已完賽驗證顯示，模型仍需要分辨兩種不同右尾：

```text
Clean-sheet Right Tail：
Spain 4-0 Saudi Arabia
Japan 4-0 Tunisia
Brazil 3-0 Haiti

BTTS Right Tail：
Netherlands 5-1 Sweden
England 4-2 Croatia
```

### 新增內容

`feature_gates.py` 新增：

```text
DeepRightTailFactors
evaluate_deep_right_tail
```

會輸出：

```text
DEEP_RIGHT_TAIL_CLEAN_SHEET
DEEP_RIGHT_TAIL_BTTS
DEEP_RIGHT_TAIL_MIXED
DEEP_RIGHT_TAIL_NONE
```

### 市場影響

Clean-sheet Right Tail：

```text
小3.5：降級 / No Bet
BTTS否：不被右尾硬殺
弱隊小0.5：可保留，但仍看 Weak-side Gate
```

BTTS Right Tail：

```text
小3.5：No Bet
BTTS否：降級 / No Bet
大2.5 / BTTS是：可觀察，但仍需 EV
```

### 測試檔

```text
examples/deep_right_tail_split_demo.py
```

測試目的：

```text
同樣是強隊右尾，
4-0 型與 5-1 型不能套同一套 BTTS 邏輯。
```
