# AGENTS.md

This file is the working contract for AI coding agents in this repository.

## Project Purpose

`fable-pyculator` exists to build a FABLE Calculator-specific notebook and documentation layer on
top of Modelwright-generated Python models.

The goal is to keep Modelwright generic while collecting FABLE-C conventions here: high-level
scenario selection controls, scenario definition surfaces, canonical output data sheets, curated
headline outputs, and user-guide workflows for analysts working in Jupyter.

This repository is not a replacement for Modelwright core. It should not implement generic workbook
conversion, formula translation, generated-code materialization, or broad validation machinery unless
the work is clearly FABLE-specific and belongs above Modelwright's package boundary.

## Current Repo State

This repository is currently a bootstrap package scaffold. It contains:

- `README.md`: project overview and local development commands.
- `ROADMAP.md`: current plan and issue-tracker map.
- `CHANGE_LOG.md`: append-only project narrative.
- `planning/`: focused planning notes and research records.
- `pyproject.toml`: package metadata and dependency extras.
- `src/fable_pyculator/`: importable package code.
- `tests/`: package-backed tests.
- `docs/`: Sphinx documentation using the Read the Docs theme.
- `benchmarks/fable-calculator/`: tracked benchmark metadata and checksums.
- `reference/fable-calculator/`: tracked public reference documentation.
- `tmp/`: ignored local working area for FABLE-C workbooks, generated models, extracts, logs, and
  validation outputs.

The package currently has early selection-control discovery, output-table discovery, widget-backed
notebook controls, pandas table rendering, and Sphinx guide scaffolding. It is pre-release. Do not
claim stable public API compatibility, arbitrary FABLE country calculator support, production FABLE-P
readiness, or full generated-model equivalence until the roadmap records evidence for those claims.

## Source Workbooks And Generated Outputs

Source FABLE-C workbooks, generated Python models, workbook extracts, validation reports, notebook
scratch outputs, and large intermediate artifacts are local working material unless the maintainer
explicitly approves a small tracked artifact.

Rules:

- Keep `tmp/` ignored.
- Do not commit FABLE-C workbook binaries, generated clones, large extracts, raw validation reports,
  or private transcripts unless explicitly requested.
- Track compact benchmark metadata, checksums, public reference links, sanitized findings, and
  reproducible scripts instead of bulky derived artifacts.
- Record workbook provenance whenever a workbook, worksheet, table, range, selection control, output
  indicator, or validation example is interpreted.
- Keep workbook-version assumptions explicit. The 2020 and 2021 public workbooks share the 16-control
  `SCENARIOS selection` pattern; the 2019 workbook is structurally older and should be treated as a
  fragility check unless later evidence says otherwise.

## Product Vision

Current direction:

- Discover FABLE-C scenario selection controls from workbook structure.
- Represent each selection table as a notebook control that writes exactly one `x` marker and clears
  the other marker cells.
- Discover output data tables from the canonical consecutive output sheets: `FOOD`, `PRODUCTION`,
  `TRADE`, `BIODIVERSITY`, `LAND`, `GHG`, and `WATER`.
- Render outputs as pandas DataFrames and, later, curated matplotlib figures and headline indicator
  cards.
- Use the 2020 public FABLE-C workbook as the primary wrapper benchmark and the 2021 workbook as a
  later generalizability check.
- Preserve the distinction between FABLE-specific notebook/user-guide behavior here and generic
  conversion/generation behavior in Modelwright.

Do not over-specify FABLE semantics before workbook inspection and validation evidence support the
claim.

## Working Principles

- Read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before making project-shaping changes.
- Preserve the distinction between source workbooks, generated models, derived working outputs,
  tracked benchmark metadata, and public documentation.
- Favor reproducible workbook inspection, discovery, rendering, and validation workflows over
  one-off manual notebook edits.
- Use structured workbook parsers and Modelwright APIs where available instead of ad hoc text
  processing.
- Document uncertainty around country-specific customizations, changed table names, hidden sheets,
  data validation extensions, formulas, named ranges, macros, external links, and generated-model
  validation boundaries.
- Keep naming conventions explicit. Do not silently normalize workbook, sheet, table, range, option,
  or output names without documenting the mapping.
- Keep changes scoped. This repo is early-stage, so avoid broad framework choices unless needed for
  the immediate FABLE notebook/user-guide task.

