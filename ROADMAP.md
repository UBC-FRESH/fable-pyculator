# Roadmap

This roadmap is the current project plan and issue tracker map for `fable-pyculator`.

The near-term direction is to build a FABLE Calculator-specific notebook/user-guide layer on top of
Modelwright-generated Python models while preserving Modelwright as the generic conversion engine.

## Current Next Steps

- Phase 7 issue #48 is active to address first-user feedback about 2021 notebook wiring and
  generated-model artifact guidance.
- `v0.1.0a1` has been published to TestPyPI and PyPI; future release work should target a new
  version.
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

Active branch: `feature/p2-output-flavour-wildcards`.

Status: complete.

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
- [x] P2.5 Add wildcard output flavour tag filters. Child issue: #21.
  - Status: complete.
  - [x] Support `DATA` as a prefix-family alias for all `DATA-*` tags.
  - [x] Support trailing-star wildcard filters such as `DATA*` and `OUTPUT-*`.
  - [x] Preserve exact-tag behavior and `DIRECT`/`AUX` context-column defaults.
  - [x] Add unit tests and docs examples for wildcard filters.

Acceptance boundary:

- May claim discovered FABLE-C output tables carry workbook-derived column flavour metadata for the
  inspected public workbook structures.
- May claim output DataFrames can be filtered by canonical flavour tags while preserving all-column
  rendering by default.
- After P2.5, may claim exact, prefix-family, and trailing-star wildcard flavour filters are
  supported.
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
- `.venv/bin/python -m pytest tests/test_surface.py -q` passed with 7 tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed after P2.5 docs updates.

Closeout evidence:

- Phase 2 parent issue #15 is closed.
- Phase 2 PR #20 merged to `main` with merge commit `1be2e19`.
- Phase 2 follow-up PR #22 merged to `main` with merge commit `6ecd076`.
- Post-merge Tests and Docs Pages workflows passed, and GitHub Pages deployed.

## Phase 3: Default Notebook Loop To All Rendered Outputs

GitHub parent issue: #23.

Active branch: `feature/p3-default-all-rendered-outputs`.

Status: complete.

Goal: make one generated-model run render every declared output table and every curated headline frame
by default so notebook users can inspect additional outputs without rerunning a model that may take
several minutes.

- [x] P3.1 Update notebook loop default selection semantics. Child issue: #25.
  - Status: complete.
  - [x] Make `run_notebook_loop` render all spec output tables by default.
  - [x] Make `run_notebook_loop` render all spec headline frames by default.
  - [x] Preserve explicit subset arguments for faster focused rendering.
  - [x] Thread the semantics through `run_2020_notebook_loop`.
- [x] P3.2 Update tests and docs for all-output defaults. Child issue: #24.
  - Status: complete.
  - [x] Add tests for default all-output rendering.
  - [x] Add tests for explicit subset rendering.
  - [x] Update README and Sphinx notebook workflow docs.

Acceptance boundary:

- May claim `run_notebook_loop` and `run_2020_notebook_loop` render all declared output tables and
  headline frames by default.
- Must preserve explicit subset rendering through `output_table_names` and `headline_series_names`.
- Must not change generated-model execution semantics.

Implementation evidence:

- Changed notebook loop defaults so `output_table_names=None` and `headline_series_names=None` render
  every declared output table and headline frame from the spec.
- Preserved explicit subset rendering for callers that pass `output_table_names` or
  `headline_series_names`.
- Updated and re-executed the 2020 example notebook so it imports `output_table_frame`, uses the
  all-output default, and renders wildcard flavour-filter examples without stale errors.
- Updated README and Sphinx notebook workflow docs to describe the run-once, inspect-any-result
  behavior.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 26 tests and 6 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- Re-executed `examples/notebooks/fable-pyculator-2020-loop.ipynb` with repo `.venv`; saved 8
  executed code cells, 0 errors, 0 stream outputs, 5 HTML table outputs, and 1 PNG figure.

Closeout evidence:

- Phase 3 parent issue #23 is closed.
- Phase 3 PR #26 merged to `main` with merge commit `9def97b`.
- Post-merge Tests and Docs Pages workflows passed, and GitHub Pages deployed.

## Phase 4: Scenario Definition Table Discovery

GitHub parent issue: #29.

Active branch: `feature/p4-scenario-definition-table-discovery`.

Status: complete.

Goal: discover the FABLE-C `SCENARIOS definition` workbook surface as structured notebook metadata
so users can inspect the parameter-definition tables behind the scenario-selection controls before
the project attempts richer editing widgets.

