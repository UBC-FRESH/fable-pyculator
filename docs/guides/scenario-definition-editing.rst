Editable Scenario-Definition Patches
====================================

FABLE Pyculator can validate conservative edits to cells discovered in the FABLE
``SCENARIOS definition`` sheet and turn those edits into generated-model input overrides.

This is not workbook mutation. Phase 26 does not write edited values back into a source
``.xlsx`` file, does not create a new workbook, and does not claim a new generated-model
equivalence result. Valid patches are ordinary input mappings keyed by normalized cell
references, just like selection-control overrides.

Editable Scope
--------------

The default editable surface is intentionally small:

- only non-formula cells in columns tagged ``DIRECT`` are editable;
- cells tagged ``SCEN``, ``DATA-*``, ``CALC``, or ``AUX`` are read-only;
- formula-valued cells are read-only even if surrounding metadata looks editable;
- unknown cells, duplicate targets, and ambiguous table/row/column selectors fail before model
  execution.

Validation output preserves the cell reference, source table, row label, column label, role tag,
original value, and scenario-location markers so a notebook or script can show users exactly what
would be overridden.

Patch Schema
------------

Patches can be JSON or YAML. Each edit uses either a full workbook cell reference or a unique
``table`` + ``row_label`` + ``column_label`` selector.

.. code-block:: yaml

   version: 1
   patch_id: diet-target-demo
   workbook_version: "2021"
   description: Public-safe example patch showing the scenario-definition edit schema.
   edits:
     - table: DietImplRates
       row_label: EATLancetAverage
       column_label: ImplTiming
       value: Linear

The tracked schema example lives at:

.. code-block:: text

   examples/scenario-definition-patches/fable_2021_diet_target_demo.yaml

Validate A Patch
----------------

Use the validation script before passing a patch into a notebook loop:

.. code-block:: bash

   .venv/bin/python scripts/validate_fable_scenario_definition_patch.py \
     --patch examples/scenario-definition-patches/fable_2021_diet_target_demo.yaml \
     --workbook-version 2021 \
     --json

The command reads the local workbook using the usual convention:

.. code-block:: text

   tmp/private-workbooks/2021_Open_FABLECalculator.xlsx

The JSON response includes:

- the normalized patch;
- a sample of editable cells;
- validation diagnostics when a target is read-only or unknown;
- the generated-model ``inputs`` mapping that would be passed into Modelwright-generated code.

Use In Notebook Loops
---------------------

Validated patches can be passed to the normal notebook-loop helpers. Selection-control inputs are
computed first, then scenario-definition patch inputs are merged in. If both surfaces try to assign
different values to the same generated-model input cell, the run fails before model execution.

.. code-block:: python

   from fable_pyculator import load_scenario_definition_patch, run_2021_notebook_loop

   patch = load_scenario_definition_patch(
       "examples/scenario-definition-patches/fable_2021_diet_target_demo.yaml"
   )

   result = run_2021_notebook_loop(
       {"gdp_scen": "SSP1"},
       scenario_definition_patch=patch,
       include_figures=False,
   )

For custom paths, pass the same patch to ``run_notebook_loop``:

.. code-block:: python

   from fable_pyculator import (
       build_2021_notebook_spec,
       load_generated_model,
       load_scenario_definition_patch,
       run_notebook_loop,
   )

   spec = build_2021_notebook_spec("tmp/private-workbooks/2021_Open_FABLECalculator.xlsx")
   generated_model = load_generated_model(
       "tmp/generated-models/fable-2021/generated_fable_2021_model.py",
       module_name="generated_fable_2021_model",
   )
   patch = load_scenario_definition_patch("tmp/local-patches/diet-target-demo.yaml")

   result = run_notebook_loop(
       generated_model,
       spec,
       {"gdp_scen": "SSP1"},
       scenario_definition_patch=patch,
   )

Current Boundary
----------------

Scenario-definition patches are separate from scenario bundles and FreshForge matrices in this
phase. Bundles still automate selection-control scenarios by default, and FreshForge still
orchestrates already-declared workflow nodes. A later phase can decide how to combine editable
scenario-definition patches with scenario bundles or matrix cases once the patch surface has enough
real modelling use.

This guide describes a parameter-editing surface for generated-model runs. It does not establish
country-calculator support beyond the inspected public FABLE-C workbook versions, and it does not
create a new equivalence claim unless explicit comparable/match/mismatch validation evidence is
recorded.
