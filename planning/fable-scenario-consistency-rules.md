# FABLE Scenario Consistency Rules and Extensible Optimization Schema

Status: **DRAFT — expert review required**

Owner: FABLE Pyculator / FABLE Canada collaboration

Purpose: give Hisham Zerriffi and FABLE Calculator experts a concrete surface to review, correct,
approve, reject, or replace. Nothing in this file should be treated as an authoritative FABLE rule
until it is marked `approved` in the rule registry.

## 1. Why this matters

The 2024 workbook exposes 24 categorical dashboard switches. Their raw Cartesian product is about
`5.12 × 10^13` combinations. Many of those are not meaningful policy narratives. Reducing the
valid combination space does three things:

- lowers the effective dimension of the optimization problem;
- stops the surrogate from learning physically or narratively incoherent regions;
- gives the exact Pyculator a defensible, inspectable scenario grammar.

The first optimization screen found 10 controls with measurable effects:

`land_scen`, `diet_scen`, `fixtrade_scen`, `livedens_scen`, `scen_exports`, `crop_scen`,
`scen_imports`, `affor_scen`, `gwp_scen`, `live_scen`.

Their raw product is about `725,760` combinations. Consistency rules should reduce that further and
make the remaining combinations reviewable.

The goal is **not** to enumerate “all FABLE scenarios.” It is to define a versioned, reviewable
scenario grammar whose valid instances can be generated, validated, optimized, and exact-replayed.

## 2. Rule vocabulary

Every rule should carry:

- `id`: stable identifier, e.g. `LAND-AFFOR-001`;
- `family`: macro narrative, land, trade, agriculture, custom tables, price, etc.;
- `severity`: `error` (hard exclusion), `warning` (review/penalty), or `info`;
- `confidence`: `high`, `medium`, `low`;
- `applies_to`: workbook versions;
- `status`: `proposed`, `under_review`, `approved`, `rejected`, `superseded`;
- `rationale`: why the rule is believed to be true;
- `review_question`: the exact question an expert must answer;
- `counterexamples`: deliberate mixed narratives that should *not* be excluded;
- `source`: workbook table, FABLE documentation, or expert review.

Hard rules remove combinations. Soft rules add penalties or warnings but do not silently delete
exploratory scenarios.

## 3. Rule families

### A. Structural rules: custom switch values require custom tables

These are the highest-confidence rules. A custom switch value is not usable in an exact run unless
the matching scenario-definition values are populated or explicitly overridden.

| Rule | Condition | Requirement | Severity | Confidence |
|---|---|---|---|---|
| CUSTOM-DIET-001 | `diet_scen = MyDiet` | `DietTarget` / `DietScenDef` custom values present | error | high |
| CUSTOM-FOODLOSS-001 | `scen_foodloss = MyFoodLossScen` | `FoodLossTarget` custom values present | error | high |
| CUSTOM-IMPORT-001 | `scen_imports = MyImportScen` | `ImpScenTarget` / `ImportDef` custom values present | error | high |
| CUSTOM-EXPORT-001 | `scen_exports` is any `MyExportScen*` | `ExpScenTarget` / `ExportDef` custom values present | error | high |
| CUSTOM-PHLOSS-001 | `postharvestloss_scen = MyPHLossScen` | `PHLoss_target` / `PhLossTarget_def` custom values present | error | high |
| CUSTOM-PRICE-001 | `price_scen = Custom` | `Price_Def` custom CPI values present | error | high |

Requirements may use a fixed `key_value` or a `key_switch` that resolves the selected row (for
example, the `scen_exports` value). A missing or empty selected key fails closed.

Expert question: are there additional custom switches whose table is not populated automatically by
the workbook, or whose default fallback is legitimate?

### B. Land, afforestation, protected areas, and urban expansion

These are suspected narrative conflicts, not yet hard exclusions.

