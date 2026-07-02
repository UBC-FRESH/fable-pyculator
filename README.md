# FABLE Pyculator

FABLE Pyculator is a FABLE Calculator-specific notebook layer built on top of
Modelwright-generated Python models.

The goal is to keep Modelwright generic while collecting FABLE-C conventions in one public package:

- discover likely FABLE scenario input controls from workbook structure;
- declare those controls as named scenario parameters;
- expose a Jupyter-friendly control surface for scenario changes;
- run a generated Modelwright model with the selected scenario inputs;
- render standard FABLE outputs as pandas tables and matplotlib figures.

This repository does not store original FABLE Calculator workbooks, decompressed generated Python
clones, or raw validation outputs. Keep those under ignored `tmp/` paths. The public 2021 generated
model is the one explicit exception: it is tracked as a compressed, validation-backed artifact under
`examples/fable_2021/`.

## Development Workflow

This project uses the same agent-assisted workflow as Modelwright:

- read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before project-shaping work;
- keep the current plan in `ROADMAP.md`;
- record completed deliverables in `CHANGE_LOG.md`;
- use `planning/` for focused investigations and contracts;
- keep source workbooks, generated models, extracts, logs, and validation reports under ignored
  `tmp/`;
- once the public GitHub repo and `gh` access exist, map roadmap phases to GitHub parent issues and
  roadmap tasks to child issues;
- close every phase through a PR back to `main`, with Sphinx docs rebuilt in CI and deployed to
  GitHub Pages after merge.

The local remote is expected to be:

```text
https://github.com/UBC-FRESH/fable-pyculator.git
```

## Install For Development

Recommended VSCode/Jupyter setup from the `fable-pyculator` repo root:

```bash
scripts/bootstrap_dev_env.sh
```

Then select this interpreter as the VSCode notebook kernel:

```text
.venv/bin/python
```

Manual equivalent:

```bash
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev,notebook,docs]'
```

## Download FABLE Calculators

The current Modelwright benchmark metadata points to this public FABLE Calculator Dropbox folder:

```text
https://www.dropbox.com/scl/fo/ndgldfnq81v794mm8yebe/ADusMz23xtmYKDXoEkiNtJM?rlkey=d87qhjf5zd0pcowd5pfl5qdu7&st=qijm4tta&e=2&dl=0
```

In this checkout, the three public FABLE-C workbooks are stored under `tmp/private-workbooks/`.
They are ignored local benchmark artifacts. Verify them with:

```bash
sha256sum -c benchmarks/fable-calculator/checksums.sha256
```

The public 2020 FABLE Calculator documentation PDF is tracked under `reference/fable-calculator/`.

The core FABLE-C output data surfaces are the consecutive workbook sheets `FOOD`, `PRODUCTION`,
`TRADE`, `BIODIVERSITY`, `LAND`, `GHG`, and `WATER`.

## Early Notebook Shape

```python
from fable_pyculator import (
    FableCalculatorSpec,
    OutputIndicator,
    ScenarioControlSurface,
    ScenarioParameter,
    discover_output_tables,
    discover_scenario_definition_tables,
    discover_selection_controls,
    output_table_frame,
    run_scenario,
    scenario_definition_table_frame,
    scenario_definition_tables_for_location,
)

spec = FableCalculatorSpec(
    parameters=[
        ScenarioParameter(name="ambition", label="Scenario ambition", cell_ref="SCENARIOS selection!D20"),
    ],
    outputs=[
        OutputIndicator(name="ghg", label="GHG emissions", cell_ref="SCENARIOS selection!D22", unit="MtCO2e"),
    ],
)

controls = ScenarioControlSurface(spec)
controls

result = run_scenario(generated_model, spec, controls.values())
result.outputs
```

For real FABLE-C workbooks, discover the high-level selection controls, scenario-definition tables,
and output tables:

```python
selection_controls = discover_selection_controls("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
definition_tables = discover_scenario_definition_tables("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
output_tables = discover_output_tables("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
spec = FableCalculatorSpec(
    selection_controls=selection_controls,
    scenario_definition_tables=definition_tables,
    output_tables=output_tables,
)

scenario_definition_table_frame(spec, "DietTarget")
scenario_definition_tables_for_location(spec, "S.3")

run = run_scenario(generated_model, spec, {"gdp_scen": "SSP1"})
output_table_frame(run, "ghg_resultsghg")
output_table_frame(run, "ghg_resultsghg", column_flavour_tags="OUTPUT-8")
output_table_frame(run, "ghg_resultsghg", column_flavour_tags="DATA")
output_table_frame(run, "ghg_resultsghg", column_flavour_tags="OUTPUT-*")
```

The first 2020 notebook loop helper uses ignored local artifacts by default:

```text
tmp/private-workbooks/2020_Open_FABLECalculator.xlsx
tmp/generated-models/fable-2020/generated_fable_2020_model.py
```

```python
from fable_pyculator import run_2020_notebook_loop

result = run_2020_notebook_loop({"gdp_scen": "SSP1"})
result.output_tables.keys()
result.output_tables["ghg_resultsghg"]
result.headline_frames["ghg_total_co2e"]
result.headline_figures["ghg_total_co2e"]
```

The 2021 helper uses separate ignored local artifacts and does not fall back to the 2020 generated
model:

```text
tmp/private-workbooks/2021_Open_FABLECalculator.xlsx
tmp/generated-models/fable-2021/generated_fable_2021_model.py
```

```python
from fable_pyculator import run_2021_notebook_loop

result = run_2021_notebook_loop({"gdp_scen": "SSP1"}, include_figures=False)
```

