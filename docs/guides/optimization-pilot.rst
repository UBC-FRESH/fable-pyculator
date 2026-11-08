FABLE Optimization Pilot
========================

This page records the first FABLE Pyculator surrogate-assisted GPU optimization pilot. It is a
feasibility experiment, not a production optimizer and not a claim of exact or global optimization.

Question
--------

Can a fast GPU surrogate drive a weighted-goal genetic search over FABLE scenario controls well
enough that the best few candidates, when replayed exactly, are better than a simple baseline?

Pilot scope
-----------

Decision vector:

- the 24 categorical selection controls from the 2024 workbook;
- all numeric scenario-definition tables held fixed;
- the baseline selection is the workbook default.

Objectives:

- maximize `food_total_kcal_feas`;
- minimize `ghg_total_co2e`;
- keep `land_total_area` near the baseline (weight 0.1).

Method
------

1. Encode each selection as an integer category.
2. Run exact Pyculator evaluations for the baseline plus 32 random combinations.
3. Train a small Torch MLP on the categorical one-hot encoding and normalized objectives.
4. Run a vectorized Torch population search on the GPU.
5. Replay the top five surrogate candidates through the exact Pyculator model.

Artifacts:

- `scripts/fable_optimization_oracle.py` — exact one-scenario worker.
- `scripts/fable_optimization_samples.py` — parallel sample collection.
- `scripts/fable_gpu_optimizer.py` — surrogate training, GPU GA, and candidate export.
- Ignored outputs under `tmp/fable-optimization/`.

Pilot results
-------------

Exact sampling:

- 33/33 samples completed without errors;
- 16 concurrent workers;
- wall time about 392 s;
- per-run exact time 179.6–233.8 s (mean 217.6 s).

Surrogate:

- device: CUDA;
- population: 512;
- generations: 300;
- training rank correlation: 0.70;
- training and validation MSE were effectively zero because the sample is far too small and the MLP
  memorized it.

Exact replay of the top five surrogate candidates:

.. list-table::
   :header-rows: 1
   :widths: 8 16 16 16 16 16

   * - Rank
     - Exact food
     - Exact GHG
     - Surrogate food
     - Surrogate GHG
     - Surrogate goal
   * - 1
     - 2,924.7
     - 89.78
     - 3,418.2
     - 60.50
     - -8.04e-05
   * - 2
     - 2,924.7
     - 86.12
     - 3,346.9
     - 57.15
     - -2.65e-05
   * - 3
     - 2,924.5
     - 89.81
     - 3,326.8
     - 56.64
     - 4.41e-06
   * - 4
     - 2,924.7
     - 89.78
     - 3,370.5
     - 55.82
     - 6.89e-06
   * - 5
     - 2,924.5
     - 90.94
     - 3,424.5
     - 60.21
     - 2.92e-05

Exact-vs-surrogate error:

- food mean relative error: 15.5%;
- GHG mean relative error: 35.0%;
- food rank correlation across the top five: 0.10;
- GHG rank correlation across the top five: -0.10;
- land rank correlation: 0.30, but land is nearly constant.

Findings
--------

The plumbing works: exact sampling, surrogate training, CUDA search, and exact replay all ran end to
end.

The surrogate quality does **not** support optimization claims:

- 33 samples cannot cover 24 categorical variables;
- the MLP memorized the sample and extrapolated confidently but wrongly;
- the surrogate’s best candidates were not the exact best candidates;
- a surrogate-only search would have reported materially wrong food and GHG values.

This is exactly why the final exact replay is mandatory.

Phase 33 scaling result
-----------------------

Phase 33 reran the experiment with a reduced decision space and a larger exact sample:

- one-at-a-time screen over all 24 controls;
- 10 controls selected: `land_scen`, `diet_scen`, `fixtrade_scen`, `livedens_scen`,
  `scen_exports`, `crop_scen`, `scen_imports`, `affor_scen`, `gwp_scen`, `live_scen`;
- 201 exact samples (baseline plus 200 random reduced-space samples);
- 24 workers, about 24 minutes wall time;
- 5-member MLP ensemble, 512 population, 400 generations, CUDA.

Ensemble fit looked good in random validation:

- training rank correlation: 0.95;
- validation MSE: about `7.6e-06`.

Exact replay of the top five:

.. list-table::
   :header-rows: 1
   :widths: 8 16 16 16 16

   * - Rank
     - Exact food
     - Exact GHG
     - Surrogate food
     - Surrogate GHG
   * - 1
     - 3,297.0
     - 97.40
     - 3,338.8
     - 78.40
   * - 2
     - 3,297.0
     - 105.60
     - 3,337.9
     - 75.24
   * - 3
     - 3,297.0
     - 118.21
     - 3,320.1
     - 77.74
   * - 4
     - 3,303.5
     - 96.67
     - 3,304.5
     - 77.26
   * - 5
     - 3,297.0
     - 94.16
     - 3,317.9
     - 79.64

Exact-vs-surrogate error for the top five:

- food mean relative error: **0.8%**;
- GHG mean relative error: **23.6%**;
- food rank correlation: **-0.60**;
- GHG rank correlation: **-0.50**;
- land is effectively constant.

The larger sample fixed the global food scale well but still failed on the local GHG ranking. The
exact best candidate was ranked last by the surrogate. Random validation did not cover the
high-food, high-GHG extrapolation region reached by the GA. Ensemble spread (roughly 8–16 MtCO2e)
also understated the actual errors.

Phase 34 reduced exact evaluator
--------------------------------

Phase 34 tested a cheaper exact path: keep every formula, but rewrite the generated model's
`_output_refs` tuple to only the 176 cells used by the three headline objectives. This is still exact;
it only removes output rendering and unrelated output evaluation.

- baseline full model: 167 s;
- baseline reduced objective model: 123 s (**1.35×**);
- food-only slice: 127 s;
- GHG-only slice: 89 s;
- land-only slice: 72 s;
- reduced vs full objective values on baseline and three samples: exact, zero difference.

Running the three single-objective models in parallel gives a wall time around the slowest slice
(about 127 s) but consumes three model processes and still is not a meaningful optimization-speed
win.

Output-ref slicing is therefore **not sufficient** for a fast exact optimizer. The dominant cost is
the shared FABLE dependency closure, not the unrelated outputs. A useful exact evaluator would need
compiled/vectorized formula execution, table-level vectorization, or a much narrower dependency slice.

Phase 36 provisional rule-aware sampling
-----------------------------------------

The scenario-consistency rules were applied provisionally to the existing exact dataset:

- 201 exact samples evaluated under draft-enforced rules;
- 134 kept, 67 rejected, 112 with at least one warning;
- the kept set was used to retrain the 5-member ensemble and rerun the GPU GA.

The filter and sampler now support:

- `--rules` and `--rule-mode` on `scripts/fable_optimization_samples.py`;
- `scripts/filter_optimization_dataset.py` for existing datasets;
- per-sample rule annotations and rule/spec hashes in the dataset.

Exact top-five replay on the provisional-valid set:

- food mean relative error: **1.8%**;
- GHG mean relative error: **46.5%**;
- GHG rank correlation: **+0.50**;
- food rank correlation: **−0.50**;
- land is constant.

Rule filtering improved GHG **ranking** from −0.50 to +0.50, but the absolute GHG error got worse. It
did not produce a usable surrogate. Applying the rules changes which region the GA explores but does
not fix the underlying approximation problem.

Phase 37 exact narrow-domain optimization
-----------------------------------------

Phase 37 dropped the surrogate and evaluated a small policy domain exactly. The varied controls were
`land_scen` (3 values), `diet_scen` (7), `fixtrade_scen` (2), and `livedens_scen` (3), for 126
combinations. All other controls stayed at baseline.

Under draft-enforced provisional rules, the 18 `diet_scen=MyDiet` combinations were rejected by
`CUSTOM-DIET-001`; the remaining **108 combinations were run through the exact 2024 Pyculator** with
zero errors. Runtime was **926.5 s** (15.4 min) with 24 workers.

Land is invariant in this domain (896,559 ha), so the exact tradeoff is food versus GHG. The exact
front has 13 unique objective triples (41 rows before collapsing duplicate `livedens` outcomes).

Key exact points:

.. list-table::
   :header-rows: 1

   * - Case
     - Land
     - Diet
     - Fix trade
     - Live density
     - Food (kcal)
     - GHG (MtCO2e)
   * - Max food
     - NoDefor2030
     - FatDiet
     - No
     - NoGrowth
     - 3300.67
     - 242.43
   * - Weighted goal
     - NoDefor2030
     - FatDiet
     - Yes
     - NoGrowth
     - 3288.73
     - 121.23
   * - Min GHG
     - NoExpansion
     - EATLancetAverage
     - Yes
     - HighGrowth
     - 1869.64
     - 59.56