| Rule | Condition | Effect | Severity | Confidence |
|---|---|---|---|---|
| LAND-AFFOR-001 | `land_scen = NoExpansion` and `affor_scen = BonnChallenge+` | warn: large afforestation target under no-expansion | warning | medium |
| LAND-PA-001 | `land_scen = NoExpansion` and `pa_scen in {PAExpansion, PAExpansion2}` | warn: protected-area expansion under no-expansion | warning | medium |
| LAND-URBAN-001 | `land_scen = NoExpansion` and `urbanarea_scen in {CurrentTrend, SSP2}` | warn: urban expansion under no-expansion | warning | medium |
| AFFOR-PA-001 | `affor_scen = BonnChallenge+` and `pa_scen in {PAExpansion, PAExpansion2}` | warn: competing land claims; expert review | warning | low |
| URBAN-POP-001 | `urbanarea_scen = SSP2` and `pop_scen not in {SSP2, UN_medium}` | warn: urbanisation uses a population narrative that differs from the population switch | warning | medium |

Expert questions:

1. Are any of these impossible rather than merely unusual?
2. Does `NoExpansion` constrain only *productive* agricultural land while allowing afforestation,
   protected areas, or urban expansion on other land?
3. Which of these should become hard errors versus soft warnings?

### C. Macro narrative coherence

This is intentionally soft. Mixed SSPs can be legitimate sensitivity experiments.

| Rule | Condition | Effect | Severity | Confidence |
|---|---|---|---|---|
| NARRATIVE-SSP-001 | `gdp_scen`, `pop_scen`, and `diet_scen` are all in `{SSP1, SSP2, SSP3}` and are not all equal | warn: mixed SSP narrative | warning | low |
| NARRATIVE-SSP-002 | `pop_scen in {SSP4, SSP5}` while `gdp_scen` and `diet_scen` are in `{SSP1, SSP2, SSP3}` | warn: population narrative has no matching GDP/diet option | warning | low |
| CLIMATE-NARRATIVE-001 | `climatechange_scen = rcp2p6...` with `gdp_scen = SSP3` or `pop_scen in {SSP3, SSP4}` | warn: climate pathway and socioeconomic narrative may disagree | warning | low |

Expert questions:

1. Which mixed-SSP combinations are deliberate and useful?
2. Should these be warnings, penalties, or no rule at all?
3. Is there a canonical mapping from UN population variants to SSP GDP/diet narratives?

### D. Trade

| Rule | Condition | Effect | Severity | Confidence |
|---|---|---|---|---|
| TRADE-FIX-001 | `fixtrade_scen = Yes` and (`scen_imports = MyImportScen` or `scen_exports` is any `MyExportScen*`) | warn: fixed trade adjustment versus user-defined trade trajectory | warning | medium |

Expert question: does fixed trade adjustment override, conflict with, or compose with custom import
and export targets?

### E. Agriculture, livestock, and land-use intensity

| Rule | Condition | Effect | Severity | Confidence |
|---|---|---|---|---|
| AGPRAC-CROP-001 | `agpractice_scen = Organic` and `crop_scen in {MiddleGrowth, HighGrowth}` | warn: organic practice with high yield-gap closure | warning | low |
| LIVE-DENS-001 | `livedens_scen = HighGrowth` and `live_scen = NoGrowth` | warn: high ruminant density with no livestock productivity growth | warning | low |
| IRR-CROP-001 | `irrarea_scen = HighGrowth` and `crop_scen = NoGrowth` | warn: large irrigation expansion with no crop productivity response | warning | low |

Expert questions:

1. Are these combinations merely ambitious, or genuinely inconsistent?
2. Do agroecological practice, irrigation, livestock density, and productivity switches interact in
   ways that require joint rather than pairwise rules?

### F. Rules that should *not* exist

- `gwp_scen` is an accounting metric, not a narrative. Any GWP can be paired with any climate
  scenario unless the analysis explicitly requires a fixed metric.
- `price_scen` is an accounting convention, not a production narrative.
- `diet_scen`, `scen_foodloss`, and `postharvestloss_scen` are different stages of the food system;
  there is no generic exclusion among them.

