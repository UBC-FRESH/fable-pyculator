# Roadmap

This roadmap is the current project plan and issue tracker map for `fable-pyculator`.

The near-term direction is to build a FABLE Calculator-specific notebook/user-guide layer on top of
Modelwright-generated Python models while preserving Modelwright as the generic conversion engine.

## Current Next Steps

- Phase 8 is closed: the validated 2021 FABLE-C generated model is published as a compressed repo
  artifact, PR #60 merged, and post-merge Test and Docs Pages workflows passed.
- Phase 9 was reactivated after Phase 12 to fill the skipped FreshForge provider pilot slot with a
  thin plan-only provider over the package workflow helpers.
- Phase 10 is closed: the Abdulateef-facing 2021 FreshForge build-plan notebook is tracked, PR #67
  merged, and post-merge Test and Docs Pages workflows passed.
- Phase 11 is closed: the Abdulateef-facing 2021 FreshForge-run notebook is tracked, PR #74 merged,
  and post-merge Test and Docs Pages workflows passed.
- Phase 13 is closed: the one-command 2021 FreshForge rebuild path is tracked, PR #95 merged, and
  post-merge Test and Docs Pages workflows passed.
- Phase 14 is active on `feature/p14-version-general-fable-build-workflows`: local implementation
  and verification are complete; open/merge the PR and confirm post-merge Test and Docs Pages
  workflows before closing parent issue #77.
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

## Phase 11: FreshForge-Run 2021 Model Build Notebook

GitHub parent issue: #69.

Active branch: `feature/p11-freshforge-2021-run-notebook`.

Status: complete.

Goal: add an Abdulateef-facing notebook that derives 2021 output refs with FABLE Pyculator, writes a
FreshForge workflow, and optionally runs the Modelwright generated-model build through FreshForge's
serial local runner.

- [x] P11.1 Add FreshForge-run notebook template. Child issue: #70.
  - [x] Add `examples/notebooks/fable-pyculator-2021-freshforge-run.ipynb`.
  - [x] Derive `OUTPUT-*` output refs from the 2021 workbook structure.
  - [x] Write the Modelwright FreshForge workflow under ignored `tmp/generated-models/fable-2021/`.
  - [x] Gate execution behind `RUN_FRESHFORGE = False`.
- [x] P11.2 Add notebook static tests and artifact hygiene checks. Child issue: #71.
  - [x] Test that the notebook is unexecuted by default.
  - [x] Test that it uses FreshForge run APIs and only 2021 generated-model paths.
  - [x] Test that it contains no 2020 generated-model fallback.
- [x] P11.3 Update docs, README, roadmap, and changelog. Child issue: #72.
  - [x] Link the notebook from `examples/notebooks/README.md`.
  - [x] Link the notebook from the Sphinx notebook-control guide.
  - [x] Record Phase 11 evidence in roadmap and changelog.
- [x] P11.4 Verify, PR, deploy docs, and close phase. Child issue: #73.
  - [x] Run full local verification.
  - [x] Open PR and verify CI/docs.
  - [x] Confirm post-merge docs deployment.

Acceptance boundary:

- May claim FABLE Pyculator has a gated notebook showing how to run the 2021 Modelwright build
  through FreshForge.
- Must not claim a new generated-model equivalence result beyond the existing Phase 8 validation
  evidence.
- Must keep source workbooks, decompressed generated models, raw reports, and run artifacts under
  ignored `tmp/` paths.

Implementation evidence:

- Added `examples/notebooks/fable-pyculator-2021-freshforge-run.ipynb`.
- The notebook derives FABLE `OUTPUT-*` refs, writes `output_refs.json`, prepares cached-workbook
  validation, writes a FreshForge workflow, validates/plans it, and gates `run_workflow(...)` behind
  `RUN_FRESHFORGE = False`.
- The notebook ends by loading the newly generated 2021 model, when present, and rendering FABLE
  Pyculator output tables/headline frames.
- Linked the notebook from examples and Sphinx docs.

Verification evidence:

- `.venv/bin/python -m pytest tests/test_examples.py` passed with 5 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 39 tests and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed and copied the new notebook download.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for local 2019, 2020, and
  2021 workbook artifacts.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.

