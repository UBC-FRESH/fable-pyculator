FABLE FreshForge Rebuild Command
================================

FABLE Pyculator provides a script-style path for preparing, reviewing, and optionally running FABLE-C
generated-model rebuilds through FreshForge and Modelwright. Phase 14 generalizes the Phase 13
2021-only command into a version-aware interface with named output-ref strategies.

The command is intentionally conservative. By default it prepares the ignored local artifacts and
stops before executing FreshForge:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_model.py

The generic command defaults to ``--workbook-version 2021``. Version-specific paths follow this
convention:

.. code-block:: text

   tmp/private-workbooks/{version}_Open_FABLECalculator.xlsx
   tmp/generated-models/fable-{version}/

Plan-Only Preparation
---------------------

The plan-only command uses FABLE Pyculator's workflow helpers to:

- build the notebook spec from the source workbook;
- derive output refs with a named strategy;
- write ``output_refs.json``;
- write a cached-workbook validation scenario;
- write a downstream Modelwright FreshForge workflow document.

On the full public 2021 FABLE-C workbook this preparation may still take a minute or two because it
loads workbook structure and cached output values, but it does not execute the generated-model build.

Typical output includes the output-ref count, comparable cached-output count, and the local artifact
paths:

.. code-block:: text

   FABLE FreshForge rebuild
   Mode: plan
   Output-ref strategy: output-columns
   Output refs: ...
   Comparable validation outputs: ...
   Artifacts:
   - output_refs: tmp/generated-models/fable-2021/output_refs.json
   - validation_scenario: tmp/generated-models/fable-2021/validation-scenario.json
   - workflow: tmp/generated-models/fable-2021/freshforge-modelwright-run-workflow.json

Use ``--json`` when you want a machine-readable summary:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_model.py --json

Explicit FreshForge Run
-----------------------

The full Modelwright rebuild can take several minutes, so execution requires an explicit flag:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_model.py --run

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

The default output-ref strategy is ``output-columns``: all discovered output-table columns tagged
``OUTPUT-*``. You can choose narrower or broader validation/build slices:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_model.py \
     --output-ref-strategy headline-only

   .venv/bin/python scripts/build_fable_model.py \
     --output-ref-strategy table \
     --table-name ghg_resultsghg

   .venv/bin/python scripts/build_fable_model.py \
     --output-ref-strategy flavour-tags \
     --column-flavour-tag OUTPUT-8

   .venv/bin/python scripts/build_fable_model.py \
     --output-ref-strategy flavour-tags \
     --column-flavour-tag DATA --column-flavour-tag OUTPUT-*

   .venv/bin/python scripts/build_fable_model.py \
     --all-columns

The available strategies are:

``output-columns``
   All cells in columns tagged ``OUTPUT-*``. This is the default and matches the original 2021
   rebuild command behavior.

``headline-only``
   Only cells used by curated headline series. This is useful for a narrow first build/validation
   slice.

``table``
   Cells from one or more named output tables, filtered to ``OUTPUT-*`` columns unless
   ``--column-flavour-tag`` or ``--all-columns`` changes the column boundary.

``flavour-tags``
   Cells matching explicit flavour tags. Exact tags, ``DATA``/``OUTPUT`` family aliases, and
   trailing-star wildcard patterns are supported.

``all-columns``
   Every cell in selected output tables, including context/supporting columns.

The 2021 shortcut remains available:

.. code-block:: bash

   .venv/bin/python scripts/build_fable_2021_model.py --json

Boundary
--------

This command is a workflow convenience layer. It does not change the validation standard:

- FABLE Pyculator derives FABLE-specific output refs and validation-scenario structure.
- FreshForge schedules the workflow.
- Modelwright performs generated-model inference, generation, execution, and validation.
- A successful run is evidence only for the selected source workbook, output-ref strategy, and
  validation scenario recorded in the generated artifacts.
- Version-general workflow preparation does not create new generated-model equivalence claims.
