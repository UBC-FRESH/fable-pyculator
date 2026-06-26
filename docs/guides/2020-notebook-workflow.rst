2020 Notebook Workflow
======================

This guide is the first end-to-end FABLE Pyculator workflow for the public 2020 FABLE-C workbook. It
connects four pieces:

- the ignored local workbook artifact;
- the ignored local Modelwright-generated Python model;
- discovered scenario selection controls;
- rendered output tables and curated headline series.

The tracked example notebook is:

- :download:`fable-pyculator-2020-loop.ipynb <../../examples/notebooks/fable-pyculator-2020-loop.ipynb>`

Local Artifacts
---------------

The default helper paths are:

.. code-block:: text

   tmp/private-workbooks/2020_Open_FABLECalculator.xlsx
   tmp/generated-models/fable-2020/generated_fable_2020_model.py

The workbook checksum is tracked under ``benchmarks/fable-calculator/checksums.sha256``. The
generated Python model is intentionally ignored; restore or generate it under ``tmp/`` before running
the notebook loop.

Build The Spec
--------------

``build_2020_notebook_spec`` reads the workbook and builds the notebook-facing declaration:

.. code-block:: python

   from fable_pyculator import build_2020_notebook_spec

   spec = build_2020_notebook_spec("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")

   len(spec.selection_controls)
   len(spec.output_tables)
   len(spec.headline_series)

The current 2020 contract discovers 16 high-level selection controls, output tables on the canonical
output sheets, and four initial headline series for FOOD, LAND, GHG, and WATER.

Choose Scenario Values
----------------------

Selection control names are normalized from workbook table names. For example, ``GDP_Scen`` becomes
``gdp_scen``.

.. code-block:: python

   selections = {
       "gdp_scen": "SSP1",
   }

   spec.input_mapping(selections)

The mapping expands one friendly selection value into marker-cell overrides: the selected row gets
``x`` and the other rows in the same selection table are cleared.

Run The Model
-------------

Use the full loop when the default artifacts are present:

.. code-block:: python

   from fable_pyculator import run_2020_notebook_loop

   result = run_2020_notebook_loop(
       {"gdp_scen": "SSP1"},
       output_table_names=("ghg_resultsghg",),
       headline_series_names=("food_total_kcal_feas", "land_total_area", "ghg_total_co2e", "water_total_footprint"),
   )

For custom artifact locations, split the loop:

.. code-block:: python

   from fable_pyculator import build_2020_notebook_spec, load_generated_model, run_notebook_loop

   spec = build_2020_notebook_spec("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
   generated_model = load_generated_model("tmp/generated-models/fable-2020/generated_fable_2020_model.py")
   result = run_notebook_loop(generated_model, spec, {"gdp_scen": "SSP1"})

Read Outputs
------------

``run_notebook_loop`` returns a ``NotebookLoopResult`` with four surfaces:

.. list-table::
   :header-rows: 1

   * - Attribute
     - Contents
   * - ``run``
     - Scenario name, generated-model inputs, calculated values, and output metadata.
   * - ``output_tables``
     - pandas DataFrames keyed by requested output table names.
   * - ``headline_frames``
     - tidy pandas DataFrames keyed by curated headline series names.
   * - ``headline_figures``
     - matplotlib figures keyed by curated headline series names.

Typical notebook cells:

.. code-block:: python

   result.output_tables["ghg_resultsghg"].head()
   result.headline_frames["ghg_total_co2e"]
   result.headline_figures["ghg_total_co2e"]

Current Boundary
----------------

This workflow is a wrapper and guide layer over a generated Modelwright model. It does not generate
the model, validate formula equivalence, or make country-calculator support claims. Those claims
belong to Modelwright validation evidence and later FABLE Pyculator validation phases.
