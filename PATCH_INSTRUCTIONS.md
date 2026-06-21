# V29-R3.7a-3 Tail Intensity Patch

## Replace

```text
v29r3/feature_gates.py
v29r3/ev_grader.py
v29r3/__init__.py
```

## Add

```text
examples/tail_intensity_demo.py
```

## Optional README update

Append:

```text
README_V29R37_LAB_APPEND.md
```

to:

```text
README_V29R37_LAB.md
```

## Commit message

```text
Add V29-R3.7a-3 tail intensity patch
```

## Test

```bash
PYTHONPATH=. python examples/tail_intensity_demo.py
```

Expected:
- Controlled 3-0 clean-sheet tail downgrades Under 3.5 but does not auto No Bet.
- Explosive 4-0/5-0 clean-sheet tail kills Under 3.5.
- BTTS positive tail allows BTTS Yes / Over candidates when EV is playable.
