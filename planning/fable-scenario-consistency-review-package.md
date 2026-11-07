# FABLE Scenario Consistency — Expert Review Package

Status: **draft for Hisham Zerriffi / FABLE Calculator experts**

Companion files:

- `planning/fable-scenario-consistency-rules.md` — full rationale and architecture
- `planning/fable-scenario-consistency-rules.yaml` — machine-readable rule registry
- `planning/fable-scenario-consistency-review-package.csv` — fillable decision worksheet

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

## Rule table

### Hard structural rules

| Rule | Proposed | Confidence | Condition | Review question |
|---|---|---|---|---|
| CUSTOM-DIET-001 | error | high | `diet_scen=MyDiet` | Is `DietTarget` authoritative, and are more columns required? |
| CUSTOM-FOODLOSS-001 | error | high | `scen_foodloss=MyFoodLossScen` | Which `FoodLossTarget` columns are mandatory? |
| CUSTOM-IMPORT-001 | error | high | `scen_imports=MyImportScen` | Does `ImportDef` also need explicit values? |
| CUSTOM-EXPORT-001 | error | high | `scen_exports` is `MyExportScen*` | Is `shift_2050` or `Exports_cur` the custom input? |
| CUSTOM-PHLOSS-001 | error | high | `postharvestloss_scen=MyPHLossScen` | Is `PhLossTarget_def` also required? |
| CUSTOM-PRICE-001 | error | high | `price_scen=Custom` | Which `Price_Def` columns are authoritative? |

### Land and spatial rules

| Rule | Proposed | Confidence | Condition | Review question |
|---|---|---|---|---|
| LAND-AFFOR-001 | warning | medium | `NoExpansion` + `BonnChallenge+` | Does no-expansion constrain afforestation land? |
| LAND-PA-001 | warning | medium | `NoExpansion` + PA expansion | Can PA expansion occur without productive-land expansion? |
| LAND-URBAN-001 | warning | medium | `NoExpansion` + urban trend/SSP2 | Does no-expansion include urban land? |
| AFFOR-PA-001 | warning | low | `BonnChallenge+` + PA expansion | Are these targets additive, overlapping, or exclusive? |
| URBAN-POP-001 | warning | medium | `urbanarea_scen=SSP2` + other population narrative | Does SSP2 urbanisation require `pop_scen=SSP2`? |

### Narrative rules

| Rule | Proposed | Confidence | Condition | Review question |
|---|---|---|---|---|
| NARRATIVE-SSP-001 | warning | low | mixed SSP1–3 across GDP/pop/diet | Which mixed-SSP cases are intentional? |
| NARRATIVE-SSP-002 | warning | low | `pop_scen` SSP4/5 with SSP1–3 GDP/diet | What is the intended mapping? |
| CLIMATE-NARRATIVE-001 | warning | low | RCP2.6 with SSP3/4 | Should climate pathway and SSP be linked? |

### Trade and agriculture

| Rule | Proposed | Confidence | Condition | Review question |
|---|---|---|---|---|
| TRADE-FIX-001 | warning | medium | fixed trade + custom import/export | Compose, override, or conflict? |
| AGPRAC-CROP-001 | warning | low | organic + middle/high crop growth | Plausible or inconsistent? |
| LIVE-DENS-001 | warning | low | high density + no livestock growth | Plausible or inconsistent? |
| IRR-CROP-001 | warning | low | high irrigation + no crop growth | Plausible or inconsistent? |

## Measured audit (provisional)

The rule engine is implemented. Two modes were run against the 201-sample exact dataset and the
10-control reduced domain:

| Mode | Exact samples valid | Reduced domain valid | Reduced domain invalid |
|---|---:|---:|---:|
| exploratory (proposed rules warn only) | 201 / 201 | 725,760 / 725,760 | 0 |
| draft-enforced (proposed hard rules block) | 134 / 201 | 466,560 / 725,760 (64.3%) | 259,200 |

In exploratory mode, 142 of 201 samples carry at least one proposed warning and 535,680 of the
725,760 reduced-domain combinations are warning-only. No rule is active yet.

Most frequent domain-level triggers (overlapping; do not sum):

- `TRADE-FIX-001`: 226,800
- `NARRATIVE-SSP-001`: 207,360
- `CUSTOM-IMPORT-001`: 181,440
- `CUSTOM-DIET-001`: 103,680
- `LAND-AFFOR-001`: 80,640
- `LIVE-DENS-001`: 60,480

So the proposed hard rules would remove about **35.7%** of the reduced domain if approved as written.
Most of that reduction comes from custom-table requirements and trade/narrative rules. The final
count depends entirely on expert decisions.

## Example scenarios for discussion

These are review examples, not approved scenarios.

### Baseline

```json
{
  "land_scen": "NoExpansion",
  "affor_scen": "Affor1",
  "diet_scen": "SSP1",
  "scen_imports": "I1",
  "scen_exports": "E1",
  "fixtrade_scen": "No",
  "crop_scen": "NoGrowth",
  "agpractice_scen": "NoChange",
  "irrarea_scen": "NoGrowth",
  "live_scen": "NoGrowth",
  "livedens_scen": "NoGrowth",
  "gwp_scen": "SAR"
}
```

Expected: no consistency warning.

### Ambiguous land combination

```json
{
  "land_scen": "NoExpansion",
  "affor_scen": "BonnChallenge+",
  "pa_scen": "PAExpansion"
}
```

Question: warning, hard error, or valid?

### Custom diet without custom values

```json
{
  "diet_scen": "MyDiet"
}
```

Expected: hard error if `DietTarget` is empty.

### Mixed SSP narrative

```json
{
  "gdp_scen": "SSP1",
  "pop_scen": "SSP3",
  "diet_scen": "SSP2"
}
```

Question: warning, no rule, or a deliberate sensitivity case?

### Trade override

```json
{
  "fixtrade_scen": "Yes",
  "scen_imports": "MyImportScen",
  "scen_exports": "MyExportScen2"
}
```

Question: does fixed trade adjustment override these custom trajectories?

### Agriculture interaction

```json
{
  "agpractice_scen": "Organic",
  "crop_scen": "HighGrowth",
  "irrarea_scen": "HighGrowth"
}
```

Question: plausible ambition or inconsistent yield assumptions?

## Architecture implications

The rule decisions will feed a versioned scenario schema, not a fixed list:

- switches, options, coefficients, rules, and extensions are typed and versioned;
- hard rules filter the valid domain; soft rules become penalties/warnings;
- coefficient overrides are bounded continuous variables with provenance;
- new switch values/switches require explicit input mappings and review status;
- the optimizer uses a sparse active schema, not a fixed-width matrix;
- schema/rule changes invalidate the surrogate and exact datasets;
- exact Pyculator replay remains the final authority.

## Review output

When the CSV is complete:

1. Update the YAML rule `status` to `approved`, `rejected`, or `superseded`.
2. Record the reviewer and decision in `comments`/provenance.
3. Implement the rule engine and recompute the valid-domain estimate.
4. Only then choose the next optimization representation: reduced exact evaluator, compiled exact
   evaluator, or a targeted surrogate.

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
