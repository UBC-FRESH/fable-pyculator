# Roadmap

This roadmap is the current project plan and issue tracker map for `fable-pyculator`.

The near-term direction is to build a FABLE Calculator-specific notebook/user-guide layer on top of
Modelwright-generated Python models while preserving Modelwright as the generic conversion engine.

## Current Next Steps

- Phase 2 implementation is complete on branch `feature/p2-output-table-column-flavour-filtering`;
  open a PR for issue #15, wait for CI, merge to `main`, and confirm docs deployment.
- Keep Sphinx docs deployment as a phase closeout gate: every phase PR must pass the docs build, and
  the merge to `main` must trigger the GitHub Pages deployment workflow.

## Phase 0: Governance Bootstrap

GitHub parent issue: #1.

Initial commit: `8a5577d`.

Status: complete.

Goal: establish the repository contract, roadmap, changelog, planning area, package/docs/test
scaffold, benchmark metadata, reference-document handling, and artifact hygiene for FABLE Pyculator.
This phase wraps the current uncommitted scaffold as bootstrap evidence.

- [x] P0.1 Establish project overview and agent operating contract. Child issue: #2.
  - [x] Add `AGENTS.md` customized for FABLE Pyculator.
  - [x] Define the project boundary relative to Modelwright.
  - [x] Record source workbook, generated-model, and local artifact rules.
- [x] P0.2 Establish roadmap, changelog, planning area, and artifact rules. Child issue: #3.
  - [x] Add `ROADMAP.md`.
  - [x] Add `CHANGE_LOG.md`.
  - [x] Add `planning/README.md`.
  - [x] Keep workbook binaries, generated models, extracts, logs, and validation reports under ignored
        `tmp/`.
- [x] P0.3 Capture current package/docs/test scaffold as bootstrap evidence. Child issue: #4.
  - [x] Add package metadata and importable `fable_pyculator` module.
  - [x] Add selection-control discovery and notebook control records.
  - [x] Add output-table discovery and pandas rendering helpers.
  - [x] Add Sphinx documentation scaffold and FABLE workbook structure notes.
  - [x] Add benchmark metadata and checksums for the public FABLE-C workbooks.
  - [x] Track the public 2020 FABLE Calculator documentation PDF under `reference/`.
- [x] P0.4 Define strict GitHub issue, branch, and PR workflow. Child issue: #5.
  - [x] Mirror Modelwright's parent issue, child issue, feature branch, PR, and changelog workflow.
  - [x] Allow issue-number placeholders until the public remote and `gh` access exist.
  - [x] Require roadmap, changelog, issue comments, and verification evidence to stay synchronized
        after issue mapping is active.

Acceptance boundary:

- May claim FABLE Pyculator has a documented agent-assisted development workflow.
- May claim the current scaffold discovers FABLE-C selection controls and output tables for the
  inspected public workbook structure.
- Must not claim stable public API compatibility, arbitrary FABLE country-calculator support,
  production FABLE-P readiness, or full generated-model equivalence.

Implementation evidence:

- Added `AGENTS.md`, `ROADMAP.md`, `CHANGE_LOG.md`, and `planning/README.md`.
- Added package scaffolding under `src/fable_pyculator/`.
- Added Sphinx documentation under `docs/`.
- Added public FABLE-C benchmark metadata under `benchmarks/fable-calculator/`.
- Added the public 2020 FABLE Calculator documentation PDF under `reference/fable-calculator/`.
- Downloaded the public 2019, 2020, and 2021 FABLE-C workbooks into ignored
  `tmp/private-workbooks/`.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with `13` tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for all three ignored workbook
  files.

Closeout evidence:

- Public GitHub repository: `UBC-FRESH/fable-pyculator`.
- Local `origin` remote points to `https://github.com/UBC-FRESH/fable-pyculator.git`.
- GitHub CLI installed locally under `~/.local/bin/gh` and authenticated as `gparadis`.
- Phase 0 parent and child issues created and mapped in this roadmap.
- Bootstrap commit pushed to `main`.

## Phase 1: FABLE-C Notebook Wrapper Maturation

GitHub parent issue: #6.

Active branch: `feature/p1-fable-c-notebook-wrapper-maturation`.

Status: complete.

Goal: turn the bootstrap selection-control and output-table discoveries into a coherent 2020 FABLE-C
notebook workflow that can drive a generated Modelwright model, render canonical outputs, and expose
clear user-guide examples.

- [x] P1.1 Harden scenario selection control discovery. Child issue: #7.
  - Status: complete.
  - [x] Validate S.1 through S.16 on the 2020 workbook.
  - [x] Confirm 2021 compatibility and document differences.
  - [x] Keep 2019 as an older-structure fragility check.
- [x] P1.2 Curate headline output indicators and figures. Child issue: #8.
  - Status: complete.
  - [x] Use `Indextables` and the canonical output sheets to select initial FOOD, LAND, GHG, and WATER
        headline outputs.
  - [x] Render notebook-friendly pandas tables and matplotlib figures.
- [x] P1.3 Build the first 2020 generated-model notebook loop. Child issue: #9.
  - Status: complete.
  - [x] Load or reference an ignored generated 2020 Modelwright model.
  - [x] Apply selection-control overrides.
  - [x] Render discovered output tables and curated headline outputs.
- [x] P1.4 Add user-guide documentation and validation evidence. Child issue: #10.
  - Status: complete.
  - [x] Expand the Sphinx guide around scenario selection, running the model, and reading outputs.
  - [x] Record 2020 benchmark evidence and 2021 follow-up scope.

Acceptance boundary:

