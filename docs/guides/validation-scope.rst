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
- publication of a compressed, validation-backed 2021 generated-model artifact under
  ``examples/fable_2021/``.

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

Compact Evidence Packaging
--------------------------

Phase 16 adds compact evidence packaging for already restored generated-model artifacts under
``tmp/generated-models/``. Packaging writes sanitized JSON and Markdown summaries under
``tmp/validation-evidence/`` and never copies raw generated source, raw generated values, source
workbooks, or full raw reports. See :doc:`validation-evidence-packaging`.

These summaries are conservative: they report ``pass`` only when explicit comparable-output, match,
and mismatch counts prove zero mismatches. Current-style execution artifacts without those counts are
reported as incomplete evidence.

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

FABLE Pyculator 2021 Evidence
-----------------------------

Phase 8 generated and validated a matching 2021 Modelwright Python model for the public 2021
FABLE-C workbook, then tracked only the compressed generated artifact under
``examples/fable_2021/generated_fable_2021_model.py.xz``.

Validation pass evidence:

- 62 sheets and 413,776 extracted cells;
- 297,002 formula cells translated with zero translation diagnostics;
- 281,922 comparable cached outputs;
- 240,124 numeric comparable outputs;
- 41,798 text comparable outputs;
- 281,922 generated-output matches;
- 0 mismatches;
- 15,080 non-comparable cached blank formula outputs recorded as boundary evidence.

This run also uncovered a generic Modelwright generated-runtime semantic gap: bare ``VLOOKUP`` misses
needed to propagate as ``#N/A`` values while ``IFNA`` and ``IFERROR`` still returned fallbacks. The
validated 2021 artifact was generated after that upstream Modelwright fix.

Remaining follow-up questions:

- Do country-specific variants preserve the S.1 through S.16 selection-control pattern?
- Which defaults differ across country calculators and later workbook releases?
- Which output tables or headline series should become stable public API, and which should remain
  benchmark-specific examples?

Claim Boundary
--------------

Current evidence supports early notebook wrapper workflows for the inspected public 2020 and 2021
FABLE-C workbooks, plus full comparable-output validation for the tracked 2021 compressed generated
model artifact. It does not support claims of production readiness, arbitrary country-calculator
support, or FABLE-P Canada equivalence.
