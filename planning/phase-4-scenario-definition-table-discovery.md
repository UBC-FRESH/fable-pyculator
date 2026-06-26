# Phase 4 Scenario Definition Table Discovery

Phase 4 starts from the public 2020 and 2021 FABLE-C workbooks stored locally under
`tmp/private-workbooks/`.

The `SCENARIOS definition` sheet is not shaped like `SCENARIOS selection`. Instead of sixteen
mutually exclusive selection tables with an `x` marker, the 2020 and 2021 definition sheets expose
twenty-eight native Excel tables. Most tables begin on row 28 and use row 23 as a column provenance
tag band with values such as `AUX`, `DIRECT`, `SCEN`, `CALC`, `DATA-1`, `DATA-2`, `DATA-3`, and
`DATA-4`.

Observed 2020 and 2021 native table names:

- `LandScenTarget`
- `GdpPopTarget`
- `income_elas`
- `FoodLossTarget`
- `FLScenTarget`
- `ImplCoefOptions`
- `ImpScenTarget`
- `ImportDef`
- `Product_ImpScen`
- `product_Exports`
- `ExpScenTarget`
- `ExportDef`
- `LivePdtyTarget`
- `LivePdtyDef`
- `CropPdtyTarget`
- `CropPdtyDef`
- `AfforTarget`
- `AfforScenDef`
- `DietTarget`
- `DietScenDef`
- `DietImplRates`
- `FinalTradeAdj`
- `CCShifters`
- `PAtarget`
- `PAtarget_def`
- `PHLoss_target`
- `PHLossTarget_def`
- `BiofuelScen_def`

Known version differences:

- The 2020 and 2021 table-name inventories match.
- `ImplCoefOptions` grows from 56 rows in 2020 to 67 rows in 2021.
- `AfforTarget` and `AfforScenDef` change shape between 2020 and 2021.
- The 2019 workbook has an older layout: `SCENARIOS definition` uses row 32 as the main provenance
  tag band and has twenty-three native tables.

Initial Phase 4 boundary:

- Discover table-level structures, not individual editable widgets.
- Preserve headers, row labels, cell refs, table refs, and per-column flavour tags.
- Render definition tables as pandas DataFrames so notebook users can inspect the model's scenario
  definition surfaces.
- Defer higher-level editing controls until the table inventory and generated-model input mapping
  have been validated.
