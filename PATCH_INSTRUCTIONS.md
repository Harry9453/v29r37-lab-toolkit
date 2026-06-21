# V29-R3.7a Right-Tail Calibration Patch - Manual Upload Instructions

Direct GitHub write from ChatGPT was blocked by the integration, so use these replacement files manually.

## Replace these files

Upload/replace:

```text
v29r3/feature_gates.py
v29r3/ev_grader.py
v29r3/__init__.py
README_V29R37_LAB.md
```

Add this new file:

```text
examples/right_tail_patch_demo.py
```

## GitHub web steps

1. Open your repo:
   `Harry9453/v29r37-lab-toolkit`

2. For each existing file:
   - click the file
   - press the pencil icon
   - delete all old content
   - paste the matching file from this patch folder
   - Commit changes

3. For the new demo file:
   - open `examples/`
   - Add file -> Create new file
   - name it `right_tail_patch_demo.py`
   - paste the demo content
   - Commit changes

## Commit message

Use:

```text
Add V29-R3.7a right-tail calibration patch
```

## Do not upload

```text
__pycache__/
*.pyc
*.cpython-313.pyc
```

## Test command

After downloading the repo locally:

```bash
PYTHONPATH=. python examples/right_tail_patch_demo.py
```

Expected behavior:
- RIGHT_TAIL / LOW_BLOCK / EARLY_FAVORITE gates trigger.
- Under 3.5 is downgraded or No Bet, depending on scores.
