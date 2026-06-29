"""High-level notebook loop helpers for FABLE-C generated models.

This module packages version-specific FABLE-C notebook workflows: build a workbook-derived spec,
import a locally generated Modelwright Python model, apply scenario selections, and render the
discovered output tables/headline series. The helpers assume local artifacts are restored under
ignored ``tmp/`` paths.

The workbook and generated model must come from the same FABLE Calculator version. A 2021 workbook
should not be paired with the 2020 generated model, because the wrapper can render outputs only as
accurately as the generated calculation artifact it wraps.
"""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from fable_pyculator.discovery import (
    curate_default_headline_series,
    discover_output_tables,
    discover_scenario_definition_tables,
    discover_selection_controls,
)
from fable_pyculator.spec import FableCalculatorSpec
from fable_pyculator.surface import (
    ScenarioRun,
    headline_frame,
    output_table_frame,
    plot_headline,
    run_scenario,
)


DEFAULT_2020_WORKBOOK_PATH = Path("tmp/private-workbooks/2020_Open_FABLECalculator.xlsx")
DEFAULT_2020_GENERATED_MODEL_PATH = Path("tmp/generated-models/fable-2020/generated_fable_2020_model.py")
DEFAULT_2021_WORKBOOK_PATH = Path("tmp/private-workbooks/2021_Open_FABLECalculator.xlsx")
DEFAULT_2021_GENERATED_MODEL_PATH = Path("tmp/generated-models/fable-2021/generated_fable_2021_model.py")
DEFAULT_OUTPUT_TABLES = None
DEFAULT_HEADLINE_SERIES = None


@dataclass(frozen=True)
class NotebookLoopResult:
    """Rendered notebook artifacts from one FABLE Pyculator scenario run."""

    run: ScenarioRun
    output_tables: dict[str, Any]
    headline_frames: dict[str, Any]
    headline_figures: dict[str, Any]


def load_generated_model(
    model_path: str | Path = DEFAULT_2020_GENERATED_MODEL_PATH,
    *,
    module_name: str = "fable_pyculator_generated_fable_2020",
) -> ModuleType:
    """Load an ignored Modelwright-generated Python model from a local path.

    The loaded module must expose the generated model interface expected by
    :class:`modelwright.wrappers.ModelFacade`, usually a ``calculate`` function.
    """

    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"generated model not found: {path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load generated model from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_notebook_spec(
    workbook_path: str | Path,
    *,
    workbook_id: str,
) -> FableCalculatorSpec:
    """Build a notebook spec from a FABLE-C workbook structure.

    This helper discovers wrapper metadata only. It does not generate Modelwright calculation code
    and it does not validate that a generated model artifact matches the workbook.
    """

    path = Path(workbook_path)
    return FableCalculatorSpec(
        selection_controls=discover_selection_controls(path),
        scenario_definition_tables=discover_scenario_definition_tables(path),
        output_tables=discover_output_tables(path),
        headline_series=curate_default_headline_series(path),
        workbook_id=workbook_id,
        provenance=str(path),
    )


def build_2020_notebook_spec(
    workbook_path: str | Path = DEFAULT_2020_WORKBOOK_PATH,
    *,
    workbook_id: str = "fable-c-2020",
) -> FableCalculatorSpec:
    """Build the notebook spec from the public 2020 FABLE-C workbook structure."""

    return build_notebook_spec(workbook_path, workbook_id=workbook_id)


def build_2021_notebook_spec(
    workbook_path: str | Path = DEFAULT_2021_WORKBOOK_PATH,
    *,
    workbook_id: str = "fable-c-2021",
) -> FableCalculatorSpec:
    """Build the notebook spec from the public 2021 FABLE-C workbook structure.

    The 2021 workbook shares the inspected 16-control wrapper structure with 2020, but running the
    loop still requires a matching 2021 Modelwright-generated Python model.
    """

    return build_notebook_spec(workbook_path, workbook_id=workbook_id)


