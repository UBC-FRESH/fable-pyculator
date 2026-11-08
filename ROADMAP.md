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
- Phase 14 is closed: version-general FABLE build workflow helpers and scripts are tracked, PR #103
  merged, and post-merge Test and Docs Pages workflows passed.
- Phase 15 is closed: scenario-bundle automation and rendered result artifacts are tracked, PR #109
  merged, and post-merge Test and Docs Pages workflows passed.
- Phase 16 is closed: validation evidence packaging and the opt-in benchmark evidence workflow are
  tracked, PR #115 merged, and post-merge Test and Docs Pages workflows passed.
- Phase 17 is closed: `v0.1.0a2` is published to PyPI and GitHub as the FABLE workflow automation
  alpha, PR #121 merged, and post-merge Test and Docs Pages workflows passed.
- Phase 18 is closed: output-ref strategy comparison workflows are tracked, PR #130 merged, and
  post-merge Test and Docs Pages workflows passed.
- Phase 19 is closed: FreshForge-backed scenario-bundle orchestration is tracked, PR #136 merged,
  and post-merge Test and Docs Pages workflows passed.
- Phase 20 is closed: opt-in benchmark evidence orchestration is tracked, PR #142 merged, and
  post-merge Test and Docs Pages workflows passed.
- Phase 21 is closed: `v0.1.0a3` is published to PyPI and GitHub as the benchmark workflow
  automation alpha, PR #148 merged, and post-merge Test and Docs Pages workflows passed.
- Phase 22 is closed: FreshForge matrix output-ref strategy runs are tracked, PR #155 merged, and
  post-merge Test and Docs Pages workflows passed.
- Phase 23 is closed: FreshForge matrix scenario-bundle runs are tracked, PR #162 merged, and
  post-merge Test and Docs Pages workflows passed.
- Phase 24 is closed: `v0.1.0a4` is published to PyPI and GitHub as the matrix workflow automation
  alpha, PR #168 merged, and post-merge Test and Docs Pages workflows passed.
- Phase 25 is closed: FABLE benchmark matrix evidence cookbook/workflow is tracked, PR #179
  merged, and post-merge Test and Docs Pages workflows passed.
- Phase 26 is closed: editable scenario-definition patches are tracked, PR #185 merged, and
  post-merge Test and Docs Pages workflows passed after rerunning a transient GitHub Pages deploy
  failure.
- Phase 27 is closed: alpha-tester notebook reliability, 2021 smoke hardening, skipped-table
  diagnostics, and notebook-failure issue hygiene are tracked, PR #201 merged, and post-merge Test
  and Docs Pages workflows passed.
- Phase 28 is closed: PR #214 was squash-merged to `main` as `a6758db`, post-merge Test and Docs
  Pages workflows passed, and parent issue #203 plus P28.9 child issue #212 are closed.
  The portal, issue-filing assistant workflow, and corrected 2021 authoritative-archive evidence
  are on `main`.
- Phase 29 is closed: PR #221 was squash-merged as `a6534d9`; a fresh Modelwright `0.1.0a9`
  regeneration from the repaired 2024 workbook reproduces the tracked archive exactly, and
  post-merge Test/Docs Pages workflows passed. Parent #215 and P29.5 #220 are closed.
- Phase 30 is closed: PR #227 was squash-merged as `ee344dd`; approved-artifact checksums, the
  `0.1.0a5` release candidate, authenticated proxy-prefix staging, and the public-host handoff are
  complete, and post-merge Test/Docs Pages workflows passed. Parent #222 and P30.4 #226 are closed.
- Released `fable-pyculator 0.1.0a5` with OIDC trusted publishing: TestPyPI rehearsal workflow
  `42348922051` passed, tag `v0.1.0a5` triggered PyPI workflow `42349225029`, and a clean PyPI
  install of the wheel and web extra imported `0.1.0a5`. The GitHub prerelease is
  https://github.com/UBC-FRESH/fable-pyculator/releases/tag/v0.1.0a5 with the wheel and sdist attached.
- Phase 31 is closed: service-token-aware verification tooling and the Cloudflare Access upgrade
  runbook merged via PR #232 (`bd7cd0c`), with post-merge Test/Docs Pages passing. The user confirmed
  that `fable-pyculator.01101.dev` serves the local `8768` process, which reports `0.1.0a5` with all
  three models prepared; parent #228 and P31.3 #231 are closed.
- Phase 32 is closed: the end-to-end surrogate/GPU-GA pipeline works, but the 33-sample surrogate
  extrapolates badly and is not suitable for optimization decisions. PR #237 merged as `cefc895`;
  the negative result and the next-step conditions are recorded. Parent #233 and P32.3 #236 are
  closed.
- Phase 33 is closed: the 10-control screen, 201 exact samples, 5-member ensemble, and exact replay
  all completed. Food scale improved to 0.8% error, but GHG local ranking remained wrong (−0.5 rank
  correlation) and the exact best candidate was ranked last. PR #243 merged as `9af5880`; the
  negative result and the consistency-rule draft are recorded. Parent #238 and P33.4 #242 are closed.
- Phase 34 is closed: the exact objective slice is validated but only 1.35× faster than the full
  model, so output-ref slicing is not enough for a useful optimizer. PR #248 merged as `d30488a`;
  the negative speed result is recorded. Parent #244 and P34.3 #247 are closed.
- Prepared a compact expert-review package for the FABLE scenario consistency rules, including a
  fillable CSV worksheet and concrete example scenarios; awaiting Hisham/FABLE expert decisions before
  implementing the rule engine or choosing the next optimizer representation.
- Phase 35 is closed: the status-aware rule engine, dataset audit, and 10-control domain enumeration
  are complete. Proposed rules warn in exploratory mode (725,760 valid, 535,680 warning-only); if
  draft-enforced, 466,560 remain valid (64.3%). PR #253 merged as `ca1fd84`; parent #249 and P35.3
  #252 are closed. Rules remain provisional pending expert review.
- Phase 36 is closed: rule-aware sampling and dataset filtering are integrated; 134 of 201 samples
  survive draft-enforced filtering. The filtered ensemble improved GHG rank correlation to +0.50 but
  worsened absolute GHG error to 46.5%, so the surrogate remains unusable. PR #257 merged as
  `d7d446d`; parent #254 and children #255-#256 are closed.
- Phase 37 is closed: the exact fallback over `land_scen`, `diet_scen`, `fixtrade_scen`, and
  `livedens_scen` ran 108 valid combinations with zero errors in 926.5 s. The exact weighted-goal
  point is NoDefor2030 / FatDiet / fixtrade Yes / NoGrowth at 3,288.73 kcal and 121.23 MtCO2e;
  fixing trade (`fixtrade Yes`) cuts GHG by 50.0% for a 0.36% food loss. PR #261 merged as
  `bc3f0f7`; parent #258 and children #259-#260 are closed.
- Phase 38 is closed: exact one-at-a-time variants around the Phase 37 point found livestock
  productivity as the strongest local GHG lever (`live_scen=HighGrowth`: −9.45% GHG, +0.05% food).
  The exact three-way candidate (`live_scen=HighGrowth`, `crop_scen=HighGrowth`,
  `affor_scen=BonnChallenge+`) reaches 3,301.11 kcal and 108.95 MtCO2e, dominating the Phase 37
  point. PR #265 merged as `9acc215`; parent #262 and children #263-#264 are closed.
- Phase 39 is closed: exact one-coordinate neighborhood verification around the Phase 38 candidate
  found no strict dominator; 30 exact evaluations, 2 rule-rejected, 0 errors, 321.6 s, 11 exact ties.
  The candidate is a local Pareto point. PR #268 merged as `44b9ab5`; parent #266 and child #267 are
  closed. Docs build passed; the GitHub Pages deploy job timed out in `finished_file_sync`.
- Phase 40 is closed: eight targeted exact land/diet/trade interactions plus a combined exact
  frontier (169 points, 160 unique selections, 15 unique Pareto objectives). Balanced and food-first
  (GHG ≤ 110) pick the Phase 38 candidate at 3,301.11 kcal / 108.95 MtCO2e; GHG-first at food ≥ 3,000
  picks 3,290.23 kcal / 108.84 MtCO2e. PR #272 merged as `5b88e8d`; parent #269 and children
  #270-#271 are closed. Post-merge Test and Docs Pages passed.
- Phase 41 is closed: the portal serves a tracked exact frontier artifact (160 points, 15 unique
  Pareto objectives) and has an Optimization page with a Three.js solution cloud,
  X/Y/Z/colour/size mapping, quality-floor and exact-front filters, pinning, comparison, and
  Workbench prefill. PR #276 merged as `1beceee`; parent #273 and children #274-#275 are closed.
  Post-merge Test and Docs Pages passed.
- Phase 42 is closed: the Optimization page now has hover values, selected-point highlighting,
  actual axis ranges, categorical legends, and a hide-provisional-warning filter (91 of 160 points
  remain). PR #279 merged as `a661259`; parent #277 and child #278 are closed. Post-merge Test and
  Docs Pages passed.
- Phase 43 is closed: the Optimization view encodes axes, colour, size, floor, filters, and selected
  point in the URL; supports copy-link; and exports the currently filtered exact points as CSV.
  PR #282 merged as `49e3bed`; parent #280 and child #281 are closed. Post-merge Test and Docs Pages
  passed.
- Phase 44 is closed: the Optimization page now has a synchronized parallel-coordinates view over
  land, diet, trade-fix, livestock, crop, afforestation, food, GHG, and goal. It renders the same
  filtered exact points and clicking a line selects the 3D point. PR #285 merged as `64e1a01`;
  parent #283 and child #284 are closed. Post-merge Test and Docs Pages passed.
- Phase 45 is implemented on `feature/p45-reference-delta`: an exact point can be set as a reference,
  compared with the selected point through objective and selection deltas, and marked in both the 3D
  and parallel views. The reference is shareable in the URL. Parent #286 and child #287 are mapped;
  PR #288 and closeout remain.
- Added a tracked `examples/fable_2024/` generated-model artifact for the 2024 FABLE Calculator
  (Canada) workbook (Modelwright `0.1.0a9` runtime-hardening line), with provenance and validation
  evidence in the example README.
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

Active branch: merged via PR #103.

Status: complete.

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
- [x] P14.5 Verify, merge, deploy docs, and close phase. Child issue: #98.
  - Status: complete.
  - [x] Run full local verification.
  - [x] Run real local smoke tests for 2021 strategy variants.
  - [x] Open and merge PR after CI passes.
  - [x] Confirm post-merge Test and Docs Pages workflows pass.

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
- PR #103 merged to `main` at merge commit `e5a7576`.
- Post-merge `Test` workflow run #28535828270 passed.
- Post-merge `Docs Pages` workflow run #28535828354 passed and deployed.

Acceptance boundary:

- May claim FABLE Pyculator can prepare version-aware FreshForge/Modelwright rebuild artifacts by
  workbook-version convention.
- May claim output-ref boundaries can be derived through named strategies for comparison and
  workflow preparation.
- Must not claim new generated-model equivalence, new country-calculator support, or scenario-bundle
  automation in this phase.

## Phase 15: Scenario-Bundle Automation And Rendered Result Artifacts

GitHub parent issue: #78.

Active branch: merged via PR #109.

Status: complete.

Goal: define and pilot scenario-bundle automation for FABLE notebook workflows, including reusable
result table and figure artifact writers.

- [x] P15.1 Define scenario-bundle schema and artifact path contract. Child issue: #104.
  - Status: complete locally.
  - [x] Define JSON/YAML bundle schema v1.
  - [x] Require path-safe `bundle_id` and `scenario_id`.
  - [x] Keep execution scoped to selection-control overrides.
  - [x] Define ignored artifact paths under `tmp/scenario-runs/fable-{version}/{bundle_id}/`.
- [x] P15.2 Add scenario-bundle runner and rendered artifact writers. Child issue: #106.
  - Status: complete locally.
  - [x] Add public dataclasses/helpers in `fable_pyculator.scenarios`.
  - [x] Validate selections against `FableCalculatorSpec`.
  - [x] Run each scenario through existing notebook-loop helpers.
  - [x] Write normalized bundle, manifest, CSV tables/frames, and optional PNG figures.
- [x] P15.3 Add script interface and public-safe examples. Child issue: #105.
  - Status: complete locally.
  - [x] Add `scripts/run_fable_scenario_bundle.py`.
  - [x] Add dry-run JSON summary and explicit path/render overrides.
  - [x] Add public-safe JSON and YAML example bundles.
- [x] P15.4 Update docs and tests. Child issue: #107.
  - Status: complete locally.
  - [x] Add a Sphinx scenario-bundle guide.
  - [x] Link README, notebook-control docs, docs index, and API reference.
  - [x] Add focused unit/script tests.
- [x] P15.5 Verify, merge, deploy docs, and close phase. Child issue: #108.
  - Status: complete.
  - [x] Run full local verification.
  - [x] Open and merge PR after CI passes.
  - [x] Confirm post-merge Test and Docs Pages workflows pass.

Acceptance boundary:

- May claim FABLE Pyculator can run named scenario bundles against an already available matching
  generated model and write rendered result artifacts.
- Must keep bundle execution limited to existing selection-control overrides.
- Must not claim scenario-definition table editing, FreshForge run matrices, or new generated-model
  equivalence evidence.

Local implementation evidence:

- Added `fable_pyculator.scenarios` with JSON/YAML bundle loading, validation, bundle execution, and
  result artifact writing.
- Added `scripts/run_fable_scenario_bundle.py` with dry-run, JSON output, path overrides, and render
  overrides.