Closeout evidence:

- Phase 11 PR #74 merged to `main`.
- PR checks passed for quality, pytest/docs, and release artifacts.
- Post-merge Docs Pages workflow passed and deployed the new notebook download.

Release evidence:

- Tag `v0.1.0a1` was pushed from closeout commit `b52057f`.
- TestPyPI release workflow run `28271969238` passed, and a clean TestPyPI install smoke test
  imported `fable_pyculator 0.1.0a1`.
- PyPI release workflow run `28272354876` passed, and a clean PyPI install smoke test imported
  `fable_pyculator 0.1.0a1`.

## Phase 7: 2021 Notebook Artifact Wiring And Generated-Model Guidance

GitHub parent issue: #48.

Active branch: `feature/p7-2021-artifact-wiring`.

Status: complete.

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
  - [x] Close the phase through PR and docs deployment.

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

- Phase 7 parent issue #48 is closed.
- Phase 7 PR #53 merged to `main` with merge commit `c51af36`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest/docs, and release-artifact
  jobs.
- Post-merge `Docs Pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  artifact verification, artifact upload, and GitHub Pages deployment.

## Phase 8: Validated 2021 Generated Model Publication

GitHub parent issue: #54.

Active branch: `feature/p8-validated-2021-generated-model`.

Status: complete.

Goal: add the public 2021 FABLE-C generated Python model to `fable-pyculator` with the same evidence
discipline used for the 2020 Modelwright benchmark: generate from the public 2021 workbook, validate
against cached workbook outputs, publish only an approved compressed generated-model artifact, and
document the exact validation boundary.

- [x] P8.1 Define 2021 validation contract and output universe. Child issue: #59.
  - Status: complete.
  - [x] Derive the 2021 output universe from the public 2021 workbook using the same comparable-output
        contract as the 2020 benchmark.
  - [x] Record comparable output counts and any non-comparable cached blanks separately.
  - [x] Keep raw workbook extracts, output refs, generated JSON files, logs, and validation reports
        under ignored `tmp/`.
- [x] P8.2 Generate and validate the 2021 Modelwright Python model. Child issue: #58.
  - Status: complete.
  - [x] Run Modelwright extraction, contract inference, code generation, execution, and cached-output
        validation from the 2021 workbook.
  - [x] Require status `pass`, zero mismatches, and match count equal to comparable output count before
        making any 2021 equivalence claim.
  - [x] If validation fails, record blocker taxonomy and do not publish an equivalence artifact.
- [x] P8.3 Publish compressed 2021 generated-model artifact. Child issue: #55.
  - Status: complete.
  - [x] Track only `examples/fable_2021/generated_fable_2021_model.py.xz` as the approved compact
        generated-model artifact.
  - [x] Add `examples/fable_2021/README.md` with source workbook checksum, validation counts,
        generation command outline, and artifact boundary.
  - [x] Keep source workbook, decompressed `.py`, generated JSON inputs, logs, and raw validation
        outputs ignored.
- [x] P8.4 Update 2021 notebook, docs, and Basecamp guidance. Child issue: #57.
  - Status: complete.
  - [x] Update the 2021 notebook to materialize the compressed 2021 generated model into the ignored
        `tmp/generated-models/fable-2021/` path.
  - [x] Update README, generated-model artifact docs, validation-scope docs, release docs, and
        notebook docs with the exact Phase 8 evidence.
  - [x] Update the Basecamp follow-up draft to point users to the published 2021 artifact and its
        validation boundary.
- [x] P8.5 Verify, merge, deploy docs, and close phase. Child issue: #56.
  - Status: complete.
  - [x] Add tests for the compressed 2021 artifact, notebook artifact references, and release artifact
        allowlisting.
  - [x] Run lint, tests, opt-in workbook tests, docs, theme verification, checksum verification, release
        artifact checks, and `git diff --check`.
  - [x] Open and merge the Phase 8 PR only after CI passes.
  - [x] Confirm post-merge `Test` and `Docs Pages` workflows pass and the deployed docs show the
        updated 2021 validation claim before closing the parent issue.

Acceptance boundary:

- May claim 2021 generated-model equivalence only if the 2021 generated model validates with
  `0` comparable-output mismatches against the 2021 source workbook.
- Must record comparable output count, match count, mismatch count, and non-comparable cached blanks
  before publishing a validation claim.
- Must not track the 2021 source workbook, raw validation report, decompressed generated model,
  generated JSON inputs, logs, or ignored `tmp/` artifacts.
- Must not claim arbitrary country-calculator support, production readiness, or full FABLE-P model
  equivalence.

Implementation evidence:

- Added `examples/fable_2021/generated_fable_2021_model.py.xz` as the approved compressed generated
  model artifact.
- Added `examples/fable_2021/README.md` and `planning/phase-8-2021-validation-summary.md` with
  sanitized validation evidence and artifact boundaries.
- Updated the 2021 notebook to materialize the compressed generated model into
  `tmp/generated-models/fable-2021/generated_fable_2021_model.py`.
- Updated README and Sphinx docs to replace the old 2021 wiring-only caveat with the Phase 8
  validation evidence.
- Hardened release artifact checks so only the approved compressed 2021 generated model is allowed.
- Modelwright PR #204 merged to `main` at `c3734d3`, closing issue #203 for the generic generated
  `VLOOKUP` `#N/A` runtime semantic fix uncovered by the 2021 validation run.

