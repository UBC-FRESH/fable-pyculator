# FreshForge Deployment Targets For Modelwright + FABLE Pyculator

Date: 2026-07-01

Purpose: collect plausible next-step FreshForge workflow automation targets for the narrower
Modelwright + FABLE Pyculator lane inside the CLEWs-C2020 project context. These are planning inputs,
not current capability claims.

Related planning:

- `phase-9-freshforge-provider-pilot.md`
- `phase-10-cross-package-freshforge-workflow.md`
- `phase-8-2021-validation-summary.md`

## Current Boundary

FABLE Pyculator owns FABLE-specific workbook knowledge: scenario-selection surfaces, scenario
definition tables, output-table discovery, output-ref derivation, and notebook rendering.

Modelwright owns generic workbook extraction, graph construction, formula translation,
generated-model contract inference, Python model generation, generated-model execution, and
validation mechanics.

FreshForge now owns workflow graph validation, planning, and serial local orchestration for providers
that expose executable nodes.

The current FABLE Pyculator notebooks demonstrate two cross-package workflows:

- `fable-pyculator-2021-freshforge-build-plan.ipynb`: derive output refs, write a workflow graph, and
  plan/show commands.
- `fable-pyculator-2021-freshforge-run.ipynb`: derive output refs, write a workflow graph, and gate
  a FreshForge-run Modelwright build behind `RUN_FRESHFORGE = False`.

## Candidate Deployment Targets

### 1. One-Command 2021 Model Rebuild

Goal: make the notebook workflow available as a repeatable script or CLI command that rebuilds the
2021 generated model from the public workbook into ignored local artifacts.

Potential workflow:

1. Confirm the 2021 workbook checksum.
2. Derive `OUTPUT-*` refs with FABLE Pyculator.
3. Write `output_refs.json`.
4. Write the FreshForge Modelwright workflow.
5. Run FreshForge.
6. Summarize generated-model, generated-values, and validation-report artifacts.

Upstream caveats:

- FABLE Pyculator needs a public helper for output-ref derivation instead of notebook-local
  comprehension code.
- The generated workflow writer should become a small tested API rather than notebook-only JSON
  assembly.
- Modelwright/FreshForge should expose stable enough run-result JSON for a script to summarize
  failures cleanly.
- The command must keep source workbooks, generated `.py`, and raw reports under ignored `tmp/`.

### 2. Version-General FABLE Build Workflow

Goal: support `year=2020`, `year=2021`, and future public FABLE workbook versions with one
version-specific workflow builder.

Potential workflow:

1. Select workbook version and expected local paths.
2. Build a workbook-derived FABLE spec.
3. Derive output refs using an explicit strategy, such as all `OUTPUT-*`, one output sheet, one table,
   or curated headline refs.
4. Build and run the Modelwright FreshForge workflow.
5. Validate and record a version-specific summary.

Upstream caveats:

- FABLE Pyculator needs a durable artifact path registry for workbook version, generated-model path,
  module name, workbook ID, and validation-output strategy.
- FABLE Pyculator should expose output-ref strategies as named options rather than ad hoc code.
- Validation claims must stay version-specific and tied to comparable-output counts.
- New workbook versions may change output-table names, column tags, or scenario surfaces.

### 3. Output-Ref Strategy Comparison

Goal: compare different generated-model boundaries before choosing a production validation target.

Candidate strategies:

- all discovered `OUTPUT-*` cells;
- only one output sheet, such as `GHG`;
- one canonical table, such as `ghg_resultsghg`;
- curated headline series;
- selected CLEWs reporting indicators.

Potential workflow:

1. Derive several candidate `output_refs.json` files.
2. Run Modelwright inference for each strategy.
3. Record symbol counts, expression counts, constants, diagnostics, generated source size, runtime,
   comparable-output count, and mismatches.
4. Pick the smallest boundary that answers the modelling question.

Upstream caveats:

- FABLE Pyculator needs reusable output-ref derivation helpers with provenance metadata.
- Modelwright run summaries should expose compact counts without requiring users to open large raw
  JSON reports.
- FreshForge may need clearer run namespace support so multiple strategies do not overwrite each
  other under `tmp/`.

### 4. Scenario Bundle Automation

Goal: automate repeated FABLE Pyculator runs for named scenario bundles once a generated model exists.

