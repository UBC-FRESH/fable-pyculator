Validation Evidence Packaging
=============================

FABLE Pyculator can package compact validation evidence from existing local generated-model
artifacts. The original packaging command is intentionally extraction-only: it does not download
workbooks, rebuild generated models, or run FreshForge.

The default input directory is:

.. code-block:: text

   tmp/generated-models/fable-2021/

The default output directory is:

.. code-block:: text

   tmp/validation-evidence/fable-2021/

The summaries are designed to be safe to upload or paste into planning notes after review. They do
not copy raw generated source, raw generated values, source workbooks, or raw validation reports.

Package Local Evidence
----------------------

Run the packaging script from the repository root:

.. code-block:: bash

   .venv/bin/python scripts/package_fable_validation_evidence.py --json

If artifacts are absent, the command exits successfully with ``evidence_status`` set to
``skipped``. Use ``--require-artifacts`` when a missing artifact should fail the command:

.. code-block:: bash

   .venv/bin/python scripts/package_fable_validation_evidence.py \
     --workbook-version 2021 \
     --require-artifacts \
     --json

The script writes:

.. code-block:: text

   tmp/validation-evidence/fable-2021/summary.json
   tmp/validation-evidence/fable-2021/summary.md

Opt-In Benchmark Orchestration
------------------------------

The newer benchmark orchestration entry point wraps the same compact evidence extraction and adds
explicit FreshForge plan/run modes:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_benchmark_evidence.py --json

It defaults to ``--mode evidence-only`` and writes an additional benchmark-level summary:

.. code-block:: text

   tmp/validation-evidence/fable-2021/benchmark-summary.json
   tmp/validation-evidence/fable-2021/benchmark-summary.md

Use :doc:`benchmark-evidence-workflow` for the manual workflow inputs, FreshForge modes, evidence
backend selection, and upload safety boundary.

Evidence Status
---------------

The summary separates artifact availability from equivalence claims:

``skipped``
   Expected local artifacts are missing and extraction was allowed to skip.

``incomplete``
   Artifacts were present, but explicit comparable-output, match, and mismatch counts were not found.

``complete``
   Explicit comparison counts were found and can support a pass/fail equivalence status.

Equivalence status is conservative:

- ``pass`` only when comparable-output count equals match count and mismatch count is zero;
- ``fail`` when explicit comparison counts show mismatches or missing matches;
- ``incomplete`` when those explicit counts are absent.

Manual Workflow
---------------

The manual GitHub Actions workflow ``Benchmark Evidence`` runs the benchmark orchestration command
and uploads only compact summaries:

.. code-block:: text

   .github/workflows/benchmark-evidence.yml

GitHub-hosted runners do not have ignored ``tmp/`` artifacts by default, so the workflow normally
records a skipped summary unless artifacts have been restored in the runner environment. It does not
upload ``tmp/generated-models/``, ``tmp/private-workbooks/``, raw generated source, raw generated
values, or raw validation reports.

Claim Boundary
--------------

Compact summaries are not automatically new validation claims. They are evidence packaging around
existing artifacts. Treat a summary as an equivalence claim only when it reports explicit comparable
output counts, match counts, mismatch counts, and a ``pass`` equivalence status.

When comparing possible generated-model boundaries before running a workflow, use
:doc:`output-ref-strategy-comparison`. That comparison can include existing evidence summaries when
available, but it does not create new equivalence evidence by itself.
