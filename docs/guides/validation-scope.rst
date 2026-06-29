Validation Scope
================

FABLE Pyculator is a notebook/user-guide layer. Its validation evidence is therefore about wrapper
behavior: workbook surface discovery, scenario selection overrides, output rendering, and artifact
hygiene.

What Is Validated Here
----------------------

The current package checks cover:

- the canonical output-sheet order;
- discovery of S.1 through S.16 selection controls in the 2020 workbook;
- compatibility of the same 16-control structure in the 2021 workbook, with the known
  ``Affor_scen`` default difference;
- the older 12-control structure in the 2019 workbook as a fragility check;
- curated FOOD, LAND, GHG, and WATER headline series from the 2020 workbook;
- import and execution of a generated-model module from an ignored local path;
- expansion of friendly selection values into marker-cell overrides;
- rendering of selected output tables, headline DataFrames, and headline figures.

Default verification commands:

.. code-block:: bash

   .venv/bin/python -m ruff check .
   .venv/bin/python -m pytest
   .venv/bin/sphinx-build -b html docs _build/html -W
   sha256sum -c benchmarks/fable-calculator/checksums.sha256

Workbook-backed checks are opt-in because they require ignored local workbook artifacts:

.. code-block:: bash

   FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv \
     tests/test_fable_workbook_selection_controls.py \
     tests/test_fable_workbook_headline_series.py

Modelwright 2020 Benchmark Evidence
-----------------------------------

The generated 2020 FABLE-C model equivalence evidence currently lives in the parent Modelwright
project, not in this wrapper package. Modelwright Phase 26 recorded a full comparable-output
validation pass for the public 2020 workbook:

- 54 sheets and 395,482 extracted cells;
- 296,976 formula cells translated with zero translation diagnostics;
- 281,741 comparable cached outputs;
- 281,741 generated-output matches;
- 0 mismatches.

FABLE Pyculator may use that generated model as an ignored local artifact, but this package should not
restate that evidence as a new independent validation run until a FABLE Pyculator validation phase
records its own execution evidence.

2021 Follow-Up Scope
--------------------

The 2021 workbook is currently a generalizability check for wrapper structure, not a validated
generated-model benchmark. The known near-term questions are:

- Has a matching 2021 Modelwright-generated Python model been produced and placed under
  ``tmp/generated-models/fable-2021/``?
- Do the curated headline table names and columns remain stable across 2021?
- Do country-specific variants preserve the S.1 through S.16 selection-control pattern?
- Which defaults differ, beyond the observed ``Affor_scen`` default?
- Does the generated-model loop need version-specific spec curation?
- Which output tables or headline series should become stable public API, and which should remain
  benchmark-specific examples?

Claim Boundary
--------------

Current evidence supports an early 2020 FABLE-C notebook wrapper workflow for inspected public
workbooks and 2021 wrapper-structure discovery. It does not support claims of 2021 generated-model
output equivalence, production readiness, arbitrary country-calculator support, or full
generated-model equivalence inside this repository.
