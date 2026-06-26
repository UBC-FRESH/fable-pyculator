Notebook Control Surface
========================

FABLE Pyculator treats the main FABLE-C scenario sheet as a set of mutually-exclusive selection
controls. A control such as ``GDP_Scen`` is displayed as one dropdown in Jupyter, but it expands to
multiple cell overrides when running the generated model:

- every marker cell in the table's first column is cleared;
- the selected option's marker cell receives ``x``;
- the generated Modelwright model receives those marker-cell overrides as ordinary inputs.

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

Current Scope
-------------

The first implementation discovers high-level selection tables. Detailed editable parameter tables
on ``SCENARIOS definition`` still need a separate curation pass before they are exposed as notebook
inputs. Output table discovery currently maps Excel table cells into DataFrame surfaces; stable
headline outputs are currently curated for FOOD, LAND, GHG, and WATER. The first curation is still
benchmark-oriented and should be validated against generated 2020 model behavior before it is treated
as a stable reporting API.
