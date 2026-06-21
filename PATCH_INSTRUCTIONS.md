# V29-R3.7a-2 Deep Right Tail Split Patch

## Replace

```text
v29r3/feature_gates.py
v29r3/ev_grader.py
v29r3/__init__.py
```

## Add

```text
examples/deep_right_tail_split_demo.py
```

## Optional README update

Append the content of:

```text
README_V29R37_LAB_APPEND.md
```

to:

```text
README_V29R37_LAB.md
```

## Commit message

```text
Add V29-R3.7a-2 deep right-tail split patch
```

## Test

```bash
PYTHONPATH=. python examples/deep_right_tail_split_demo.py
```

Expected:
- Clean-sheet right tail kills Under 3.5 but does not kill BTTS No.
- BTTS right tail kills Under 3.5 and downgrades / kills BTTS No.