- Added public-safe JSON and YAML 2021 SSP demo bundles.
- Added a Sphinx scenario-bundle guide and linked it from README, notebook-control docs, docs index,
  and API reference.

Local verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
- Real 2021 scenario-bundle dry-run smoke test passed for
  `examples/scenario-bundles/fable_2021_ssp_demo.yaml`.
- PR #109 merged to `main` at merge commit `5e69427`.
- Post-merge `Test` workflow run #28537043841 passed.
- Post-merge `Docs Pages` workflow run #28537043793 passed and deployed.

## Phase 16: Validation Evidence Packaging And Opt-In Benchmark Workflow

GitHub parent issue: #79.

Active branch: `feature/p16-validation-evidence-packaging`.

Status: complete.

Goal: package compact validation evidence for FABLE generated-model runs and add an opt-in benchmark
workflow when source workbooks are available locally.

- [x] P16.1 Define compact validation-evidence schema. Child issue: #112.
  - Status: complete.
  - [x] Define sanitized summary records.
  - [x] Record artifact presence, stage statuses, diagnostics counts, and comparison status.
  - [x] Claim `pass` only with explicit comparable/match/mismatch counts.
- [x] P16.2 Add evidence extraction and writers. Child issue: #110.
  - Status: complete.
  - [x] Add `fable_pyculator.validation`.
  - [x] Extract compact evidence from existing local artifacts.
  - [x] Write stable JSON and Markdown summaries.
  - [x] Support missing-artifact skipped/incomplete behavior.
- [x] P16.3 Add script interface and opt-in workflow. Child issue: #111.
  - Status: complete.
  - [x] Add `scripts/package_fable_validation_evidence.py`.
  - [x] Add manual `benchmark-evidence.yml`.
  - [x] Upload only sanitized evidence summaries.
- [x] P16.4 Update docs and tests. Child issue: #113.
  - Status: complete.
  - [x] Add Sphinx validation-evidence packaging guide.
  - [x] Update README, validation-scope, generated-model-artifacts, and API docs.
  - [x] Add focused unit/script/workflow tests.
- [x] P16.5 Verify, merge, deploy docs, and close phase. Child issue: #114.
  - Status: complete.
  - [x] Run full local verification.
  - [x] Run local evidence packaging smoke test if artifacts are restored.
  - [x] Open and merge PR after CI passes.
  - [x] Confirm post-merge Test and Docs Pages workflows pass.

Acceptance boundary:

- May claim FABLE Pyculator can package compact validation evidence from restored local artifacts.
- Must report incomplete evidence unless explicit comparable-output, match, and mismatch counts are
  available.
- Must not download workbooks, run full FreshForge generation, upload raw reports, or claim new
  equivalence evidence by default.

Local implementation evidence:

- Added `fable_pyculator.validation` with compact evidence path, summary, extraction, and writer
  helpers.
- Added `scripts/package_fable_validation_evidence.py` for JSON/human evidence packaging from
  restored local artifacts.
- Added manual `.github/workflows/benchmark-evidence.yml`, which uploads only sanitized evidence
  summaries under `tmp/validation-evidence/**`.
- Added the Sphinx validation-evidence packaging guide and linked it from README, validation-scope,
  generated-model artifact, docs index, and API reference pages.
- Added focused unit, script, and workflow tests for pass/fail/incomplete/skipped evidence,
  sanitized output writing, CLI behavior, and manual workflow artifact boundaries.

Local verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 81 passed and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
- `.venv/bin/python scripts/package_fable_validation_evidence.py --json` passed against restored
  local 2021 artifacts and correctly reported incomplete equivalence because explicit
  comparable/match/mismatch counts were unavailable.
- PR #115 merged to `main` at merge commit `675c0ae`.
- Post-merge `Test` workflow run #28539084681 passed.
- Post-merge `Docs Pages` workflow run #28539084645 passed and deployed.

## Phase 17: v0.1.0a2 FABLE Workflow Automation Alpha Release

GitHub parent issue: #116.

Release branch: `feature/p17-v0.1.0a2-release`.

Status: complete.

Goal: publish `fable-pyculator==0.1.0a2` as the FABLE workflow automation alpha in the coordinated
FreshForge -> Modelwright -> FABLE Pyculator release train.

- [x] P17.1 Bump version and dependency metadata. Child issue: #120.
  - Status: complete.
  - [x] Bump package version and import version to `0.1.0a2`.
  - [x] Bump FABLE Pyculator FreshForge provider metadata to `0.1.0a2`.
  - [x] Raise the Modelwright dependency floor to `modelwright[notebook]>=0.1.0a7`.
  - [x] Update version assertions and release artifact checks.
- [x] P17.2 Update release docs and alpha boundary. Child issue: #118.
  - Status: complete.
  - [x] Update the release deployment guide for `v0.1.0a2`.
  - [x] Update README alpha-line language and automation scope.
  - [x] Update FreshForge installation guidance to use `v0.1.0a2`.
  - [x] Record local verification and release evidence after checks pass.
- [x] P17.3 Verify release candidate and smoke tests. Child issue: #119.
  - Status: complete.
  - [x] Run full local verification.
  - [x] Open and merge the release PR after CI passes.
  - [x] Confirm post-merge Test and Docs Pages workflows pass.
- [x] P17.4 Publish PyPI/GitHub release and close phase. Child issue: #117.
  - Status: complete.
  - [x] Push annotated `v0.1.0a2` tag.
  - [x] Confirm PyPI publication.
  - [x] Verify clean install from PyPI.
  - [x] Create GitHub prerelease.
  - [x] Close child issues and parent issue after evidence is recorded.

Acceptance boundary:

- May claim FABLE Pyculator publishes the current FABLE-C notebook wrapper, validated 2021 compressed
  generated-model artifact, FreshForge provider/workflow helpers, version-general build workflow
  scripts, scenario-bundle automation, and compact validation-evidence packaging as an alpha.
- Must keep generated-model equivalence claims limited to recorded 2020/2021 public FABLE-C
  validation evidence.
- Must not claim stable public API compatibility, production workflow orchestration, arbitrary
  country-calculator support, or full scenario-definition editing.

Local implementation evidence:

- Bumped package metadata, import version, and FABLE Pyculator FreshForge provider metadata to
  `0.1.0a2`.
- Raised the dependency floor to `modelwright[notebook]>=0.1.0a7`.
- Updated README, release deployment docs, FreshForge provider install guidance, tests, release
  artifact checks, and changelog language for the FABLE workflow automation alpha.

Local verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 81 passed and 9 workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed, including clean wheel install of
  `fable-pyculator 0.1.0a2` with `modelwright 0.1.0a7`.
- `git diff --check` passed.
- `.venv/bin/python scripts/package_fable_validation_evidence.py --json` passed and reported
  conservative incomplete equivalence from restored local artifacts.
- Import/API smoke test confirmed `fable_pyculator 0.1.0a2`, `modelwright 0.1.0a7`,
  version-specific validation-evidence paths, and version-specific FreshForge build paths.
- PR #121 merged to `main` at merge commit `8148b4d`.
- Post-merge `Test` workflow run #28540822913 passed.
- Post-merge `Docs Pages` workflow run #28540823006 passed and deployed.
- Tag `v0.1.0a2` was pushed from merge commit `8148b4d`.
- Tag-triggered `Release` workflow run #28540880479 passed and published wheel and sdist artifacts
  to PyPI.
- PyPI JSON verification confirmed `fable-pyculator 0.1.0a2` lists
  `fable_pyculator-0.1.0a2-py3-none-any.whl` and `fable_pyculator-0.1.0a2.tar.gz`.
- Clean PyPI install of `fable-pyculator[notebook]==0.1.0a2` imported `fable_pyculator 0.1.0a2`
  with `modelwright 0.1.0a7`.
- GitHub prerelease published at `https://github.com/UBC-FRESH/fable-pyculator/releases/tag/v0.1.0a2`.

## Phase 18: Output-Ref Strategy Comparison Workflows

GitHub parent issue: #122.

Active branch: `feature/p18-output-ref-strategy-comparison-workflows`.

Status: complete.

Goal: compare FABLE output-ref strategies as explicit generated-model workflow boundaries before
choosing validation or modelling targets.

- [x] P18.1 Define strategy comparison records and artifact paths. Child issue: #127.
- [x] P18.2 Add strategy comparison preparation and optional run-summary ingestion. Child issue: #126.
- [x] P18.3 Add script interface and public-safe examples. Child issue: #128.
- [x] P18.4 Update docs and tests. Child issue: #125.
- [x] P18.5 Verify, PR, deploy docs, and close phase. Child issue: #129.
  - [x] Open PR #130 from `feature/p18-output-ref-strategy-comparison-workflows` to `main`.
  - [x] Merge PR #130 to `main`.
  - [x] Confirm post-merge Test workflow run #28557443902 passed.
  - [x] Confirm post-merge Docs Pages workflow run #28557443878 passed and deployed.
  - [x] Smoke-check the published Sphinx page for the output-ref strategy comparison guide.

Dependencies:

- FreshForge Phase 7 for run namespaces and workflow-run summaries.
- Modelwright Phase 35 for generated-model stage summaries and provider diagnostics.

Acceptance boundary:

- May compare `output-columns`, `headline-only`, `table`, `flavour-tags`, and `all-columns`
  strategies with compact counts, artifacts, diagnostics, and validation-boundary summaries.
- Must not claim new generated-model equivalence from strategy comparison alone.

Implementation evidence:

- Added `fable_pyculator.strategy_comparison` with public strategy case, path, entry, and result
  records plus default FABLE output-ref strategy cases.
- Added `compare_output_ref_strategies(...)` and `write_output_ref_strategy_comparison(...)` to
  derive per-strategy output refs, cached comparable-output counts, validation scenarios, optional
  FreshForge workflow JSON, and optional existing evidence summaries.
- Added `scripts/compare_fable_output_ref_strategies.py` as a plan-first strategy comparison command.
- Added Sphinx guide and API reference coverage, plus links from README, generated-model artifact,
  FreshForge provider, rebuild-command, and validation-evidence packaging docs.

Local verification:

- `.venv/bin/python -m pytest tests/test_strategy_comparison.py tests/test_scripts.py -q` passed with
  22 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 90 tests and 9 skipped workbook tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for the restored 2019, 2020,
  and 2021 public workbooks.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported
  `fable_pyculator 0.1.0a2` against published `modelwright 0.1.0a7`.
- `git diff --check` passed.
- Real local 2021 smoke comparison passed for `output-columns` and `headline-only` with
  `--include-workflows --include-existing-evidence`, reporting 16,478 output-column refs and 99
  headline refs while correctly marking absent per-strategy generated-model evidence as skipped.
- Merged Phase 18 through PR #130 and confirmed post-merge Test workflow run #28557443902 plus
  Docs Pages workflow run #28557443878 passed, including GitHub Pages deployment.
- Smoke-checked the live Sphinx page at
  `https://ubc-fresh.github.io/fable-pyculator/guides/output-ref-strategy-comparison.html`.

## Phase 19: FreshForge-Backed Scenario-Bundle Orchestration

GitHub parent issue: #123.

Active branch: `main` after PR #136.

Status: complete.

Goal: upgrade existing FABLE Pyculator scenario bundles so repeated bundle runs can be orchestrated
and summarized cleanly through FreshForge.

- [x] P19.1 Define FreshForge scenario-bundle workflow contract. Child issue: #131.
- [x] P19.2 Add executable FABLE provider nodes for scenario-bundle runs. Child issue: #132.
- [x] P19.3 Add script interface, examples, and summary artifacts. Child issue: #133.
- [x] P19.4 Update docs and tests. Child issue: #134.
- [x] P19.5 Verify, PR, deploy docs, and close phase. Child issue: #135.
  - [x] Open PR #136 from `feature/p19-freshforge-scenario-bundle-orchestration` to `main`.
  - [x] Merge PR #136 to `main`.
  - [x] Confirm post-merge Test workflow run #28558440319 passed.
  - [x] Confirm post-merge Docs Pages workflow run #28558440328 passed and deployed.

Dependencies:

- FreshForge Phase 7 for run namespaces and summaries.
- Existing Phase 15 scenario-bundle APIs and generated-model artifact conventions.

Acceptance boundary:

- May orchestrate and summarize repeated selection-control scenario-bundle runs.
- Must keep FABLE scenario semantics in FABLE Pyculator.
- Must preserve direct scenario-bundle execution as the default script/API path.
- Must not add scenario-definition table editing, generated-model rebuild orchestration, remote
  execution, caching, retries, production scheduling, or new generated-model equivalence claims.

Implementation evidence:

- Added `fable_pyculator.scenario_workflows` with FreshForge path and plan records, workflow
  preparation, workflow execution, and compact run-summary writing for scenario bundles.
- Extended the FABLE Pyculator FreshForge provider with executable `scenario_bundle_prepare`,
  `scenario_run`, and `scenario_bundle_manifest` nodes while keeping earlier Phase 9 node types
  plan-only.
- Extended `scripts/run_fable_scenario_bundle.py` with explicit `--freshforge-plan`,
  `--freshforge-run`, `--run-namespace`, `--workflow-path`, and `--run-summary-path` options while
  preserving direct dry-run/run behavior.
- Added a public-safe FreshForge scenario-bundle workflow example for the 2021 SSP demo bundle and
  Sphinx guide/API coverage.

Local verification:

- `.venv/bin/python -m pytest tests/test_scenario_workflows.py tests/test_scripts.py -q` passed with
  22 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 96 tests and 9 skipped workbook tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for the restored 2019, 2020,
  and 2021 public workbooks.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported
  `fable_pyculator 0.1.0a2` against published `modelwright 0.1.0a7`.
