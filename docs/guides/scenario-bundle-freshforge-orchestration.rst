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

Python API
----------

.. code-block:: python

   from fable_pyculator import (
       build_2021_notebook_spec,
       default_generated_model_path,
       fable_scenario_bundle_freshforge_paths,
       load_scenario_bundle,
       prepare_scenario_bundle_freshforge_workflow,
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

Boundary
--------

FreshForge-backed scenario bundles do not rebuild generated models, edit ``SCENARIOS definition``
tables, validate new generated-model equivalence, schedule remote jobs, cache runs, or retry failed
nodes. They run selection-control scenarios against an existing matching generated model.