- [x] P4.1 Inspect scenario definition workbook tables. Child issue: #30.
  - Status: complete.
  - [x] Record the 2020/2021 `SCENARIOS definition` native table inventory.
  - [x] Capture provenance-tag row behavior and known 2019 older-structure difference.
  - [x] Add a focused planning note with assumptions and follow-up risks.
- [x] P4.2 Add scenario definition table discovery API. Child issue: #31.
  - Status: complete.
  - [x] Add typed scenario-definition table declarations.
  - [x] Discover native Excel tables from `SCENARIOS definition`.
  - [x] Preserve headers, cell refs, range refs, row/column labels, and role/source-marker
        provenance.
  - [x] Include discovered tables in `build_2020_notebook_spec`.
- [x] P4.3 Add notebook inspection helpers for definition tables. Child issue: #32.
  - Status: complete.
  - [x] Add pandas rendering helper(s) for one or all scenario-definition tables.
  - [x] Include DataFrame attrs for workbook provenance and column metadata.
  - [x] Add focused synthetic tests.
- [x] P4.4 Document and validate scenario definition discovery. Child issue: #33.
  - Status: complete.
  - [x] Update README and Sphinx guides.
  - [x] Add opt-in workbook-backed checks for 2020/2021 table inventory stability.
  - [x] Update roadmap and changelog evidence.
  - [x] Run default verification and record results.

Acceptance boundary:

- May claim the inspected 2020 and 2021 public FABLE-C workbooks expose notebook-inspectable
  scenario-definition table metadata.
- May claim definition table DataFrames preserve workbook headers, row labels, cell refs, and
  column role/source-marker provenance.
- Must not claim full editable scenario-definition widgets, stable API compatibility, production
  readiness, or arbitrary country-calculator support.

Implementation evidence:

- Added `planning/phase-4-scenario-definition-table-discovery.md` with the 2020/2021 table inventory
  and known 2019 older-structure note.
- Added `ScenarioDefinitionTable` and `discover_scenario_definition_tables`.
- Added `scenario_definition_table_frame` and `scenario_definition_tables` notebook inspection
  helpers.
- Included scenario-definition table discovery in `build_2020_notebook_spec`.
- Updated README and Sphinx guides with scenario-definition table inspection examples.
- Added synthetic and opt-in workbook-backed tests for scenario-definition table discovery.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 29 tests and 8 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -q tests/test_fable_workbook_scenario_definition_tables.py`
  passed with 2 tests against ignored local workbook artifacts.

Closeout evidence:

- Phase 4 parent issue #29 is closed.
- Phase 4 PR #34 merged to `main` with merge commit `862f964`.
- Post-merge Tests and Docs Pages workflows passed, and GitHub Pages deployed.

## Phase 5: Scenario Definition Input Semantics

GitHub parent issue: #35.

Active branch: `feature/p5-scenario-definition-input-semantics`.

Status: complete.

Goal: correct the Phase 4 terminology and API boundary for `SCENARIOS definition`, keeping
output-sheet column flavour metadata separate from scenario-definition role/source metadata, then
add workbook-derived links from selection-control locations such as `S.3` to the relevant
scenario-definition tables.

- [x] P5.1 Separate definition role metadata from output flavour tags. Child issue: #36.
  - Status: complete.
  - [x] Rename scenario-definition table metadata away from `column_flavour_*`.
  - [x] Keep output-sheet flavour tags scoped to output tables.
  - [x] Remove `SCEN` from output flavour-tag normalization.
  - [x] Add synthetic regression tests for the vocabulary separation.
- [x] P5.2 Discover selection-location links for definition tables. Child issue: #37.
  - Status: complete.
  - [x] Discover `S.x` and `S.x.y` markers above native `SCENARIOS definition` tables.
  - [x] Preserve marker source cell refs.
  - [x] Add workbook-backed assertions for representative 2020/2021 links.
- [x] P5.3 Add selection-to-definition lookup helpers. Child issue: #38.
  - Status: complete.
  - [x] Add helper(s) that return scenario-definition tables for a selection location.
  - [x] Support family lookups such as `S.3` returning `S.3.a`, `S.3.b`, and `S.3.c` tables.
  - [x] Add notebook-friendly DataFrame examples/tests.
- [x] P5.4 Document and validate scenario definition semantics. Child issue: #39.
  - Status: complete.
  - [x] Update README and Sphinx guides.
  - [x] Add/update planning notes.
  - [x] Update roadmap and changelog evidence.
  - [x] Run default verification and record results.

Acceptance boundary:

- May claim output-table flavour metadata and scenario-definition role/source metadata are separate
  concepts in the public notebook API.
- May claim discovered scenario-definition tables can be looked up by selection location/family for
  the inspected 2020 and 2021 public workbook structures.
- Must not claim full editable scenario-definition widgets, stable API compatibility, production
  readiness, or arbitrary country-calculator support.

Implementation evidence:

- Renamed scenario-definition table metadata to `column_role_tags`, `raw_column_role_tags`, and
  `column_role_tag_refs`.
- Kept `OutputTable.column_flavour_*` and output flavour filtering scoped to canonical output sheets.
- Removed `SCEN` from output flavour-tag normalization and added regression coverage.
- Added `ScenarioDefinitionTable.scenario_locations` and `scenario_location_refs`.
- Added `scenario_definition_tables_for_location` with exact and family matching.
- Added `planning/phase-5-scenario-definition-input-semantics.md`.
- Updated README and Sphinx docs to distinguish output flavour tags from scenario-definition
  role/source markers.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 30 tests and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -q tests/test_fable_workbook_output_flavour_tags.py tests/test_fable_workbook_scenario_definition_tables.py`
  passed with 5 tests against ignored local workbook artifacts.

