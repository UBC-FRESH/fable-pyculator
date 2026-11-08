Optional Web Portal
===================

FABLE Pyculator includes an optional local web portal for analysts who want to prepare a workbook
version, run named FABLE scenarios, read headline indicators and output tables, compare saved runs,
and inspect compact validation evidence without leaving the browser.

The portal is deliberately a presentation layer over the existing notebook APIs. It reads the same
generated model and artifacts the notebook workflow uses, runs the same
:func:`fable_pyculator.notebook.run_notebook_loop` path, and never recomputes a FABLE result in
JavaScript.

Install and run
---------------

Install the optional web extra and start the service from the repository root:

.. code-block:: bash

   python -m pip install -e '.[web]'
   fable-pyculator web --root . --port 8766

The default bind is ``127.0.0.1``. A non-loopback bind needs an explicit remote-bind opt-in because
the first release has no authentication:

.. code-block:: bash

   fable-pyculator web --root . --host 0.0.0.0 --allow-remote

Use ``--root-path /user/me/proxy/8766`` when the service is published under a notebook proxy prefix.
The SPA uses relative asset and API URLs, so one build works at ``/`` and under a prefix.

Artifact prerequisites
----------------------

A version is preparable when both of these exist:

.. code-block:: text

   tmp/private-workbooks/<version>_Open_FABLECalculator.xlsx
   tmp/generated-models/fable-<version>/generated_fable_<version>_model.py

The default headline curation is version-tolerant. The 2020 and 2021 workbooks expose FOOD, LAND,
GHG, and WATER headline series; the 2024 Canada workbook has no ``TotalResultsWF`` water-footprint
table, so its portal preparation succeeds with FOOD, LAND, and GHG headline series. The 2024
``LAND[TOTAL]`` formula is also broken with ``#REF!`` in the workbook itself; the portal shows a
clearly labelled *Total land area (component sum)* series that reproduces the workbook's valid
``calc_land_cor[TotallandFin]`` total and records the broken source formula in the series
description. Missing tables are skipped rather than reported as a failed preparation.

The GHG headline is built from declared `OUTPUT-8` components rather than the `TotalCO2e` `CALC`
cell. This makes it numeric for 2020, 2021, and 2024. Values are generated-model outputs, so they can
differ from workbook-cached totals where an individual component model differs. The 2024 series
explicitly excludes `LandSeqAffor` because that column is not a declared `OUTPUT-8` cell in the
current artifact.

The workflow artifact may instead be present as the approved compressed archive:

.. code-block:: text

   examples/fable_<version>/generated_fable_<version>_model.py.xz

The portal materializes that archive into the ignored working path before loading it. A clean
checkout can therefore browse artifacts and validation evidence, but the workbench remains disabled
with the missing file named explicitly until the source workbook is restored.

Preparation and execution are background jobs because real workbooks and generated models are large.
On a warm checkout, the 2021 workbook spec takes roughly two minutes to discover and a scenario run
takes roughly one minute. Prepared specs are cached under ``runtime/portal/specs/``, saved runs
under ``runtime/portal/runs/``, persistent chats under ``runtime/portal/chats/``, and the assistant
grounding sheet under ``runtime/portal/assistant/``. These directories are ignored by Git.

Pages
-----

Overview
   Readiness cards for each configured workbook version and recent saved runs.

Workbench
   Prepare a version, choose one option per selection control, optionally choose output tables and
   an output-column flavour filter, and run the generated model.

Results
   KPI cards derived from the declared headline series, one chart per headline series, and every
   rendered output table with client-side CSV export. Each saved run also records provenance:
   portal version, workbook and generated-model paths/sizes, prepared timestamp, and workbook id.

Compare
   Align two or more saved runs by year and show selection and latest-value differences.