The most important exact result is the trade-fix comparison. Holding `land_scen=NoDefor2030`,
`diet_scen=FatDiet`, and `livedens_scen=NoGrowth` fixed, changing `fixtrade_scen` from `No` to `Yes`
moves food from 3300.67 to 3288.73 kcal (**−0.36%**) and GHG from 242.43 to 121.23 MtCO2e
(**−50.0%**). This is an exact result, not a surrogate prediction.

The exact best-GHG point trades away 43.4% of food to cut GHG by 75.4% relative to the max-food
point. Of the 108 valid scenarios, 60 carry at least one provisional warning: 36
`LIVE-DENS-001` and 36 `NARRATIVE-SSP-001` hits.

The surrogate had predicted 62.6 MtCO2e for a similar high-food trade-fix candidate, while the
exact value is 121.23 MtCO2e. The exact run confirms the candidate direction but also confirms that
the surrogate's absolute GHG prediction is unusable.

This result is **limited to the four varied controls**, with all other controls at baseline. It is
not a full FABLE optimization and the provisional rules are not expert-approved.

Phase 38 exact local sensitivity
--------------------------------

Phase 38 varied the six remaining priority controls one at a time around the Phase 37 weighted-goal
point: `affor_scen`, `crop_scen`, `scen_exports`, `scen_imports`, `gwp_scen`, and `live_scen`.
Everything else stayed fixed, including `land_scen=NoDefor2030`, `diet_scen=FatDiet`,
`fixtrade_scen=Yes`, and `livedens_scen=NoGrowth`.

- 20 exact evaluations: baseline plus 19 valid variants;
- 1 rejected variant (`MyImportScen`) by provisional `CUSTOM-IMPORT-001`;
- 0 errors;
- **168.9 s** with 24 workers;
- baseline: 3,288.73 kcal and 121.23 MtCO2e.

Exact local deltas:

.. list-table::
   :header-rows: 1

   * - Control
     - Value
     - Δ food (kcal)
     - Δ food (%)
     - Δ GHG (MtCO2e)
     - Δ GHG (%)
   * - `live_scen`
     - HighGrowth
     - +1.79
     - +0.05
     - −11.46
     - −9.45
   * - `live_scen`
     - LowGrowth
     - +1.15
     - +0.04
     - −9.17
     - −7.56
   * - `live_scen`
     - BAUGrowth
     - +0.53
     - +0.02
     - −6.64
     - −5.48
   * - `affor_scen`
     - BonnChallenge+
     - +10.63
     - +0.32
     - +0.11
     - +0.09
   * - `crop_scen`
     - HighGrowth
     - −0.29
     - −0.01
     - −0.93
     - −0.77
   * - `crop_scen`
     - ReducedGrowth
     - +2.0
     - +0.06
     - +16.66
     - +13.74
   * - `gwp_scen`
     - AR5
     - 0
     - 0
     - +7.22
     - +5.95
   * - `scen_exports`
     - E2 / E3 / custom
     - 0
     - 0
     - 0
     - 0
   * - `scen_imports`
     - I2 / I3
     - 0
     - 0
     - 0
     - 0

The strongest local GHG lever is livestock productivity (`live_scen=HighGrowth`): −11.46 MtCO2e
(−9.45%) with a tiny food gain. `gwp_scen` changes are metric conventions, not mitigation.
Custom export variants are exactly zero under this fixed-trade point. They were not rejected because
`CUSTOM-EXPORT-001` checks the populated `MyExportScen` row for all three custom export values; that
rule needs a per-value review before it can be treated as authoritative.

Two exact combined checks, added because the one-at-a-time result suggested additivity:

- `live_scen=HighGrowth` + `crop_scen=HighGrowth`: **3,290.23 kcal**, **108.84 MtCO2e**
  (food +0.05%, GHG −10.22%);
- add `affor_scen=BonnChallenge+`: **3,301.11 kcal**, **108.95 MtCO2e**
  (food +0.38%, GHG −10.13%).

The second candidate dominates the Phase 37 weighted-goal point on both food and GHG at the same land
area. It is an exact local candidate, not a global optimum. One-at-a-time variants cannot reveal
interactions, and only two combined checks were run.

Phase 39 exact candidate neighborhood
-------------------------------------

Phase 39 checked the immediate one-coordinate neighborhood of the Phase 38 candidate
(`live_scen=HighGrowth`, `crop_scen=HighGrowth`, `affor_scen=BonnChallenge+`) across all ten reduced
controls.

- 30 exact evaluations: baseline plus 29 valid variants;
- 2 rejected variants (`MyDiet`, `MyImportScen`) by provisional custom-table rules;
- 0 errors;
- **321.6 s** with 24 workers;
- baseline: 3,301.11 kcal and 108.95 MtCO2e.

