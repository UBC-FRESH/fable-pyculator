Output-Ref Strategy Comparison
==============================

FABLE Pyculator can compare several output-ref strategies before a generated-model rebuild. This is
a planning step: it helps users understand the size and validation boundary of each strategy without
running FreshForge or claiming generated-model equivalence.

Why Compare Strategies?
-----------------------

The output-ref list tells Modelwright which workbook cells define the generated-model boundary. A
small list is easier to debug, while a broad list gives more validation coverage. FABLE Pyculator can
derive those lists from workbook metadata instead of asking users to copy cell references manually.

The default comparison includes:

``output-columns``
   All discovered output-table cells tagged ``OUTPUT-*``.

``headline-only``
   Curated headline series refs.

``ghg-output-columns``
   The ``ghg_resultsghg`` table restricted to ``OUTPUT-*`` columns.

``ghg-output-8``
   The ``ghg_resultsghg`` table restricted to ``OUTPUT-8`` columns.

``all-columns``
   Every discovered output-table cell, including context and support columns.

Run A Comparison
----------------

From the repository root:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py --json

By default this reads:

.. code-block:: text

   tmp/private-workbooks/2021_Open_FABLECalculator.xlsx

and writes:

.. code-block:: text

   tmp/strategy-comparisons/fable-2021/summary.json
   tmp/strategy-comparisons/fable-2021/summary.md
   tmp/strategy-comparisons/fable-2021/<strategy>/output_refs.json

Restrict the comparison to selected default cases:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py \
     --strategy output-columns \
     --strategy headline-only \
     --json

Add ``--include-workflows`` when you also want per-strategy FreshForge workflow JSON files. The
workflow files are still plan artifacts; FreshForge execution remains explicit and separate.

FreshForge Matrix
-----------------

Phase 22 can also write a FreshForge matrix document for the compared strategies:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py \
     --include-matrix \
     --json

This implies per-strategy workflow files and writes:

.. code-block:: text

   tmp/strategy-comparisons/fable-2021/strategy-matrix.yaml
   tmp/strategy-comparisons/fable-2021/strategy-matrix-workflow-template.yaml

Plan the matrix without running Modelwright:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py \
     --matrix-plan \
     --json

Run the matrix only after reviewing the strategy boundaries and restoring the required local
workbook artifacts:

.. code-block:: bash

   .venv/bin/python scripts/compare_fable_output_ref_strategies.py \
     --matrix-run \
     --workdir . \
     --fail-fast \
     --json

FreshForge remains optional. Matrix document creation does not require FreshForge, but planning and
running require a FreshForge version with matrix support.

FreshForge Namespaces
---------------------

Each comparison entry records an intended FreshForge run namespace such as:

.. code-block:: text

   strategy/output-columns
   strategy/headline-only

FreshForge namespaces let later repeated runs avoid overwriting artifacts from other strategies.
The Phase 22 matrix uses those namespaces for the explicit strategy cases.

Evidence Summaries
------------------

If local per-strategy run artifacts already exist, pass ``--include-existing-evidence``. FABLE
Pyculator will summarize whatever compact evidence can be found. When the local Modelwright version
exposes generic validation-evidence helpers, those are used; otherwise the FABLE-local evidence
packaging helper is used as a fallback.

Claim Boundary
--------------

Strategy comparison is not generated-model equivalence validation. It reports output-ref counts,
cached comparable-output counts, artifact paths, and optional existing evidence summaries. Treat a
strategy as validated only after a matching generated model has been run and explicit
comparable-output, match, and mismatch counts support that claim.