Verification evidence:

- Clean Phase 8 validation summary: 281,922 comparable outputs, 281,922 matches, 0 mismatches, 15,080
  non-comparable cached blank formula outputs, zero graph diagnostics, and zero translation
  diagnostics.
- Modelwright targeted checks for PR #204 passed before merge: `.venv/bin/python -m ruff check .` and
  `.venv/bin/python -m pytest tests/test_python_generation.py tests/test_generated_execution.py -q`.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 37 tests and 9 workbook-backed skips.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -q tests/test_fable_workbook_output_flavour_tags.py tests/test_fable_workbook_selection_controls.py tests/test_fable_workbook_scenario_definition_tables.py` passed with 8 tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.

Closeout evidence:

- Phase 8 child issues #59, #58, #55, #57, and #56 are closed.
- Phase 8 PR #60 merged to `main` with merge commit `c073f4e`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest/docs, and release-artifact
  jobs.
- Post-merge `Docs Pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  artifact verification, artifact upload, and GitHub Pages deployment.

## Phase 9: FreshForge Provider Pilot For FABLE Notebook Workflows

GitHub parent issue: #61.

Active branch: `feature/p9-fable-freshforge-provider`.

Status: complete.

Goal: add a plan-only FreshForge provider for FABLE Pyculator notebook workflow stages after the
Modelwright FreshForge provider pilot exists. The provider should expose FABLE-specific workbook
surface discovery and notebook-loop planning while keeping generic generated-model inference,
generation, execution, and validation in Modelwright.

- [x] P9.1 Define FABLE Pyculator FreshForge provider boundary. Child issue: #85.
  - [x] Reactivate Phase 9 in the roadmap after Phase 12.
  - [x] Keep the provider plan-only.
  - [x] Record that Modelwright keeps generated-model mechanics.
  - [x] Record that FABLE Pyculator owns FABLE output-ref/notebook semantics.
- [x] P9.2 Add plan-only FABLE notebook workflow node vocabulary. Child issue: #86.
  - [x] Add `fable_pyculator.freshforge`.
  - [x] Add provider id `fable_pyculator`.
  - [x] Add provider factory `fable_pyculator.freshforge:provider_factory`.
  - [x] Add plan-only node metadata and validation diagnostics.
  - [x] Add a PyPI-safe `freshforge.providers` entry point without a FreshForge dependency.
- [x] P9.3 Add public-safe FABLE notebook workflow example. Child issue: #87.
  - [x] Add `examples/freshforge/fable_2021_notebook_workflow.yaml`.
  - [x] Use only public-safe ignored `tmp/` artifact paths.
  - [x] Compose FABLE Pyculator nodes around downstream Modelwright workflow artifact boundaries.
  - [x] Keep the example plan-only.