def run_notebook_loop(
    generated_model: ModuleType | object,
    spec: FableCalculatorSpec,
    selections: Mapping[str, object] | None = None,
    *,
    scenario_name: str = "scenario",
    output_table_names: Sequence[str] | None = DEFAULT_OUTPUT_TABLES,
    output_table_column_flavour_tags: str | Sequence[str] | None = None,
    include_context_columns: bool = True,
    headline_series_names: Sequence[str] | None = DEFAULT_HEADLINE_SERIES,
    include_figures: bool = True,
) -> NotebookLoopResult:
    """Run a generated model and render selected FABLE notebook artifacts.

    By default, ``output_table_names=None`` and ``headline_series_names=None`` render every declared
    output table and headline frame from the spec after a single generated-model execution.
    """

    run = run_scenario(generated_model, spec, selections, name=scenario_name)
    selected_output_table_names = _output_table_names(spec, output_table_names)
    selected_headline_series_names = _headline_series_names(spec, headline_series_names)
    tables = {
        table_name: output_table_frame(
            run,
            table_name,
            column_flavour_tags=output_table_column_flavour_tags,
            include_context_columns=include_context_columns,
        )
        for table_name in selected_output_table_names
    }
    headline_tables = {
        series_name: headline_frame(run, series_name)
        for series_name in selected_headline_series_names
    }
    figures = (
        {
            series_name: plot_headline(run, series_name)
            for series_name in selected_headline_series_names
        }
        if include_figures
        else {}
    )
    return NotebookLoopResult(
        run=run,
        output_tables=tables,
        headline_frames=headline_tables,
        headline_figures=figures,
    )


def run_2020_notebook_loop(
    selections: Mapping[str, object] | None = None,
    *,
    workbook_path: str | Path = DEFAULT_2020_WORKBOOK_PATH,
    generated_model_path: str | Path = DEFAULT_2020_GENERATED_MODEL_PATH,
    scenario_name: str = "scenario",
    output_table_names: Sequence[str] | None = DEFAULT_OUTPUT_TABLES,
    output_table_column_flavour_tags: str | Sequence[str] | None = None,
    include_context_columns: bool = True,
    headline_series_names: Sequence[str] | None = DEFAULT_HEADLINE_SERIES,
    include_figures: bool = True,
) -> NotebookLoopResult:
    """Run the default 2020 FABLE-C notebook loop from ignored local artifacts."""

    spec = build_2020_notebook_spec(workbook_path)
    generated_model = load_generated_model(generated_model_path, module_name="fable_pyculator_generated_fable_2020")
    return run_notebook_loop(
        generated_model,
        spec,
        selections,
        scenario_name=scenario_name,
        output_table_names=output_table_names,
        output_table_column_flavour_tags=output_table_column_flavour_tags,
        include_context_columns=include_context_columns,
        headline_series_names=headline_series_names,
        include_figures=include_figures,
    )


def run_2021_notebook_loop(
    selections: Mapping[str, object] | None = None,
    *,
    workbook_path: str | Path = DEFAULT_2021_WORKBOOK_PATH,
    generated_model_path: str | Path = DEFAULT_2021_GENERATED_MODEL_PATH,
    scenario_name: str = "scenario",
    output_table_names: Sequence[str] | None = DEFAULT_OUTPUT_TABLES,
    output_table_column_flavour_tags: str | Sequence[str] | None = None,
    include_context_columns: bool = True,
    headline_series_names: Sequence[str] | None = DEFAULT_HEADLINE_SERIES,
    include_figures: bool = True,
) -> NotebookLoopResult:
    """Run the default 2021 FABLE-C notebook loop from ignored local artifacts.

    This helper intentionally points to a separate 2021 generated-model path. It never falls back to
    the tracked compressed 2020 generated model in the sibling Modelwright repository.
    """

    spec = build_2021_notebook_spec(workbook_path)
    generated_model = load_generated_model(generated_model_path, module_name="fable_pyculator_generated_fable_2021")
    return run_notebook_loop(
        generated_model,
        spec,
        selections,
        scenario_name=scenario_name,
        output_table_names=output_table_names,
        output_table_column_flavour_tags=output_table_column_flavour_tags,
        include_context_columns=include_context_columns,
        headline_series_names=headline_series_names,
        include_figures=include_figures,
    )


def _output_table_names(spec: FableCalculatorSpec, output_table_names: Sequence[str] | None) -> tuple[str, ...]:
    if output_table_names is None:
        return tuple(table.name for table in spec.output_tables)
    return tuple(output_table_names)


def _headline_series_names(spec: FableCalculatorSpec, headline_series_names: Sequence[str] | None) -> tuple[str, ...]:
    if headline_series_names is None:
        return tuple(series.name for series in spec.headline_series)
    return tuple(headline_series_names)