The 2021 example notebook can materialize
`examples/fable_2021/generated_fable_2021_model.py.xz` into the ignored generated-model path above.
Phase 8 validated that generated model against the public 2021 workbook with 281,922 comparable
outputs, 281,922 matches, and 0 mismatches.

To rebuild a generated model from a local source workbook with the FreshForge/Modelwright workflow,
start with plan-only preparation. The generic command defaults to the public 2021 path convention:

```bash
.venv/bin/python scripts/build_fable_model.py
```

To compare output-ref boundaries before choosing a rebuild target, run:

```bash
.venv/bin/python scripts/compare_fable_output_ref_strategies.py --json
```

Use `--workbook-version 2020` or `--workbook-version 2021` to choose a workbook version by
convention, and use `--output-ref-strategy headline-only`, `--table-name ghg_resultsghg`, or
`--column-flavour-tag OUTPUT-8` to compare smaller generated-model boundaries. The older
`scripts/build_fable_2021_model.py` command remains a 2021 shortcut. Use `--run` only after
reviewing the generated `tmp/generated-models/fable-YYYY/` workflow artifacts.

FABLE Pyculator discovers wrapper metadata and renders notebook surfaces. It does not currently
generate Modelwright `contract.json`, `expressions.json`, or `constants.json` files from a FABLE
workbook. See `docs/guides/generated-model-artifacts.rst` for the generated-model artifact boundary
and the 2020/2021 path contract.

By default the loop renders every discovered output table and every curated headline frame from the
single generated-model run. Pass `output_table_names` or `headline_series_names` only when you want a
smaller rendered subset.

To repeat that loop across named selection-control scenarios, use a JSON or YAML scenario bundle:

```bash
.venv/bin/python scripts/run_fable_scenario_bundle.py \
  --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
  --dry-run \
  --json
```

Remove `--dry-run` after the matching workbook and generated model are restored locally. Bundle
outputs are written under ignored `tmp/scenario-runs/fable-YYYY/<bundle-id>/` paths. See
`docs/guides/scenario-bundles.rst` for the bundle schema and artifact layout.

When repeated bundle runs need explicit graph planning, namespace-isolated artifacts, and a compact
FreshForge run summary, use the FreshForge-backed path:

```bash
.venv/bin/python scripts/run_fable_scenario_bundle.py \
  --bundle examples/scenario-bundles/fable_2021_ssp_demo.yaml \
  --freshforge-plan \
  --json
```

Switch to `--freshforge-run --run-namespace scenario/demo` only after the plan and local artifacts
look right. See `docs/guides/scenario-bundle-freshforge-orchestration.rst`.

To package compact validation evidence from existing local generated-model artifacts, use:

```bash
.venv/bin/python scripts/package_fable_validation_evidence.py --json
```

This writes sanitized summaries under `tmp/validation-evidence/fable-YYYY/`. Missing local artifacts
produce a skipped summary by default; use `--require-artifacts` when absence should fail. See
`docs/guides/validation-evidence-packaging.rst` for the evidence status and claim boundary.

Tracked notebook example:

```text
examples/notebooks/fable-pyculator-2020-loop.ipynb
examples/notebooks/fable-pyculator-2021-loop.ipynb
examples/notebooks/fable-pyculator-2021-freshforge-build-plan.ipynb
examples/notebooks/fable-pyculator-2021-freshforge-run.ipynb
```

The 2020 notebook is intentionally committed after a successful 2020 benchmark run so GitHub can
render the example tables and figure directly in the browser. The 2021 notebook is a runnable
artifact-wiring template: it still requires the ignored local workbook, but it can restore the
validated generated model from the tracked compressed 2021 archive. The FreshForge notebooks show
how to rebuild that model from the source workbook: one notebook plans the graph, and the run
companion gates the full FreshForge/Modelwright build behind `RUN_FRESHFORGE = False`.

In VSCode, point the notebook kernel at the `.venv` created in the `fable-pyculator` repo root.
The notebook setup cell prints the active environment prefix and warns if the selected kernel does
not appear to be that repo-local `.venv`.

The Sphinx guide expands this into a full workflow under
`docs/guides/2020-notebook-workflow.rst`, with validation boundaries recorded in
`docs/guides/validation-scope.rst`.

`fable-pyculator` is pre-release. The current alpha line is `0.1.0a2`; alpha releases must not be
described as stable public API compatibility, full editable scenario-definition widgets, production
readiness, or arbitrary country-calculator support. Generated-model equivalence claims are limited
to the exact 2020 and 2021 public FABLE-C validation evidence recorded in the docs. The `0.1.0a2`
line adds the current FABLE workflow automation surface: FreshForge planning/run examples,
version-general build helpers, scenario bundles, and compact validation-evidence packaging.

The public API is intentionally small while the FABLE-specific conventions are being discovered from
real country calculators.

## Build Docs

```bash
.venv/bin/python -m pip install -e '.[dev,notebook,docs]'
.venv/bin/sphinx-build -b html docs _build/html -W
```

The `Docs Pages` GitHub Actions workflow builds Sphinx docs on pull requests to `main` and deploys
the built HTML to GitHub Pages after merges to `main`.

GitHub Pages URL:

```text
https://ubc-fresh.github.io/fable-pyculator/
```

See `docs/guides/release-deployment.rst` for the release and deployment runbook.

## Release Checks

Build and inspect release artifacts locally:

```bash
scripts/check_release_artifacts.sh
```

Release checks write build outputs under ignored `tmp/release-checks/`.

## Default Checks

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest
.venv/bin/sphinx-build -b html docs _build/html -W
.venv/bin/python scripts/verify_docs_theme.py _build/html
scripts/check_release_artifacts.sh
sha256sum -c benchmarks/fable-calculator/checksums.sha256
```