## Planning Workflow

This repo uses an agent-assisted roadmap and GitHub issue workflow.

Active rules now:

- Keep the current plan in `ROADMAP.md`.
- Keep the immediate edge of work in the `Current Next Steps` section of `ROADMAP.md`.
- Record completed deliverables in `CHANGE_LOG.md` with dated bullets.
- Use `planning/` for focused notes, investigations, and contracts that are too detailed for the
  roadmap.
- Before non-trivial work, update or confirm the roadmap entry that governs it.
- Use GitHub issues with `gh` in tandem with the roadmap once the public remote and GitHub CLI access
  exist:
  - roadmap phases map to GitHub parent issues;
  - roadmap tasks map to child issues linked from the parent issue body;
  - substantial subtasks may map to third-level implementation issues linked from the task issue
    body;
  - lightweight subtasks stay as checklists inside the task issue body;
  - do not use more than three issue levels: phase, task, and implementation subtask;
  - record issue numbers beside roadmap phases and tasks once created.

Until the public GitHub repo and `gh` access exist, roadmap issue fields may remain explicit
placeholders.

## Strict Development Workflow

Use this workflow for active development from the first post-bootstrap phase boundary onward:

- One active roadmap phase should generally correspond to one GitHub parent issue and one feature
  branch.
- Create or activate the GitHub parent issue before starting a roadmap phase.
- Create the feature branch from current `main` for that parent issue.
- Create child issues for roadmap tasks under the parent issue.
- Document task subtasks as checklist steps inside the child issue body unless they are large enough
  to deserve third-level implementation issues.
- Work child issues one at a time where practical, usually in roadmap order.
- Before closing a child issue, update every issue-body checklist item to checked, or rewrite the
  issue body to make explicitly clear which items were superseded or are not applicable.
- Close each child issue only after its repo changes, documentation, issue-body checklist, and
  verification for that task are complete.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, and issue comments synchronized as task state changes.
- Open a PR from the phase branch back to `main` when the parent issue's child issues are complete or
  explicitly deferred.
- Close the parent issue only after the PR has merged back to `main`.
- Do not start a new active parent issue and branch until the current parent issue is closed, unless
  the maintainer explicitly approves a parallel lane.

## Expected Deliverables Over Time

Expected near-term phases:

1. Governance bootstrap: establish the repo contract, roadmap, changelog, planning structure, package
   scaffold, docs scaffold, benchmark metadata, and artifact hygiene.
2. Notebook wrapper maturation: harden selection-control discovery, output table surfaces, curated
   headline outputs, and the initial 2020 benchmark notebook loop.
3. User guide: build a full Sphinx FABLE Pyculator guide from the public FABLE-C documentation and
   inspected workbook structures.
4. Validation: compare notebook-wrapper behavior against the generated 2020 FABLE-C model, then test
   the 2021 workbook to identify generalizable patterns and fragile assumptions.
5. Packaging and publication: decide release readiness only after the notebook/user-guide workflow is
   coherent and validated.

Use these phases as orientation, not as permission to add large systems prematurely.

## Tooling And Verification

Current default verification commands:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest
.venv/bin/sphinx-build -b html docs _build/html -W
sha256sum -c benchmarks/fable-calculator/checksums.sha256
```

When adding tooling:

- Document required commands in `README.md` or a dedicated planning note.
- Add the smallest useful verification path for the change.
- Prefer commands that can be rerun from a clean checkout with source workbooks restored under
  `tmp/`.
- Do not require absolute machine-specific paths outside this repository unless unavoidable; if
  unavoidable, document them clearly.

## Git Hygiene

- Treat existing uncommitted changes as user work unless you made them.
- Do not revert user changes without explicit instruction.
- Avoid committing generated, bulky, private, or environment-specific files.
- Keep `.gitignore` aligned with data handling rules, especially for `tmp/`, source workbooks,
  generated models, and output directories.

## Documentation Standards

Documentation should be practical and provenance-oriented:

- Say what was inspected, where it came from, and how it was interpreted.
- Include exact local paths for workbook sources or scratch outputs only when useful and safe.
- Include commands used for repeatable inspection steps.
- Capture assumptions, known gaps, and follow-up questions.
- Avoid presenting generated behavior, recovered workbook meaning, or country-calculator support as
  authoritative until validated against source workbook behavior.