Closeout evidence:

- Phase 5 parent issue #35 is closed.
- Phase 5 PR #40 merged to `main` with merge commit `2dfd65e`.
- Post-merge Tests and Docs Pages workflows passed, and GitHub Pages deployed.

## Phase 6: Alpha Release Readiness

GitHub parent issue: #41.

Active branch: `feature/p6-alpha-release-readiness`.

Status: complete.

Goal: prepare FABLE Pyculator for a narrow `v0.1.0a1` alpha release by mirroring Modelwright's
package-release workflow and tightening documentation/API coverage.

- [x] P6.1 Align package metadata and release artifact checks. Child issue: #42.
  - Status: complete.
  - [x] Bump package version to `0.1.0a1`.
  - [x] Add Modelwright-style `quality`, `test`, and `release` dependency extras.
  - [x] Add `__version__` to the package root.
  - [x] Add `scripts/check_release_artifacts.sh` adapted for FABLE Pyculator.
  - [x] Add CI release-artifact checks.
- [x] P6.2 Add GitHub release publication workflow. Child issue: #43.
  - Status: complete.
  - [x] Add Modelwright-style `.github/workflows/release.yml`.
  - [x] Use trusted-publishing environments for TestPyPI/PyPI.
  - [x] Upload release artifacts from the build job.
  - [x] Document tag and workflow dispatch behavior.
- [x] P6.3 Expand API documentation and public docstrings. Child issue: #44.
  - Status: complete.
  - [x] Expand Sphinx API docs to module-level coverage.
  - [x] Review public source modules for concise but useful docstrings.
  - [x] Keep alpha boundaries clear in docs.
  - [x] Verify docs build with warnings as errors.
- [x] P6.4 Document alpha release runbook and verify release readiness. Child issue: #45.
  - Status: complete.
  - [x] Add release/deployment Sphinx guide.
  - [x] Update README, roadmap, and changelog.
  - [x] Run full checks plus release artifact checks.
  - [x] Record release-readiness evidence and remaining alpha caveats.

Acceptance boundary:

- May claim FABLE Pyculator has Modelwright-aligned release artifact checks and release workflow
  scaffolding for a `0.1.0a1` alpha.
- May claim the alpha package installs and exposes documented notebook-wrapper APIs.
- Must not claim stable public API compatibility, full editable scenario-definition widgets,
  production readiness, full generated-model equivalence, or arbitrary country-calculator support.

Implementation evidence:

- Bumped the package release target to `0.1.0a1` in `pyproject.toml` and
  `fable_pyculator.__version__`.
- Added Modelwright-style `quality`, `test`, and `release` optional dependency extras.
- Added `scripts/check_release_artifacts.sh` to build sdist/wheel artifacts, run `twine check`,
  inspect package contents for private workbook/generated-model leakage, and smoke-test a clean wheel
  install.
- Split CI into quality, pytest/docs, and release-artifact jobs.
- Added `.github/workflows/release.yml` with artifact upload and trusted-publishing jobs for
  TestPyPI/PyPI.
- Expanded Sphinx API docs to cover the package facade and public modules.
- Expanded public module, dataclass, and helper docstrings across `spec`, `discovery`, `controls`,
  `notebook`, and `surface`.
- Added `docs/guides/release-deployment.rst` with local checks, artifact gates, TestPyPI/PyPI
  publication steps, GitHub Pages closeout expectations, rollback notes, and alpha caveats.
- Updated README, bootstrap instructions, roadmap, and changelog for the release-readiness workflow.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 31 tests and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed for `fable-pyculator 0.1.0a1`, including clean wheel
  install and import smoke checks.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for the ignored local 2019,
  2020, and 2021 workbook artifacts.