- `git diff --check` passed.
- `.venv/bin/freshforge validate examples/freshforge/fable_2021_scenario_bundle_workflow.yaml --json`
  passed.
- `.venv/bin/freshforge plan examples/freshforge/fable_2021_scenario_bundle_workflow.yaml --json`
  passed.
- Real local 2021 smoke plan passed with
  `.venv/bin/python scripts/run_fable_scenario_bundle.py --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml --freshforge-plan --json`,
  reporting a 4-node FreshForge workflow.
- Merged Phase 19 through PR #136 and confirmed post-merge Test workflow run #28558440319 plus
  Docs Pages workflow run #28558440328 passed, including GitHub Pages deployment.

## Phase 20: Opt-In Benchmark Workflow Upgrade

GitHub parent issue: #124.

Active branch: `feature/p20-opt-in-benchmark-workflow-upgrade`.

Status: complete.

Goal: upgrade the existing manual benchmark evidence workflow from extraction-only summaries toward
repeatable benchmark execution when restored public workbook artifacts are available.

- [x] P20.1 Define opt-in benchmark workflow contract. Child issue: #137.
- [x] P20.2 Add benchmark orchestration script and evidence backend selection. Child issue: #138.
- [x] P20.3 Upgrade manual GitHub Actions workflow. Child issue: #139.
- [x] P20.4 Update docs and tests. Child issue: #140.
- [x] P20.5 Verify, PR, deploy docs, and close phase. Child issue: #141.
  - [x] Open PR #142 from `feature/p20-opt-in-benchmark-workflow-upgrade` to `main`.
  - [x] Merge PR #142 to `main`.
  - [x] Confirm post-merge Test workflow run #28558959744 passed.
  - [x] Confirm post-merge Docs Pages workflow run #28558959735 passed and deployed.

Dependencies:

- Modelwright Phase 36 for compact generated-model validation evidence extraction.
- FreshForge Phase 7 run summaries and, optionally, FreshForge Phase 8 matrices.
- FABLE Pyculator Phase 18/19 if benchmark workflows compare strategies or scenario bundles.

Acceptance boundary:

- May run manual/opt-in benchmark workflows and upload sanitized summary evidence.
- Must not run by default on every PR.
- Must not upload source workbooks, raw generated models, raw validation reports, or unsupported
  equivalence claims.

Implementation evidence:

- Added `fable_pyculator.benchmarks` with FABLE benchmark path and summary records, conservative
  benchmark evidence packaging, Modelwright-generic evidence backend selection, FABLE-local fallback,
  optional FreshForge plan/run summary handling, and compact Markdown/JSON writers.
- Added `scripts/run_fable_benchmark_evidence.py` with `evidence-only`, `freshforge-plan`, and
  explicit `freshforge-run` modes plus workbook version, output-ref strategy, scenario-bundle,
  namespace, required-artifact, and JSON flags.
- Upgraded `.github/workflows/benchmark-evidence.yml` to remain `workflow_dispatch` only while
  exposing benchmark mode, output-ref strategy, scenario-bundle, required-artifact, and namespace
  inputs; uploads remain restricted to compact summaries under `tmp/validation-evidence/**` and
  `tmp/benchmark-evidence-summary.json`.
- Added Sphinx documentation for the opt-in benchmark evidence workflow and linked it from README,
  validation evidence packaging, validation scope, generated-model artifact, scenario-bundle
  FreshForge orchestration, and API reference docs.

Local verification:

- `.venv/bin/python -m pytest tests/test_benchmarks.py tests/test_benchmark_evidence_workflow.py tests/test_scripts.py -q`
  passed with 31 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 108 tests and 9 skipped workbook tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for the restored 2019, 2020,
  and 2021 public workbooks.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported
  `fable_pyculator 0.1.0a2` against published `modelwright 0.1.0a7`.
- `git diff --check` passed.
- Real local smoke passed with `.venv/bin/python scripts/run_fable_benchmark_evidence.py --json`,
  selecting the `modelwright` evidence backend and reporting incomplete equivalence when explicit
  comparison counts were unavailable.
- Merged Phase 20 through PR #142 and confirmed post-merge Test workflow run #28558959744 plus
  Docs Pages workflow run #28558959735 passed, including GitHub Pages deployment.

## Phase 21: v0.1.0a3 Benchmark Workflow Automation Alpha Release

GitHub parent issue: #143.

Release branch: `feature/p21-v0.1.0a3-release`.

Status: complete after PR #148, tag `v0.1.0a3`, PyPI publication, GitHub prerelease, and clean
PyPI install smoke tests.

Goal: publish `fable-pyculator==0.1.0a3` to GitHub and PyPI as the benchmark workflow automation
alpha release after FreshForge `v0.1.0a3` and Modelwright `v0.1.0a8`.

- [x] P21.1 Bump FABLE Pyculator version and dependency metadata. Child issue: #144.
  - [x] Bump package and import metadata to `0.1.0a3`.
  - [x] Bump FABLE Pyculator FreshForge provider metadata to `0.1.0a3`.
  - [x] Raise the Modelwright dependency floor to `modelwright[notebook]>=0.1.0a8`.
  - [x] Update version assertions and release artifact checks.
- [x] P21.2 Update release docs and FreshForge/Modelwright guidance. Child issue: #145.
  - [x] Update the release deployment guide for the `v0.1.0a3` alpha boundary.
  - [x] Update README alpha-line language for the benchmark workflow automation release.
  - [x] Update FreshForge installation guidance to use `v0.1.0a3`.
- [x] P21.3 Verify FABLE Pyculator release artifacts and smoke tests. Child issue: #146.
  - [x] Run local quality, tests, docs, theme, checksum, and release artifact checks.
  - [x] Smoke-test benchmark evidence packaging entry points.
- [x] P21.4 Tag, publish PyPI/GitHub release, and close phase. Child issue: #147.
  - [x] Open and merge release PR after CI passes.
  - [x] Create annotated tag `v0.1.0a3`.
  - [x] Publish to PyPI through trusted publishing.
  - [x] Create GitHub prerelease and verify clean PyPI install.

Acceptance boundary:

- May claim output-ref strategy comparison workflows, FreshForge-backed scenario-bundle
  orchestration, opt-in benchmark evidence packaging, and dependency alignment with Modelwright
  `0.1.0a8` plus FreshForge `v0.1.0a3`.
- Must not claim stable public API compatibility, production readiness, arbitrary FABLE
  country-calculator support, scenario-definition table editing, or new generated-model equivalence
  beyond recorded public 2020/2021 evidence.

Local verification:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 108 tests and 9 skipped workbook tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for the restored 2019, 2020,
  and 2021 public workbooks.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported
  `fable_pyculator 0.1.0a3` against published `modelwright 0.1.0a8`.
- `.venv/bin/python scripts/run_fable_benchmark_evidence.py --json` passed, selecting the
  `modelwright` evidence backend and reporting incomplete equivalence when explicit comparison
  counts were unavailable.
- `git diff --check` passed.

Release evidence:

- PR #148 merged to `main`.
- Post-merge Test workflow run #28559940344 passed.
- Post-merge Docs Pages workflow run #28559940366 passed and deployed.
- Annotated tag `v0.1.0a3` was pushed.
- Release workflow run #28559980122 built artifacts and published `fable-pyculator==0.1.0a3` to
  PyPI.
- PyPI listed both `fable_pyculator-0.1.0a3-py3-none-any.whl` and
  `fable_pyculator-0.1.0a3.tar.gz`.
- GitHub prerelease `v0.1.0a3` was created with the workflow-built wheel and sdist.
- Clean PyPI install of `fable-pyculator[notebook]==0.1.0a3` imported
  `fable_pyculator 0.1.0a3` with `modelwright 0.1.0a8` and smoke-tested the benchmark, strategy
  comparison, and FreshForge scenario-workflow API exports.

## Phase 22: FreshForge Matrix Output-Ref Strategy Runs

GitHub parent issue: #149.

Active branch: `feature/p22-freshforge-strategy-matrices`.

Status: complete after PR #155 and post-merge Test and Docs Pages workflows.

Goal: connect output-ref strategy comparison with FreshForge Phase 8 matrices so users can prepare
one explicit matrix across strategy cases and optionally plan or run it through FreshForge.

- [x] P22.1 Define strategy matrix contract and artifacts. Child issue: #150.
- [x] P22.2 Add matrix document writer and optional planner/runner integration. Child issue: #151.
- [x] P22.3 Update strategy comparison CLI, docs, and examples. Child issue: #152.
- [x] P22.4 Add tests and verification. Child issue: #153.
- [x] P22.5 PR, docs deploy, and close phase. Child issue: #154.

Acceptance boundary:

- May claim FABLE Pyculator can prepare FreshForge matrix documents for output-ref strategy
  comparisons.
- May claim users can explicitly plan or run those matrices when FreshForge Phase 8 is installed.
- Must keep FreshForge optional and avoid normal import-time FreshForge imports.
- Must not claim new generated-model equivalence from matrix creation, planning, or execution unless
  explicit validation evidence exists.
- Must not add scenario-bundle matrices in this phase.

Implementation evidence:

- Added FreshForge-free strategy matrix records, matrix YAML/template writers, and lazy FreshForge
  plan/run adapters to `fable_pyculator.strategy_comparison`.
- Extended `scripts/compare_fable_output_ref_strategies.py` with `--include-matrix`,
  `--matrix-plan`, explicit `--matrix-run`, `--matrix-path`, `--workdir`, and `--fail-fast`.
- Updated the output-ref strategy comparison guide and README with compare-only, matrix-writing,
  matrix-planning, and explicit matrix-run examples.

Local verification:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 115 tests and 9 skipped workbook tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for restored public workbook
  artifacts.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
- Real local 2021 smoke passed with
  `.venv/bin/python scripts/compare_fable_output_ref_strategies.py --strategy headline-only --include-matrix --json`,
  writing the strategy matrix and workflow template under ignored `tmp/strategy-comparisons/`.
- Real local 2021 FreshForge matrix planning smoke passed with
  `.venv/bin/python scripts/compare_fable_output_ref_strategies.py --strategy headline-only --matrix-plan --json`.

Closeout evidence:

- PR #155 merged to `main` with squash commit `6ef33e6`.
- Post-merge Test workflow passed.
- Post-merge Docs Pages workflow passed and deployed.

## Phase 23: FreshForge Matrix Scenario-Bundle Runs

GitHub parent issue: #156.

Phase branch: `feature/p23-freshforge-scenario-bundle-matrices`.

Status: complete.

Goal: add FreshForge matrix orchestration for existing FABLE scenario bundles so each scenario can
run as a namespaced matrix case with compact planning/run summaries.

- [x] P23.1 Define scenario-bundle matrix contract and artifacts. Child issue: #157.
- [x] P23.2 Add matrix document writer and optional planner/runner integration. Child issue: #158.
- [x] P23.3 Update scenario-bundle CLI, docs, and examples. Child issue: #159.
- [x] P23.4 Add tests and verification. Child issue: #160.
- [x] P23.5 PR, docs deploy, and close phase. Child issue: #161.

Acceptance boundary:

- May claim FABLE Pyculator can prepare FreshForge matrix documents for scenario-bundle cases.
- May claim users can explicitly plan or run scenario-bundle matrices when FreshForge Phase 8 is
  installed.
- Must keep FreshForge optional and avoid normal import-time FreshForge imports.
- Must preserve direct scenario-bundle execution and existing FreshForge workflow mode.
- Must not add scenario-definition table editing, generated-model rebuilding, remote execution,
  caching, retries, or new generated-model equivalence claims.

Implementation evidence:

- Added scenario-bundle matrix path and plan records, matrix/template builders, and lazy matrix
  plan/run/summary helpers to `fable_pyculator.scenario_workflows`.
- Extended `scripts/run_fable_scenario_bundle.py` with `--freshforge-matrix-plan`,
  `--freshforge-matrix-run`, `--matrix-path`, `--matrix-template-path`, `--matrix-summary-path`, and
  `--fail-fast`.
- Added public-safe scenario-bundle matrix examples under `examples/freshforge/`.
- Updated README and the FreshForge scenario-bundle orchestration guide.

Local verification:

- `.venv/bin/python -m pytest tests/test_scenario_workflows.py tests/test_scripts.py -q` passed with
  35 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 121 tests and 9 skipped workbook tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for restored public workbook
  artifacts.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
- Real local 2021 matrix-plan smoke passed with
  `.venv/bin/python scripts/run_fable_scenario_bundle.py --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml --freshforge-matrix-plan --json`.
- Public-safe example matrix planning passed with
  `.venv/bin/freshforge matrix plan examples/freshforge/fable_2021_scenario_bundle_matrix.yaml --json`.

Closeout evidence:

- PR #162 merged to `main` with squash commit `9ea77e6`.
- Post-merge Test workflow passed: run `28562394428`.
- Post-merge Docs Pages workflow passed and deployed: run `28562394444`.

## Phase 24: v0.1.0a4 Matrix Workflow Automation Alpha Release

GitHub parent issue: #163.

Release branch: `feature/p24-v0.1.0a4-release`.

Status: complete after PR #168, tag `v0.1.0a4`, PyPI publication, GitHub prerelease, and clean
PyPI install smoke testing.

Goal: publish `fable-pyculator==0.1.0a4` to GitHub and PyPI as the matrix workflow automation
alpha after FreshForge `v0.1.0a4`.

- [x] P24.1 Bump version and dependency guidance. Child issue: #164.
  - [x] Bump package and import metadata to `0.1.0a4`.
  - [x] Bump FABLE Pyculator FreshForge provider metadata to `0.1.0a4`.
  - [x] Update FreshForge installation guidance to `v0.1.0a4`.
  - [x] Update version assertions and release artifact checks.
