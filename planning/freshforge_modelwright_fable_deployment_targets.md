# Post-v0.1.0a2 FreshForge Deployment Targets For Modelwright + FABLE Pyculator

Date: 2026-07-01

Purpose: track the remaining FreshForge workflow automation targets for the narrower Modelwright +
FABLE Pyculator lane inside the CLEWs-C2020 project context after the `v0.1.0a2` FABLE workflow
automation alpha. These are planning inputs, not current capability claims.

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

## Completed Since This Note Was First Drafted

The `v0.1.0a2` alpha line completed several original deployment targets:

- one-command 2021 model rebuild preparation;
- version-general FABLE build workflow helpers and scripts;
- named output-ref strategies;
- selection-control scenario bundles with rendered result artifacts;
- compact FABLE-side validation evidence packaging;
- opt-in extraction-only benchmark evidence workflow.

The remaining work is less about extracting notebook-local helper code and more about making repeated
runs comparable, namespaced, and compactly summarized across FreshForge, Modelwright, and FABLE
Pyculator.

## Remaining Candidate Deployment Targets

### 1. Output-Ref Strategy Comparison

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

Roadmap phase: FABLE Pyculator Phase 18, parent issue #122.

Upstream caveats:

- FreshForge Phase 7 should provide run namespaces so multiple strategies do not overwrite each
  other under `tmp/`.
- Modelwright Phase 35 should expose compact stage summaries so users do not need to open large raw
  JSON reports.
- Strategy comparison must not create new equivalence claims unless validation evidence supports
  them.

### 2. FreshForge-Backed Scenario Bundle Orchestration

Goal: upgrade existing FABLE Pyculator scenario bundles so repeated bundle runs can be orchestrated
and summarized cleanly through FreshForge once a generated model exists.

Potential workflow:

1. Define named scenario selections, such as SSP1, SSP2, SSP3, or CLEWs-specific variants.
2. Load the matching generated model.
3. Run FABLE Pyculator notebook-loop helpers for each scenario.
4. Save selected output tables/headline frames.
5. Render comparison tables/figures.

Roadmap phase: FABLE Pyculator Phase 19, parent issue #123.

Upstream caveats:

- FreshForge Phase 7 should provide run namespaces/summaries.
- FreshForge Phase 8 may provide generic matrix expansion if bundle orchestration needs grid
  expansion rather than simple repeated runs.
- Scenario definition table inputs remain out of scope until a later FABLE-specific editing phase.

### 3. Build-And-Run Notebook Smoke Test

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

### 4. Validation Evidence Packaging

Goal: shift generic compact validation evidence extraction toward Modelwright while preserving
FABLE-specific publication/rendering guidance in FABLE Pyculator.

Potential workflow:

1. Run a version-specific Modelwright/FABLE workflow under ignored `tmp/`.
2. Extract sanitized counts and status from inference, generation, execution, and evaluation reports.
3. Write a compact validation summary Markdown/JSON artifact.
4. Optionally update a planning note or docs page after maintainer review.

Roadmap phases: Modelwright Phase 36, parent issue #221; FABLE Pyculator Phase 20, parent issue #124.

Upstream caveats:

- Modelwright should own generic generated-model validation evidence extraction.
- FABLE Pyculator should consume that evidence for FABLE-facing summaries and benchmark workflows.
- Both packages must preserve private/raw artifact hygiene.

### 5. GitHub Actions Opt-In Benchmark Workflow

Goal: make benchmark runs repeatable in CI-like environments when public workbook artifacts are
available.

Potential workflow:

1. Restore public benchmark workbooks.
2. Run a narrow or full FreshForge/Modelwright build.
3. Run FABLE Pyculator output rendering smoke checks.
4. Upload sanitized summary artifacts.

Roadmap phase: FABLE Pyculator Phase 20, parent issue #124.

Upstream caveats:

- Full FABLE generation and validation may be too slow or memory-heavy for default CI.
- Workflow should be manually triggered or opt-in, not part of every PR.
- Workbook download/checksum materialization must be robust before CI use.
- Generated raw artifacts must not be uploaded unless explicitly approved.

## Coordinated Implementation Order

1. FreshForge Phase 7: run namespaces and workflow-run summaries.
2. Modelwright Phase 35: generated-model workflow summaries and provider diagnostics.
3. Modelwright Phase 36: compact validation evidence extraction.
4. FABLE Pyculator Phase 18: output-ref strategy comparison workflows.
5. FreshForge Phase 8: run matrices and scenario-grid workflow expansion.
6. FABLE Pyculator Phase 19: FreshForge-backed scenario-bundle orchestration.
7. FABLE Pyculator Phase 20: opt-in benchmark workflow upgrade.

## Functional Expansion Watchlist

FABLE Pyculator:

- Output-ref strategy comparison records and examples.
- FreshForge-backed scenario-bundle orchestration.
- Editable scenario-definition parameter surface.
- Benchmark workflow upgrade using sanitized compact evidence.

Modelwright:

- Stable generated-model workflow summaries.
- Better compact failure diagnostics for inference/generation/evaluation.
- Generic compact validation evidence extraction.
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
