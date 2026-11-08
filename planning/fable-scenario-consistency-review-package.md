# FABLE Scenario Consistency — Expert Review Package

Status: **draft for Hisham Zerriffi / FABLE Calculator experts**

Companion files:

- `planning/fable-scenario-consistency-rules.md` — full rationale and architecture
- `planning/fable-scenario-consistency-rules.yaml` — machine-readable rule registry
- `planning/fable-scenario-consistency-review-package.csv` — fillable decision worksheet
- `scripts/build_rule_review_package.py` — regenerates the CSV and Markdown rule block; `--check`
  fails when they drift from the registry

## What we need from reviewers

For each rule in the CSV, choose one:

- `approve_error` — this combination is invalid for exact runs;
- `approve_warning` — keep it as a warning/penalty, not an exclusion;
- `reject` — delete the rule;
- `replace` — rewrite the rule; explain the replacement in `comments`;
- `defer` — needs more evidence or another expert.

Also fill `reviewer` and any `comments`. The CSV is the authoritative review record; the Markdown
and YAML are supporting material.

## Why this matters

The 24 raw switches have about `5.12 × 10^13` combinations. The 10 effective controls from the exact
screen have about `725,760` raw combinations. Expert-approved rules should reduce that to a smaller,
defensible space for optimization and for the Scenario Rules UI.

The goal is not to declare one “correct” scenario. It is to distinguish:

- structurally invalid scenarios;
- unusual but legitimate scenarios;
- accounting choices that should not be treated as narrative constraints.

## Highest-priority questions

1. **`NoExpansion` scope.** Does it constrain only productive agricultural land, or all land uses?
   This determines whether the land/afforestation/PA/urban warnings should become hard errors.
2. **Mixed SSPs.** Are mixed SSP narratives legitimate first-class sensitivity experiments? If yes,
   `NARRATIVE-SSP-001` should stay a warning or be removed.
3. **UN population variants.** What is the authoritative mapping from `UN_*` population scenarios to
   SSP GDP/diet narratives?
4. **Custom tables.** For each `My*` switch, which table and columns are mandatory for an exact run?
5. **Trade adjustment.** Does `fixtrade_scen=Yes` compose with custom import/export trajectories,
   override them, or conflict?
6. **Agriculture/livestock.** Are the organic/high-yield, high-density/no-growth, and
   high-irrigation/no-growth combinations merely ambitious or genuinely inconsistent?
7. **Coefficient overrides.** Which coefficients may advanced users override, and within what
   bounds? Which need a review/approval gate?
8. **New switches/values.** Who approves them, and what exact input mapping is required before they
   can enter an exact run?

`CUSTOM-EXPORT-001` resolves the row from the selected `scen_exports` value; a missing selected row
fails closed. The rule remains provisional.

## Rule table

<!-- BEGIN GENERATED RULE TABLE -->
_Generated from `planning/fable-scenario-consistency-rules.yaml` (SHA-256 `b67875df946da0e1cbc7cdc15eddffed540ed419c24e1646e32cf7c6b956022f`). Do not edit this block by hand; run `python scripts/build_rule_review_package.py`._

- Rules: 18
- Severity: 6 error, 12 warning
- Status: 18 proposed

### Custom tables

| Rule | Status | Severity | Confidence | Condition | Requirement | Review question |
|---|---|---|---|---|---|---|
| CUSTOM-DIET-001 | proposed | error | high | `diet_scen in {MyDiet}` | `scenarios_definition_diettarget[key_value: MyDiet] non-null: target` | Is DietTarget the authoritative custom diet table, and are there additional required columns? |
| CUSTOM-FOODLOSS-001 | proposed | error | high | `scen_foodloss in {MyFoodLossScen}` | `scenarios_definition_foodlosstarget[key_value: MyFoodLossScen] non-null: Target` | Which FoodLossTarget columns are mandatory for an exact run? |
| CUSTOM-IMPORT-001 | proposed | error | high | `scen_imports in {MyImportScen}` | `scenarios_definition_impscentarget[key_value: MyImportScen] non-null: ImportShare_2050` | Does ImportDef also require explicit values, or are its defaults valid? |
| CUSTOM-EXPORT-001 | proposed | error | high | `scen_exports in {MyExportScen, MyExportScen2, MyExportScen3}` | `scenarios_definition_expscentarget[key_switch: scen_exports] non-null: shift_2050` | Is shift_2050 or Exports_cur the authoritative custom input, and what distinguishes MyExportScen, MyExportScen2, and MyExportScen3? |
| CUSTOM-PHLOSS-001 | proposed | error | high | `postharvestloss_scen in {MyPHLossScen}` | `scenarios_definition_phloss_target[key_value: MyPHLossScen] non-null: RelTarget2050` | Is PhLossTarget_def also required? |
| CUSTOM-PRICE-001 | proposed | error | high | `price_scen in {Custom}` | `scenarios_definition_price_def[key_value: Custom] non-null: Custom` | Which price columns are authoritative for the exact model? |

