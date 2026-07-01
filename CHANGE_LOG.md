# CHANGE_LOG.md

This file records completed project work in chronological order.

## 2026-07-01

- Activated Phase 16 on `feature/p16-validation-evidence-packaging`, created child issues #112,
  #110, #111, #113, and #114 under parent issue #79, and scoped the phase around compact validation
  evidence summaries from restored local artifacts plus an extraction-only opt-in benchmark workflow.
- Added `fable_pyculator.validation` with compact validation-evidence path helpers, sanitized
  summary extraction, conservative pass/fail/incomplete equivalence classification, and stable JSON
  plus Markdown writers that avoid copying raw workbook, generated source, and generated-value
  payloads.
- Added `scripts/package_fable_validation_evidence.py` and a manual-only
  `.github/workflows/benchmark-evidence.yml` workflow so restored local generated-model artifacts can
  be summarized and uploaded as compact sanitized evidence without running full model generation by
  default.
- Added Sphinx documentation for validation-evidence packaging and linked it from README,
  validation-scope, generated-model artifact, docs index, and API reference pages.
- Verified the Phase 16 local implementation with Ruff, pytest, Sphinx warning-as-error docs, Read
  the Docs theme verification, workbook checksums, release artifact checks, whitespace checks, and a
  real local 2021 evidence-packaging smoke test that correctly reported incomplete equivalence when
  explicit comparison counts were unavailable.
- Activated Phase 15 on `feature/p15-scenario-bundles-result-artifacts`, created child issues
  #104, #106, #105, #107, and #108 under parent issue #78, and scoped the phase around
  selection-control scenario bundles plus rendered result artifacts under ignored `tmp/`.
- Added `fable_pyculator.scenarios` with JSON/YAML scenario-bundle loading, selection-control
  validation, bundle execution through the existing notebook loop, and deterministic rendered
  artifact writers for normalized bundle metadata, manifests, CSV frames, and optional headline
  figures.
- Added `scripts/run_fable_scenario_bundle.py`, public-safe JSON/YAML example bundles, and Sphinx
  documentation for running named scenario bundles against existing generated models without
  expanding generated-model equivalence claims.
- Verified the Phase 15 slice with Ruff, pytest, Sphinx warning-as-error docs, Read the Docs theme
  verification, workbook checksums, release artifact checks, whitespace checks, and a real 2021
  scenario-bundle dry-run smoke test against the restored local workbook.
- Merged Phase 15 through PR #109 and confirmed post-merge Test workflow run #28537043841 plus Docs
  Pages workflow run #28537043793 passed, including GitHub Pages deployment.
- Activated Phase 14 on `feature/p14-version-general-fable-build-workflows`, created child issues
  #99, #101, #100, #102, and #98 under parent issue #77, and scoped the phase around
  version-general FABLE build workflows plus output-ref strategy comparison.
- Added version-general FreshForge build helpers, including `fable_freshforge_build_paths`,
  `prepare_freshforge_rebuild`, and named output-ref strategies for output columns, headline-only
  slices, named tables, explicit flavour tags, and all columns, while preserving the 2021
  compatibility wrappers.
- Added `scripts/build_fable_model.py` as the version-general plan-first rebuild command and kept
  `scripts/build_fable_2021_model.py` as a 2021 shortcut.
- Updated README and Sphinx docs to describe version conventions, strategy choices, and 2021
  examples without expanding generated-model equivalence claims.
- Verified Phase 14 locally with Ruff, pytest, Sphinx warning-as-error docs, Read the Docs theme
  verification, workbook checksums, release artifact checks, whitespace checks, and real 2021
  plan-mode smoke tests for default output columns, headline-only refs, and the `ghg_resultsghg`
  table strategy.
- Merged Phase 14 through PR #103 and confirmed post-merge Test workflow run #28535828270 plus Docs
  Pages workflow run #28535828354 passed, including GitHub Pages deployment.