Potential workflow:

1. Define named scenario selections, such as SSP1, SSP2, SSP3, or CLEWs-specific variants.
2. Load the matching generated model.
3. Run FABLE Pyculator notebook-loop helpers for each scenario.
4. Save selected output tables/headline frames.
5. Render comparison tables/figures.

Upstream caveats:

- FABLE Pyculator needs a durable scenario-bundle schema for selection-control overrides.
- Scenario definition table inputs are currently inspectable, but not yet a full editable/validated
  parameter surface.
- FABLE Pyculator should define output artifact formats for rendered DataFrames/figures before
  automating report output.
- FreshForge needs either FABLE Pyculator executable provider nodes or a small workflow script that
  calls FABLE Pyculator APIs.

### 5. Build-And-Run Notebook Smoke Test

Goal: provide a lightweight smoke workflow for onboarding users without asking them to run the full
multi-minute generated-model build immediately.

Potential workflow:

1. Confirm workbook and environment readiness.
2. Derive a small output-ref slice, such as one table or curated headline refs.
3. Run FreshForge/Modelwright for the small slice.
4. Load the generated model and render a tiny FABLE Pyculator output view.

Upstream caveats:

- Need a deliberately small public output-ref strategy that is fast and pedagogically useful.
- Must clearly label this as a smoke test, not full comparable-output validation.
- If the smoke output uses cached values, the documentation must explain cached-workbook validation
  boundaries.

### 6. Validation Evidence Packaging

Goal: produce compact, shareable validation evidence from a FreshForge run without tracking raw
generated models or full reports.

Potential workflow:

1. Run a version-specific Modelwright/FABLE workflow under ignored `tmp/`.
2. Extract sanitized counts and status from inference, generation, execution, and evaluation reports.
3. Write a compact validation summary Markdown/JSON artifact.
4. Optionally update a planning note or docs page after maintainer review.

Upstream caveats:

- Need a small summary extractor in FABLE Pyculator or Modelwright.
- Must preserve private/raw artifact hygiene.
- Must avoid claiming equivalence unless comparable-output counts, match counts, mismatch counts, and
  validation boundaries are recorded.

### 7. GitHub Actions Opt-In Benchmark Workflow

Goal: make benchmark runs repeatable in CI-like environments when public workbook artifacts are
available.

Potential workflow:

1. Restore public benchmark workbooks.
2. Run a narrow or full FreshForge/Modelwright build.
3. Run FABLE Pyculator output rendering smoke checks.
4. Upload sanitized summary artifacts.

Upstream caveats:

- Full FABLE generation and validation may be too slow or memory-heavy for default CI.
- Workflow should be manually triggered or opt-in, not part of every PR.
- Workbook download/checksum materialization must be robust before CI use.
- Generated raw artifacts must not be uploaded unless explicitly approved.

## Likely Implementation Order

1. Extract notebook-local output-ref derivation into tested FABLE Pyculator helper APIs.
2. Extract notebook-local FreshForge workflow JSON assembly into a tested helper.
3. Add a small CLI or script for the 2021 rebuild workflow.
4. Add strategy comparison support for output-ref boundaries.
5. Add scenario-bundle automation once scenario selection and scenario definition input surfaces are
   clearer.
6. Add compact validation-summary extraction before any CI benchmark automation.

## Functional Expansion Watchlist

FABLE Pyculator:

- Public output-ref derivation helpers.
- Version-specific artifact path registry.
- Scenario-bundle schema and validation.
- Editable scenario-definition parameter surface.
- Result artifact writers for tables, figures, and summaries.
- Compact validation-summary extraction.

Modelwright:

- Stable generated-model workflow summaries.
- Better compact failure diagnostics for inference/generation/evaluation.
- Continued performance/memory guardrails for full FABLE-scale runs.
- Public API stability for the payload helpers currently mirrored by CLI behavior.

FreshForge:

- Run namespace support for repeated strategy/scenario runs.
- Better run-result summaries and failure rendering.
- Optional run matrices or workflow expansion once concrete scenario-grid examples justify it.
- Provider-discovery and dependency guidance for cross-repo development environments.

## Non-Claims

This note does not claim that all listed automation targets are currently implemented. Each target
needs a roadmap phase or issue, acceptance criteria, tests, docs, and validation evidence before it
becomes a supported workflow.
