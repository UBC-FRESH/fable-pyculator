"""FABLE Calculator-specific notebook helpers for Modelwright-generated models."""

from fable_pyculator.discovery import (
    curate_default_headline_series,
    discover_output_tables,
    discover_scenario_parameters,
    discover_selection_controls,
)
from fable_pyculator.spec import (
    FABLE_OUTPUT_SURFACE_SHEETS,
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    OutputIndicator,
    OutputTable,
    ScenarioParameter,
    SelectionControl,
    SelectionOption,
)
from fable_pyculator.controls import ScenarioControlSurface
from fable_pyculator.surface import (
    ScenarioRun,
    headline_frame,
    headline_frames,
    output_table_frame,
    output_tables,
    outputs_frame,
    plot_headline,
    plot_outputs,
    run_scenario,
    scenario_frame,
)

__all__ = [
    "FableCalculatorSpec",
    "FABLE_OUTPUT_SURFACE_SHEETS",
    "HeadlinePoint",
    "HeadlineSeries",
    "OutputIndicator",
    "OutputTable",
    "ScenarioControlSurface",
    "ScenarioParameter",
    "ScenarioRun",
    "SelectionControl",
    "SelectionOption",
    "curate_default_headline_series",
    "discover_output_tables",
    "discover_scenario_parameters",
    "discover_selection_controls",
    "headline_frame",
    "headline_frames",
    "output_table_frame",
    "output_tables",
    "outputs_frame",
    "plot_headline",
    "plot_outputs",
    "run_scenario",
    "scenario_frame",
]