Optimization
   Explore the tracked exact Pareto frontier for the optimization pilot. The page maps food, GHG,
   land, and the weighted-goal score to X/Y/Z, supports colour, size, quality-floor filtering, an
   exact-front-only toggle, a provisional-warning filter, hover values, selected-point highlighting,
   and actual axis ranges. It also lets you inspect, pin, compare, and load a frontier point into the
   Workbench. A synchronized parallel-coordinates panel shows the same filtered exact points across
   land, diet, trade-fix, livestock, crop, afforestation, food, GHG, and goal axes; clicking a line
   selects the matching 3D point. Dragging vertically on an axis brushes a range and filters both
   views; **Clear brush** resets it. A point can be set as a reference, with an exact
   selected-vs-reference delta card and synchronized reference markers. The current axes, colour,
   size, filters, brush, selected point, and reference are encoded in the URL; **Copy view link**
   shares that exact state, and **Download filtered CSV** exports the visible exact points. The viewer reads
   ``examples/optimization/fable_2024/frontier.json`` through
   ``/api/optimization/frontiers``; it never runs an optimizer or a surrogate in the browser.

   .. image:: /_static/optimization-frontier.png
      :alt: Optimization page with the exact FABLE Pareto solution cloud and decision views
      :width: 100%

   .. image:: /_static/optimization-parallel.png
      :alt: Parallel-coordinates view of the same exact Pareto points
      :width: 100%

Validation
   Read the compact evidence summary at
   ``tmp/validation-evidence/fable-<version>/summary.json``. The portal deliberately does not load
   the multi-gigabyte inference, expression, generation, or evaluation stage artifacts.

Artifacts
   A file-by-file readiness table with paths and sizes, model materialization, and tracked
   scenario-bundle examples. For 2021 and 2024, the page shows whether the working model matches
   the tracked uncompressed checksum. A mismatch offers a re-materialize action; preparation also
   detects and repairs a stale model from the approved archive.

Assistant
   Enabled only when the service is started with ``--allow-agent``. A green **+ Ask** pill in the
   header opens a fixed overlay. The overlay keeps a local OpenCode session across turns, renders
   markdown for both the user and the assistant (including code blocks, lists, links, and tables),
   shows tool-action chips, and supports ``Enter`` to send with ``Shift+Enter`` for multiline
   prompts. Chats are persisted under ``runtime/portal/chats/`` and listed in the overlay, so users
   can resume a conversation after a reload or service restart. Chats can be renamed, searched,
   pinned, archived, deleted, and exported as Markdown; short/generic first prompts are replaced by
   an automatic title derived from the first meaningful assistant line. On the first turn of a new chat, the
   assistant is required to read the generated grounding sheet at
   ``runtime/portal/assistant/cheat-sheet.md`` and the FABLE/Modelwright documentation and source
   paths it lists before answering. The sheet is compiled from every listed doc, contains a
   documentation digest plus an AST-generated source API index, and is also available at
   ``GET /api/assistant/cheatsheet.md``. The agent must open the full cited file when a question
   needs exact signatures, behaviour, examples, or caveats. The bridge invokes the installed
   ``opencode`` CLI in the repository root and passes compact portal context. The service never
   reads provider keys. For issue-filing requests, the assistant follows
   :doc:`github-issue-workflow`: it asks for missing type, scope, scale, and verification details,
   drafts the canonical phase/task body, validates it with ``scripts/check_issue_body.py``, shows the
   draft for confirmation, and posts it with ``gh issue create --body-file``.

Service surface
---------------

The service is intentionally small and readable:

.. list-table::
   :header-rows: 1
   :widths: 46 54

   * - Endpoint
     - Purpose
   * - ``GET /api/health``
     - Service version, configured versions, prepared state, assistant state.
   * - ``GET /api/options``
     - Portal title, runtime directory, versions, docs URL.
   * - ``GET /api/agent``
     - Assistant enablement, executable availability, model, working directory, and timeout.
   * - ``GET /api/artifacts``
     - Readiness summaries for every configured version.
   * - ``GET /api/artifacts/{version}``
     - One artifact summary plus compact validation state.
   * - ``GET /api/validation/{version}``
     - Compact validation evidence or an explicit unavailable message.
   * - ``GET /api/models/{version}/status``
     - In-memory preparation status.
   * - ``POST /api/models/{version}/prepare``
     - Start the materialize/discover/load job.
   * - ``POST /api/models/{version}/materialize``
     - Decompress the approved model archive synchronously.
   * - ``GET /api/models/{version}/spec``
     - Compact control, table, and headline metadata after preparation.
   * - ``GET /api/jobs/{job_id}``
     - Poll a preparation or run job.
   * - ``GET /api/runs`` / ``POST /api/runs``
     - List saved runs or start a scenario run.
   * - ``GET /api/runs/{run_id}``
     - Saved run summary and headline frames.
   * - ``GET /api/runs/{run_id}/tables/{table_name}``
     - One saved rendered table.
   * - ``POST /api/compare``
     - Align saved runs by headline series and selection values.
   * - ``GET /api/chats`` / ``POST /api/chats``
     - List persistent assistant chats or create one.
   * - ``GET /api/chats/{chat_id}`` / ``DELETE /api/chats/{chat_id}``
     - Load or delete one persistent chat.
   * - ``GET /api/assistant/cheatsheet.md``
     - The generated grounding sheet and required-reading list.
   * - ``GET /api/scenario-bundles``
     - Tracked scenario-bundle examples.
   * - ``POST /api/assistant``
     - Optional local assistant turn; returns ``403`` unless enabled.