These are recorded so the rule registry does not over-constrain the space.

## 4. From rules to optimization dimensions

Rules should be evaluated by a scenario-schema compiler before optimization:

```text
schema registry
  -> active switch/value domains
  -> hard-rule filtering
  -> soft-rule penalties
  -> valid scenario instances
  -> exact Pyculator input mapping
```

Soft rules become objective penalties or reviewer warnings. Hard rules remove candidates. The
optimizer should never silently treat a hard-invalid scenario as feasible.

The optimization matrix must be **sparse and schema-driven**, not a fixed 24-column vector:

- a variable is a typed descriptor, not an integer column index;
- domains can grow when a switch gains a new value;
- coefficient overrides add bounded continuous variables or conditional parameters;
- the schema/rule-set hash is part of the dataset and surrogate provenance;
- changing the schema invalidates the surrogate and requires retraining or transfer.

## 5. Architecture for user-defined coefficients, switch values, and switches

The system must treat the workbook as a **base schema**, not the final schema.

### Base model

- `ScenarioSwitchDefinition`: id, label, semantic family, options, default, source.
- `SwitchOption`: id, label, input-cell bindings, coefficient bindings, required tables.
- `CoefficientDefinition`: id, unit, source table/cell, default, bounds, override policy.
- `ScenarioRule`: the reviewable rules above.
- `ScenarioSchema`: versioned collection of switches, coefficients, rules, and extensions.
- `ScenarioInstance`: schema version, switch values, coefficient overrides, extension values,
  provenance.

### Extensions

- A **new coefficient value** is an override record:
  `coefficient_id`, `value`, `bounds`, `unit`, `author`, `reason`, `status`.
- A **new switch option** is an extension record with a binding to input cells and/or coefficient
  values, plus required tables; an option without a binding cannot enter an exact run.
- A **new switch** is a composite extension: a new input-cell mapping, option set, coefficient
  bindings, rules, and review status.
- Every extension has a stable id, schema version, author, reviewer, timestamp, and provenance.
- The exact Pyculator input mapper must include both switch-cell overrides and scenario-definition
  patches; source workbooks are never mutated.

### Optimization implications

- Coefficient overrides can be treated as bounded continuous variables, but only a curated subset
  should be active at once. Otherwise the “infinite columns” problem destroys the surrogate.
- Variable groups can be switched on/off per experiment; the active schema and its hash are recorded
  in every dataset and result.
- New switch values expand the categorical domain; the surrogate must be retrained or adapted, and
  old datasets must be flagged as schema-incompatible.
- New switches require a mapping to exact model inputs before they can be optimized. An unmapped
  switch is a UI-only label and must be rejected for exact runs.

## 6. Review and UI surface

The planning surface should become a **Scenario Rules** page:

- rule table with severity, confidence, scope, status, rationale, reviewer, and version;
- side-by-side example scenarios: accepted, warned, rejected;
- approve/reject/comment workflow with a named reviewer;
- “exploratory” mode that permits proposed rules with visible warnings;
- “production” mode that uses only approved rules;
- coefficient editor with source cell/table, bounds, unit, override provenance, and review status;
- switch/value extension wizard with input mapping and validation;
- optimizer setup that shows the active schema version, valid-domain estimate, surrogate status,
  and exact-replay requirement.

## 7. Open decisions for Hisham and FABLE experts

1. Which rules are hard errors, which are warnings, and which should be deleted?
2. Is mixed-SSP analysis a first-class use case that must remain unconstrained?
3. What is the authoritative mapping from UN population variants to SSP narratives?
4. Under `NoExpansion`, which land uses are actually constrained?
5. Which coefficients are legitimately user-overridable, and within what bounds?
6. Who approves new switch values/switches, and how are they versioned and published?
7. Should optimization use only approved rules, or also allow exploratory proposed rules?
8. What is the minimum acceptable exact-replay and review evidence before a scenario can be called
   “consistent”?
