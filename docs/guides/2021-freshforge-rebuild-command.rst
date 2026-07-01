2021 FreshForge Rebuild Command
================================

Phase 13 adds a script-style path for preparing, reviewing, and optionally running the 2021 FABLE-C
generated-model rebuild through FreshForge and Modelwright.

The command is intentionally conservative. By default it prepares the ignored local artifacts and
stops before executing FreshForge:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_2021_model.py

The default source workbook path is:

.. code-block:: text

   tmp/private-workbooks/2021_Open_FABLECalculator.xlsx

The command writes the rebuild artifacts under:

.. code-block:: text

   tmp/generated-models/fable-2021/

Plan-Only Preparation
---------------------

The plan-only command uses FABLE Pyculator's workflow helpers to:

- build the 2021 notebook spec from the source workbook;
- derive output refs from discovered output-table columns tagged ``OUTPUT-*``;
- write ``output_refs.json``;
- write a cached-workbook validation scenario;
- write a downstream Modelwright FreshForge workflow document.

On the full public 2021 FABLE-C workbook this preparation may still take a minute or two because it
loads workbook structure and cached output values, but it does not execute the generated-model build.

Typical output includes the output-ref count, comparable cached-output count, and the local artifact
paths:

.. code-block:: text

   FABLE 2021 FreshForge rebuild
   Mode: plan
   Output refs: ...
   Comparable validation outputs: ...
   Artifacts:
   - output_refs: tmp/generated-models/fable-2021/output_refs.json
   - validation_scenario: tmp/generated-models/fable-2021/validation-scenario.json
   - workflow: tmp/generated-models/fable-2021/freshforge-modelwright-run-workflow.json

Use ``--json`` when you want a machine-readable summary:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_2021_model.py --json

Explicit FreshForge Run
-----------------------

The full Modelwright rebuild can take several minutes, so execution requires an explicit flag:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_2021_model.py --run

In run mode the script loads the generated FreshForge workflow and calls FreshForge's local serial
runner. Modelwright provider nodes then infer the contract, generate the Python model, execute it,
and evaluate generated outputs against the cached-workbook validation scenario.

If the run completes, the key ignored artifacts are:

.. code-block:: text

   tmp/generated-models/fable-2021/contract.json
   tmp/generated-models/fable-2021/expressions.json
   tmp/generated-models/fable-2021/constants.json
   tmp/generated-models/fable-2021/generated_fable_2021_model.py
   tmp/generated-models/fable-2021/generated-values.json
   tmp/generated-models/fable-2021/evaluation-report.json

Those files are local working artifacts. Do not commit them. The only approved tracked generated
model artifact is the compressed validated 2021 model under ``examples/fable_2021/``.

Output-Ref Options
------------------

The default output-ref strategy is all discovered output-table columns tagged ``OUTPUT-*``. You can
choose a narrower or different validation slice:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_2021_model.py \
     --table-name ghg_resultsghg

   .venv/bin/python scripts/build_fable_2021_model.py \
     --column-flavour-tag OUTPUT-8

   .venv/bin/python scripts/build_fable_2021_model.py \
     --column-flavour-tag DATA --column-flavour-tag OUTPUT-*

   .venv/bin/python scripts/build_fable_2021_model.py \
     --all-columns

The tag filters use the same rules as :func:`fable_pyculator.derive_output_refs`: exact tags,
``DATA``/``OUTPUT`` family aliases, and trailing-star wildcard patterns are supported.

Boundary
--------

This command is a workflow convenience layer. It does not change the validation standard:

- FABLE Pyculator derives FABLE-specific output refs and validation-scenario structure.
- FreshForge schedules the workflow.
- Modelwright performs generated-model inference, generation, execution, and validation.
- A successful run is evidence only for the selected source workbook, output-ref strategy, and
  validation scenario recorded in the generated artifacts.
