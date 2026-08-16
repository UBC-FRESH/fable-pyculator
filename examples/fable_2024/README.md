# FABLE 2024 (Canada) Generated Model Artifact

This directory contains the approved compressed 2024 FABLE Calculator (Canada) generated Python
model produced by the 2024 FABLE runtime-hardening work in Modelwright `0.1.0a9`.

Tracked artifact:

```text
examples/fable_2024/generated_fable_2024_model.py.xz
```

The source workbook is not tracked. Restore it locally under:

```text
tmp/private-workbooks/2024_Open_FABLECalculator.xlsx
```

A pristine reference copy (`2024_FABLECalculator_CAN_UP46_v1.xlsx`) exists alongside the working
copy used for generation; the generated model header records the working copy as its source
workbook.

## Validation Evidence

This model was generated from the 2024 FABLE Calculator (Canada) workbook using Modelwright
`0.1.0a9` (2024 FABLE runtime-hardening alpha), which adds static
`INDIRECT(ADDRESS(ROW(), COLUMN()))` resolution, corrupted structured-reference repair, and
Excel-faithful generated-runtime error semantics.

Validation summary:

- source workbook checksum:
  `808dde4db5283cf7cd77a720379f636f164e5f50c5d1d52e449869f6dee9b798`;
- extracted cells: 536,593;
- formula cells: 410,299;
- declared contract outputs: 10,274;
- runtime errors across all declared outputs: 0;
- cached-value comparison (300-output random sample against the workbook's cached values):
  94% exact matches; the remaining mismatches were 0.05-0.3% relative, consistent with Excel
  recalculation tolerance;
- previously untranslatable cells (e.g. `8_calc_emissions!V70`, `LAND!AA17`) translate in this
  model.

The generated model source is about 114 MiB uncompressed and about 1.7 MiB as the tracked `.xz`
archive. The compressed archive checksum is:

```text
0bb21e0a2e0ce05a5a2f4b0cd3274b766e5509b514f6a7a1eb5cdc82daa8981e
```

## Artifact Boundary

Only the compressed generated Python model is tracked here. Do not commit the 2024 source workbook,
decompressed generated source, `contract.json`, `expressions.json`, `constants.json`, raw validation
reports, logs, or scratch outputs. Those belong under ignored `tmp/` paths.
