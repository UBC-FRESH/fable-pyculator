# Phase 1 Selection-Control Validation

Date: 2026-06-25

## Purpose

P1.1 hardens the first FABLE-C notebook input surface: the high-level mutually-exclusive selection
tables on `SCENARIOS selection`.

## Local Artifacts

Workbook binaries are ignored local benchmark artifacts:

- `tmp/private-workbooks/2019_Open_FABLECalculator.xlsx`
- `tmp/private-workbooks/2020_Open_FABLECalculator.xlsx`
- `tmp/private-workbooks/2021_Open_FABLECalculator.xlsx`

Checksums are tracked in `benchmarks/fable-calculator/checksums.sha256`.

## Validation Command

```bash
FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv tests/test_fable_workbook_selection_controls.py
```

## Findings

- The 2020 workbook exposes the target S.1 through S.16 selection-control structure.
- The 2021 workbook preserves the same table names, ranges, option counts, and defaults except
  `Affor_scen`, where the default is `BonnChallenge` instead of the 2020 `NoAffor` default.
- The 2019 workbook exposes an older 12-control structure and skips S.11, S.14, S.15, and S.16
  relative to the 2020/2021 structure.
- Each discovered 2020 control has exactly one selected `x` marker in the source workbook.

## Implication

The first notebook wrapper contract should target the 2020/2021 16-control structure. The 2019
workbook should remain a fragility and older-structure compatibility check, not the primary interface
contract.