- [x] P24.2 Update release docs, README, roadmap, and changelog. Child issue: #165.
  - [x] Update README alpha language for strategy and scenario-bundle matrices.
  - [x] Update the release deployment guide for the `v0.1.0a4` alpha boundary.
  - [x] Record Phase 24 in the roadmap and changelog.
- [x] P24.3 Verify artifacts, tag, publish PyPI/GitHub release. Child issue: #166.
  - [x] Run local quality, tests, docs, workbook checksum, and release artifact checks.
  - [x] Create annotated tag `v0.1.0a4`.
  - [x] Verify the release workflow publishes `fable-pyculator==0.1.0a4` to PyPI.
  - [x] Create GitHub prerelease with checked artifacts attached.
  - [x] Run a clean PyPI install smoke test.
- [x] P24.4 PR, docs deploy, and close phase. Child issue: #167.
  - [x] Open and merge release PR after CI passes.
  - [x] Confirm post-merge Test and Docs Pages workflows.
  - [x] Update roadmap and changelog closeout evidence.

Acceptance boundary:

- May claim FABLE Pyculator has a PyPI/GitHub alpha release for output-ref strategy matrices and
  scenario-bundle matrices.
- May point users to FreshForge `v0.1.0a4` for optional matrix planning/running.
- Must keep FreshForge optional rather than a required runtime dependency.
- Must not claim stable API, production readiness, arbitrary country-calculator support,
  scenario-definition table editing, remote execution, or new generated-model equivalence.

Local verification:

- `.venv/bin/python -m pip install -e .[dev,notebook,docs]` refreshed editable metadata for
  `fable-pyculator 0.1.0a4` with published `modelwright 0.1.0a8`.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 121 tests and 9 skipped workbook tests.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed for restored public workbook
  artifacts.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported
  `fable_pyculator 0.1.0a4` against published `modelwright 0.1.0a8`.
- `git diff --check` passed.

Closeout evidence:

- Phase 24 PR #168 merged to `main` at `238165b`.
- Post-merge Test workflow passed: run `28562906226`.
- Post-merge Docs Pages workflow passed and deployed: run `28562906254`.
- Annotated tag `v0.1.0a4` was pushed.
- Release workflow run #28562950207 built artifacts and published `fable-pyculator==0.1.0a4` to
  PyPI.
- Downloaded workflow-built artifacts passed `twine check`.
- GitHub prerelease `v0.1.0a4` was created with the workflow-built wheel and sdist.
- Clean PyPI install of `fable-pyculator[notebook]==0.1.0a4` imported
  `fable_pyculator 0.1.0a4` with `modelwright 0.1.0a8` and smoke-tested the matrix helper exports.

## Phase 25: FABLE Benchmark Matrix Evidence Cookbook

GitHub parent issue: #171.

Status: complete.

Goal: consume Modelwright Phase 38 matrix evidence aggregation to document and package a FABLE-facing
2021 benchmark matrix workflow.

Planned scope:

- [x] P25.1 Define FABLE benchmark matrix evidence path contract. Child issue: #174.
- [x] P25.2 Add matrix evidence packaging helpers. Child issue: #175.
- [x] P25.3 Add script/workflow cookbook commands. Child issue: #176.
- [x] P25.4 Update docs, examples, and tests. Child issue: #177.
- [x] P25.5 Verify, PR, deploy docs, and close phase. Child issue: #178.

Scope:

- Document compare-only, matrix-plan, and explicit matrix-run workflows for 2021 FABLE output-ref
  strategy cases.
- Package FABLE-facing summaries from generic Modelwright matrix evidence.
- Keep generated-model equivalence claims tied only to explicit comparable/match/mismatch evidence.

Out of scope:

- Editable scenario-definition parameters.
- New generated-model equivalence claims without evidence.
- FreshForge core feature work.
- Remote execution, caching, retries, or production scheduling.

Implementation evidence:

- Added FABLE-facing benchmark matrix evidence records and helpers that delegate generic matrix
  aggregation to Modelwright Phase 38.
- Added `scripts/package_fable_matrix_evidence.py` for compact matrix evidence packaging.
- Added the 2021 benchmark matrix evidence cookbook and linked it from adjacent docs.
- Local verification passed with Ruff, full pytest (`130` passed, `9` skipped workbook tests),
  warning-clean Sphinx docs, Read the Docs theme verification, public workbook checksums, release
  artifact checks, and `git diff --check`.
- PR #179 merged to `main`; post-merge Test workflow #28627076860 passed and post-merge Docs Pages
  workflow #28627076848 passed after rerunning a transient GitHub Pages deploy failure.

## Phase 26: Editable Scenario-Definition Parameter Surface

GitHub parent issue: #172.

Status: complete.

Goal: expose FABLE scenario-definition table editing and validation as a first-class FABLE Pyculator
modelling surface after benchmark matrix evidence workflows are documented.

Tasks:

- [x] P26.1 Define editable scenario-definition surface records. Child issue: #180.
- [x] P26.2 Add patch validation, loading, writing, and input mapping. Child issue: #181.
- [x] P26.3 Add notebook-loop execution integration. Child issue: #182.
- [x] P26.4 Update docs, examples, and tests. Child issue: #183.
- [x] P26.5 Verify, PR, deploy docs, and close phase. Child issue: #184.

Scope:

- Add APIs for editable scenario-definition parameter surfaces.
- Validate edited parameter tables before generated-model execution.
- Integrate later with scenario bundles and FreshForge matrices.
- Keep workbook-version assumptions explicit.

Out of scope:

- Arbitrary country-calculator support.
- Generic Modelwright workbook conversion logic.
- Remote execution, caching, retries, or production scheduling.
- New generated-model equivalence claims.

Implementation evidence:

- Added `fable_pyculator.scenario_definitions` with editable-cell records, patch records, patch
  loading/writing, validation, and generated-model input mapping.
- Integrated optional `scenario_definition_patch` inputs into `run_scenario`, `run_notebook_loop`,
  `run_2020_notebook_loop`, and `run_2021_notebook_loop`.
- Added `scripts/validate_fable_scenario_definition_patch.py` and a public-safe YAML patch schema
  example under `examples/scenario-definition-patches/`.
- Added Sphinx documentation for editable scenario-definition patches and linked it from the
  notebook control, scenario bundle, README, index, and API docs.
- Added unit, script, and workbook-backed tests for editable `DIRECT` cells, read-only role/formula
  rejection, patch selectors, duplicate/ambiguous targets, generated-model input mapping, notebook
  loop integration, and validation-script output.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with `140` tests and `11` workbook-backed skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed with a clean wheel install smoke test.
- `git diff --check` passed.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -q tests/test_fable_workbook_scenario_definition_tables.py`
  passed with `5` workbook-backed tests.
- `.venv/bin/python scripts/validate_fable_scenario_definition_patch.py --patch examples/scenario-definition-patches/fable_2021_diet_target_demo.yaml --workbook-version 2021 --json`
  passed against the restored 2021 workbook and produced one generated-model input override.

Closeout evidence:

- PR #185 merged to `main` with merge commit `5e08862`.
- Post-merge Test workflow #28629339255 passed.
- Post-merge Docs Pages workflow #28629339241 passed after rerunning a transient GitHub Pages deploy
  failure.

## Phase 27: Alpha-Tester Notebook Reliability And 2021 Smoke Hardening

GitHub parent issue: #194.

Branch: `feature/p27-alpha-tester-notebook-hardening`.

Status: complete.

Goal: harden the Abdulateef-facing 2021 notebook loop after recent output-table rendering fixes by
adding a repeatable smoke path, clearer skipped-table diagnostics, and better notebook failure
reporting.

Tasks:

- [x] P27.1 Define notebook smoke scope and alpha-tester failure contract. Child issue: #195.
- [x] P27.2 Add opt-in 2021 notebook smoke script/test. Child issue: #196.
- [x] P27.3 Improve notebook-loop rendering diagnostics. Child issue: #197.
- [x] P27.4 Harden GitHub issue/reporting workflow for notebook failures. Child issue: #198.
- [x] P27.5 Update docs, verification, PR, deploy docs, and close phase. Child issue: #199.

Scope:

- Keep the 2021 loop notebook as a concrete, unexecuted alpha-tester artifact.
- Add an opt-in restored-artifact smoke command for the 2021 notebook loop.
- Record default filtered output tables skipped because no requested flavour tags matched.
- Preserve explicit output-table request failures.
- Keep screenshots and display captures as UI symptom evidence, not validation evidence.

Out of scope:

- New modelling semantics.
- New generated-model equivalence claims.
- Source workbook mutation.
- FreshForge or Modelwright feature work unless a clear upstream bug is discovered.

Implementation evidence:

- Added `NotebookLoopResult.skipped_output_tables` so default filtered rendering records tables
  skipped because no requested output-column flavour tags matched.
- Added `scripts/smoke_2021_notebook_loop.py` for the restored-artifact 2021 loop smoke path.
- Added an opt-in restored-artifact pytest smoke test gated by
  `FABLE_PYCULATOR_RUN_2021_NOTEBOOK_SMOKE=1`.
- Updated `examples/notebooks/fable-pyculator-2021-loop.ipynb` to print rendered/skipped table
  counts and use `result.run.scenario_name`.
- Added a notebook-run failure GitHub issue template.
- Cleaned issue #190 body formatting after auditing recent Abdulateef notebook bug issues.
- Recorded workbook-load investigation findings in
  `planning/phase-27-alpha-tester-notebook-hardening.md`.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with `147` tests and `12` skips.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `sha256sum -c benchmarks/fable-calculator/checksums.sha256` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
- `.venv/bin/python scripts/smoke_2021_notebook_loop.py --json` passed against restored local
  2021 artifacts in about 213 seconds, rendering 10 output tables, skipping 4 non-matching default
  `OUTPUT-*` tables, and proving populated `trade_resultstrade` `PRODUCT`/`YEAR` context columns.

Closeout evidence:

- PR #201 merged to `main` with merge commit `37cf162`.
- Post-merge Test workflow #28631757605 passed.
- Post-merge Docs Pages workflow #28631757588 passed.

## Phase 28: Optional Multi-Page Web Portal

GitHub parent issue: #203.

Branch: `feature/p28-web-portal`.

Status: complete.

Pull request: #214 (merged as `a6758db`).

Goal: add a local multi-page portal over the artifacts and notebook APIs FABLE Pyculator already
uses, so analysts can prepare a matching workbook/model pair, run named scenarios, read and export
generated outputs, compare saved runs, inspect compact validation evidence, browse artifact
readiness, and optionally ask a local assistant.

Tasks:

- [x] P28.1 Define the portal service and artifact contract. Child issue: #204.
- [x] P28.2 Add artifact discovery, compressed-model materialization, and spec caching. Child issue: #205.
- [x] P28.3 Add preparation and scenario-run background jobs. Child issue: #206.
- [x] P28.4 Add saved-run persistence, table retrieval, and run comparison. Child issue: #207.
- [x] P28.5 Add the dependency-free multi-page SPA. Child issue: #208.
- [x] P28.6 Add compact validation-evidence and scenario-bundle browsing. Child issue: #209.
- [x] P28.7 Add the optional local assistant bridge and CLI entry point. Child issue: #210.
- [x] P28.8 Add tests, documentation, and roadmap/changelog evidence. Child issue: #211.
- [x] P28.10 Add GitHub issue-filing guidance, templates, and validation to the portal assistant. Child issue: #213.
- [x] P28.9 Open the PR, map issues, deploy docs, and close the phase. Child issue: #212.

Scope:

- Optional `fable-pyculator[web]` extra with FastAPI and uvicorn.
- FastAPI service plus a vanilla ES-module SPA with no Node build.
- Loopback-only default and an explicit `--allow-remote` guard.
- Preparation, execution, saved runs, comparison, validation, artifacts, and assistant pages.
- Real generated-model values only; no browser-side FABLE calculation.
- Ignored `runtime/portal/` cache for prepared specs and saved runs.

Out of scope:

- Authentication, accounts, multi-tenant storage, or remote execution scheduling.
- Source workbook mutation from the browser.
- New generated-model equivalence claims.
- Loading multi-gigabyte raw validation stage artifacts for display.

Implementation evidence:

- Added `src/fable_pyculator/web/` with artifact discovery/materialization, spec JSON caching,
  background jobs, scenario execution, saved-run comparison, validation lookup, FastAPI app factory,
  and the optional assistant bridge. Saved runs carry a provenance block with the portal version,
  workbook and generated-model paths/sizes, preparation timestamp, and workbook id.
- Added the global **+ Ask** pill and fixed overlay assistant with markdown rendering for user and
  assistant messages, safe links/code/tables, session continuation, tool-action chips, run context,
  Enter-to-send, Shift+Enter newline, and keyboard shortcuts.
- Added persistent assistant chats under `runtime/portal/chats/`, with a saved-chat list in the
  overlay, last-chat restoration, and OpenCode session continuation across service restarts.
- Added a generated grounding sheet at `runtime/portal/assistant/cheat-sheet.md` with served model
  instances, artifact paths, prepared spec counts, saved runs, API surface, known version
  differences, a digest compiled from all listed FABLE/Modelwright docs, and an AST source API
  index. New chats must read it and open full cited files for exact details. It is served at
  `GET /api/assistant/cheatsheet.md`.
- Added deterministic assistant grounding evaluations plus opt-in live source-citation cases, and a
  Playwright Chromium smoke for overlay, Enter/Shift+Enter, markdown, and reload-persistence checks.
- Fixed the FABLE 2024 broken `ResultsLand[TOTAL]` headline by falling back to a labelled component
  sum when the workbook TOTAL formula contains `#REF!`, and bumped the spec-cache version so stale
  specs rebuild automatically. Added `scripts/repair_fable_2024_land_total.py` and repaired the local
  workbook formula and cached totals from `calc_land_cor[TotallandFin]`; the portal also applies the
  same component repair to the stale generated model's displayed LAND TOTAL column with an explicit
  warning note.
