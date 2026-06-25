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