- [x] P9.4 Add docs and tests for provider discovery/planning. Child issue: #88.
  - [x] Add Sphinx provider guide.
  - [x] Link guide from docs index and API reference.
  - [x] Add tests for metadata, entry point, import boundary, example planning, and diagnostics.
  - [x] Keep FreshForge-present tests skipped when FreshForge is unavailable.
- [x] P9.5 Verify, PR, and close phase. Child issue: #89.
  - [x] Run Ruff, pytest, Sphinx, docs theme verification, checksums, release artifact checks, and
        `git diff --check`.
  - [x] Open PR from `feature/p9-fable-freshforge-provider` to `main`.
  - [x] Merge only after CI passes.
  - [x] Confirm post-merge `Test` and `Docs Pages` workflows before closing parent #61.

Acceptance boundary:

- May claim FABLE Pyculator exposes FABLE-specific workflow planning metadata to FreshForge.
- Must not claim FreshForge executes FABLE notebook loops or materializes artifacts.
- Must not move generic Modelwright conversion logic into FABLE Pyculator.
- Must not claim additional FABLE country-calculator compatibility from this planning layer alone.

Implementation evidence:

- Added `fable_pyculator.freshforge` with lazy FreshForge imports, provider id `fable_pyculator`,
  and a plan-only provider factory.
- Added plan-only node metadata for notebook spec discovery, output-ref derivation,
  validation-scenario preparation, Modelwright workflow construction, and notebook-loop planning.
- Added a PyPI-safe `freshforge.providers` entry point without adding a FreshForge runtime
  dependency.
- Added `examples/freshforge/fable_2021_notebook_workflow.yaml` as a public-safe plan-only workflow.
- Added `docs/guides/freshforge-provider-integration.rst`, linked it from the docs index and API
  reference, and added provider discovery/planning tests.

Verification evidence:

- `.venv/bin/python -m pytest tests/test_freshforge_integration.py -q` passed with 6 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 51 tests and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.

Closeout evidence:

- Phase 9 child issues #85, #86, #87, #88, and #89 are closed.
- Phase 9 PR #90 merged to `main` with merge commit `33d5903`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest/docs, and release-artifact
  jobs.
- Post-merge `Docs Pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  artifact verification, artifact upload, and GitHub Pages deployment.
- Live docs verification confirmed `guides/freshforge-provider-integration.html` documents the
  plan-only provider and `reference/api.html` includes `fable_pyculator.freshforge`.

## Phase 10: Cross-Package FreshForge Workflow Example

GitHub parent issue: #62.

Active branch: `feature/p10-2021-freshforge-build-notebook`.

Status: complete.

Goal: add a plan-only FreshForge workflow example that composes FABLE Pyculator workbook-surface
discovery with Modelwright generated-model inference, generation, execution, and validation planning.

- [x] P10.1 Add 2021 FreshForge build-plan notebook. Child issue: #64.
  - Status: complete.
  - [x] Add a 2021 notebook example for Abdulateef.
  - [x] Use FABLE Pyculator to derive/select 2021 output refs from workbook structure.
  - [x] Use FreshForge to validate/inspect/plan the Modelwright workflow graph.
  - [x] Show Modelwright commands for infer-contract, generate, execute, and evaluate.
  - [x] State clearly that FreshForge planning does not execute nodes.
- [x] P10.2 Document and test the 2021 FreshForge build-plan notebook. Child issue: #65.
  - Status: complete.
  - [x] Link the notebook from examples/docs surfaces.
  - [x] Add static tests for notebook JSON and workflow boundary text.
  - [x] Confirm no 2020 generated-model fallback is referenced.
  - [x] Preserve source workbook and raw generated artifacts under ignored `tmp` paths.
- [ ] P10.3 Verify and close FreshForge build-plan slice. Child issue: #66.
  - Status: complete.
  - [x] Run Ruff, pytest, Sphinx docs, docs theme verification, checksum verification, release artifact
        checks, and `git diff --check`.
  - [x] Open PR from `feature/p10-2021-freshforge-build-notebook` to `main`.
  - [x] Merge only after CI passes.
  - [x] Confirm post-merge Test and Docs Pages workflows pass.
  - [x] Close parent #62 after deployment evidence is recorded.

Acceptance boundary:

- May claim the cross-package graph explains the intended orchestration path.
- Must not claim FreshForge execution, artifact materialization, or new generated-model equivalence.
- Must keep source workbooks, raw generated models, logs, and validation reports ignored under `tmp/`.

Implementation evidence:

- Added `examples/notebooks/fable-pyculator-2021-freshforge-build-plan.ipynb` as an unexecuted
  plan-first notebook for rebuilding the 2021 generated model.
- The notebook derives `OUTPUT-*` output refs from the 2021 workbook structure, writes a FreshForge
  Modelwright workflow graph under ignored `tmp/`, validates/plans the graph when FreshForge is
  installed, and shows gated Modelwright build commands behind `RUN_BUILD = False`.
- Linked the notebook from `examples/notebooks/README.md` and the notebook-control Sphinx guide.
- Added static notebook tests that verify the FreshForge/Modelwright/FABLE boundary and prevent a
  2020 generated-model fallback reference.

Verification evidence:

- `.venv/bin/python -m pytest tests/test_examples.py -q` passed with 4 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 38 tests and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed and copied the new notebook download.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for the local 2019, 2020, and
  2021 workbook artifacts.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.

Closeout evidence:

- Phase 10 child issues #64 and #65 are closed; child issue #66 closed after PR and deployment
  evidence.
- Phase 10 PR #67 merged to `main` with merge commit `812ef39`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest/docs, and release-artifact
  jobs.
- Post-merge `Docs Pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  artifact verification, artifact upload, and GitHub Pages deployment.