- May claim a coherent early FABLE-C notebook wrapper workflow for the inspected 2020 workbook.
- Must not claim production readiness or cross-country support until country-specific validation
  evidence is recorded.

Implementation evidence:

- Added opt-in workbook-backed tests for the 2020, 2021, and 2019 public FABLE-C workbooks.
- Added `planning/phase-1-selection-control-validation.md` with validation findings.
- Added curated `HeadlineSeries` declarations for initial FOOD, LAND, GHG, and WATER outputs.
- Added `curate_default_headline_series`, `headline_frame`, `headline_frames`, and `plot_headline`.
- Added `planning/phase-1-headline-output-curation.md` with source table and column mappings.
- Added `.github/workflows/docs-pages.yml` so Sphinx docs build on PRs and deploy to GitHub Pages
  after merges to `main`.
- Confirmed GitHub Pages is configured for workflow deployment at
  `https://ubc-fresh.github.io/fable-pyculator/`.
- Added the first 2020 notebook-loop helpers: `build_2020_notebook_spec`, `load_generated_model`,
  `run_notebook_loop`, and `run_2020_notebook_loop`.
- Added tracked example notebook `examples/notebooks/fable-pyculator-2020-loop.ipynb`.
- Added `planning/phase-1-2020-notebook-loop.md` with ignored generated-model artifact paths and
  loop boundaries.
- Added Sphinx guide pages `docs/guides/2020-notebook-workflow.rst` and
  `docs/guides/validation-scope.rst`.
- Added `planning/phase-1-user-guide-validation-closeout.md` with Phase 1 closeout evidence and
  2021 follow-up scope.
- Aligned Sphinx configuration and Pages workflow with Modelwright's Read the Docs themed docs setup,
  including RTD theme options, docs requirements, and a theme artifact verifier.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 16 tests and 4 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv tests/test_fable_workbook_selection_controls.py`
  passed against ignored local workbook artifacts.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv tests/test_fable_workbook_headline_series.py`
  passed against the ignored local 2020 workbook artifact.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv tests/test_fable_workbook_selection_controls.py tests/test_fable_workbook_headline_series.py`
  passed with 4 workbook-backed tests.
- `.venv/bin/python -m pytest tests/test_notebook.py` passed with 4 tests.
- `.venv/bin/python -m pytest tests/test_examples.py` passed with 1 test.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.

Closeout evidence:

- Phase 1 parent issue #6 is closed.
- Phase 1 PR #11 merged to `main` with merge commit `c85378a`.
- RTD docs alignment PR #12 merged to `main` with merge commit `24a6f24`.
- Post-merge `Docs Pages` workflow built, verified the Read the Docs theme artifact, and deployed to
  `https://ubc-fresh.github.io/fable-pyculator/`.

## Phase 2: Output Table Column-Flavour Filtering

GitHub parent issue: #15.

Active branch: `feature/p2-output-table-column-flavour-filtering`.

Status: active.

Goal: add workbook-derived column flavour metadata to discovered output tables and let notebooks
render DataFrames filtered by tags such as `OUTPUT-1`, `DATA-4`, `CALC`, and `DIRECT` while
preserving current all-column rendering by default.

- [x] P2.1 Discover output table column flavour metadata. Child issue: #16.
  - Status: complete.
  - [x] Extend `OutputTable` with canonical, raw, and source-cell column flavour metadata.
  - [x] Detect the closest recognized pre-header tag row above each canonical output Excel table.
  - [x] Normalize variants such as `DATA -3.2` and `OUTPUT - 8` while preserving raw values.
- [x] P2.2 Add output table flavour filtering API. Child issue: #18.
  - Status: complete.
  - [x] Add filter arguments to `output_table_frame` and `output_tables`.
  - [x] Thread filter arguments through `run_notebook_loop` and `run_2020_notebook_loop`.
  - [x] Keep `DIRECT` and `AUX` context columns by default when filtering.
- [x] P2.3 Document output table flavour tags. Child issue: #19.
  - Status: complete.
  - [x] Document the workbook pre-header flavour-tag row in the Sphinx guides.
  - [x] Add notebook/user-guide examples for all columns, `OUTPUT-8`, and one `DATA-*` filter.
- [x] P2.4 Validate output flavour tags across workbooks. Child issue: #17.
  - Status: complete.
  - [x] Add opt-in workbook-backed checks for 2020 and 2021 tag inventories.
  - [x] Confirm GHG `OUTPUT - 8` normalizes to `OUTPUT-8`.
  - [x] Record verification evidence before parent issue closeout.

Acceptance boundary:

- May claim discovered FABLE-C output tables carry workbook-derived column flavour metadata for the
  inspected public workbook structures.
- May claim output DataFrames can be filtered by canonical flavour tags while preserving all-column
  rendering by default.
- Must not claim stable public API compatibility or arbitrary country-calculator support until later
  validation and release-readiness evidence exists.

Implementation evidence:

- Added `OutputTable.column_flavour_tags`, `raw_column_flavour_tags`, and
  `column_flavour_tag_refs`.
- Updated output-table discovery to capture and normalize workbook pre-header tag rows.
- Added render-time filtering to `output_table_frame`, `output_tables`, `run_notebook_loop`, and
  `run_2020_notebook_loop`.
- Added Sphinx guide examples for filtered output table rendering.
- Added synthetic and opt-in workbook-backed tests for discovery, filtering, and 2020/2021 inventory
  stability.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 24 tests and 6 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -vv tests/test_fable_workbook_output_flavour_tags.py`
  passed against ignored local workbook artifacts.