- Activated Phase 13 on `feature/p13-one-command-2021-freshforge-rebuild`, created child issues #91
  through #94 under parent issue #76, and scoped the tranche around a plan-first one-command 2021
  FreshForge/Modelwright rebuild path.
- Added `prepare_2021_freshforge_rebuild` and `FableFreshForgeRebuildPlan` to consolidate the
  notebook-local 2021 output-ref derivation, cached-workbook validation scenario writing, and
  Modelwright FreshForge workflow construction into tested package APIs.
- Added executable script `scripts/build_fable_2021_model.py`, which defaults to plan-only artifact
  preparation under `tmp/generated-models/fable-2021/`, prints a concise summary, supports
  output-table/tag filtering options, and requires `--run` before invoking FreshForge execution.
- Switched cached-workbook validation-scenario preparation to indexed workbook access after the real
  2021 smoke test exposed pathological random access through `openpyxl` read-only worksheets.
- Added focused tests for the package rebuild preparation helper and script help, missing-workbook,
  and plan-mode behavior.
- Added Sphinx documentation for the 2021 FreshForge rebuild command and linked it from the generated
  model artifact guide and README.
- Verified the Phase 13 slice with the real 2021 plan-only command, which wrote 16,478 `OUTPUT-*`
  refs and 16,478 comparable cached outputs under ignored `tmp/generated-models/fable-2021/`, plus
  Ruff, pytest, Sphinx warning-as-error docs, Read the Docs theme verification, workbook checksum
  verification, release-artifact checks, and `git diff --check`.
- Addressed issue #96 by adding narrow suppression for known-benign `openpyxl` warnings about
  unsupported WMF images and data-validation extension metadata during FABLE workbook loads. These
  workbook features are not part of FABLE Pyculator's scenario, output, notebook, or rebuild
  surfaces.

## 2026-06-25

- Added FreshForge orchestration roadmap placeholders: Phase 9 for a future plan-only FABLE Pyculator
  provider and Phase 10 for a future cross-package FABLE Pyculator plus Modelwright workflow example,
  with GitHub parent issues #61 and #62 and planning notes under `planning/`.
- Activated Phase 10 on `feature/p10-2021-freshforge-build-notebook`, created child issues #64
  through #66, and added an Abdulateef-facing
  `examples/notebooks/fable-pyculator-2021-freshforge-build-plan.ipynb` template that uses FABLE
  Pyculator to derive 2021 output refs, FreshForge to plan the Modelwright workflow graph, and gated
  Modelwright commands to infer, generate, and execute the 2021 model from ignored local artifacts.
- Verified the Phase 10 notebook slice with targeted example tests, Ruff, full pytest, Sphinx
  warning-as-error docs, Read the Docs theme verification, workbook checksum verification, release
  artifact checks, and `git diff --check`.
- Merged Phase 10 PR #67, verified post-merge Test and Docs Pages workflows, confirmed GitHub Pages
  deployment, and closed the Phase 10 issue set.
- Activated Phase 11 on `feature/p11-freshforge-2021-run-notebook`, created parent issue #69 and
  child issues #70 through #73, and scoped the phase around an Abdulateef-facing companion notebook
  that runs the 2021 Modelwright build through FreshForge's serial local runner.
- Added `examples/notebooks/fable-pyculator-2021-freshforge-run.ipynb`, which derives 2021
  `OUTPUT-*` output refs, prepares cached-workbook validation, writes a Modelwright FreshForge
  workflow, validates/plans it, gates `run_workflow(...)` behind `RUN_FRESHFORGE = False`, and loads
  the newly generated 2021 model for FABLE Pyculator output inspection when present.
- Verified Phase 11 locally with targeted example tests, Ruff, full pytest, Sphinx warning-as-error
  docs, Read the Docs theme verification, workbook checksum verification, release-artifact checks,
  and `git diff --check`.
- Merged Phase 11 PR #74, verified PR checks and post-merge Docs Pages deployment, and closed the
  Phase 11 issue set.
