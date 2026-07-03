# Post-v0.1.0a4 Workflow Roadmap

This note records the next FABLE Pyculator workflow phases after the matrix workflow automation
alpha.

## Phase 25: Benchmark Matrix Evidence Cookbook

FABLE Pyculator should consume Modelwright's generic matrix generated-model evidence aggregation
rather than duplicating generic generated-model evidence parsing locally.

The intended FABLE-facing workflow is:

1. Compare 2021 output-ref strategies.
2. Write or plan a FreshForge matrix.
3. Optionally run restored local generated-model workflows.
4. Package compact matrix evidence through Modelwright.
5. Render FABLE-facing benchmark evidence summaries without unsupported equivalence claims.

## Phase 26: Editable Scenario-Definition Parameter Surface

After matrix evidence workflows are documented, FABLE Pyculator should expose scenario-definition
table editing and validation as a first-class modelling surface.

This work is intentionally later because it touches workbook semantics more deeply than selection
controls or output-ref strategy matrices.

## Boundaries

- Keep generic generated-model evidence in Modelwright.
- Keep workflow orchestration primitives in FreshForge.
- Keep FABLE workbook semantics and scenario-definition editing in FABLE Pyculator.
- Do not claim arbitrary country-calculator support or new generated-model equivalence without
  explicit validation evidence.