- Curated the GHG headline from declared `OUTPUT-8` components instead of the `TotalCO2e` `CALC`
  cell, so 2020/2021/2024 results pages now have a numeric GHG series. The 2024 series explicitly
  notes that `LandSeqAffor` is excluded because it is not a declared `OUTPUT-8` cell in that
  artifact. Derived values are generated-model outputs; cached-total validation matched 2020 to
  ~1e-12 and exposed late-year component-model differences for 2021/2024.
- Added `scripts/repair_fable_2024_generated_model.py` and repaired the tracked 2024 generated-model
  expressions for `LAND!AA17:AA27`; old-vs-repaired execution across all 10,274 declared outputs
  changed only those 11 cells.
- Added an optional 2070 trend extension in the Workbench: native FABLE results stay 2000-2050;
  headline series and one-row-per-year tables are extrapolated from the 2035-2050 linear trend;
  multi-row-per-year tables are extended group-by-group on text identity columns when possible, and
  unsupported tables stay native with an explicit note. Every extended run records the method and
  non-native warning.
- Finished assistant chat management: rename, search, pin, archive, delete, Markdown export, and
  automatic titles from the first exchange; added PATCH/export chat endpoints.
- Re-ran the release artifact check; it passed and the wheel contains chats, cheat-sheet, grounding
  evals, and all portal static assets.
- Added deployment support: optional HTTP Basic auth, a `scripts/run_portal.sh` environment
  wrapper, systemd/nginx examples, proxy root-path support, and the web-deployment guide.
- Added the UBC-FRESH phase/task issue templates and `docs/guides/github-issue-workflow.rst`; the
  portal assistant now asks for issue type, scope, scale, impact, and verification details, drafts
  the canonical body, runs `scripts/check_issue_body.py`, confirms with the user, posts with
  `gh issue create --body-file`, links child tasks to the parent, and reads the issue back.
- Added run-scoped data-quality notes to Results for the 2070 extension, 2024 land component
  fallback, missing 2024 water series, GHG-vs-cached divergence, and unextended tables; notes are
  persisted in `run.json` as `quality_warnings`.
- Wired `scripts/evaluate_assistant_grounding.py` into the Test workflow; live agent and Chromium
  checks remain opt-in.
- Added `src/fable_pyculator/cli.py` and the `fable-pyculator web` entry point.
- Added a multi-page static SPA under `src/fable_pyculator/web/static/` with Overview, Workbench,
  Results, Compare, Validation, Artifacts, and Assistant pages.
- Added the `web` optional dependency extra and package-data declaration for static assets.
- Added `tests/web/test_portal.py` covering spec round-tripping, artifact naming and materialization,
  preparation, scenario execution, table retrieval, comparison, validation lookup, the
  assistant-disabled guard, and the bind guard.
- Added `docs/guides/web-portal.rst`, API reference entries, README guidance, and
  `planning/phase-28-web-portal.md`.
- Added version-tolerant default headline curation: unsupported tables are skipped so the 2024
  Canada workbook prepares with FOOD, LAND, and GHG series despite lacking `TotalResultsWF`;
  `strict=True` preserves fail-fast behavior and `build_notebook_spec` exposes `strict_headlines`.
- Added `runtime/` to `.gitignore`.

Verification evidence:

- `.venv/bin/python -m ruff check src/fable_pyculator/web src/fable_pyculator/cli.py tests/web`
  passed.
- `.venv/bin/python -m ruff format --check src/fable_pyculator/web src/fable_pyculator/cli.py tests/web`
  passed after formatting.
- `.venv/bin/python -m pytest -q` passed with `198` tests and `15` skips.
- `FABLE_PYCULATOR_RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/web/test_browser_e2e.py`
  passed against real Chromium and a live assistant chat across a page reload.
- `scripts/evaluate_assistant_grounding.py` structural checks passed, and
  `scripts/evaluate_assistant_grounding.py --live` passed the five grounding cases against the real
  OpenCode CLI, including `github_issue_filing` in 17.3 s.
- PR #214 CI on `46a92a2`: quality, pytest, release-artifacts, and the Docs Pages build passed; the
  deploy job correctly skipped on the pull request.
- PR #214 was squash-merged as `a6758db`. Post-merge Test workflow `42308703202` and Docs Pages
  workflow `42308703198` both passed.
- `FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 .venv/bin/python -m pytest -q tests/test_fable_workbook_headline_series.py`
  passed with `2` workbook-backed tests for 2020 and 2024.
- Real restored-artifact 2021 preparation and scenario execution passed through the HTTP portal:
  16 controls, 14 output tables, 4 headline series, a background prepare job, an 85.7 s scenario run,
  a saved 968-row `trade_resultstrade` table, saved-run detail, and compact validation lookup.
  A second app instance reloaded the prepared spec from cache in 0.54 s.
- Re-materialized the authoritative 2021 archive and reran the live portal smoke: `430.13 → 107.63
  MtCO2e`, with no GHG data-quality warning.
- Real restored-artifact 2024 preparation and scenario execution passed: 47.7 s prepare, 108.5 s run,
  24 controls, 17 output tables, 3 headline series, and saved tables.
- After the land-total fallback, a real 2024 run prepared in 1.0 s from cache and ran in 105.7 s,
  reporting numeric total land area (`896,559.0`) with the component-sum label matching the
  workbook's `calc_land_cor[TotallandFin]` total. The displayed `land_resultsland` TOTAL column also
  shows the repaired value with an explicit display-repair note instead of `#REF!`.
- After repairing the tracked generated-model expressions, a fresh 2024 run prepared in 41.4 s and
  ran in 108.6 s; the `land_resultsland` TOTAL column came directly from the model with no display
  repair note, and all 11 LAND TOTAL values were `896,559.0` (float tolerance).
- Old-vs-repaired generated-model execution comparison across all 10,274 declared outputs found
  exactly 11 differences, all `LAND!AA17:AA27` (`#REF!` → `896,559.0`).
- Live 2024 GHG smoke after the derivation: `59.99 → 95.61 MtCO2e` with the workbook default
  `gwp_scen = SAR`; cached workbook GHG values use `AR6`, so they are not directly comparable.
- Investigated a live 2021 `LandSeq`/GHG discrepancy at 2050. The apparent generated-model defect
  was a stale 85 MB local working model that omitted six `SCENARIOS definition` row-50 formulas
  (`EQ50`-`EV50`). The tracked 122 MB archive already contains those formulas and, when
  re-materialized, matches the cached 2050 outputs (`GHG!AI28 -302.1950203334845`,
  `LAND!V27 25000.0`, `LAND!X27 81407.07618113697`); no tracked-artifact repair was needed. The
  live 2021 smoke is now `430.13 → 107.63 MtCO2e` with no GHG data-quality warning.
- Live 2024 horizon-2070 run: headline series extended to 2070 (`food 1,611.3`, `GHG 110.14`,
  `land 896,559.0`); `land_resultsland` rendered 15 rows; grouped `food_results_diets` extended
  from 187 to 255 rows; grouped `trade_resultstrade` extended from 990 to 1,350 rows.
- Real restored-artifact 2020 preparation and scenario execution passed: 137.0 s prepare,
  167.2 s run, 16 controls, 14 output tables, 4 headline series, and saved tables.
- The live local assistant returned markdown in 11.9 s with an OpenCode session id, and a second turn
  continued the same session in 7.2 s.
- The grounded new-chat assistant read `notebook.py` and answered the exact
  `build_notebook_spec` signature in 25.5 s; after a service restart the saved chat listed,
  reloaded, and continued the same OpenCode session in 10.4 s.
- `.venv/bin/fable-pyculator web --root . --port 8767` served `/api/health`, `/`, and
  `/static/app.js` successfully after an editable install with the `web` extra.
- `.venv/bin/sphinx-build -b html docs _build/html -W -q` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed, and the built wheel contains the portal package and
  `web/static/*` assets.

Closeout evidence:

- PR #214 squash-merged to `main` as `a6758db`.
- Post-merge Test workflow `42308703202` and Docs Pages workflow `42308703198` passed.
- Parent issue #203 and child issue #212 are closed; completed child issues #204-#211 and #213 were
  closed with closeout comments.

## Phase 29: 2024 Generated-Model Regeneration

GitHub parent issue: #215.

Branch: `feature/p29-2024-regeneration`.

Status: complete.

Pull request: #221 (merged as `a6534d9`).

Goal: regenerate the 2024 FABLE Calculator (Canada) Python model from the repaired workbook with
the current Modelwright checkout, eliminate the post-generation LAND TOTAL repair if possible, and
validate the result against the workbook and the tracked artifact before replacing anything.

Tasks:

- [x] P29.1 Baseline the repaired workbook, tracked artifact, and validation contract. Child issue: #216.
- [x] P29.2 Run a fresh 2024 regeneration from the repaired workbook. Child issue: #217.
- [x] P29.3 Resolve Modelwright translation gaps or record a concrete blocker. Child issue: #218.
- [x] P29.4 Validate the regenerated model and decide whether to replace the tracked archive. Child issue: #219.
- [x] P29.5 Update provenance, documentation, tests, and close Phase 29. Child issue: #220.

Scope:

- Baseline the original, pristine, and repaired workbooks and the tracked 2024 archive.
- Run a fresh Modelwright extraction, dependency analysis, translation, inference, and generation.
- Resolve or explicitly block output-closure translation failures.
- Validate all declared outputs, with special attention to LAND AA17:AA27, GHG, FOOD, and TRADE.
- Update the tracked artifact only when old-vs-new and workbook comparisons support it.

Out of scope:

- Changing FABLE Calculator semantics.
- Hardcoding generated values or silently accepting unexplained output regressions.
- Releasing Modelwright without a separate approval.
- Unrelated portal feature work.

Architecture notes:

- Modelwright remains the generic workbook-to-Python conversion engine.
- FABLE Pyculator owns the 2024-specific validation contract and tracked artifact decision.
- The repaired workbook is the source of truth for the LAND TOTAL correction.
- Any tracked-artifact replacement needs provenance, checksums, and portal smoke evidence.

Acceptance boundary:

- A fresh regeneration from the repaired workbook is attempted with a reproducible command.
- Every output-closure failure is fixed, proven out of scope, or recorded as a concrete blocker.
- The tracked 2024 artifact is replaced only if the regenerated model is validated as at least as correct.
- LAND AA17:AA27 are native generated formulas and reproduce the workbook total if regeneration succeeds.
- Docs, tests, checksums, and portal smoke evidence agree with the final artifact.

Implementation evidence:

- Added `scripts/regenerate_fable_2024_model.py`, which builds the workbook spec, derives the 10,274
  declared outputs, runs Modelwright extraction/dependency/translation/inference/generation, and
  compares the result with the tracked archive.
- Bumped the runtime dependency to `modelwright[notebook]>=0.1.0a9`; the failed repro logs used the
  stale `0.1.0a8` environment.
- A fresh conversion from the repaired workbook (checksum
  `519f68d70d6338ca7030ab470e00686f76e62fe008d3adaf0210613d19d365fc`) translated 410,299 of
  410,299 formulas, closed all 10,274 declared outputs with 0 failures, generated the model with 0
  diagnostics, and produced SHA-256
  `cc8ac21ab55293f648aa9f6b3b8782b1f2dbe1b7789fda43bb1d100c1d8221ee`.
- That checksum is byte-identical to the decompressed tracked archive. `LAND!AA17:AA27` are native
  generated formulas; no archive replacement or surgical patch is needed.
- Updated the 2024 example README, generated-model-artifact guide, README, changelog, and script
  help to document the reproduction command and the `0.1.0a9` floor.

Verification evidence:

