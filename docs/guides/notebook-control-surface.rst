Notebook Control Surface
========================

FABLE Pyculator treats the main FABLE-C scenario sheet as a set of mutually-exclusive selection
controls. A control such as ``GDP_Scen`` is displayed as one dropdown in Jupyter, but it expands to
multiple cell overrides when running the generated model:

- every marker cell in the table's first column is cleared;
- the selected option's marker cell receives ``x``;
- the generated Modelwright model receives those marker-cell overrides as ordinary inputs.

For the current end-to-end 2020 workflow, see :doc:`2020-notebook-workflow`.

Minimal Example
---------------

.. code-block:: python

   from fable_pyculator import (
       FableCalculatorSpec,
       ScenarioControlSurface,
       curate_default_headline_series,
       discover_output_tables,
       discover_scenario_definition_tables,
       discover_selection_controls,
       headline_frame,
       output_table_frame,
       plot_headline,
       run_scenario,
       scenario_definition_table_frame,
       scenario_definition_tables_for_location,
   )

   workbook_path = "tmp/private-workbooks/2020_Open_FABLECalculator.xlsx"
   controls = discover_selection_controls(workbook_path)
   definition_tables = discover_scenario_definition_tables(workbook_path)
   output_tables = discover_output_tables(workbook_path)
   headlines = curate_default_headline_series(workbook_path)
   spec = FableCalculatorSpec(
       selection_controls=controls,
       scenario_definition_tables=definition_tables,
       output_tables=output_tables,
       headline_series=headlines,
   )

   surface = ScenarioControlSurface(spec)
   surface

   model_inputs = spec.input_mapping(surface.values())
   scenario_definition_table_frame(spec, "DietTarget")
   scenario_definition_tables_for_location(spec, "S.3")

When a generated Modelwright module is available, run the selected scenario and render a discovered
output table:

.. code-block:: python

   run = run_scenario(generated_model, spec, surface.values())
   output_table_frame(run, "ghg_resultsghg")
   headline_frame(run, "ghg_total_co2e")
   plot_headline(run, "ghg_total_co2e")

Discovered output tables can also be rendered with selected column flavour tags. Context columns
tagged ``DIRECT`` or ``AUX`` are kept by default so filtered frames still include identifiers such as
``Year`` or ``Product``:

.. code-block:: python

   output_table_frame(run, "ghg_resultsghg", column_flavour_tags="OUTPUT-8")
   output_table_frame(run, "ghg_resultsghg", column_flavour_tags="DATA-5")
   output_table_frame(run, "ghg_resultsghg", column_flavour_tags="DATA")
   output_table_frame(run, "ghg_resultsghg", column_flavour_tags="DATA*")
   output_table_frame(run, "ghg_resultsghg", column_flavour_tags="OUTPUT-*")
   output_table_frame(
       run,
       "ghg_resultsghg",
       column_flavour_tags=("DATA-5", "OUTPUT-8"),
       include_context_columns=False,
   )

2020 Notebook Loop
------------------

The first convenience loop points to ignored local 2020 artifacts:

- ``tmp/private-workbooks/2020_Open_FABLECalculator.xlsx``
- ``tmp/generated-models/fable-2020/generated_fable_2020_model.py``

Use ``run_2020_notebook_loop`` when those artifacts have been restored locally:

- :download:`fable-pyculator-2020-loop.ipynb <../../examples/notebooks/fable-pyculator-2020-loop.ipynb>`

.. code-block:: python

   from fable_pyculator import run_2020_notebook_loop

   result = run_2020_notebook_loop(
       {"gdp_scen": "SSP1"},
       output_table_column_flavour_tags="OUTPUT-8",
   )

   result.output_tables.keys()
   result.output_tables["ghg_resultsghg"]
   result.headline_frames["ghg_total_co2e"]
   result.headline_figures["ghg_total_co2e"]

For notebooks that need more control over paths or rendering choices, split the loop into its
pieces:

.. code-block:: python

   from fable_pyculator import build_2020_notebook_spec, load_generated_model, run_notebook_loop

   spec = build_2020_notebook_spec("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
   generated_model = load_generated_model("tmp/generated-models/fable-2020/generated_fable_2020_model.py")
   result = run_notebook_loop(generated_model, spec, {"gdp_scen": "SSP1"})

2021 Notebook Loop
------------------

The 2021 convenience loop uses separate ignored local artifacts:

- ``tmp/private-workbooks/2021_Open_FABLECalculator.xlsx``
- ``tmp/generated-models/fable-2021/generated_fable_2021_model.py``

The notebook can restore the matching 2021 generated model from the tracked compressed archive:

.. code-block:: text

   examples/fable_2021/generated_fable_2021_model.py.xz

Use ``run_2021_notebook_loop`` after the source workbook is restored locally:

- :download:`fable-pyculator-2021-loop.ipynb <../../examples/notebooks/fable-pyculator-2021-loop.ipynb>`

.. code-block:: python

   from fable_pyculator import run_2021_notebook_loop

   result = run_2021_notebook_loop(
       {"gdp_scen": "SSP1"},
       include_figures=False,
   )

The 2021 helper intentionally does not fall back to the compressed 2020 generated model. Phase 8
validated the tracked 2021 artifact with 281,922 comparable outputs, 281,922 matches, and 0
mismatches. For the generated-model artifact boundary, see :doc:`generated-model-artifacts`.

2021 FreshForge Build Plan
--------------------------

The FreshForge build-plan notebook shows how to rebuild a 2021 generated model from a restored source
workbook while keeping the orchestration boundary visible:

- :download:`fable-pyculator-2021-freshforge-build-plan.ipynb <../../examples/notebooks/fable-pyculator-2021-freshforge-build-plan.ipynb>`

The notebook uses FABLE Pyculator to derive explicit ``OUTPUT-*`` output refs from the 2021 workbook,
uses FreshForge to validate and plan the Modelwright workflow graph, and then shows the Modelwright
commands that actually infer, generate, and execute the model. FreshForge planning is not execution;
the build cell is gated behind ``RUN_BUILD = False`` by default.

Current Scope
-------------

The current implementation discovers high-level selection tables and renders native
``SCENARIOS definition`` tables for inspection. The definition tables are not yet exposed as a full
editable widget surface. Output table discovery maps Excel table cells into DataFrame surfaces;
headline outputs are currently curated for FOOD, LAND, GHG, and WATER. The first curation is still
benchmark-oriented. Generated-model equivalence remains a validation-phase claim rather than a
wrapper API claim, and is currently limited to the recorded public 2020/2021 FABLE-C benchmark
evidence.
