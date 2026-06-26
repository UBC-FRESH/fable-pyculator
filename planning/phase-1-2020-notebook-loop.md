# Phase 1 2020 Notebook Loop

Date: 2026-06-26

## Purpose

P1.3 creates the first reusable notebook loop for the 2020 FABLE-C benchmark: build the workbook
spec, load a Modelwright-generated model, apply high-level selection-control overrides, and return
notebook-friendly output tables plus curated headline frames and figures.

## Local Artifacts

The loop references ignored local artifacts by default:

- `tmp/private-workbooks/2020_Open_FABLECalculator.xlsx`
- `tmp/generated-models/fable-2020/generated_fable_2020_model.py`

The workbook checksums are tracked in `benchmarks/fable-calculator/checksums.sha256`. The generated
model is intentionally not tracked here; it should be restored or generated into `tmp/` before
running the real benchmark loop.

## Public API

- `build_2020_notebook_spec(...)` discovers selection controls, output tables, and curated headline
  series from the 2020 workbook.
- `load_generated_model(...)` imports a generated Python module from an ignored local path.
- `run_notebook_loop(...)` applies named selections, runs the generated model, and renders selected
  output tables and headline series.
- `run_2020_notebook_loop(...)` combines the three steps using the default ignored 2020 paths.

## Example Notebook

The tracked example notebook is:

- `examples/notebooks/fable-pyculator-2020-loop.ipynb`

It is committed without cell outputs and raises an explicit `FileNotFoundError` if the ignored
workbook or generated model has not been restored locally.

## Verification Command

```bash
.venv/bin/python -m pytest tests/test_notebook.py
```

## Findings

- Selection-control overrides are applied through `FableCalculatorSpec.input_mapping`, so each
  selected dropdown value expands to workbook marker-cell inputs.
- Output tables and headline frames render from the generated model's returned cell-value mapping.
- Matplotlib figures can be suppressed with `include_figures=False` for tests, headless scripts, or
  notebook cells that only need DataFrames.
- Missing generated model paths fail explicitly with `FileNotFoundError` rather than silently
  falling back to a tracked artifact.

## Implication

The package now has a coherent first notebook loop shape without committing the generated 2020 model.
P1.4 should turn this into fuller user-guide prose and record which real 2020 generated-model run was
used as validation evidence.