Design lineage
--------------

The portal reuses patterns proven in adjacent UBC FRESH projects:

- **FHOPS and WS4**: FastAPI behind an optional extra, a vanilla ES-module SPA, a loopback-only
  default, an explicit remote-bind guard, and a reader service that calls existing computation rather
  than embedding a second model.
- **Fresh Urban Forest Lab**: a multi-page decision-support shell with KPI cards, scenario state,
  explicit artifact readiness, and an optional local assistant.
- **fresh-fvsbc**: provenance-oriented run records. Every saved portal run keeps the portal version,
  workbook and generated-model paths/sizes, prepared timestamp, and workbook id beside the outputs.
- **HectaresBC**: dependency-free workspace tabs, accessible empty states, and progressive detail
  panels instead of a build toolchain.
- **FABLE Pyculator itself**: the typed spec, selection controls, output-table renderer, headline
  frames, scenario bundles, and validation-evidence vocabulary remain the source of truth.

2070 trend extension
--------------------

The native FABLE workbooks and generated models end at 2050. The portal optionally extends a run to
2070 using a linear trend fitted over the 2035-2050 values for each numeric series.

- The 2070 option extrapolates 2055, 2060, 2065, and 2070.
- Headline series and one-row-per-year output tables are extended.
- Multi-row-per-year tables are extended group-by-group using text identity columns such as
  `PROD_GROUP`, `Product`, `PRODUCT`, or `CROP`.
- Tables without a usable identity column or trend are left at native 2050 and carry an explicit
  "not extended" table note.
- Every extended run records the method and a warning that 2055-2070 are not native FABLE results.
- The extension never changes the generated model or workbook; it is a presentation-layer projection.

Use it from the Workbench **Horizon** selector. Select **Native FABLE horizon (2050)** for actual
model results.

Data-quality warnings
---------------------

The Results page shows a run-scoped **Data quality** panel. It includes only the notes that apply to
the selected run, such as:

- 2070 trend-extension warning;
- 2024 land-total component fallback;
- missing 2024 water-footprint series;
- derived GHG versus cached `TotalCO2e` divergence;
- output tables that could not be extended.

Warnings are persisted in `run.json` as `quality_warnings` and are available from
`GET /api/runs/{run_id}`.

Security and limitations
------------------------

- No authentication, accounts, multi-tenant storage, or remote execution scheduling.
- No browser-side FABLE calculation and no hidden UI-only values.
- Source workbooks are never mutated.
- The assistant is opt-in and executes the installed local CLI with the service user's permissions.
- A deployed portal should sit behind an authenticated proxy and use a non-loopback bind only with
  ``--allow-remote``.

Verification
------------

The portal tests cover artifact naming and materialization, spec JSON round-tripping, preparation
jobs, scenario runs, saved table retrieval, comparison, validation lookup, persistent chats,
assistant enablement and session passthrough, markdown safety, grounding checks, and the bind guard:

.. code-block:: bash

   python -m pytest -q tests/web/test_portal.py tests/web/test_chats.py tests/web/test_assistant.py
   python -m pytest -q tests/web/test_markdown.py tests/web/test_grounding_evals.py
   python scripts/evaluate_assistant_grounding.py
   python -m ruff check src/fable_pyculator/web src/fable_pyculator/cli.py tests/web

See :doc:`assistant-grounding-evals` for the opt-in live assistant and Chromium smoke checks.