- `python scripts/regenerate_fable_2024_model.py` passed with an exact tracked-archive match.
- `.venv/bin/python -m pytest -q` passed with `199` tests and `15` skips.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/sphinx-build -b html docs _build/html -W -q` and
  `scripts/verify_docs_theme.py _build/html` passed.
- Live 2024 portal smoke with the explicit prior selection set: `food 2,720.9 → 1,984.5`,
  `GHG 59.99 → 95.61 MtCO2e`, `land 896,559.0 → 896,559.0`; no unexplained output regression.
- `scripts/check_release_artifacts.sh` passed.
- PR #221 CI on `cdd4258` passed quality, pytest, release-artifacts, and Docs Pages build.
- PR #221 was squash-merged as `a6534d9`; post-merge Test workflow `42347244877` and Docs Pages
  workflow `42347245017` passed.

Closeout evidence:

- PR #221 squash-merged to `main` as `a6534d9`.
- Post-merge Test workflow `42347244877` and Docs Pages workflow `42347245017` passed.
- Parent issue #215 and child issue #220 are closed; P29.1-P29.4 are closed with closeout comments.

## Phase 30: Release and Deployment Hardening

GitHub parent issue: #222.

Branch: `feature/p30-release-deployment`.

Status: complete.

Pull request: #227 (merged as `ee344dd`).

Goal: harden the portal release and deployment path after the 2024 artifact provenance work:
verify working models against approved checksums, prepare a `0.1.0a5` release candidate, run
authenticated staging with a proxy prefix, and document the host handoff.

Tasks:

- [x] P30.1 Add approved-artifact checksum verification and stale-model handling. Child issue: #223.
- [x] P30.2 Prepare and verify the v0.1.0a5 release candidate. Child issue: #224.
- [x] P30.3 Run authenticated staging with proxy prefix and deployment smoke tests. Child issue: #225.
- [x] P30.4 Document host handoff, review evidence, open the PR, and close Phase 30. Child issue: #226.

Scope:

- Approved-artifact checksum verification and stale-model handling.
- Release candidate versioning, metadata, docs, and artifact checks.
- Authenticated staging through `scripts/run_portal.sh`.
- Deployment handoff inputs for the maintainer.
- Phase PR, CI, and closeout.

Out of scope:

- Provisioning a public host, DNS, TLS, or credentials without maintainer-supplied details.
- Creating a release tag or publishing to PyPI without separate approval.
- New portal features unrelated to deployment hardening.

Architecture notes:

- The tracked archive remains authoritative; working models must match its checksum or be explicitly re-materialized.
- Basic auth is a shared deployment credential; health remains public.
- Proxy-prefix support is exercised through `FABLE_PORTAL_ROOT_PATH`.
- Release publication remains a gated maintainer action.

Acceptance boundary:

- Stale working models are detected and cannot silently affect results.
- Version 0.1.0a5 builds and passes release checks without publication.
- Authenticated staging enforces auth while keeping health public and works under a proxy prefix.
- The public deployment handoff is explicit and complete.

Implementation evidence:

- Added tracked uncompressed checksum sidecars for the 2021 and 2024 archives, portal checksum
  state in artifact summaries, a model-verification pill and re-materialize action on the Artifacts
  page, and pre-preparation stale-model detection with automatic re-materialization from the
  approved archive.
- Bumped the package to `0.1.0a5`, updated provider/version assertions, release notes, README, and
  the release/deployment guide, and kept `modelwright>=0.1.0a9`.
- Verified the local authenticated staging path with `FABLE_PORTAL_ROOT_PATH=/fable`: health returned
  `200` without auth, API/static routes returned `401` without auth and `200` with auth, and the SPA
  and one proxied 2024 run completed.
- Added the public deployment handoff checklist covering hostname/DNS, TLS, proxy prefix,
  credentials, service/runtime paths, assistant ownership, monitoring, firewall, rollback, and the
  approving maintainer.

Verification evidence:

- `.venv/bin/python -m pytest -q` passed with `202` tests and `15` skips.
- `.venv/bin/python -m ruff check .` passed.
- Sphinx warning-as-error build and Read the Docs theme check passed.
- `scripts/check_release_artifacts.sh` passed and installed `fable-pyculator-0.1.0a5`.
- Artifact API reports `2021 verified`, `2024 verified`, `2020 unknown` (no tracked 2020 checksum).
- Authenticated staging proxy smoke: health `200`, unauth API `401`, auth API `200`, prefixed root
  and static `200`; 2024 run `food 2,720.9 → 1,984.5`, `GHG 59.99 → 95.61 MtCO2e`,
  `land 896,559.0`.
- PR #227 CI on `4a377f3` passed quality, pytest, release-artifacts, and Docs Pages build.
- PR #227 was squash-merged as `ee344dd`; post-merge Test workflow `42348441589` and Docs Pages
  workflow `42348441626` passed.

Closeout evidence:

- PR #227 squash-merged to `main` as `ee344dd`.
- Post-merge Test workflow `42348441589` and Docs Pages workflow `42348441626` passed.
- Parent issue #222 and child issue #226 are closed; P30.1-P30.3 are closed with closeout comments.

## Phase 31: Live Deployment Verification and Upgrade

GitHub parent issue: #228.

Branch: `feature/p31-live-deployment`.

Status: complete.

Pull request: #232 (merged as `bd7cd0c`).

Goal: verify and upgrade the existing public deployment at `fable-pyculator.01101.dev`, which is
protected by Cloudflare Access, and make the access and upgrade path reproducible.

Tasks:

- [x] P31.1 Add Cloudflare Access-aware deployment verification tooling. Child issue: #229.
- [x] P31.2 Document Cloudflare Access, health policy, and upgrade runbook. Child issue: #230.
- [x] P31.3 Verify and upgrade the live deployment to 0.1.0a5. Child issue: #231.

Scope:

- Add service-token-aware deployment verification tooling.
- Document Cloudflare Access, health monitoring, and the upgrade runbook.
- Record the live version, prepared models, and checksum state.
- Upgrade the host to `0.1.0a5` when access and host update details are supplied.
- Run an authenticated smoke test.

Out of scope:

- Storing Cloudflare tokens, passwords, or host credentials in tracked files.
- Changing DNS, TLS, or Cloudflare Access policy without maintainer approval.
- New portal features unrelated to deployment verification.

Architecture notes:

- Cloudflare Access currently protects every public path, including `/api/health`.
- The deployment checker reads optional service-token headers from environment variables.
- A health bypass is one monitoring option; a service token is the safer default.
- The published `0.1.0a5` artifact is the upgrade target.

Acceptance boundary:

- The deployment checker works with Access service tokens and reports version/checksum state.
- The docs explain the health-policy tradeoff and the upgrade sequence.
- The live deployment reports `0.1.0a5` and passes an authenticated smoke test.

Implementation evidence:

- Added `scripts/check_deployed_portal.py`, which checks `/api/health`, `/api/agent`, `/`, and
  `/api/artifacts`, supports Cloudflare Access service-token headers and optional portal Basic auth,
  and enforces `--expect-version`.
- Documented Cloudflare Access, the health-bypass tradeoff, service-token use, and the live upgrade
  runbook in `docs/guides/web-deployment.rst`; linked the checker from the README.
- The unauthenticated live check correctly detects the Cloudflare Access redirect at
  `https://fable-pyculator.01101.dev/api/health` and reports that a service token is required.

Verification evidence:

- `.venv/bin/python -m pytest -q` passed with `206` tests and `15` skips.
- `.venv/bin/python -m ruff check .` passed.
- Sphinx warning-as-error build and Read the Docs theme check passed.
- `scripts/check_deployed_portal.py --url https://fable-pyculator.01101.dev --json
  --allow-access-redirect` detected `access_required: true`.

Closeout evidence:

- P31.1 and P31.2 are complete and were merged in PR #232 (`bd7cd0c`); post-merge Test workflow
  `42350786820` and Docs Pages workflow `42350786800` passed.
- The user confirmed that `fable-pyculator.01101.dev` serves the local `8768` process. Local health
  reports `0.1.0a5` with all three models prepared; checksum states are 2021 verified, 2024 verified,
  and 2020 unknown (no tracked checksum). Parent #228 and P31.3 #231 are closed.

## Phase 32: FABLE Surrogate-Assisted GPU Optimization

GitHub parent issue: #233.

Branch: `feature/p32-fable-gpu-optimization`.

Status: complete.

Pull request: #237 (merged as `cefc895`).

Goal: test whether a GPU-accelerated surrogate-assisted genetic search can turn the FABLE Pyculator
into a fast, flexible weighted-goal optimization surface while preserving exact Pyculator verification
for the reported incumbents.

Tasks:

- [x] P32.1 Build the exact FABLE sample oracle and baseline decision space. Child issue: #234.
- [x] P32.2 Implement the GPU surrogate GA with weighted goals and exact top-K replay. Child issue: #235.
- [x] P32.3 Run the feasibility pilot, document limits, and close Phase 32. Child issue: #236.

Scope:

- Start with the 24 categorical scenario controls and fixed numeric scenario tables.
- Use the three current headline objectives: food, land, and GHG.
- Build an exact one-scenario oracle and a small baseline dataset.
- Train a Torch surrogate and run a GPU GA with weighted goals.
- Exact-replay top candidates and measure surrogate/exact agreement.

Out of scope:

- Claiming exact optimization over the entire FABLE state space.
- Continuous scenario-definition variables in the first spike.
- Production portal UI integration.
- More than a bounded feasibility sample.

Architecture notes:

- WS4 supplies the GPU population-search pattern; FABLE supplies the decision space and exact oracle.
- Fresh Solutions' adapter contract is the long-term integration point; this pilot uses a Torch vectorized search directly.
- The exact Pyculator remains the final authority for every reported incumbent.
- A small sample set is a plumbing test, not a surrogate-quality claim.

Acceptance boundary:

- The exact worker records reproducible objective values.
- The GPU GA runs and produces a weighted-goal ranked population.
- Top candidates are exact-replayed and compared.
- The pilot report states whether the approach is worth scaling.

Implementation evidence:

- Added `scripts/fable_optimization_oracle.py` for exact one-scenario evaluation and provenance.
- Added `scripts/fable_optimization_samples.py` for parallel exact sample collection.
- Added `scripts/fable_gpu_optimizer.py` for Torch surrogate training, CUDA population search,
  weighted-goal scalarization, and candidate export.
- Added `docs/guides/optimization-pilot.rst` and focused tests.

Pilot evidence:

- 33/33 exact samples completed with 16 workers; per-run time 179.6–233.8 s (mean 217.6 s);
  wall time about 392 s.
- GPU GA: 512 population, 300 generations, CUDA.
- Surrogate training rank correlation: 0.70; training/validation MSE near zero due to severe
  overfitting on 33 samples.
- Exact replay of the top five: exact food ~2,924 kcal and GHG ~86–91 MtCO2e, versus surrogate
  ~3,300–3,420 kcal and ~56–60 MtCO2e.
- Mean relative error: food 15.5%, GHG 35.0%; top-five rank correlation: food 0.10, GHG -0.10.
- The pipeline is a plumbing success but not a surrogate-quality success.

Verification evidence:

- `.venv/bin/python -m pytest -q` passed with `207` tests and `16` skips.
- `.venv/bin/python -m ruff check .` passed.
- Sphinx warning-as-error build and Read the Docs theme check passed.
- GPU pilot and exact top-five replay completed on CUDA.

Verification evidence:

- PR #237 CI on `362cad1` passed quality, pytest, release-artifacts, and Docs Pages build.
- PR #237 was squash-merged as `cefc895`; post-merge Test workflow `42353841087` and Docs Pages
  workflow `42353841014` passed.

Closeout evidence:

- Parent #233 and P32.3 #236 are closed with the negative-result pilot evidence.
- Do not scale this surrogate without a reduced decision space, more exact samples, and uncertainty
  handling.

## Phase 33: FABLE Optimization Scaling

GitHub parent issue: #238.

Branch: `feature/p33-optimization-scaling`.

Status: complete.

Pull request: #243 (merged as `9af5880`).

Goal: scale the surrogate-assisted optimization pilot from a plumbing test to a defensible
reduced-space experiment: screen control effects, freeze 8–12 variables, collect 200–400 exact
samples, add ensemble uncertainty, and exact-replay the best candidates.

Tasks:

- [x] P33.1 Screen control sensitivity and freeze the reduced decision space. Child issue: #239.
- [x] P33.2 Collect a larger exact sample set over the reduced controls. Child issue: #240.
- [x] P33.3 Add ensemble uncertainty and rerun the GPU surrogate. Child issue: #241.
- [x] P33.4 Exact replay, compare, document, and close Phase 33. Child issue: #242.

Scope:

- Exact one-at-a-time control screening.
- Reduced decision space with fixed baseline for excluded controls.
- Larger exact sample collection.
- Ensemble surrogate and uncertainty-aware GPU GA.
- Exact top-K replay and comparison.

Out of scope:

- Claiming exact optimization over the full FABLE state space.
- Continuous scenario-definition variables in this phase.
- Production UI integration.

Architecture notes:

- Exact Pyculator remains the oracle and final authority.
- The reduced space must be explicit and reproducible.
- Ensemble spread is an uncertainty signal, not a correctness proof.
- A negative result is acceptable if it is measured and documented.

Acceptance boundary:

- The reduced control set is frozen from exact one-at-a-time effects.
- At least 200 exact samples complete or the shortfall is documented.
- The ensemble GA reports uncertainty and exact top-K replay.
- The phase records whether to continue, change approach, or stop.

Implementation evidence:

- Added exact one-at-a-time screening and a reduced-control sample mode.
- Added `scripts/fable_optimization_screen.py` and a 10-control reduced space.
- Added 5-member ensemble uncertainty scoring to `scripts/fable_gpu_optimizer.py`.
- Added the draft scenario-consistency rule surface and extensible coefficient/switch architecture in
  `planning/fable-scenario-consistency-rules.md` and `.yaml`.

Pilot evidence:

- Screen: 25/25 exact runs, 10 controls selected.
- Reduced sample: 201/201 exact runs, 24 workers, ~23.8 min wall; mean exact runtime ~177 s.
- Ensemble: 5 members, 512 population, 400 generations, CUDA; training rank correlation 0.95.
- Exact top-five: food mean relative error 0.8%, GHG 23.6%; food rank correlation −0.60, GHG −0.50.
- The exact best GHG candidate was ranked last by the surrogate; random validation did not cover the
  high-food/high-GHG extrapolation region.

Verification evidence:

- Full regression suite and docs build to be rerun after the Phase 33 commits.
- Exact screen, sample, ensemble, and exact replay artifacts are present under
  `tmp/fable-optimization-p33/`.

Verification evidence:

- PR #243 CI on `04e2be3` passed quality, pytest, release-artifacts, and Docs Pages build.
- PR #243 was squash-merged as `9af5880`; post-merge Test workflow `42396463342` and Docs Pages
  workflow `42396463322` passed.

Closeout evidence:

- Parent #238 and P33.4 #242 are closed.
- Do not scale this surrogate without a reduced exact evaluator, physics-informed features plus OOD
  rejection, or a narrower policy question.

## Phase 34: Reduced Exact Objective Evaluator

GitHub parent issue: #244.

