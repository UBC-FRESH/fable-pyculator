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

Next step
---------

Do not scale the current surrogate. First:

1. Reduce the decision vector to the 8–12 controls with measurable effects.
2. Use a space-filling design with at least 200–500 exact samples.
3. Use an ensemble or uncertainty-aware surrogate and reject out-of-distribution candidates.
4. Keep exact top-K replay as a hard gate.
5. Compare against a reduced exact evaluator before investing in a production UI.

If those steps do not produce useful exact regret, the better path is a reduced exact evaluator or a
narrower policy optimization problem, not a larger black-box surrogate.

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
