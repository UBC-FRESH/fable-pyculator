FreshForge Scenario-Bundle Orchestration
========================================

Scenario bundles can run directly through FABLE Pyculator, or they can be represented as a
FreshForge workflow. The FreshForge path is useful when repeated runs need an explicit graph,
namespaced artifacts, and compact run summaries.

This orchestration still uses the same bundle schema documented in :doc:`scenario-bundles`.
FABLE Pyculator owns the scenario semantics and rendered artifacts; FreshForge owns execution order,
namespaces, and run summaries.

Plan A Workflow
---------------

Use ``--freshforge-plan`` to write a workflow without executing it:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_scenario_bundle.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
     --freshforge-plan \
     --json

The workflow is written under the scenario output directory by default:

.. code-block:: text

   tmp/scenario-runs/fable-2021/fable-2021-ssp-demo/freshforge-scenario-bundle-workflow.json

The workflow contains one prepare node, one scenario node per bundle scenario, and one manifest
node. The public-safe example in ``examples/freshforge/fable_2021_scenario_bundle_workflow.yaml``
shows the same shape with ignored ``tmp/`` paths.

Run With A Namespace
--------------------

Use ``--freshforge-run`` to execute the workflow through FreshForge. A namespace keeps repeated runs
from overwriting each other:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_scenario_bundle.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
     --freshforge-run \
     --run-namespace scenario/ssp-demo-test \
     --json

With the namespace above, artifacts are written under:

.. code-block:: text

   tmp/scenario-runs/fable-2021/fable-2021-ssp-demo/scenario/ssp-demo-test/

That directory contains the normalized bundle, per-scenario CSV artifacts, the manifest, and
``freshforge-run-summary.json``. When ``--freshforge-run`` is used without ``--run-namespace``, the
script creates a timestamp namespace.

Plan A Matrix
-------------

Use ``--freshforge-matrix-plan`` when you want FreshForge to treat each scenario as its own matrix
case:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_scenario_bundle.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
     --freshforge-matrix-plan \
     --json

This writes:

.. code-block:: text

   tmp/scenario-runs/fable-2021/fable-2021-ssp-demo/freshforge-scenario-bundle-matrix.yaml
   tmp/scenario-runs/fable-2021/fable-2021-ssp-demo/freshforge-scenario-bundle-matrix-template.yaml

The public-safe example files in ``examples/freshforge/`` show the same matrix/template shape.

Run A Matrix
------------

Use ``--freshforge-matrix-run`` only after the matching workbook and generated model exist locally:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_scenario_bundle.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
     --freshforge-matrix-run \
     --fail-fast \
     --json

Each scenario case gets its own namespace such as ``scenario/ssp1`` or ``scenario/ssp2`` under the
scenario-bundle output root. The command writes a compact ``freshforge-matrix-summary.json`` beside
the matrix files.

Python API
----------

.. code-block:: python

   from fable_pyculator import (
       build_2021_notebook_spec,
       default_generated_model_path,
       fable_scenario_bundle_freshforge_matrix_paths,
       fable_scenario_bundle_freshforge_paths,
       load_scenario_bundle,
       prepare_scenario_bundle_freshforge_matrix,
       prepare_scenario_bundle_freshforge_workflow,
       plan_scenario_bundle_freshforge_matrix,
       run_scenario_bundle_freshforge_workflow,
       write_scenario_bundle_freshforge_summary,
   )

   bundle_path = "examples/scenario-bundles/fable_2021_ssp_demo.yaml"
   bundle = load_scenario_bundle(bundle_path)
   spec = build_2021_notebook_spec("tmp/private-workbooks/2021_Open_FABLECalculator.xlsx")
   paths = fable_scenario_bundle_freshforge_paths(
       workbook_version=bundle.workbook_version,
       bundle_id=bundle.bundle_id,
   )
   plan = prepare_scenario_bundle_freshforge_workflow(
       bundle,
       bundle_path=bundle_path,
       workbook_path="tmp/private-workbooks/2021_Open_FABLECalculator.xlsx",
       generated_model_path=default_generated_model_path(workbook_version="2021"),
       paths=paths,
       spec=spec,
   )
   run = run_scenario_bundle_freshforge_workflow(
       plan,
       run_namespace="scenario/ssp-demo-test",
   )
   write_scenario_bundle_freshforge_summary(run, paths)

   matrix_paths = fable_scenario_bundle_freshforge_matrix_paths(
       workbook_version=bundle.workbook_version,
       bundle_id=bundle.bundle_id,
   )
   matrix_plan = prepare_scenario_bundle_freshforge_matrix(
       bundle,
       bundle_path=bundle_path,
       workbook_path="tmp/private-workbooks/2021_Open_FABLECalculator.xlsx",
       generated_model_path=default_generated_model_path(workbook_version="2021"),
       paths=matrix_paths,
       spec=spec,
   )
   plan_scenario_bundle_freshforge_matrix(matrix_plan)

Boundary
--------

FreshForge-backed scenario bundles do not rebuild generated models, edit ``SCENARIOS definition``
tables, validate new generated-model equivalence, schedule remote jobs, cache runs, or retry failed
nodes. They run selection-control scenarios against an existing matching generated model. Matrix mode
adds repeated-run structure and summaries; it does not change the scenario semantics.

When a benchmark evidence run needs to mention an existing scenario-bundle run summary, use the
opt-in benchmark wrapper documented in :doc:`benchmark-evidence-workflow`. That path ingests compact
summary status only; it does not upload scenario work directories or rerun scenario bundles by
default.