### Land and spatial

| Rule | Status | Severity | Confidence | Condition | Requirement | Review question |
|---|---|---|---|---|---|---|
| LAND-AFFOR-001 | proposed | warning | medium | `all(land_scen in {NoExpansion}; affor_scen in {BonnChallenge+})` | — | Does NoExpansion constrain the land available for BonnChallenge+ afforestation? |
| LAND-PA-001 | proposed | warning | medium | `all(land_scen in {NoExpansion}; pa_scen in {PAExpansion, PAExpansion2})` | — | Can protected-area expansion occur without productive-land expansion? |
| LAND-URBAN-001 | proposed | warning | medium | `all(land_scen in {NoExpansion}; urbanarea_scen in {CurrentTrend, SSP2})` | — | Does NoExpansion include urban land, or only agricultural land? |
| AFFOR-PA-001 | proposed | warning | low | `all(affor_scen in {BonnChallenge+}; pa_scen in {PAExpansion, PAExpansion2})` | — | Are these targets additive, overlapping, or mutually exclusive? |
| URBAN-POP-001 | proposed | warning | medium | `all(urbanarea_scen in {SSP2}; pop_scen not in {SSP2, UN_medium})` | — | Does urbanarea_scen=SSP2 require pop_scen=SSP2, or is it independent? |

### Narrative

| Rule | Status | Severity | Confidence | Condition | Requirement | Review question |
|---|---|---|---|---|---|---|
| NARRATIVE-SSP-001 | proposed | warning | low | `equal_when_all_in_ssp_1_3(gdp_scen, pop_scen, diet_scen)` | — | Which mixed-SSP combinations are legitimate sensitivity experiments? |
| NARRATIVE-SSP-002 | proposed | warning | low | `all(pop_scen in {SSP4, SSP5}; gdp_scen in {SSP1, SSP2, SSP3}; diet_scen in {SSP1, SSP2, SSP3})` | — | What is the intended mapping for SSP4/SSP5 population scenarios? |
| CLIMATE-NARRATIVE-001 | proposed | warning | low | `all(climatechange_scen in {rcp2p6_hadgem2-es_n_GEPIC}; any(gdp_scen in {SSP3}; pop_scen in {SSP3, SSP4}))` | — | Should climate pathway and SSP narrative be linked at all? |

### Trade

| Rule | Status | Severity | Confidence | Condition | Requirement | Review question |
|---|---|---|---|---|---|---|
| TRADE-FIX-001 | proposed | warning | medium | `all(fixtrade_scen in {true}; any(scen_imports in {MyImportScen}; scen_exports in {MyExportScen, MyExportScen2, MyExportScen3}))` | — | Does fixtrade_scen=Yes compose with or override custom trade targets? |

### Agriculture

| Rule | Status | Severity | Confidence | Condition | Requirement | Review question |
|---|---|---|---|---|---|---|
| AGPRAC-CROP-001 | proposed | warning | low | `all(agpractice_scen in {Organic}; crop_scen in {MiddleGrowth, HighGrowth})` | — | Are organic systems compatible with MiddleGrowth/HighGrowth yield targets? |
| IRR-CROP-001 | proposed | warning | low | `all(irrarea_scen in {HighGrowth}; crop_scen in {NoGrowth})` | — | Can irrigation expansion occur without a crop productivity response? |

### Livestock

| Rule | Status | Severity | Confidence | Condition | Requirement | Review question |
|---|---|---|---|---|---|---|
| LIVE-DENS-001 | proposed | warning | low | `all(livedens_scen in {HighGrowth}; live_scen in {NoGrowth})` | — | Is this combination biologically or economically plausible? |

<!-- END GENERATED RULE TABLE -->



## Current status

- Draft rules: 18
- Hard structural rules: 6
- Soft warnings: 12
- Expert decisions recorded: 0
- Rule engine: implemented (`src/fable_pyculator/scenario_rules.py`)
- Audit script: `scripts/evaluate_scenario_rules.py`
- Exploratory domain: 725,760 valid, 535,680 warning-only
- Draft-enforced domain: 466,560 valid (64.3%), 259,200 invalid
- Rule-engine hashes and full counts: `tmp/fable-rules-audit/`

Do not treat any rule as active until it is marked `approved` in the registry.