- Added `planning/freshforge_modelwright_fable_deployment_targets.md` to collect next-step
  FreshForge workflow automation targets for the narrower Modelwright + FABLE Pyculator lane within
  the CLEWs-C2020 project context, including upstream functional caveats.
- Bootstrapped the `fable-pyculator` package scaffold as a FABLE Calculator-specific notebook layer on
  top of Modelwright-generated Python models.
- Added typed scenario parameter, selection control, output indicator, and output table declarations
  under `src/fable_pyculator/`.
- Added discovery helpers for FABLE-C `SCENARIOS selection` tables and canonical output-sheet Excel
  tables.
- Added an `ipywidgets` scenario control surface and pandas/matplotlib notebook rendering helpers.
- Added tests for constants, control surfaces, workbook discovery, spec mapping, and output rendering.
- Added a Sphinx Read the Docs themed documentation scaffold with artifact, workbook-structure, and
  notebook-control-surface guides.
- Downloaded and tracked the public 2020 FABLE Calculator documentation PDF under
  `reference/fable-calculator/`.
- Downloaded the public 2019, 2020, and 2021 FABLE-C workbooks into ignored
  `tmp/private-workbooks/` and tracked checksums plus benchmark metadata under
  `benchmarks/fable-calculator/`.
- Inspected the public workbook structure and recorded that the 2020 and 2021 workbooks expose 16
  high-level `SCENARIOS selection` controls, while the 2019 workbook exposes an older 12-control
  structure.
- Established the FABLE-C output data surface order as `FOOD`, `PRODUCTION`, `TRADE`,
  `BIODIVERSITY`, `LAND`, `GHG`, and `WATER`.
- Adopted the Modelwright-style agent-assisted development workflow by adding `AGENTS.md`,
  `ROADMAP.md`, `CHANGE_LOG.md`, and `planning/README.md`.
- Configured the local Git remote `origin` as `https://github.com/UBC-FRESH/fable-pyculator.git`,
  created the public `UBC-FRESH/fable-pyculator` GitHub repository, installed and authenticated
  GitHub CLI locally, pushed the bootstrap commit to `main`, created Phase 0 parent issue #1 and
  child issues #2 through #5, and recorded the issue mapping in `ROADMAP.md`.
- Closed Phase 0 after posting verification evidence to child issues #2 through #5 and parent issue
  #1.
- Activated Phase 1 on `feature/p1-fable-c-notebook-wrapper-maturation`, created GitHub parent issue
  #6 and child issues #7 through #10, and scoped the phase around hardening FABLE-C selection-control
  discovery, curating headline outputs and figures, building the first 2020 generated-model notebook
  loop, and adding user-guide/validation evidence.
- Completed P1.1 by adding opt-in workbook-backed tests that validate the 2020 S.1 through S.16
  selection-control contract, confirm 2021 shares the same control structure with the known
  `Affor_scen` default difference, and preserve 2019 as an older 12-control fragility check; recorded
  findings in `planning/phase-1-selection-control-validation.md`.
- Completed P1.2 by adding curated headline output series for FOOD, LAND, GHG, and WATER, plus
  notebook rendering helpers for tidy pandas headline frames and matplotlib line figures; recorded
  source table mappings in `planning/phase-1-headline-output-curation.md`.
- Added a `Docs Pages` GitHub Actions workflow and phase close-out guidance so Sphinx docs build on
  pull requests to `main` and deploy to GitHub Pages after merges to `main`.
- Completed P1.3 by adding the first 2020 notebook-loop helpers that build a workbook-derived spec,
  load an ignored generated Modelwright model from `tmp/generated-models/fable-2020/`, apply
  selection-control overrides, and return rendered output tables plus curated headline frames and
  figures; added `examples/notebooks/fable-pyculator-2020-loop.ipynb` and recorded the contract in
  `planning/phase-1-2020-notebook-loop.md`.
