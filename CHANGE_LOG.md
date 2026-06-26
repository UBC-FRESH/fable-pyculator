# CHANGE_LOG.md

This file records completed project work in chronological order.

## 2026-06-25

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