Closeout evidence:

- Phase 6 parent issue #41 is closed.
- Phase 6 PR #46 merged to `main` with merge commit `f90cde1`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest/docs, and release-artifact
  jobs.
- Post-merge `Docs Pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  artifact verification, artifact upload, and GitHub Pages deployment.

Release evidence:

- Tag `v0.1.0a1` was pushed from closeout commit `b52057f`.
- TestPyPI release workflow run `28271969238` passed, and a clean TestPyPI install smoke test
  imported `fable_pyculator 0.1.0a1`.
- PyPI release workflow run `28272354876` passed, and a clean PyPI install smoke test imported
  `fable_pyculator 0.1.0a1`.

## Phase 7: 2021 Notebook Artifact Wiring And Generated-Model Guidance

GitHub parent issue: #48.

Active branch: `feature/p7-2021-artifact-wiring`.

Status: active.

Goal: address first-user feedback that the 2020 example notebook is easy to misuse with a 2021
workbook and that the docs do not clearly explain where Modelwright generated-model artifacts come
from.

- [x] P7.1 Add version-specific notebook loop helpers. Child issue: #50.
  - Status: complete.
  - [x] Add 2021 default workbook and generated-model paths.
  - [x] Add `build_2021_notebook_spec`.
  - [x] Add `run_2021_notebook_loop`.
  - [x] Preserve 2020 helper behavior and exports.
  - [x] Add unit tests for 2021 helper wiring.
- [x] P7.2 Add 2021 example notebook without 2020 fallback. Child issue: #52.
  - Status: complete.
  - [x] Add a 2021 example notebook.
  - [x] Use `tmp/private-workbooks/2021_Open_FABLECalculator.xlsx`.
  - [x] Use `tmp/generated-models/fable-2021/generated_fable_2021_model.py`.
  - [x] Do not decompress or reference the 2020 Modelwright generated model archive.
  - [x] Add/update notebook tracking tests.
- [x] P7.3 Document generated-model artifact boundary. Child issue: #51.
  - Status: complete.
  - [x] Explain that FABLE Pyculator wraps Modelwright generated models but does not create
        generation contracts.
  - [x] Explain what `contract.json`, `expressions.json`, and `constants.json` are for.
  - [x] Document 2020 vs 2021 artifact paths and validation boundaries.
  - [x] Link the generated-model guide from README and Sphinx docs.
- [x] P7.4 Validate docs and close user-feedback loop. Child issue: #49.
  - Status: complete.
  - [x] Update roadmap and changelog.
  - [x] Run lint, tests, docs, release artifact checks, and workbook checksums.
  - [x] Record evidence.
  - [ ] Close the phase through PR and docs deployment.

Acceptance boundary:

- May claim FABLE Pyculator has explicit 2020 and 2021 notebook wrapper artifact paths.
- May claim 2021 workbook structure can be discovered by wrapper helpers.
- Must not claim 2021 generated-model output equivalence until a matching 2021 generated model is
  produced and validated.
- Must not claim FABLE Pyculator can generate Modelwright `contract.json`, `expressions.json`, or
  `constants.json` from a FABLE workbook.

Implementation evidence:

- Added version-specific 2021 notebook defaults and helpers: `DEFAULT_2021_WORKBOOK_PATH`,
  `DEFAULT_2021_GENERATED_MODEL_PATH`, `build_2021_notebook_spec`, and `run_2021_notebook_loop`.
- Added `build_notebook_spec` as the shared explicit workbook-spec builder used by 2020 and 2021
  helpers.
- Preserved the existing 2020 helper behavior while loading 2020 and 2021 generated models under
  separate module names.
- Added `examples/notebooks/fable-pyculator-2021-loop.ipynb` as an unexecuted wiring template that
  checks for matching 2021 artifacts and never falls back to the 2020 generated model archive.
- Added `docs/guides/generated-model-artifacts.rst` documenting the artifact boundary, 2020/2021
  generated-model path contract, and Modelwright JSON generation inputs.
- Linked generated-model artifact guidance from README, Sphinx index, notebook-control docs, the
  2020 workflow guide, and validation-scope docs.
- Hardened release artifact smoke checks so installed wheels expose the new 2021 helper API.
- Created Modelwright follow-up issue UBC-FRESH/modelwright#201 for generated-model contract
  materialization documentation/tooling.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 36 tests and 9 workbook-backed skips.
- `.venv/bin/python -m pytest tests/test_notebook.py tests/test_examples.py tests/test_scripts.py -q`
  passed with 13 tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed, including clean installed-wheel smoke checks for the
  new 2021 exports.

Closeout evidence:

- Pending.
