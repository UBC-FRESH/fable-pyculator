# Phase 1 User Guide And Validation Closeout

Date: 2026-06-26

## Purpose

P1.4 closes the first notebook-wrapper maturation phase by turning the discovered FABLE-C surfaces
and notebook-loop helpers into user-guide material, while keeping validation claims scoped to the
evidence actually recorded in this repository.

## Added Guide Pages

- `docs/guides/2020-notebook-workflow.rst`
- `docs/guides/validation-scope.rst`

The workflow page links the tracked output-free example notebook:

- `examples/notebooks/fable-pyculator-2020-loop.ipynb`

## Local Validation Evidence

Default package checks cover:

- linting;
- unit tests;
- Sphinx docs build with warnings treated as errors;
- workbook checksum verification for ignored local workbook artifacts.

Workbook-backed checks are opt-in:

```bash
FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv \
  tests/test_fable_workbook_selection_controls.py \
  tests/test_fable_workbook_headline_series.py
```

These checks validate the 2020 selection-control contract, the 2021 structural compatibility check,
the 2019 older-structure fragility check, and the 2020 headline-series curation contract.

## Parent Modelwright Evidence

The generated-model equivalence evidence for the 2020 FABLE-C model remains in Modelwright. The
local Modelwright Phase 26 planning record reports:

- 281,741 comparable cached outputs;
- 281,741 generated-output matches;
- 0 mismatches.

FABLE Pyculator uses generated models as ignored local artifacts, so this phase records the
relationship to the evidence but does not claim an independent full validation run.

## 2021 Follow-Up Scope

The 2021 workbook is ready for follow-up as a generalizability check:

- confirm headline table/column stability;
- record all changed defaults beyond the known `Affor_scen` difference;
- decide whether version-specific spec curation is needed;
- test the notebook loop against a generated 2021 model once such an ignored artifact exists.

## Phase Closeout

Before merging Phase 1:

- open a PR from `feature/p1-fable-c-notebook-wrapper-maturation` to `main`;
- confirm the test workflow and `Docs Pages` workflow pass on the PR;
- merge to `main`;
- confirm the post-merge Pages deployment succeeds;
- close parent issue #6 only after the PR is merged.