Branch: `feature/p34-reduced-exact-evaluator`.

Status: complete.

Pull request: #248 (merged as `d30488a`).

Goal: build and validate an exact evaluator that computes only the objective/headline slice, then
benchmark whether it is fast enough to replace or augment the surrogate in the optimization loop.

Tasks:

- [x] P34.1 Build a reduced exact evaluator for the objective cell set. Child issue: #245.
- [x] P34.2 Validate the reduced evaluator against the full model. Child issue: #246.
- [x] P34.3 Benchmark, document, and close Phase 34. Child issue: #247.

Scope:

- Extract objective/headline cell refs from the spec.
- Build a reduced generated-model copy with only those output refs.
- Compare reduced and full objective values on baseline and sampled scenarios.
- Benchmark exact speedup and document the boundary.

Out of scope:

- New surrogate training.
- Production UI integration.
- Changing FABLE formulas or workbook semantics.

Architecture notes:

- The reduced evaluator is still exact; only the output-ref tuple changes.
- The objective closure is the dependency set required by food, land, and GHG headlines.
- The full generated model remains the reference.

Acceptance boundary:

- Reduced and full objective values match.
- Runtime and exactness are recorded.
- The next optimization path is explicit.

Implementation evidence:

- Added `scripts/fable_reduced_exact_evaluator.py`, which rewrites only the generated model's
  `_output_refs` tuple to the selected headline cells.
- The 2024 objective slice contains 176 cell refs (food, land, GHG).
- Baseline and three sample comparisons were exact: zero difference in all objective values.

Benchmark evidence:

- full baseline: 167 s;
- reduced objective model: 123 s (1.35×);
- food-only: 127 s; GHG-only: 89 s; land-only: 72 s;
- running the three slices in parallel is bounded by the slowest slice and consumes three model
  processes.

Negative result: output-ref slicing does not materially reduce the shared FABLE dependency cost. The
next exact path requires compiled/vectorized formula execution or a much narrower dependency slice.

Verification evidence:

- `.venv/bin/python -m pytest -q` to be rerun after the Phase 34 commits.
- Sphinx warning-as-error build and theme check to be rerun.
- Reduced-vs-full comparison JSON under `tmp/fable-reduced-exact/`.

Verification evidence:

- PR #248 CI on `0568648` passed quality, pytest, release-artifacts, and Docs Pages build.
- PR #248 was squash-merged as `d30488a`; post-merge Test workflow `42399834408` and Docs Pages
  workflow `42399834335` passed.

Closeout evidence:

- Parent #244 and P34.3 #247 are closed.
- Output-ref slicing is exact but insufficient; next exact path requires compiled/vectorized formula
  execution or a much narrower dependency slice.

## Phase 35: Scenario Rule Engine and Valid-Domain Audit

GitHub parent issue: #249.

Branch: `feature/p35-scenario-rule-engine`.

Status: complete.

Pull request: #253 (merged as `ca1fd84`).

Goal: implement a status-aware scenario rule engine and quantify how the proposed consistency rules
affect the exact sample dataset and the 10-control reduced domain.

Tasks:

- [x] P35.1 Implement a status-aware scenario rule engine and tests. Child issue: #250.
- [x] P35.2 Audit the exact dataset and enumerate the reduced valid domain. Child issue: #251.
- [x] P35.3 Document findings, open the PR, and close Phase 35. Child issue: #252.

Scope:

- Typed rule loading and condition evaluation.
- Custom-table requirement checks.
- Approved, proposed, and rejected rule semantics.
- Audit of 201 exact samples.
- Enumeration of the 10-control reduced domain.
- Decision-ready report for FABLE experts.

Out of scope:

- Declaring proposed rules authoritative.
- New surrogate or optimizer representation.
- Production UI integration.

Architecture notes:

- Proposed rules warn in exploratory mode and do not silently block.
- Approved hard rules block; approved soft rules warn.
- Rejected rules are ignored.
- Table-population status comes from the prepared workbook spec.
- Counts are reproducible and versioned by rule/spec hashes.

Acceptance boundary:

- The rule engine behaves differently for approved, proposed, and rejected rules.
- The dataset audit and reduced-domain counts are reproducible.
- The review package reports the measured impact.

Implementation evidence:

- Added `src/fable_pyculator/scenario_rules.py`: typed rule loading, condition evaluation, per-key
  custom-table checks, approved/proposed/rejected semantics, and domain enumeration.
- Added `scripts/evaluate_scenario_rules.py` and focused tests.
- Updated the expert review package with measured counts.

Audit evidence:

- 201 exact samples: exploratory 201 valid / 0 invalid; draft-enforced 134 valid / 67 invalid.
- 10-control domain: 725,760 total; exploratory 725,760 valid / 535,680 warning-only;
  draft-enforced 466,560 valid (64.3%) / 259,200 invalid / 276,480 warning-only.
- Top domain triggers: trade-fix 226,800; narrative SSP 207,360; custom import 181,440; custom diet
  103,680; land-affor 80,640; live-density 60,480 (overlapping).

Verification evidence:

- `.venv/bin/python -m pytest -q` passed with `211` tests and `16` skips.
- `.venv/bin/python -m ruff check .` passed.
- Sphinx warning-as-error build and Read the Docs theme check passed.
- `scripts/evaluate_scenario_rules.py` produced `tmp/fable-rules-audit/exploratory.json` and
  `draft_enforced.json`.

Closeout evidence:

- Pending phase PR, CI, and review.

## Phase 36: Provisional Rule-Aware Sampling

GitHub parent issue: #254.

Branch: `feature/p36-provisional-rule-sampling`.

Status: complete.

Pull request: #257 (merged as `d7d446d`).

Goal: apply the draft scenario-consistency rules provisionally, filter the existing exact dataset,
retrain the ensemble, and compare against the unfiltered Phase 33 result.

Tasks:

- [x] P36.1 Integrate provisional rule filtering into sampling and filter the existing dataset. Child issue: #255.
- [x] P36.2 Retrain the ensemble on provisional-valid data and exact-replay. Child issue: #256.

Scope:

- Rule-aware sample filtering and annotation.
- Provisional-valid dataset from the existing 201 samples.
- Ensemble/GPU GA and exact top-five replay on the filtered set.
- Comparison and documentation.

Out of scope:

- Treating provisional rules as expert-approved.
- New exact sampling unless required.
- Production UI integration.

Architecture notes:

- Draft-enforced mode is an explicit provisional experiment.
- Soft warnings remain attached to samples.
- Rule/spec hashes are recorded.
- Exact replay remains mandatory.

Acceptance boundary:

- The filtered dataset is reproducible.
- The ensemble comparison is recorded with exact values.
- The outcome is documented explicitly.

Implementation evidence:

- Added `--rules` and `--rule-mode` to `scripts/fable_optimization_samples.py`, with per-sample rule
  annotations and rejection of hard-invalid scenarios in draft-enforced mode.
- Added `scripts/filter_optimization_dataset.py` to filter existing datasets without rerunning exact
  models.
- Added tests for the filter path.

Pilot evidence:

- 201 input samples: 134 kept, 67 rejected, 112 with warnings under draft-enforced provisional rules.
- Ensemble remained 5 members, 512 population, 400 generations, CUDA.
- Exact top-five: food error 1.8%, GHG error 46.5%; food rank correlation −0.50, GHG +0.50.
- Rule filtering changed the explored region but did not make the surrogate usable.

Verification evidence:

- Full test suite and docs build to be rerun after committing the integration.

Closeout evidence:

- Pending phase PR, CI, and review.

## Phase 37: Narrow Exact Optimization Pilot

GitHub parent issue: #258.

Branch: `feature/p37-narrow-exact-optimization`.

Status: complete.

Pull request: #261 (merged as `bc3f0f7`).

Goal: run every scenario in a narrow 4-control policy domain through the exact Pyculator and compute
the exact Pareto and weighted-goal front. This is the exact fallback after the surrogate failed.

Tasks:

- [x] P37.1 Enumerate and exactly evaluate a narrow policy domain. Child issue: #259.
- [x] P37.2 Compute the exact Pareto and weighted-goal front, document, and close. Child issue: #260.

Scope:

- `land_scen`, `diet_scen`, `fixtrade_scen`, `livedens_scen`.
- 126 combinations before provisional rule filtering.
- Exact food/GHG/land objectives.
- Pareto and weighted-goal ranking.

Out of scope:

- Surrogate approximation.
- Claims over the full FABLE state space.
- Production UI integration.

Architecture notes:

- Every reported objective is a real Pyculator run.
- Provisional rule filtering is recorded, not treated as expert-approved.
- The narrow-domain boundary must be repeated in every summary.

Acceptance boundary:

- All 126 combinations are attempted or documented.
- Exact objectives and Pareto/weighted rankings are reproducible.
- The report distinguishes narrow-domain results from full-space claims.

Implementation evidence:

- Added `scripts/fable_exact_optimization.py`, an exhaustive exact evaluator with Pareto and
  weighted-goal ranking.
- Added unit tests for Pareto dominance, duplicate-objective collapsing, weighted ranking, and CLI
  help.
- Full run: 126 combinations enumerated; 18 rejected by provisional `CUSTOM-DIET-001`; 108 exact
  valid scenarios; 0 errors; 926.5 s with 24 workers.
- Exact front: 13 unique objective triples (41 rows before collapsing duplicate `livedens` outcomes).
- Exact weighted-goal point: NoDefor2030 / FatDiet / fixtrade Yes / NoGrowth, 3,288.73 kcal and
  121.23 MtCO2e.
- Exact max-food point: NoDefor2030 / FatDiet / fixtrade No / NoGrowth, 3,300.67 kcal and
  242.43 MtCO2e.
- Exact min-GHG point: NoExpansion / EATLancetAverage / fixtrade Yes / HighGrowth, 1,869.64 kcal and
  59.56 MtCO2e.
- Trade-fix effect at fixed land/diet/live density: food −0.36%, GHG −50.0%.
- Land is invariant at 896,559 ha; the narrow-domain tradeoff is food versus GHG.
- 60 valid scenarios carry provisional warnings: 36 `LIVE-DENS-001` and 36 `NARRATIVE-SSP-001` hits.

Verification evidence:

- Exact smoke test: one baseline run, 149.8 s, no errors.
- Full suite and docs build rerun after the report and PR are prepared.

Closeout evidence:

- Pending phase PR, CI, and review.

## Phase 38: Exact Local Sensitivity

GitHub parent issue: #262.

Branch: `feature/p38-exact-local-sensitivity`.

Status: complete.

Pull request: #265 (merged as `9acc215`).

Goal: exact-run one-at-a-time variants around the Phase 37 weighted-goal point and report the local
food/GHG effects of the remaining priority controls.

Tasks:

- [x] P38.1 Enumerate exact one-at-a-time variants for the remaining priority controls. Child issue: #263.
- [x] P38.2 Report exact local effects, document, and close. Child issue: #264.

Scope:

- `affor_scen`, `crop_scen`, `scen_exports`, `scen_imports`, `gwp_scen`, `live_scen`.
- Baseline plus every non-default value.
- Exact objectives, provisional rule annotations, and deltas.

Out of scope:

- Surrogate approximation.
- Interaction claims or full-space claims.
- Expert approval of provisional rules.

Architecture notes:

- This is a local exact sensitivity analysis, not a global optimization.
- All other controls stay at the Phase 37 weighted-goal selections.
- One-at-a-time cannot reveal interactions.

Implementation evidence:

- Added `scripts/fable_exact_sensitivity.py` and unit tests for exact delta calculation and CLI help.
- 20 exact evaluations (baseline plus 19 valid variants); 1 rejected variant (`MyImportScen`) by
  provisional `CUSTOM-IMPORT-001`; 0 errors; 168.9 s with 24 workers.
- Baseline: 3,288.73 kcal and 121.23 MtCO2e.
- Strongest local lever: `live_scen=HighGrowth` at −11.46 MtCO2e (−9.45%) and +1.79 kcal (+0.05%).
- `affor_scen=BonnChallenge+`: +10.63 kcal (+0.32%) and +0.11 MtCO2e (+0.09%).
- `crop_scen=HighGrowth`: −0.93 MtCO2e (−0.77%) and −0.29 kcal (−0.01%).
- `gwp_scen` AR4/AR5/AR6 increase reported GHG by 5.3–6.0% with unchanged food; this is a metric
  conversion, not mitigation.
- Exact combined candidate `live_scen=HighGrowth` + `crop_scen=HighGrowth`:
  3,290.23 kcal and 108.84 MtCO2e; add `affor_scen=BonnChallenge+`: 3,301.11 kcal and 108.95 MtCO2e.
- The three-way candidate dominates the Phase 37 weighted-goal point on food and GHG at constant land.
- `CUSTOM-EXPORT-001` did not reject `MyExportScen2` or `MyExportScen3` because `key_value` is fixed
  to the populated `MyExportScen` row; this must be reviewed before the rule is authoritative.

Verification evidence:

- Full suite: 219 passed, 16 skipped.
- Docs build and theme artifact verification passed.
- Post-merge Test workflow passed.
- Post-merge Docs Pages deploy timed out in `finished_file_sync` on the initial run and on retry;
  this is a GitHub Pages infrastructure failure, not a docs build failure.

Closeout evidence:

- PR #268 squash-merged as `44b9ab5`; parent #266 and child #267 closed.

## Phase 39: Exact Candidate Neighborhood Verification

GitHub parent issue: #266.

Branch: `feature/p39-candidate-neighborhood`.

Status: complete.

Pull request: #268 (merged as `44b9ab5`).

Goal: exact-check the immediate one-coordinate neighborhood of the Phase 38 candidate and verify that
no single-coordinate neighbor strictly dominates it.

