# Phase 5 Scenario Definition Input Semantics

Phase 5 corrects an important boundary from Phase 4: `SCENARIOS definition` metadata must not be
treated as output-sheet column flavour metadata.

Output tables use the `column_flavour_*` API because output sheets expose tags such as `OUTPUT-8`,
`OUTPUT-9`, and `DATA-5` that support output DataFrame filtering. Scenario-definition tables now use
`column_role_*` metadata because their row-23 markers describe workbook roles or sources such as
`AUX`, `DIRECT`, `SCEN`, `CALC`, and `DATA-1`. `SCEN` is valid as a scenario-definition role marker,
but it is not a valid output-table flavour tag.

The 2020 and 2021 public workbooks also carry scenario-definition location markers above many native
definition tables. Examples:

- `S.3.B`: `DietImplRates`
- `S.3.C`: `DietTarget`
- `S.3.D`: `DietScenDef`
- `S.4.A`: `FLScenTarget`
- `S.4.B`: `FoodLossTarget`

These markers are useful for browsing related input-definition tables, but they are not currently a
complete one-to-one map to the 16 high-level controls on `SCENARIOS selection`. The definition sheet
contains additional markers beyond the current selection-control count, so helpers should expose the
markers as workbook evidence rather than forcing them into a stricter interpretation.

Initial Phase 5 boundary:

- Keep output flavour metadata and scenario-definition role metadata as separate APIs.
- Add helpers for looking up definition tables by scenario-definition location or family.
- Do not add editable widgets yet.
- Do not claim complete scenario-selection-to-definition-table equivalence.
