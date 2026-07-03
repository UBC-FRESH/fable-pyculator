# Phase 27: Alpha-Tester Notebook Reliability And 2021 Smoke Hardening

## Summary

Phase 27 hardens the Abdulateef-facing 2021 notebook loop after the output-table context-column
bugfixes from issues #188, #190, and #192. The phase turns those fixes into a repeatable smoke
surface that maintainers and alpha testers can run against restored local artifacts.

## Reliability Contract

- The 2021 loop notebook remains an unexecuted tracked template.
- Restored local artifacts stay under ignored `tmp/` paths.
- The smoke script can skip cleanly when the private workbook or generated model is absent.
- Context/support columns such as `PRODUCT` and `YEAR` may be filled from workbook-cached display
  values, but generated-model validation remains limited to selected generated output refs.
- Screenshots can clarify user-facing symptoms in GitHub issues, but they are not validation
  evidence.

## Implementation Notes

- `NotebookLoopResult.skipped_output_tables` records default output tables skipped because an
  output-table flavour filter matched no columns.
- Explicit table requests preserve fail-fast behavior and still raise `KeyError` when a requested
  table does not match the requested filter.
- The 2021 smoke script checks the concrete path reported by Abdulateef: `trade_resultstrade`
  rendered with `OUTPUT-*` output refs and populated `PRODUCT`/`YEAR` context columns.

## Closeout Expectations

- Local default tests must pass without restored private artifacts.
- The opt-in restored-artifact smoke test should pass when
  `FABLE_PYCULATOR_RUN_2021_NOTEBOOK_SMOKE=1` is set and the 2021 workbook/generated model exist.
- Issue bodies for recent Abdulateef notebook bugs should be readable and follow the UBC-FRESH
  summary/scope/acceptance/verification style.

## Investigation Notes

- A direct OpenPyXL check showed `data_only=True` still preserved the `TRADE` worksheet table
  metadata in the restored 2021 workbook, but this was not broad enough evidence to collapse
  all output-table discovery to a single workbook load in this reliability tranche.
- Keep the current correctness-preserving cached-value discovery path unless a later performance
  tranche compares all canonical output-sheet table metadata across `data_only` modes.
- A restored-artifact 2021 smoke run on 2026-07-03 passed in about 213 seconds, rendering 10 output
  tables, skipping 4 non-matching default `OUTPUT-*` tables, and proving populated
  `trade_resultstrade` `PRODUCT`/`YEAR` context columns.
