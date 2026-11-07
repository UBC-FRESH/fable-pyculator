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
- previously untranslatable cells (e.g. `8_calc_emissions!V70`) translate in this model.

Post-publication repair and regeneration verification (2026-11-06):

- The source 2024 workbook shipped with `SUMIFS(#REF!, calc_land_cor[Year], …)` inside
  `ResultsLand[TOTAL]` (`LAND!AA17:AA27`). The pristine reference workbook has the same defect.
- The missing term was recovered as `calc_land_cor[CalcLoggedForest]`; subtracting it reproduces the
  workbook's own valid `calc_land_cor[TotallandFin]` total (`896,559.0`).
- `scripts/repair_fable_2024_land_total.py` repairs the local workbook formula/cached values, and
  `scripts/repair_fable_2024_generated_model.py` repairs the 11 corresponding generated expressions.
- Repaired local workbook checksum:
  `519f68d70d6338ca7030ab470e00686f76e62fe008d3adaf0210613d19d365fc` (original:
  `808dde4db5283cf7cd77a720379f636f164e5f50c5d1d52e449869f6dee9b798`).
- Old-vs-repaired generated-model execution comparison across all 10,274 declared outputs showed
  only the 11 `LAND!AA17:AA27` cells changed; no other output changed.

Fresh regeneration check:

- command: `python scripts/regenerate_fable_2024_model.py`;
- Modelwright version: `0.1.0a9` or newer;
- repaired workbook checksum:
  `519f68d70d6338ca7030ab470e00686f76e62fe008d3adaf0210613d19d365fc`;
- extracted cells: 536,593;
- dependency edges: 5,100,500;
- translated formulas: 410,299 of 410,299;
- declared outputs: 10,274;
- output-closure failures: 0;
- generation result: `generated=True` with 0 diagnostics;
- uncompressed model checksum:
  `cc8ac21ab55293f648aa9f6b3b8782b1f2dbe1b7789fda43bb1d100c1d8221ee`.

The regenerated model is byte-identical to the decompressed tracked archive. `LAND!AA17:AA27` are
native generated formulas, and `8_calc_emissions!V70` translates with the current runtime. The
earlier surgical repair is therefore equivalent to a fresh regeneration from the repaired workbook.
Earlier failed repro logs used Modelwright `0.1.0a8`; `0.1.0a9` is the minimum supported version.

The generated model source is about 114 MiB uncompressed and about 1.7 MiB as the tracked `.xz`
archive. The repaired compressed archive checksum is:

```text
f62c74b246fa29068b54b2c8ad82ed34b35026e490f2e2d205148c18277ae469
```

The decompressed model checksum is:

```text
cc8ac21ab55293f648aa9f6b3b8782b1f2dbe1b7789fda43bb1d100c1d8221ee
```

The same checksum is tracked in `generated_fable_2024_model.py.sha256` and is used by the portal to
detect stale working models before preparation.

## Artifact Boundary

Only the compressed generated Python model and its checksum sidecar are tracked here. Do not commit
the 2024 source workbook, decompressed generated source, `contract.json`, `expressions.json`,
`constants.json`, raw validation reports, logs, or scratch outputs. Those belong under ignored
`tmp/` paths.
