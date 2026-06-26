# FABLE Pyculator

FABLE Pyculator is a FABLE Calculator-specific notebook layer built on top of
Modelwright-generated Python models.

The goal is to keep Modelwright generic while collecting FABLE-C conventions in one public package:

- discover likely FABLE scenario input controls from workbook structure;
- declare those controls as named scenario parameters;
- expose a Jupyter-friendly control surface for scenario changes;
- run a generated Modelwright model with the selected scenario inputs;
- render standard FABLE outputs as pandas tables and matplotlib figures.

This repository does not store original FABLE Calculator workbooks, generated Python clones, or raw
validation outputs. Keep those under ignored `tmp/` paths.

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
    discover_selection_controls,
    output_table_frame,
    run_scenario,
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

For real FABLE-C workbooks, discover the high-level selection controls and output tables:

```python
selection_controls = discover_selection_controls("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
output_tables = discover_output_tables("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
spec = FableCalculatorSpec(selection_controls=selection_controls, output_tables=output_tables)

run = run_scenario(generated_model, spec, {"gdp_scen": "SSP1"})
output_table_frame(run, "ghg_resultsghg")
```

The first 2020 notebook loop helper uses ignored local artifacts by default:

```text
tmp/private-workbooks/2020_Open_FABLECalculator.xlsx
tmp/generated-models/fable-2020/generated_fable_2020_model.py
```

```python
from fable_pyculator import run_2020_notebook_loop

result = run_2020_notebook_loop({"gdp_scen": "SSP1"})
result.output_tables["ghg_resultsghg"]
result.headline_frames["ghg_total_co2e"]
result.headline_figures["ghg_total_co2e"]
```

Tracked notebook example:

```text
examples/notebooks/fable-pyculator-2020-loop.ipynb
```

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

## Default Checks

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest
.venv/bin/sphinx-build -b html docs _build/html -W
sha256sum -c benchmarks/fable-calculator/checksums.sha256
```