No single-coordinate neighbor **strictly dominates** the candidate. There are 11 exact ties: land
`FreeExpansion`, live density `BAUGrowth`/`HighGrowth`, exports `E2`/`E3`/custom, imports `I2`/`I3`,
and afforestation `Affor2` all reproduce the same objective values.

The nearest one-coordinate tradeoffs are:

- `land_scen=NoExpansion`: 2,435.90 kcal, 80.88 MtCO2e (−865.21 kcal, −28.07 MtCO2e);
- `diet_scen=EATLancetAverage`: 2,254.06 kcal, 81.59 MtCO2e (−1,047.04 kcal, −27.35 MtCO2e);
- `diet_scen=SSP1/SSP2/SSP3/NoChange`: 2,939.96 kcal, 98.04 MtCO2e (−361.15 kcal, −10.91 MtCO2e);
- `fixtrade_scen=No`: 3,303.48 kcal, 213.40 MtCO2e (+2.38 kcal, +104.45 MtCO2e);
- `affor_scen=Affor1`: 3,290.23 kcal, 108.84 MtCO2e (−10.88 kcal, −0.11 MtCO2e).

The candidate is therefore a local Pareto point, not a global optimum. The result is exact for this
neighborhood; multi-coordinate interactions outside the Phase 38 combined checks remain untested.

Phase 40 exact decision frontier
--------------------------------

Phase 40 added eight targeted land/diet/trade interaction runs around the candidate, then combined
every exact point from Phases 37–40 into one decision frontier.

- 8 targeted exact runs, 0 errors; each run took 151.5–163.3 s;
- 169 exact points collected, 160 unique selections;
- 15 unique exact Pareto objective triples (29 rows before collapsing duplicates);
- exact ranges: 1,571.24–3,303.48 kcal and 59.56–691.93 MtCO2e;
- land remains invariant at 896,559 ha.

The **balanced** weighting picks the Phase 38 candidate: 3,301.11 kcal and 108.95 MtCO2e.

Decision views depend on the policy cap or floor:

.. list-table::
   :header-rows: 1

   * - View
     - Constraint
     - Exact pick
     - Food (kcal)
     - GHG (MtCO2e)
   * - Food-first
     - GHG ≤ 80
     - NoExpansion / SSP2 / trade Yes / live NoGrowth / crop NoGrowth / Affor1
     - 2,249.39
     - 76.78
   * - Food-first
     - GHG ≤ 90
     - NoExpansion / FatDiet / trade Yes / live HighGrowth / crop HighGrowth / BonnChallenge+
     - 2,435.90
     - 80.88
   * - Food-first
     - GHG ≤ 100
     - NoDefor2030 / SSP1 / trade Yes / live HighGrowth / crop HighGrowth / BonnChallenge+
     - 2,939.96
     - 98.04
   * - Food-first
     - GHG ≤ 110
     - NoDefor2030 / FatDiet / trade Yes / live HighGrowth / crop HighGrowth / BonnChallenge+
     - 3,301.11
     - 108.95
   * - GHG-first
     - food ≥ 2,000
     - NoExpansion / NoChange / trade Yes / live NoGrowth / crop NoGrowth / Affor1
     - 2,184.58
     - 61.24
   * - GHG-first
     - food ≥ 2,400
     - NoExpansion / FatDiet / trade Yes / live HighGrowth / crop HighGrowth / BonnChallenge+
     - 2,435.90
     - 80.88
   * - GHG-first
     - food ≥ 2,800
     - NoDefor2030 / SSP1 / trade Yes / live HighGrowth / crop HighGrowth / BonnChallenge+
     - 2,939.96
     - 98.04
   * - GHG-first
     - food ≥ 3,000
     - NoDefor2030 / FatDiet / trade Yes / live HighGrowth / crop HighGrowth / Affor1
     - 3,290.23
     - 108.84

At a 3,000 kcal food floor, the strict GHG-first pick is the live-high/crop-high point **without**
additional afforestation: 108.84 MtCO2e at 3,290.23 kcal. The balanced candidate buys 10.88 kcal for
0.11 MtCO2e by adding `affor_scen=BonnChallenge+`.

The exact max-food point is 3,303.48 kcal at 213.40 MtCO2e (`fixtrade_scen=No`); the exact min-GHG
point is 1,869.64 kcal at 59.56 MtCO2e. The decision frontier is the full 15-point set in
`tmp/fable-exact-decision/decision.json`.