## Phase 12: Output-Ref Derivation And FreshForge Workflow-Builder APIs

GitHub parent issue: #75.

Active branch: `feature/p12-output-ref-workflow-builder-apis`.

Status: complete.

Goal: extract the 2021 FreshForge notebook's output-ref derivation and workflow JSON assembly into
tested FABLE Pyculator helper APIs.

- [x] P12.1 Add output-ref derivation helpers. Child issue: #80.
  - [x] Add a public helper that derives output refs from a FABLE Pyculator spec.
  - [x] Support flavour filters such as `OUTPUT-*` and optional table-name restriction.
  - [x] Write stable sorted output-ref JSON.
  - [x] Add synthetic unit tests.
- [x] P12.2 Add FreshForge Modelwright workflow builder. Child issue: #81.
  - [x] Add a small artifact-path helper for version-specific build directories.
  - [x] Build the Modelwright FreshForge workflow document for infer, generate, execute, and evaluate.
  - [x] Write deterministic workflow JSON.
  - [x] Add tests for required nodes and artifact paths.
- [x] P12.3 Update 2021 FreshForge notebooks and docs. Child issue: #82.
  - [x] Update the 2021 build-plan notebook to use package helpers.
  - [x] Update the 2021 run notebook to use package helpers.
  - [x] Keep `RUN_FRESHFORGE = False` and avoid 2020 fallback references.
  - [x] Document the helper APIs in Sphinx docs.
- [x] P12.4 Verify, PR, deploy docs, and close phase. Child issue: #83.
  - [x] Run Ruff, pytest, Sphinx docs, docs theme verification, checksum verification, release
        artifact checks, and `git diff --check`.
  - [x] Open PR from `feature/p12-output-ref-workflow-builder-apis` to `main`.
  - [x] Merge only after CI passes.
  - [x] Confirm post-merge `Test` and `Docs Pages` workflows before closing parent #75.

Acceptance boundary:

- May claim reusable output-ref derivation and FreshForge workflow-builder APIs for FABLE
  generated-model workflows.
- Must not add the one-command 2021 rebuild script, scenario-bundle automation, or CI benchmark
  execution in this phase.

Implementation evidence:

- Added `fable_pyculator.workflows` with `derive_output_refs`, stable JSON writers,
  `freshforge_2021_build_paths`, cached-workbook validation-scenario generation, and a Modelwright
  FreshForge workflow builder for infer, generate, execute, and evaluate stages.
- Exported the workflow helpers from the package facade and documented them in the API reference.
- Updated the 2021 FreshForge build-plan and run notebooks to use the package helpers instead of
  hand-building output refs, validation scenarios, and workflow JSON inline.
