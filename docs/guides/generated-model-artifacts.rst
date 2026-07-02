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
Modelwright checkout. The 2021 example notebook materializes the validated compressed 2021 generated
model tracked in this repository:

.. code-block:: text

   examples/fable_2021/generated_fable_2021_model.py.xz

That archive is the only tracked generated-model exception in this repository. Source workbooks,
decompressed generated models, raw generation JSON files, and validation reports still belong under
ignored ``tmp/`` paths.

To prepare or explicitly run a local 2021 rebuild from the public source workbook, see
:doc:`2021-freshforge-rebuild-command`.
To compare output-ref boundaries before choosing a rebuild target, see
:doc:`output-ref-strategy-comparison`.

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
creates them from a FABLE workbook, and it should not silently invent them. The 2021 generated model
published here was created by Modelwright during Phase 8 and then compressed for notebook users.

Current Validation Boundary
---------------------------

The 2020 generated model tracked in the sibling Modelwright repository has Modelwright validation
evidence. Phase 8 added matching FABLE Pyculator evidence for the public 2021 FABLE-C generated
model artifact:

- extracted sheets: 62;
- extracted cells: 413,776;
- formula cells: 297,002;
- translated formula cells: 297,002;
- comparable cached outputs: 281,922;
- generated-output matches: 281,922;
- mismatches: 0;
- non-comparable cached blank formula outputs: 15,080.

The 2021 claim is limited to the public 2021 FABLE-C workbook and the compressed generated model
artifact in ``examples/fable_2021/``. It is not a claim about arbitrary country calculators,
production readiness, or FABLE-P Canada equivalence.

Compact Evidence Summaries
--------------------------

After running a local Modelwright/FreshForge generated-model workflow, use
``scripts/package_fable_validation_evidence.py`` to summarize restored artifacts under
``tmp/generated-models/fable-YYYY/``. The command writes compact summaries under
``tmp/validation-evidence/fable-YYYY/`` and reports incomplete evidence unless explicit comparison
counts are present. See :doc:`validation-evidence-packaging`.
