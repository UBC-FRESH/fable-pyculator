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

It is intentionally committed after a successful 2020 benchmark run so GitHub can render the example
tables and figure directly in the browser.

Before opening it in VSCode, create the repo-local environment from the ``fable-pyculator`` repository
root:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh

Then select ``.venv/bin/python`` as the notebook kernel. The setup cell prints the active Python
executable and environment prefix, and warns if the selected kernel does not appear to come from that
repo-local environment.

Local Artifacts
---------------

The default helper paths are:

.. code-block:: text

   tmp/private-workbooks/2020_Open_FABLECalculator.xlsx
   tmp/generated-models/fable-2020/generated_fable_2020_model.py

The workbook checksum is tracked under ``benchmarks/fable-calculator/checksums.sha256``. The
generated Python model is intentionally ignored; restore or generate it under ``tmp/`` before running
the notebook loop.

For the version-specific generated-model artifact contract, including why 2021 workbooks must use a
matching 2021 generated model rather than the 2020 benchmark model, see
:doc:`generated-model-artifacts`.

The tracked notebook resolves the ``fable-pyculator`` repository root from the kernel's current
working directory before constructing these paths. This matters in VSCode, where the notebook kernel
may start in ``examples/notebooks/`` instead of the repository root. If the generated model is missing
and a sibling Modelwright checkout has ``examples/fable_2020/generated_fable_2020_model.py.xz``, the
notebook materializes that archive into the ignored FABLE Pyculator ``tmp/`` path. If required
artifacts are still missing, setup reports the missing absolute paths and later execution cells skip
instead of raising an artifact error.

Build The Spec
--------------

``build_2020_notebook_spec`` reads the workbook and builds the notebook-facing declaration:

.. code-block:: python

   from fable_pyculator import build_2020_notebook_spec

   spec = build_2020_notebook_spec("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")

   len(spec.selection_controls)
   len(spec.scenario_definition_tables)
   len(spec.output_tables)
   len(spec.headline_series)

The current 2020 contract discovers 16 high-level selection controls, 28 native
``SCENARIOS definition`` tables for inspection, output tables on the canonical output sheets, and
four initial headline series for FOOD, LAND, GHG, and WATER.

The definition tables expose separate role/source metadata and scenario-definition location markers.
Those markers are for browsing the input-definition surface and are not the same as output-table
column flavour tags.

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

   result = run_2020_notebook_loop({"gdp_scen": "SSP1"})

By default, the loop renders every discovered output table and every curated headline frame from the
single generated-model run. Use explicit ``output_table_names`` or ``headline_series_names`` only
when you deliberately want a smaller rendered result.

To render a focused output table, request one or more column flavour tags. Exact tags such as
``OUTPUT-8`` work, ``DATA`` selects the whole ``DATA-*`` family, and trailing-star patterns such as
``DATA*`` or ``OUTPUT-*`` select matching prefixes. The default keeps context columns such as
``Year`` alongside the requested flavour:

.. code-block:: python

   result = run_2020_notebook_loop(
       {"gdp_scen": "SSP1"},
       output_table_column_flavour_tags="OUTPUT-*",
       include_figures=False,
   )

   result.output_tables["ghg_resultsghg"]

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
   output_table_frame(result.run, "ghg_resultsghg", column_flavour_tags="DATA")
   output_table_frame(result.run, "ghg_resultsghg", column_flavour_tags="DATA-5")
   result.headline_frames["ghg_total_co2e"]
   result.headline_frames["water_total_footprint"]
   result.headline_figures["ghg_total_co2e"]

Current Boundary
----------------

This workflow is a wrapper and guide layer over a generated Modelwright model. It does not generate
the model, validate formula equivalence, or make country-calculator support claims. Those claims
belong to Modelwright validation evidence and later FABLE Pyculator validation phases.
