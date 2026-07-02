FABLE 2021 Benchmark Matrix Evidence Cookbook
=============================================

This cookbook connects the FABLE output-ref strategy matrix workflow to Modelwright's generic
matrix evidence aggregation. It is a local, opt-in workflow: compare and plan first, run only when
the 2021 workbook and generated-model prerequisites are restored, then package compact evidence.

1. Compare Strategy Boundaries
------------------------------

Start with the compare-only view:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py \
     --workbook-version 2021 \
     --json

This writes the strategy comparison under:

.. code-block:: text

   tmp/strategy-comparisons/fable-2021/

The summary reports output-ref counts and cached comparable-output counts. It is not an equivalence
claim.

2. Write And Plan The Matrix
----------------------------

Write the per-strategy Modelwright workflows and FreshForge matrix, then plan it:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py \
     --workbook-version 2021 \
     --matrix-plan \
     --json

This writes:

.. code-block:: text

   tmp/strategy-comparisons/fable-2021/strategy-matrix.yaml
   tmp/strategy-comparisons/fable-2021/strategy-matrix-workflow-template.yaml
   tmp/strategy-comparisons/fable-2021/<strategy>/freshforge-modelwright-run-workflow.json

Planning checks the matrix shape without running Modelwright.

3. Optional Explicit Matrix Run
-------------------------------

Run the matrix only after reviewing the plan and restoring the required local workbook artifacts:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py \
     --workbook-version 2021 \
     --matrix-run \
     --workdir . \
     --fail-fast \
     --json | tee tmp/strategy-comparisons/fable-2021/matrix-run-summary.json

The ``tee`` path is the default matrix-run input used by the evidence packaging command. Matrix
execution may take minutes because each case can run a generated-model workflow.

4. Package Matrix Evidence
--------------------------

Package compact evidence from the completed matrix run:

.. code-block:: bash

   .venv/bin/python scripts/package_fable_matrix_evidence.py \
     --workbook-version 2021 \
     --json

If the default matrix-run summary is not present, provide it explicitly:

.. code-block:: bash

   .venv/bin/python scripts/package_fable_matrix_evidence.py \
     --workbook-version 2021 \
     --matrix-run tmp/strategy-comparisons/fable-2021/matrix-run-summary.json \
     --json

The command writes Modelwright's generic compact summaries plus a FABLE-facing wrapper summary:

.. code-block:: text

   tmp/validation-evidence/fable-2021/matrix/summary.json
   tmp/validation-evidence/fable-2021/matrix/summary.md
   tmp/validation-evidence/fable-2021/matrix/benchmark-matrix-summary.json
   tmp/validation-evidence/fable-2021/matrix/benchmark-matrix-summary.md

Backend Requirement
-------------------

Matrix evidence packaging requires a Modelwright version that exposes ``modelwright.evidence`` matrix
aggregation. Until that support is part of the next published Modelwright alpha, install Modelwright
from the current source checkout when using this cookbook.

Claim Boundary
--------------

This workflow does not create a new generated-model equivalence claim by itself. Equivalence is
``pass`` only when the packaged Modelwright matrix evidence contains explicit comparable-output,
match, and mismatch counts proving zero mismatches. Strategy comparison, matrix planning, and
generated-model execution without comparison counts remain planning or incomplete evidence.
