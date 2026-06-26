"""Notebook scenario execution, table rendering, and plotting helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from numbers import Real
import re
from types import ModuleType
from typing import Any

from modelwright.wrappers import ModelFacade, cell

from fable_pyculator.spec import FableCalculatorSpec, HeadlineSeries, OutputTable


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


def output_table_frame(
    run: ScenarioRun,
    table_name: str,
    column_flavour_tags: str | Sequence[str] | None = None,
    *,
    include_context_columns: bool = True,
) -> Any:
    """Render one declared FABLE output table from a scenario run."""

    table = _output_table(run.spec, table_name)
    return _table_frame(
        table,
        run.values,
        column_flavour_tags=column_flavour_tags,
        include_context_columns=include_context_columns,
    )


def output_tables(
    run: ScenarioRun,
    column_flavour_tags: str | Sequence[str] | None = None,
    *,
    include_context_columns: bool = True,
) -> dict[str, Any]:
    """Render all declared FABLE output tables from a scenario run."""

    return {
        table.name: _table_frame(
            table,
            run.values,
            column_flavour_tags=column_flavour_tags,
            include_context_columns=include_context_columns,
        )
        for table in run.spec.output_tables
    }


def headline_frame(run: ScenarioRun, series_name: str) -> Any:
    """Render one curated FABLE headline series as a tidy pandas DataFrame."""

    series = _headline_series(run.spec, series_name)
    return _headline_frame(series, run.values)


def headline_frames(run: ScenarioRun) -> dict[str, Any]:
    """Render all declared FABLE headline series as tidy pandas DataFrames."""

    return {series.name: _headline_frame(series, run.values) for series in run.spec.headline_series}


def plot_headline(run: ScenarioRun, series_name: str) -> Any:
    """Plot one curated FABLE headline series as a notebook-friendly line chart."""

    plt = _load_matplotlib()
    series = _headline_series(run.spec, series_name)
    frame = _headline_frame(series, run.values)
    figure, axis = plt.subplots(figsize=(8, 4))
    axis.plot(frame["year"], frame["value"], marker="o")
    axis.set_title(series.label)
    axis.set_xlabel("year")
    axis.set_ylabel(series.unit or "value")
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    return figure


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


def _headline_series(spec: FableCalculatorSpec, series_name: str) -> HeadlineSeries:
    for series in spec.headline_series:
        if series.name == series_name or series.label == series_name:
            return series
    raise KeyError(f"unknown headline series {series_name!r}")


def _table_frame(
    table: OutputTable,
    values: Mapping[str, object],
    *,
    column_flavour_tags: str | Sequence[str] | None = None,
    include_context_columns: bool = True,
) -> Any:
    pd = _load_pandas()
    column_indices, requested_tags, matched_tags = _output_table_column_selection(
        table,
        column_flavour_tags,
        include_context_columns=include_context_columns,
    )
    rows = [
        [values.get(row[index]) for index in column_indices]
        for row in table.cell_refs
    ]
    frame = pd.DataFrame(
        rows,
        index=list(table.row_labels),
        columns=[table.column_labels[index] for index in column_indices],
    )
    frame.index.name = "row"
    frame.attrs.update(
        {
            "name": table.name,
            "label": table.label,
            "description": table.description,
            "sheet": table.sheet,
            "range_ref": table.range_ref,
            "selected_column_flavour_tags": requested_tags,
            "matched_column_flavour_tags": matched_tags,
            "include_context_columns": include_context_columns,
            "column_flavour_tags": list(table.column_flavour_tags),
            "raw_column_flavour_tags": list(table.raw_column_flavour_tags),
            "column_flavour_tag_refs": list(table.column_flavour_tag_refs),
            "cell_refs": [list(row) for row in table.cell_refs],
            "selected_cell_refs": [[row[index] for index in column_indices] for row in table.cell_refs],
        }
    )
    return frame


def _output_table_column_selection(
    table: OutputTable,
    column_flavour_tags: str | Sequence[str] | None,
    *,
    include_context_columns: bool,
) -> tuple[tuple[int, ...], tuple[str, ...] | None, tuple[str, ...] | None]:
    requested_tags = _requested_column_flavour_tags(column_flavour_tags)
    if requested_tags is None:
        return tuple(range(len(table.column_labels))), None, None
    if not table.column_flavour_tags:
        raise ValueError(f"output table {table.name!r} does not have column flavour metadata")
    available_tags = set(tag for tag in table.column_flavour_tags if tag is not None)
    matched_tags = _matched_column_flavour_tags(requested_tags, available_tags)
    if not matched_tags:
        raise KeyError(
            f"output table {table.name!r} does not contain column flavour tag pattern(s): "
            f"{', '.join(requested_tags)}"
        )
    selected_tags = set(matched_tags)
    if include_context_columns:
        selected_tags.update(("AUX", "DIRECT"))
    column_indices = tuple(
        index for index, tag in enumerate(table.column_flavour_tags) if tag in selected_tags
    )
    return column_indices, requested_tags, tuple(sorted(matched_tags))


def _requested_column_flavour_tags(column_flavour_tags: str | Sequence[str] | None) -> tuple[str, ...] | None:
    if column_flavour_tags is None:
        return None
    if isinstance(column_flavour_tags, str):
        values = (column_flavour_tags,)
    else:
        values = tuple(column_flavour_tags)
    normalized = tuple(_canonical_column_flavour_tag(value) for value in values)
    unknown = [value for value, tag in zip(values, normalized, strict=True) if tag is None]
    if unknown:
        raise ValueError(f"unknown column flavour tag value(s): {', '.join(str(value) for value in unknown)}")
    return normalized


def _matched_column_flavour_tags(requested_tags: tuple[str, ...], available_tags: set[str]) -> set[str]:
    matched_tags: set[str] = set()
    for requested_tag in requested_tags:
        if requested_tag.endswith("*"):
            prefix = requested_tag.removesuffix("*")
            matched_tags.update(tag for tag in available_tags if tag.startswith(prefix))
        elif requested_tag in {"DATA", "OUTPUT"}:
            matched_tags.update(tag for tag in available_tags if tag.startswith(f"{requested_tag}-"))
        elif requested_tag in available_tags:
            matched_tags.add(requested_tag)
    return matched_tags


def _canonical_column_flavour_tag(value: str) -> str | None:
    text = re.sub(r"\s+", " ", str(value).strip()).upper()
    if not text:
        return None
    if text in {"DATA", "OUTPUT"}:
        return text
    if text.endswith("*"):
        prefix = text.removesuffix("*")
        prefix = re.sub(r"^(DATA|OUTPUT)\s*-\s*", r"\1-", prefix)
        prefix = re.sub(r"^OUTPUT\s+(\d)", r"OUTPUT-\1", prefix)
        prefix = re.sub(r"\s*,\s*", ",", prefix)
        if re.match(r"^(AUX|CALC|DIRECT|DATA(?:-\d*(?:\.\d+)?)?|OUTPUT(?:-\d*(?:,\d+)*)?)$", prefix):
            return f"{prefix}*"
        return None
    text = re.sub(r"^(DATA|OUTPUT)\s*-\s*", r"\1-", text)
    text = re.sub(r"^OUTPUT\s+(\d)", r"OUTPUT-\1", text)
    text = re.sub(r"\s*,\s*", ",", text)
    if re.match(r"^(AUX|CALC|DIRECT|DATA-\d+(?:\.\d+)?|OUTPUT-\d+(?:,\d+)*)$", text):
        return text
    return None


def _headline_frame(series: HeadlineSeries, values: Mapping[str, object]) -> Any:
    pd = _load_pandas()
    rows = [
        {
            "name": series.name,
            "label": series.label,
            "group": series.group,
            "year": point.year,
            "value": _headline_value(series, point.cell_refs, values),
            "unit": series.unit,
            "cell_refs": tuple(point.cell_refs),
            "description": series.description,
        }
        for point in series.points
    ]
    frame = pd.DataFrame(
        rows,
        columns=["name", "label", "group", "year", "value", "unit", "cell_refs", "description"],
    )
    frame.attrs.update(
        {
            "name": series.name,
            "label": series.label,
            "group": series.group,
            "sheet": series.sheet,
            "table_name": series.table_name,
            "unit": series.unit,
            "aggregation": series.aggregation,
            "description": series.description,
        }
    )
    return frame


def _headline_value(series: HeadlineSeries, cell_refs: tuple[str, ...], values: Mapping[str, object]) -> object:
    point_values = [values.get(cell_ref) for cell_ref in cell_refs]
    if series.aggregation == "value":
        return point_values[0] if point_values else None
    if series.aggregation == "sum":
        if all(isinstance(value, Real) and not isinstance(value, bool) for value in point_values):
            return sum(point_values)
        return None
    raise ValueError(f"unsupported headline aggregation {series.aggregation!r}")


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
