"""FABLE Calculator-specific notebook helpers for Modelwright-generated models."""

from fable_pyculator.discovery import discover_output_tables, discover_scenario_parameters, discover_selection_controls
from fable_pyculator.spec import (
    FABLE_OUTPUT_SURFACE_SHEETS,
    FableCalculatorSpec,
    OutputIndicator,
    OutputTable,
    ScenarioParameter,
    SelectionControl,
    SelectionOption,
)
from fable_pyculator.controls import ScenarioControlSurface
from fable_pyculator.surface import (
    ScenarioRun,
    output_table_frame,
    output_tables,
    outputs_frame,
    plot_outputs,
    run_scenario,
    scenario_frame,
)

__all__ = [
    "FableCalculatorSpec",
    "FABLE_OUTPUT_SURFACE_SHEETS",
    "OutputIndicator",
    "OutputTable",
    "ScenarioControlSurface",
    "ScenarioParameter",
    "ScenarioRun",
    "SelectionControl",
    "SelectionOption",
    "discover_output_tables",
    "discover_scenario_parameters",
    "discover_selection_controls",
    "output_table_frame",
    "output_tables",
    "outputs_frame",
    "plot_outputs",
    "run_scenario",
    "scenario_frame",
]