- Added `tests/test_workflows.py` and strengthened static notebook tests to require helper usage.

Verification evidence:

- `.venv/bin/python -m pytest tests/test_workflows.py tests/test_examples.py -q` passed with 11 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 45 tests and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.

Closeout evidence:

- Phase 12 child issues #80, #81, #82, and #83 are closed.
- Phase 12 PR #84 merged to `main` with merge commit `9f09c1d`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest/docs, and release-artifact
  jobs.
- Post-merge `Docs Pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  artifact verification, artifact upload, and GitHub Pages deployment.
- Live docs verification confirmed `reference/api.html` includes `fable_pyculator.workflows` and
  `guides/notebook-control-surface.html` includes the Phase 12 helper example.

## Phase 13: One-Command 2021 FreshForge Rebuild Workflow

GitHub parent issue: #76.

Active branch: `feature/p13-one-command-2021-freshforge-rebuild`.

Status: complete.

Goal: add a script-style one-command path for planning and optionally running the 2021 generated-model
rebuild through FreshForge.

- [x] P13.1 Define one-command rebuild boundary. Child issue: #91.
  - Status: complete.
  - [x] Keep the command focused on the 2021 public FABLE-C workbook path contract.
  - [x] Default to plan-only behavior.
  - [x] Require an explicit run switch before invoking FreshForge execution.
  - [x] Keep source workbooks and generated artifacts under ignored `tmp/` paths.
- [x] P13.2 Add 2021 FreshForge rebuild script. Child issue: #93.
  - Status: complete.
  - [x] Add `scripts/build_fable_2021_model.py`.
  - [x] Build the 2021 notebook spec from the configured workbook path.
  - [x] Derive output refs using Phase 12 helper APIs.
  - [x] Write output refs, validation scenario, and Modelwright FreshForge workflow JSON.
  - [x] Print a concise artifact summary for plan-only use.
  - [x] Invoke FreshForge only when explicitly requested.
- [x] P13.3 Document one-command rebuild workflow. Child issue: #92.
  - Status: complete.
  - [x] Add Sphinx documentation for plan-only and explicit-run usage.
  - [x] Link the guide from relevant FreshForge/generated-model docs.
  - [x] Update README with the plan-first command.
  - [x] Confirm docs build warning-free.
- [x] P13.4 Add tests and verification evidence. Child issue: #94.
  - Status: complete.
  - [x] Test script help, missing-workbook failure behavior, and plan-mode summary output.
  - [x] Test package-level rebuild artifact preparation against a synthetic workbook/spec.
  - [x] Run full Phase 13 verification.
  - [x] Record verification evidence in roadmap, changelog, and issue comments.

Acceptance boundary:

- May claim FABLE Pyculator has a one-command 2021 rebuild preparation path that writes output refs,
  cached-workbook validation scenario JSON, and a Modelwright FreshForge workflow under ignored
  local artifacts.
- May claim users can opt into FreshForge execution with `--run` when FreshForge and Modelwright are
  installed in the active environment.
- Must not claim the script changes the 2021 validation standard, supports arbitrary workbook
  versions, or replaces the tracked compressed validated 2021 generated-model artifact.

Implementation evidence:

- Added `FableFreshForgeRebuildPlan` and `prepare_2021_freshforge_rebuild`.
- Added `scripts/build_fable_2021_model.py` with plan-only default behavior, `--json`, output-ref
  filter options, and explicit `--run` FreshForge execution.
- Added `docs/guides/2021-freshforge-rebuild-command.rst` and linked it from the Sphinx index,
  generated-model artifact guide, and README.
- Optimized cached-workbook validation-scenario preparation away from `openpyxl` read-only random
  access after a real 2021 smoke test exposed slow selected-output lookup.

Verification evidence:

- `.venv/bin/python scripts/build_fable_2021_model.py --json` passed against the local 2021 public
  workbook artifact, producing 16,478 `OUTPUT-*` refs and 16,478 comparable cached outputs under
  ignored `tmp/generated-models/fable-2021/`.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 55 tests and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.

Closeout evidence:

- Phase 13 PR #95 merged to `main` with commit `7dd6371`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest, docs build, and release
  artifact jobs.
- Post-merge `Docs Pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  verification, artifact upload, and GitHub Pages deployment.