The caps and floors are policy inputs, not model truths. The frontier is exact but local to the
evaluated scenario set, and the provisional rules are not expert-approved.

Next step
---------

Do not scale the surrogate further without a structural change. The useful paths are now:

1. Choose the policy cap or food floor with the decision owner; the exact frontier already answers
   the main tradeoff views.
2. Have FABLE experts review the provisional rules, especially the per-value custom-export rule.
3. Expand the exact domain only if the chosen policy view needs points outside the current local
   frontier.
4. Build a compiled/vectorized exact evaluator only if broader exact search is required.
5. Keep exact top-K replay as a hard gate regardless.

Portal viewer
-------------

The portal now has an **Optimization** page that reads
`examples/optimization/fable_2024/frontier.json` through `/api/optimization/frontiers`. It maps food,
GHG, land, and the weighted-goal score to X/Y/Z, supports colour and size mapping, quality-floor
filtering, an exact-front-only toggle, and a hide-provisional-warning filter. Hover shows exact
values, the selected point is highlighted, and the panel shows the actual range of each mapped
dimension. A point can be selected, pinned with up to two other points for comparison, and loaded
into the Workbench as a scenario prefill. A synchronized parallel-coordinates view shows the same
filtered exact points across controls and outcomes, and clicking a line selects the matching 3D point.
Dragging on a parallel axis brushes a range and filters both views; Shift-drag adds another axis
brush, with removable chips and a clear-all action. A selected point can be compared against a
reference point with exact objective deltas and changed selections; the reference is marked in both
views. Complete viewer states, including multiple brushes and the reference, can be saved as local
presets in the **Saved views** panel, and the preset library can be exported/imported as JSON or
shared as a named preset link carrying the full viewer state. A server-backed **Shared library** stores
named views for everyone with portal access, with optional self-declared author, note, and
draft/reviewed metadata. The shared panel has a needs-review queue, draft/reviewed counts, a
mark-reviewed action, and a compact created/updated/reviewed history per preset. A read-only audit
table, filterable activity timeline, per-author workload summary, saved timeline filter views, and
JSON/CSV audit exports cover the full shared library. The view state is shareable through URL query
parameters, and the currently filtered exact points can be downloaded as CSV.

This is the same interaction pattern as the urban-forest lab and WS4 Pareto explorer. The FABLE
viewer is read-only over exact points: it does not run the optimizer, a surrogate, or a hidden model
in the browser. The artifact can be regenerated with `--artifact-output` on
`scripts/fable_exact_decision.py`.

The detailed scenario-consistency rule surface and the extensible coefficient/switch architecture are
in `planning/fable-scenario-consistency-rules.md` and
`planning/fable-scenario-consistency-rules.yaml`.

Commands
--------

.. code-block:: bash

   .venv/bin/python scripts/fable_optimization_samples.py \
     --version 2024 --count 32 --workers 16 --seed 7

   /home/gep/.venv/bin/python scripts/fable_gpu_optimizer.py \
     --dataset tmp/fable-optimization/dataset.json \
     --output tmp/fable-optimization/ga-result.json \
     --population 512 --generations 300 --epochs 800 --top-k 5 --device cuda --seed 7

   .venv/bin/python scripts/fable_optimization_oracle.py \
     --version 2024 \
     --selections-file tmp/fable-optimization/replay/candidate_1.selections.json \
     --output tmp/fable-optimization/replay/candidate_1.json

   .venv/bin/python scripts/filter_optimization_dataset.py \
     --dataset tmp/fable-optimization-p33/dataset/dataset.json \
     --output tmp/fable-optimization-p36/dataset-provisional.json \
     --rejected-output tmp/fable-optimization-p36/rejected.json

   .venv/bin/python scripts/fable_exact_optimization.py \
     --version 2024 --workers 24 \
     --output-dir tmp/fable-exact-optimization

   .venv/bin/python scripts/fable_exact_sensitivity.py \
     --baseline-file tmp/fable-exact-optimization/baseline.json \
     --workers 24 --output-dir tmp/fable-exact-sensitivity

   .venv/bin/python scripts/fable_exact_decision.py \
     --input tmp/fable-exact-optimization/domain.json \
     tmp/fable-exact-sensitivity/sensitivity.json \
     tmp/fable-exact-sensitivity/combined \
     tmp/fable-exact-neighborhood/sensitivity.json \
     tmp/fable-exact-decision/targeted \
     --output tmp/fable-exact-decision/decision.json \
     --artifact-output examples/optimization/fable_2024/frontier.json
