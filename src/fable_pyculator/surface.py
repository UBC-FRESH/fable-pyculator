"""Notebook scenario execution, table rendering, and plotting helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import ModuleType
from typing import Any

from modelwright.wrappers import ModelFacade, cell

from fable_pyculator.spec import FableCalculatorSpec, OutputTable


@dataclass(frozen=True)
class ScenarioRun:
    """Result from running one FABLE Pyculator scenario."""

    spec: FableCalculatorSpec
    scenario_name: str
    inputs: dict[str, object]
    values: dict[str, object]

    @property
    def outputs(self) -> dict[str, object]:
        return {output.name: self.values.get(output.cell_ref) for output in self.spec.outputs}


def run_scenario(
    generated_model: ModuleType | object,
    spec: FableCalculatorSpec,
    values: Mapping[str, object] | None = None,
    *,
    name: str = "scenario",
) -> ScenarioRun:
    """Run a generated Modelwright model using FABLE parameter names."""

    facade = _facade(generated_model, spec)
    scenario_inputs = spec.input_mapping(dict(values or {}))
    scenario = facade.scenario(name=name, inputs=scenario_inputs)
    calculated = facade.calculate(scenario)
    return ScenarioRun(
        spec=spec,
        scenario_name=name,
        inputs=scenario.inputs,
        values={**scenario.inputs, **calculated},
    )


def scenario_frame(run: ScenarioRun) -> Any:
    """Render scenario inputs as a pandas DataFrame."""

    pd = _load_pandas()
    rows = []
    parameters_by_ref = {parameter.cell_ref: parameter for parameter in run.spec.parameters}
    for cell_ref, value in run.inputs.items():
        parameter = parameters_by_ref.get(cell_ref)
        rows.append(
            {
                "scenario": run.scenario_name,
                "name": parameter.name if parameter else cell_ref,
                "label": parameter.label if parameter else None,
                "cell_ref": cell_ref,
                "value": value,
                "unit": parameter.unit if parameter else None,
            }
        )
    return pd.DataFrame(rows, columns=["scenario", "name", "label", "cell_ref", "value", "unit"])


def outputs_frame(run: ScenarioRun) -> Any:
    """Render declared FABLE output indicators as a pandas DataFrame."""

    pd = _load_pandas()
    rows = [
        {
            "name": output.name,
            "label": output.label,
            "group": output.group,
            "cell_ref": output.cell_ref,
            "value": run.values.get(output.cell_ref),
            "unit": output.unit,
            "description": output.description,
        }
        for output in run.spec.outputs
    ]
    return pd.DataFrame(rows, columns=["name", "label", "group", "cell_ref", "value", "unit", "description"])


def output_table_frame(run: ScenarioRun, table_name: str) -> Any:
    """Render one declared FABLE output table from a scenario run."""

    table = _output_table(run.spec, table_name)
    return _table_frame(table, run.values)


def output_tables(run: ScenarioRun) -> dict[str, Any]:
    """Render all declared FABLE output tables from a scenario run."""

    return {table.name: _table_frame(table, run.values) for table in run.spec.output_tables}


def plot_outputs(run: ScenarioRun, *, group: str | None = None) -> Any:
    """Plot numeric output indicators as a simple horizontal bar chart."""

    plt = _load_matplotlib()
    frame = outputs_frame(run)
    if group is not None:
        frame = frame[frame["group"] == group]
    numeric = frame[frame["value"].map(lambda value: isinstance(value, int | float) and not isinstance(value, bool))]
    figure, axis = plt.subplots(figsize=(8, max(2.5, 0.35 * len(numeric))))
    axis.barh(numeric["label"], numeric["value"])
    axis.set_xlabel("value")
    axis.set_title(run.scenario_name)
    figure.tight_layout()
    return figure


def _facade(generated_model: ModuleType | object, spec: FableCalculatorSpec) -> ModelFacade:
    return ModelFacade(
        generated_model,
        cells=[
            *[
                cell(parameter.cell_ref, name=parameter.name, label=parameter.label, role="input", unit=parameter.unit)
                for parameter in spec.parameters
            ],
            *[
                cell(output.cell_ref, name=output.name, label=output.label, role="output", unit=output.unit)
                for output in spec.outputs
            ],
        ],
    )


def _output_table(spec: FableCalculatorSpec, table_name: str) -> OutputTable:
    for table in spec.output_tables:
        if table.name == table_name or table.label == table_name:
            return table
    raise KeyError(f"unknown output table {table_name!r}")


def _table_frame(table: OutputTable, values: Mapping[str, object]) -> Any:
    pd = _load_pandas()
    rows = [
        [values.get(cell_ref) for cell_ref in row]
        for row in table.cell_refs
    ]
    frame = pd.DataFrame(rows, index=list(table.row_labels), columns=list(table.column_labels))
    frame.index.name = "row"
    frame.attrs.update(
        {
            "name": table.name,
            "label": table.label,
            "description": table.description,
            "sheet": table.sheet,
            "range_ref": table.range_ref,
            "cell_refs": [list(row) for row in table.cell_refs],
        }
    )
    return frame


def _load_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as error:
        raise RuntimeError("Install fable-pyculator with the notebook extra to use pandas helpers.") from error
    return pd


def _load_matplotlib() -> Any:
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise RuntimeError("Install fable-pyculator[notebook] to plot outputs.") from error
    return plt
