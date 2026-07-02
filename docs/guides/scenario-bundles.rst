Scenario Bundles
================

Scenario bundles run the same FABLE Pyculator notebook loop for several named scenarios and write
rendered outputs under ignored local ``tmp/`` paths. They are useful once a matching generated model
already exists locally.

This feature is deliberately narrow:

- bundle selections target discovered ``SCENARIOS selection`` controls such as ``gdp_scen``;
- each selection is still expanded through ``FableCalculatorSpec.input_mapping``;
- ``SCENARIOS definition`` table editing is not part of this workflow;
- running a bundle does not rebuild a generated model or create new equivalence evidence.

Bundle Format
-------------

Bundles may be written as JSON or YAML. YAML support is available by default through ``PyYAML``.

.. code-block:: yaml

   version: 1
   bundle_id: fable-2021-ssp-demo
   workbook_version: "2021"
   description: Public-safe demo bundle for repeated 2021 FABLE Pyculator notebook-loop runs.
   render:
     output_table_names:
       - ghg_resultsghg
     output_table_column_flavour_tags: OUTPUT-*
     include_context_columns: true
     headline_series_names:
       - ghg_total_co2e
     include_figures: false
   scenarios:
     - scenario_id: ssp1
       label: SSP1
       selections:
         gdp_scen: SSP1
     - scenario_id: ssp2
       label: SSP2
       selections:
         gdp_scen: SSP2

``bundle_id`` and every ``scenario_id`` must be path-safe because they become output directory
names. Unknown selection controls and invalid option values fail before model execution.

Examples are tracked in:

.. code-block:: text

   examples/scenario-bundles/fable_2021_ssp_demo.json
   examples/scenario-bundles/fable_2021_ssp_demo.yaml

Run From Python
---------------

.. code-block:: python

   from fable_pyculator import (
       build_2021_notebook_spec,
       fable_scenario_bundle_artifact_paths,
       load_generated_model,
       load_scenario_bundle,
       run_scenario_bundle,
       write_scenario_bundle_artifacts,
   )

   bundle = load_scenario_bundle("examples/scenario-bundles/fable_2021_ssp_demo.yaml")
   spec = build_2021_notebook_spec("tmp/private-workbooks/2021_Open_FABLECalculator.xlsx")
   generated_model = load_generated_model(
       "tmp/generated-models/fable-2021/generated_fable_2021_model.py",
       module_name="fable_pyculator_generated_fable_2021",
   )

   result = run_scenario_bundle(generated_model, spec, bundle)
   paths = fable_scenario_bundle_artifact_paths(
       workbook_version=bundle.workbook_version,
       bundle_id=bundle.bundle_id,
   )
   manifest = write_scenario_bundle_artifacts(result, paths)

Run From The Script
-------------------

Dry-run mode validates the bundle and reports planned artifact paths without loading the generated
model:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_scenario_bundle.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
     --dry-run \
     --json

Run mode loads the matching generated model and writes artifacts:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_scenario_bundle.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml

By default, artifacts are written under:

.. code-block:: text

   tmp/scenario-runs/fable-2021/fable-2021-ssp-demo/

The output directory contains:

- ``bundle.json``: normalized bundle metadata;
- ``manifest.json``: paths and counts for the rendered artifacts;
- ``scenarios/<scenario_id>/scenario_inputs.csv``;
- ``scenarios/<scenario_id>/output_tables/*.csv``;
- ``scenarios/<scenario_id>/headline_frames/*.csv``;
- ``scenarios/<scenario_id>/headline_figures/*.png`` when figures are enabled.

Render Overrides
----------------

The script can override bundle render settings for quick slices:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_scenario_bundle.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
     --output-table-name ghg_resultsghg \
     --headline-series-name ghg_total_co2e \
     --column-flavour-tag OUTPUT-8 \
     --include-figures

Use ``--workbook-version``, ``--workbook-path``, ``--generated-model-path``, and ``--output-dir``
when working with non-default local artifact paths.

FreshForge Orchestration
------------------------

Use :doc:`scenario-bundle-freshforge-orchestration` when the same bundle should be represented as a
FreshForge graph with one node per scenario, namespace-isolated artifacts, and a compact run summary.
The direct runner remains the default path; FreshForge execution is explicit through
``--freshforge-plan`` or ``--freshforge-run``.
