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

Next step
---------

Do not scale this surrogate further without a structural change. The useful paths are:

1. Build a reduced exact evaluator for the objective slice (best fidelity).
2. Add physics-informed features and out-of-distribution rejection, not just more random samples.
3. Optimize a narrower policy question with fewer interacting controls.
4. Keep exact top-K replay as a hard gate regardless.

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