## Phase 14: Version-General FABLE Build Workflows And Output-Ref Strategy Comparison

GitHub parent issue: #77.

Active branch: `feature/p14-version-general-fable-build-workflows`.

Status: active.

Goal: generalize FreshForge build helpers across FABLE workbook versions and support named output-ref
strategies such as headline-only, one-table, all `OUTPUT-*` columns, and selected flavour tags.

- [ ] P14.1 Define version-general build path contract. Child issue: #99.
- [x] P14.1 Define version-general build path contract. Child issue: #99.
  - Status: complete locally.
  - [x] Add a generic path builder for FABLE workbook versions.
  - [x] Preserve the 2021 compatibility wrapper.
  - [x] Keep generated artifacts under ignored `tmp/` paths.
  - [x] Record version/path assumptions in docs and issue evidence.
- [x] P14.2 Add named output-ref strategies. Child issue: #101.
  - Status: complete locally.
  - [x] Add `output-columns`, `headline-only`, `table`, `flavour-tags`, and `all-columns`.
  - [x] Preserve lower-level `derive_output_refs` behavior.
  - [x] Reject unknown strategies clearly.
  - [x] Add focused unit tests.
- [x] P14.3 Generalize rebuild preparation and script interface. Child issue: #100.
  - Status: complete locally.
  - [x] Add generic `prepare_freshforge_rebuild`.
  - [x] Preserve `prepare_2021_freshforge_rebuild` compatibility.
  - [x] Add `scripts/build_fable_model.py`.
  - [x] Keep `scripts/build_fable_2021_model.py` as a 2021 shortcut.
- [x] P14.4 Update docs, examples, and tests. Child issue: #102.
  - Status: complete locally.
  - [x] Update Sphinx docs with version-general paths and strategy examples.
  - [x] Update README.
  - [x] Add/update script and workflow tests.
  - [x] Keep claims narrow around workflow preparation and boundary comparison.
- [ ] P14.5 Verify, merge, deploy docs, and close phase. Child issue: #98.
  - Status: local verification complete; PR/merge/docs deployment pending.
  - [x] Run full local verification.
  - [x] Run real local smoke tests for 2021 strategy variants.
  - [ ] Open and merge PR after CI passes.
  - [ ] Confirm post-merge Test and Docs Pages workflows pass.

Local implementation evidence:

- Added `fable_freshforge_build_paths`, `prepare_freshforge_rebuild`, and
  `derive_output_refs_for_strategy` as version-general workflow helpers.
- Kept `freshforge_2021_build_paths`, `prepare_2021_freshforge_rebuild`, and
  `scripts/build_fable_2021_model.py` as compatibility shortcuts.
- Added `scripts/build_fable_model.py` with plan-first defaults, `--workbook-version`,
  `--output-ref-strategy`, `--table-name`, `--column-flavour-tag`, `--all-columns`, `--json`,
  and explicit `--run` execution.
- Updated README and Sphinx docs for version-general path conventions, named output-ref strategies,
  and 2021 examples.

Local verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
- Real 2021 plan-mode smoke tests passed for default `output-columns`, `headline-only`, and
  `ghg_resultsghg` table-only strategies with benign OpenPyXL warnings suppressed.

Acceptance boundary:

- May claim FABLE Pyculator can prepare version-aware FreshForge/Modelwright rebuild artifacts by
  workbook-version convention.
- May claim output-ref boundaries can be derived through named strategies for comparison and
  workflow preparation.
- Must not claim new generated-model equivalence, new country-calculator support, or scenario-bundle
  automation in this phase.

## Phase 15: Scenario-Bundle Automation And Rendered Result Artifacts

GitHub parent issue: #78.

Status: planned backlog.

Goal: define and pilot scenario-bundle automation for FABLE notebook workflows, including reusable
result table and figure artifact writers.

## Phase 16: Validation Evidence Packaging And Opt-In Benchmark Workflow

GitHub parent issue: #79.

Status: planned backlog.

Goal: package compact validation evidence for FABLE generated-model runs and add an opt-in benchmark
workflow when source workbooks are available locally.
