# Phase 1 Headline Output Curation

Date: 2026-06-26

## Purpose

P1.2 creates the first notebook-friendly headline output layer for FABLE-C. The curation is narrow:
one time series each from FOOD, LAND, GHG, and WATER, backed by workbook table metadata and rendered
as pandas DataFrames and matplotlib figures.

## Local Artifacts

Workbook binaries are ignored local benchmark artifacts:

- `tmp/private-workbooks/2020_Open_FABLECalculator.xlsx`
- `tmp/private-workbooks/2021_Open_FABLECalculator.xlsx`

Checksums are tracked in `benchmarks/fable-calculator/checksums.sha256`.

## Initial Series

| Series | Workbook source | Mapping |
| --- | --- | --- |
| `food_total_kcal_feas` | `FOOD` table `Total_results_diets` | `PROD_GROUP == "TOTAL"`, `YEAR`, `kcal_feas` |
| `land_total_area` | `LAND` table `ResultsLand` | `Year`, `TOTAL` |
| `ghg_total_co2e` | `GHG` table `ResultsGHG` | `Year`, `TotalCO2e` |
| `water_total_footprint` | `WATER` table `TotalResultsWF` | `Product == "TOTAL"`, `YEAR`, sum of green/blue/grey crop and livestock columns |

## Validation Command

```bash
FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv tests/test_fable_workbook_headline_series.py
```

## Findings

- The 2020 workbook exposes all four initial headline source tables.
- Each initial series has 11 five-year points from 2000 through 2050.
- The WATER headline value is not a single workbook column. It is currently represented as a sum of
  six source columns from `TotalResultsWF`.
- `Indextables` descriptions can be matched to workbook table names after case-insensitive
  alphanumeric normalization, which handles spelling variants such as `Total_Results_diets` versus
  `Total_results_diets`.

## Implication

The first notebook reporting API should expose curated headline series alongside raw discovered
output tables. Future validation should compare rendered headline values against the generated 2020
model and then test the 2021 workbook to identify brittle assumptions.