- Completed P1.4 by adding Sphinx guide pages for the 2020 notebook workflow and validation scope,
  linking the tracked example notebook into the docs, and recording 2020 benchmark evidence plus 2021
  follow-up scope in `planning/phase-1-user-guide-validation-closeout.md`.
- Aligned FABLE Pyculator's Sphinx configuration and Pages workflow with Modelwright's Read the Docs
  themed documentation setup, including matching RTD theme options, `docs/requirements.txt`, and a
  generated-artifact theme verifier.
- Added a repo-local VSCode/Jupyter bootstrap script, documented the expected `.venv` notebook
  kernel, and made the 2020 example notebook resolve the repository root from its working directory
  instead of assuming the kernel starts at the repo root.
- Committed the 2020 example notebook after a successful benchmark run so GitHub can render the
  example output tables and headline figure directly in the browser.
- Activated Phase 2 on `feature/p2-output-table-column-flavour-filtering`, promoted issue #15 to the
  phase parent, and created child issues #16, #18, #19, and #17 for output table column-flavour
  metadata, filtering API, documentation, and workbook-backed validation.
- Completed Phase 2 implementation by adding workbook-derived output table column flavour metadata,
  render-time flavour filtering for output DataFrames and notebook loops, Sphinx guide examples, and
  opt-in workbook-backed validation for the 2020 and 2021 public FABLE-C tag inventories.
- Reopened Phase 2 for follow-up issue #21 to add wildcard and prefix-family output flavour filters
  such as `DATA`, `DATA*`, and `OUTPUT-*`.
- Completed Phase 2 follow-up issue #21 by adding prefix-family and trailing-star wildcard output
  flavour filters plus README and Sphinx examples.
- Activated Phase 3 on `feature/p3-default-all-rendered-outputs`, created parent issue #23 and child
  issues #25 and #24, and scoped the phase around rendering all output tables and headline frames by
  default from a single generated-model run.
- Completed Phase 3 implementation by making notebook loops render all declared output tables and
  headline frames by default, preserving explicit subset rendering, and re-executing the 2020 example
  notebook with working wildcard flavour-filter examples.
- Started post-Phase-3 polish issue #27 to make the 2020 example notebook's rendered output
  inspection cells clearer in GitHub preview.
- Activated Phase 4 on `feature/p4-scenario-definition-table-discovery`, created parent issue #29
  and child issues #30 through #33, and scoped the phase around discovering
  `SCENARIOS definition` native tables as notebook-inspectable metadata before richer editing widgets.
- Completed the Phase 4 implementation by adding typed scenario-definition table declarations,
  workbook discovery, pandas inspection helpers, documentation, and synthetic plus opt-in
  workbook-backed validation for the 2020/2021 definition-table inventory.
- Closed Phase 4 after PR #34 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed.
- Activated Phase 5 on `feature/p5-scenario-definition-input-semantics`, created parent issue #35
  and child issues #36 through #39, and scoped the phase around separating output-table flavour
  metadata from scenario-definition role/source metadata while adding selection-location links.
- Completed the Phase 5 implementation by renaming scenario-definition table metadata to
  `column_role_*`, removing `SCEN` from output flavour-tag normalization, adding
  scenario-definition location markers and `scenario_definition_tables_for_location`, and updating
  docs/tests/planning evidence.
- Closed Phase 5 after PR #40 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed.
- Activated Phase 6 on `feature/p6-alpha-release-readiness`, created parent issue #41 and child
  issues #42 through #45, and scoped the phase around `v0.1.0a1` alpha release readiness, release
  workflow symmetry with Modelwright, and expanded API/docs coverage.
- Completed the Phase 6 implementation by aligning package metadata and release extras with
  Modelwright, adding release artifact checks and a trusted-publishing workflow, expanding Sphinx API
  documentation and public docstrings, and documenting the `v0.1.0a1` alpha release runbook and
  caveats.
