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
       discover_selection_controls,
       headline_frame,
       output_table_frame,
       plot_headline,
       run_scenario,
   )

   workbook_path = "tmp/private-workbooks/2020_Open_FABLECalculator.xlsx"
   controls = discover_selection_controls(workbook_path)
   output_tables = discover_output_tables(workbook_path)
   headlines = curate_default_headline_series(workbook_path)
   spec = FableCalculatorSpec(
       selection_controls=controls,
       output_tables=output_tables,
       headline_series=headlines,
   )

   surface = ScenarioControlSurface(spec)
   surface

   model_inputs = spec.input_mapping(surface.values())

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

Current Scope
-------------

The current implementation discovers high-level selection tables. Detailed editable parameter tables
on ``SCENARIOS definition`` still need a separate curation pass before they are exposed as notebook
inputs. Output table discovery currently maps Excel table cells into DataFrame surfaces; headline
outputs are currently curated for FOOD, LAND, GHG, and WATER. The first curation is still
benchmark-oriented. The 2020 notebook loop can run against an ignored generated model artifact, but
full generated-model equivalence remains a validation-phase claim rather than a wrapper API claim.
