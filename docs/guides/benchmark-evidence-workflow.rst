Opt-In Benchmark Evidence Workflow
==================================

FABLE Pyculator can now orchestrate a manual benchmark evidence run around existing local FABLE
generated-model artifacts. The workflow remains opt-in and conservative: it does not run on pull
requests, does not download workbooks, and does not upload raw workbooks, generated Python source,
generated values, or validation reports.

The recommended command is:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_benchmark_evidence.py --json

By default this uses:

.. code-block:: text

   --workbook-version 2021
   --mode evidence-only
   --artifact-dir tmp/generated-models/fable-2021
   --output-dir tmp/validation-evidence/fable-2021

If artifacts are absent, the command exits successfully with ``evidence_status`` set to
``skipped``. Use ``--require-artifacts`` when missing local artifacts should fail the command.

Modes
-----

``evidence-only``
   Package compact validation evidence from existing local artifacts. This is the default and is the
   safest mode for GitHub-hosted manual workflow runs.

``freshforge-plan``
   Prepare the FABLE Pyculator/Modelwright FreshForge rebuild workflow when the source workbook is
   restored locally. If the workbook is absent and artifacts are not required, this mode records a
   skipped FreshForge planning summary.

``freshforge-run``
   Explicitly run the prepared FreshForge/Modelwright workflow. This mode requires FreshForge,
   Modelwright provider support, and restored local workbook/generated-model workflow artifacts. Use
   it only after inspecting the plan.

Examples
--------

Package compact evidence only:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_benchmark_evidence.py \
     --workbook-version 2021 \
     --json

Prepare the benchmark workflow boundary without running the long build:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_benchmark_evidence.py \
     --workbook-version 2021 \
     --mode freshforge-plan \
     --output-ref-strategy output-columns \
     --json

Run FreshForge only after local artifacts are restored and the plan looks right:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_benchmark_evidence.py \
     --workbook-version 2021 \
     --mode freshforge-run \
     --run-namespace benchmark/output-columns \
     --json

Evidence Backend
----------------

When ``modelwright.evidence`` is importable, FABLE Pyculator uses the generic Modelwright compact
evidence extractor and records ``evidence_backend`` as ``modelwright``. When that API is unavailable,
it falls back to the FABLE-local extractor introduced in Phase 16 and records ``evidence_backend`` as
``fable-local``.

Both paths preserve the same claim boundary: equivalence status is ``pass`` only when explicit
comparable-output, match, and mismatch counts prove zero mismatches. Generated execution alone is
not enough to claim equivalence.

Manual GitHub Workflow
----------------------

The manual ``Benchmark Evidence`` workflow exposes the same controls through
``workflow_dispatch``:

.. code-block:: text

   .github/workflows/benchmark-evidence.yml

It uploads only compact summaries under:

.. code-block:: text

   tmp/validation-evidence/**
   tmp/benchmark-evidence-summary.json

The workflow must not upload ``tmp/private-workbooks/``, ``tmp/generated-models/``, raw generated
Python, raw generated values, raw validation reports, or full FreshForge work directories.

Scenario-Bundle Context
-----------------------

The benchmark command can mention a scenario bundle and optionally ingest a compact FreshForge
scenario-bundle run summary when one already exists:

.. code-block:: bash

   .venv/bin/python scripts/run_fable_benchmark_evidence.py \
     --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
     --include-scenario-bundle-summary \
     --json

This is summary ingestion only. Scenario-bundle execution remains documented in
:doc:`scenario-bundles` and :doc:`scenario-bundle-freshforge-orchestration`.
