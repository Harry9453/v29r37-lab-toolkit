

## V29-R3.7a-1 Market-Specific Gate Patch

這不是 V29-R4。這是 V29-R3.7a 的小修正。

### 修正原因

V29-R3.7a 成功讓強右尾局的小 3.5 降級或 No Bet，但發現 `RIGHT_TAIL_SCORE = no_bet` 若直接套用全部市場，會誤殺 BTTS No、弱隊小 0.5、強隊勝等市場。

Spain 4-0 Saudi Arabia 的復盤顯示：

```text
小3.5：應該 No Bet，因為 4-0、3-1、5-0 右尾集中。
BTTS No：不應被 Right Tail 自動殺掉，因為強隊右尾常常伴隨弱隊零進球。
```

### 修正內容

`ev_grader.py` 改為 Market-Specific Gate：

```text
RIGHT_TAIL_SCORE / LOW_BLOCK_FRAGILITY / EARLY_FAVORITE_BURST：
- 硬性作用於 Under 2.5 / Under 3.5
- 作用於讓分與受讓安全性
- 不直接殺 BTTS No
- 不直接殺弱隊小 0.5
- 不直接殺強隊勝

WEAK_SIDE_TRANSITION_CHAIN：
- 才是 BTTS No / 弱隊小 0.5 的主要降級依據
```

### 新增測試

```text
examples/market_specific_gate_demo.py
```

預期：

```text
Under 3.5 在強右尾 Gate 下被打成 No Bet。
BTTS No 不會被 Right Tail 自動 No Bet，只會依弱隊進球鏈降級。
```