Tasks:

- [x] P39.1 Verify no single-coordinate neighbor strictly dominates the Phase 38 candidate. Child issue: #267.

Scope:

- Ten reduced controls, one at a time.
- Exact food/GHG/land objectives.
- Strict-dominance check and local boundary.

Out of scope:

- Surrogate approximation.
- Full-space claims.
- Multi-coordinate interaction claims beyond the Phase 38 combined checks.

Architecture notes:

- This is a local verification, not a new global search.
- Equal-objective coordinate changes are allowed and recorded as ties.
- The candidate is only defensible within the stated local neighborhood.

Implementation evidence:

- Ran `scripts/fable_exact_sensitivity.py` with the Phase 38 candidate as baseline and all ten reduced
  controls.
- 30 exact evaluations (baseline plus 29 valid variants); 2 rejected variants (`MyDiet`,
  `MyImportScen`); 0 errors; 321.6 s with 24 workers.
- Baseline: 3,301.11 kcal and 108.95 MtCO2e.
- No strict single-coordinate dominator.
- 11 exact ties: land `FreeExpansion`; live density `BAUGrowth`/`HighGrowth`; exports
  `E2`/`E3`/custom; imports `I2`/`I3`; afforestation `Affor2`.
- Nearest tradeoffs: `land_scen=NoExpansion` at 2,435.90 kcal / 80.88 MtCO2e;
  `diet_scen=EATLancetAverage` at 2,254.06 kcal / 81.59 MtCO2e; `fixtrade_scen=No` at
  3,303.48 kcal / 213.40 MtCO2e; `affor_scen=Affor1` at 3,290.23 kcal / 108.84 MtCO2e.
- The candidate is a local Pareto point, not a global optimum.

Verification evidence:

- Full suite: 223 passed, 16 skipped.
- Docs build and theme verification passed.
- Post-merge Test and Docs Pages passed.

Closeout evidence:

- PR #272 squash-merged as `5b88e8d`; parent #269 and children #270-#271 closed.

## Phase 40: Exact Interaction Checks and Decision Frontier

GitHub parent issue: #269.

Branch: `feature/p40-exact-decision-frontier`.

Status: complete.

Pull request: #272 (merged as `5b88e8d`).

Goal: fill key exact interaction gaps around the Phase 38 candidate and combine all exact points into
a decision frontier with balanced, food-first, and GHG-first picks.

Tasks:

- [x] P40.1 Run targeted exact interaction checks and build the decision frontier. Child issue: #270.
- [x] P40.2 Write the exact decision brief, document, and close. Child issue: #271.

Scope:

- Eight targeted land/diet/trade interactions at fixed live/crop/afforestation levers.
- Combined exact frontier from Phases 37-40.
- Explicit caps, floors, and local boundary.

Out of scope:

- Surrogate approximation.
- Global FABLE optimization.
- Expert approval of provisional rules.

Architecture notes:

- Every point is a real Pyculator run.
- Caps and floors are policy inputs, not model truths.
- The frontier is local to the evaluated scenario set.

Implementation evidence:

- Added `scripts/fable_exact_decision.py` and unit tests for Pareto filtering, constrained selection,
  deduplication, and CLI help.
- Added eight targeted exact runs; 0 errors; each run 151.5-163.3 s.
- Combined 169 exact points, 160 unique selections; 15 unique exact Pareto objective triples
  (29 rows before collapsing duplicates).
- Exact ranges: 1,571.24-3,303.48 kcal and 59.56-691.93 MtCO2e; land invariant at 896,559 ha.
- Balanced pick: NoDefor2030 / FatDiet / trade Yes / live HighGrowth / crop HighGrowth /
  BonnChallenge+, 3,301.11 kcal and 108.95 MtCO2e.
- Food-first at GHG ≤ 110: same candidate.
- Food-first at GHG ≤ 80: 2,249.39 kcal / 76.78 MtCO2e; at GHG ≤ 90: 2,435.90 / 80.88; at GHG ≤ 100:
  2,939.96 / 98.04.
- GHG-first at food ≥ 2,000: 2,184.58 kcal / 61.24 MtCO2e; at food ≥ 2,400: 2,435.90 / 80.88; at
  food ≥ 2,800: 2,939.96 / 98.04; at food ≥ 3,000: 3,290.23 / 108.84.
- At the 3,000 kcal floor, the strict GHG-first pick is live-high/crop-high without added
  afforestation; the balanced candidate buys 10.88 kcal for 0.11 MtCO2e with BonnChallenge+.

Verification evidence:

- Full test suite and docs build to be rerun after the report and PR are prepared.

Closeout evidence:

- Pending phase PR, CI, and review.

## Phase 41: Interactive Exact Pareto Solution-Space Viewer

GitHub parent issue: #273.

Branch: `feature/p41-pareto-viewer`.

Status: complete.

Pull request: #276 (merged as `1beceee`).

Goal: port the reference multi-dimensional Pareto solution-space interaction into the FABLE portal,
backed by the exact Phases 37-40 frontier.

Tasks:

- [x] P41.1 Publish the exact frontier artifact and read API. Child issue: #274.
- [x] P41.2 Add the interactive 3D Optimization page. Child issue: #275.

Scope:

- Tracked exact frontier artifact and read API.
- Interactive 3D Optimization page.
- X/Y/Z, colour, size, quality floor, exact-front filter, pinning, comparison, and Workbench prefill.

Out of scope:

- Live exact optimization from a browser request.
- Surrogate points.
- Global-frontier claims.

Architecture notes:

- Every point is an exact Pyculator run.
- The viewer reads a tracked artifact; it does not run the optimizer.
- Land is invariant in the current frontier; food, GHG, land, and goal remain selectable dimensions.
- Three.js and OrbitControls are vendored for offline use.

Implementation evidence:

- Added `examples/optimization/fable_2024/frontier.json` (160 exact points, 15 unique Pareto
  objectives, 205 KB) generated by `scripts/fable_exact_decision.py --artifact-output`.
- Added `/api/optimization/frontiers` and `/api/optimization/frontiers/{version}` read endpoints.
- Added the Optimization tab and page with a vendored Three.js/OrbitControls 3D canvas.
- Exact-front filtering reduces the current view from 160 to 29 front rows; 15 unique decision views
  are listed below the canvas.
- Selected points can be pinned (up to three) and compared across food, GHG, land, goal, and key
  scenario selections.
- `Load in Workbench` prefills the exact selections; verified with FABLE 2024 prepared.
- Browser smoke with Playwright: no page errors; 160 points, 15 view cards, 29 front rows, and
  Workbench prefill (FatDiet / NoDefor2030 / fixtrade Yes / live HighGrowth / crop HighGrowth).

Verification evidence:

- Full suite: 227 passed, 16 skipped.
- Ruff passed.
- Sphinx warning-as-error docs build and theme check passed.
- Release artifact check passed; the wheel includes the vendored Three.js assets.
- Browser smoke passed with no console/page errors.
- Post-merge Test and Docs Pages passed.

Closeout evidence:

- PR #276 squash-merged as `1beceee`; parent #273 and children #274-#275 closed.

## Phase 42: Pareto Viewer Interaction Polish

GitHub parent issue: #277.

Branch: `feature/p42-pareto-viewer-polish`.

Status: complete.

Pull request: #279 (merged as `a661259`).

Goal: polish the exact Pareto viewer interactions without changing the exact frontier data.

Tasks:

- [x] P42.1 Add hover, selection marker, real axis ranges, and warning filtering. Child issue: #278.

Scope:

- Hover tooltip with exact objectives and point id.
- Highlight the selected point in the 3D scene.
- Show actual value ranges for the selected X/Y/Z dimensions.
- Add categorical colour legends.
- Add a hide-provisional-warning filter.

Out of scope:

- New optimization runs.
- Surrogate or global-frontier claims.
- Changing the tracked frontier artifact.

Architecture notes:

- The viewer remains read-only over exact points.
- Provisional warnings are display metadata; hiding them is not approval.
- Three.js interaction work stays bounded to the current 160-point scene.

Implementation evidence:

- Added a hover tooltip with exact food, GHG, and goal values; verified hovering `p080`.
- Added a persistent wireframe marker for the selected point.
- Added actual range text for the selected X/Y/Z dimensions.
- Added a categorical colour legend for front membership, phase origin, and control values.
- Added a hide-provisional-warning filter; 91 of 160 points remain visible.
- Existing exact-front filter, pin/compare, and Workbench prefill remain intact.

Verification evidence:

- Full suite: 227 passed, 16 skipped.
- Ruff passed.
- Sphinx warning-as-error docs build and theme check passed.
- Browser smoke passed with no page errors; warning filter and Workbench prefill verified.
- Post-merge Test and Docs Pages passed.

Closeout evidence:

- PR #279 squash-merged as `a661259`; parent #277 and child #278 closed.

## Phase 43: Shareable Pareto State and Filtered Export

GitHub parent issue: #280.

Branch: `feature/p43-pareto-share-export`.

Status: complete.

Pull request: #282 (merged as `49e3bed`).

Goal: make exact Pareto views shareable and exportable without changing the frontier data.

Tasks:

- [x] P43.1 Add URL state, copy-link, and filtered CSV export. Child issue: #281.

Scope:

- Encode version, axes, colour, size, floor, filters, and selected point in the URL.
- Add a copy-link action.
- Add filtered CSV export.
- Browser-smoke and document the workflow.

Out of scope:

- New optimization runs.
- Global-frontier claims.
- Rule approval.

Architecture notes:

- The query string holds viewer state; the hash remains the portal page selector.
- CSV rows are the currently visible exact points, not a recomputation.
- The frontier remains local and provisional.

Implementation evidence:

- URL state round-trip restored X/Y/Z, colour, size, floor, exact-front, warning filter, and point
  `p012`.
- Copy-link copied the full state URL to the clipboard in the browser smoke.
- Filtered CSV export produced 13 rows with 13 visible points under the tested filters.
- Existing hover, pin/compare, and Workbench prefill remain intact.

Verification evidence:

- Full suite: 227 passed, 16 skipped.
- Ruff passed.
- Sphinx warning-as-error docs build and theme check passed.
- Browser smoke passed with no page errors; URL round-trip, clipboard copy, and CSV export verified.
- Post-merge Test and Docs Pages passed.

Closeout evidence:

- PR #282 squash-merged as `49e3bed`; parent #280 and child #281 closed.

## Phase 44: Parallel Coordinates for the Exact Frontier

GitHub parent issue: #283.

Branch: `feature/p44-parallel-coordinates`.

Status: complete.

Pull request: #285 (merged as `64e1a01`).

Goal: add a synchronized parallel-coordinates view for the same exact Pareto points.

Tasks:

- [x] P44.1 Add synchronized parallel coordinates. Child issue: #284.

Scope:

- Scenario controls and outcomes as parallel axes.
- Current exact-front, warning, and quality-floor filters.
- Click a line to select and highlight the same point in the 3D viewer.
- Read-only exact view.

Out of scope:

- New optimization runs.
- Surrogate points.
- Global-frontier claims.

Architecture notes:

- The parallel view consumes the same filtered exact points as the 3D view.
- Axis scales are relative to the current exact artifact.
- Selected lines use the same point id as the 3D marker.

Implementation evidence:

- Added an SVG parallel-coordinates panel with 9 axes: land, diet, trade-fix, livestock, crop,
  afforestation, food, GHG, and goal.
- The panel renders all 160 exact points under the current filters; selected lines are highlighted
  gold and are shared with the 3D selection.
- Clicking a line selects the matching point and enables Workbench prefill.
- The existing share-link, CSV export, hover, marker, and pin/compare behavior remains intact.

Verification evidence:

- Full suite: 227 passed, 16 skipped.
- Ruff passed.
- Sphinx warning-as-error docs build and theme check passed.
- Browser smoke passed with no page errors; 160 lines and 9 axes rendered, line selection worked.
- Post-merge Test and Docs Pages passed.

Closeout evidence:

- PR #285 squash-merged as `64e1a01`; parent #283 and child #284 closed.

## Phase 45: Reference Point and Delta Comparison

GitHub parent issue: #286.

Branch: `feature/p45-reference-delta`.

Status: pr-open.

Pull request: #288.

Goal: let a user pin one exact point as the reference and compare the selected point against it.

Tasks:

- [x] P45.1 Add reference selection, delta card, and synchronized reference markers. Child issue: #287.

Scope:

- Set and clear a reference point.
- Exact food, GHG, land, goal, and selection deltas.
- Reference markers in the 3D scene and parallel coordinates.
- Reference in shareable URL state.

Out of scope:

- New optimization runs.
- Surrogate points.
- Global-frontier claims.

Architecture notes:

- The reference is another exact point, not a baseline model run.
- Deltas are selected minus reference.
- The reference marker is distinct from the selected marker.

Implementation evidence:

- Added set/clear reference controls and a selected-vs-reference delta card.
- Browser smoke compared selected `p033` against reference `p012`: food −10.88 kcal, GHG −0.1064
  MtCO2e, land 0, afforestation `Affor2 → Affor1`.
- Added a blue dashed reference line in parallel coordinates and a blue wireframe reference marker in
  3D.
- Added `opt_reference` URL state; clear-reference removes it.
- Existing filters, hover, marker, share-link, CSV, pin/compare, and Workbench prefill remain intact.

Verification evidence:

- Full suite: 227 passed, 16 skipped.
- Ruff passed.
- Sphinx warning-as-error docs build and theme check passed.
- Browser smoke passed with no page errors; reference marker/line and delta card verified.

Closeout evidence:

- Pending phase PR, CI, and review.