- Closed Phase 6 after PR #46 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed, including the release-artifact job and GitHub Pages deployment.

## 2026-06-29

- Activated Phase 7 on `feature/p7-2021-artifact-wiring`, created parent issue #48 and child issues
  #50, #52, #51, and #49, and scoped the phase around first-user feedback that 2021 workbook testing
  could accidentally reuse the 2020 generated model and that generated-model artifact creation was
  under-documented.
- Completed the Phase 7 implementation by adding explicit 2021 workbook/generated-model defaults,
  `build_2021_notebook_spec`, `run_2021_notebook_loop`, a shared `build_notebook_spec`, a 2021
  notebook wiring template with no 2020 fallback, generated-model artifact documentation, and tests
  guarding the 2020/2021 artifact boundary.
- Created Modelwright follow-up issue UBC-FRESH/modelwright#201 to clarify how Modelwright
  `contract.json`, `expressions.json`, and `constants.json` generation inputs are produced for new
  production-sized workbook models.
- Closed Phase 7 after PR #53 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed, including release-artifact checks and GitHub Pages deployment.
- Activated Phase 8 on `feature/p8-validated-2021-generated-model`, created parent issue #54 and
  child issues #59, #58, #55, #57, and #56, and scoped the phase around publishing a compressed 2021
  generated-model artifact only if Modelwright validation reaches the same zero-mismatch
  comparable-output standard used for the 2020 benchmark.
- Completed the core Phase 8 validation path: Modelwright extraction, graph construction, formula
  translation, contract inference, Python generation, generated-model execution, and cached-output
  comparison passed for the public 2021 FABLE-C workbook with 281,922 comparable outputs, 281,922
  matches, 0 mismatches, and 15,080 non-comparable cached blank formula outputs recorded as boundary
  evidence.
- Published the approved compressed 2021 generated model under
  `examples/fable_2021/generated_fable_2021_model.py.xz`, added sanitized validation evidence in
  `examples/fable_2021/README.md` and `planning/phase-8-2021-validation-summary.md`, and updated the
  2021 notebook to materialize that archive into ignored `tmp/generated-models/fable-2021/` working
  space.
- Merged upstream Modelwright PR #204 at `c3734d3` to fix generated `VLOOKUP` `#N/A` propagation,
  then reran the 2021 generation/validation path and recorded the clean Phase 8 verification suite.
- Closed Phase 8 after PR #60 merged to `main` at `c073f4e` and the post-merge Test and Docs Pages
  workflows passed, including GitHub Pages deployment.
- Created FreshForge deployment parent issues #75 through #79 for FABLE Pyculator Phases 12 through
  16, created active Phase 12 child issues #80 through #83, and opened
  `feature/p12-output-ref-workflow-builder-apis` to extract notebook-local output-ref/workflow logic
  into tested package helpers before adding a one-command 2021 rebuild workflow.
- Implemented the Phase 12 helper extraction by adding `fable_pyculator.workflows`, public output-ref
  derivation, version-specific FreshForge build paths, stable output-ref/workflow/validation JSON
  writers, cached-workbook validation-scenario generation, and Modelwright FreshForge workflow
  construction; updated the 2021 FreshForge notebooks and Sphinx API docs to use the new package
  helpers.
- Closed Phase 12 after PR #84 merged to `main`, post-merge Test and Docs Pages workflows passed,
  and live docs verification confirmed the new workflow-helper API and notebook-control guide content
  were deployed.
- Reactivated skipped Phase 9 on `feature/p9-fable-freshforge-provider`, created child issues #85
  through #89, and implemented a plan-only FABLE Pyculator FreshForge provider with a public-safe
  2021 notebook workflow example, Sphinx docs, entry-point metadata, and provider discovery/planning
  tests.
- Closed Phase 9 after PR #90 merged to `main`, post-merge Test and Docs Pages workflows passed, and
  live docs verification confirmed the new provider guide and API reference content were deployed.
