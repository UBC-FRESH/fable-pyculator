Generated Model Artifacts
=========================

FABLE Pyculator is a wrapper and notebook interface for Modelwright-generated Python models. It
does not currently generate those models from a FABLE workbook.

That boundary matters when comparing workbook versions. The 2021 workbook should be paired with a
2021 generated Python model. Running a 2021 workbook-derived wrapper against the 2020 generated
model can produce plausible-looking tables with the wrong calculation artifact behind them.

Local Artifact Contract
-----------------------

Keep generated models under ignored ``tmp/`` paths:

.. list-table::
   :header-rows: 1

   * - Workbook version
     - Source workbook
     - Matching generated model
   * - 2020
     - ``tmp/private-workbooks/2020_Open_FABLECalculator.xlsx``
     - ``tmp/generated-models/fable-2020/generated_fable_2020_model.py``
   * - 2021
     - ``tmp/private-workbooks/2021_Open_FABLECalculator.xlsx``
     - ``tmp/generated-models/fable-2021/generated_fable_2021_model.py``

The 2020 example notebook may materialize the compressed 2020 generated model from a sibling
Modelwright checkout. The 2021 notebook does not do that, because a 2020 generated model is not a
valid substitute for a 2021 generated model.

Spec Discovery Versus Model Generation
--------------------------------------

The notebook spec helpers discover FABLE-C wrapper metadata:

.. code-block:: python

   from fable_pyculator import build_2021_notebook_spec

   spec = build_2021_notebook_spec("tmp/private-workbooks/2021_Open_FABLECalculator.xlsx")

This reads workbook structure such as scenario selection controls, scenario-definition tables, output
tables, and curated headline series. It does not produce generated calculation source.

The run helpers load an already-generated Python model:

.. code-block:: python

   from fable_pyculator import run_2021_notebook_loop

   result = run_2021_notebook_loop(
       {"gdp_scen": "SSP1"},
       workbook_path="tmp/private-workbooks/2021_Open_FABLECalculator.xlsx",
       generated_model_path="tmp/generated-models/fable-2021/generated_fable_2021_model.py",
       include_figures=False,
   )

If the generated model path is missing, restore or create that artifact first. Do not point the
2021 helper at ``tmp/generated-models/fable-2020/generated_fable_2020_model.py``.

About Modelwright JSON Inputs
-----------------------------

Modelwright's low-level generation command expects explicit JSON artifacts:

- ``contract.json`` describes the generated module boundary: selected inputs, selected outputs,
  generated symbols, and dependency scope.
- ``expressions.json`` contains translated formula expressions for generated symbols.
- ``constants.json`` contains literal input values or cached constants needed by the generated model.

Those files are Modelwright generation inputs. FABLE Pyculator does not currently expose an API that
creates them from a FABLE workbook, and it should not silently invent them. A future Modelwright or
project-specific workflow may materialize a validated 2021 generated model and place it under the
ignored 2021 path above.

Current Validation Boundary
---------------------------

The 2020 generated model tracked in the sibling Modelwright repository has Modelwright validation
evidence. The 2021 FABLE Pyculator helpers currently validate wrapper structure and artifact wiring,
not generated-model output equivalence.

Until a matching 2021 generated model has been produced and validated, 2021 results should be treated
as a wrapper integration target rather than an equivalence claim.
