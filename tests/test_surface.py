from __future__ import annotations

from fable_pyculator import (
    FableCalculatorSpec,
    OutputIndicator,
    OutputTable,
    ScenarioParameter,
    output_table_frame,
    outputs_frame,
    run_scenario,
)


def calculate(inputs=None):
    inputs = inputs or {}
    ambition = inputs.get("SCENARIOS selection!D20", 1)
    return {
        "SCENARIOS selection!D20": ambition,
        "SCENARIOS selection!D22": ambition * 10,
    }


def test_run_scenario_maps_parameter_values_and_outputs() -> None:
    spec = FableCalculatorSpec(
        parameters=[
            ScenarioParameter(name="ambition", label="Ambition", cell_ref="SCENARIOS selection!D20"),
        ],
        outputs=[
            OutputIndicator(name="ghg", label="GHG", cell_ref="SCENARIOS selection!D22", unit="MtCO2e"),
        ],
    )

    run = run_scenario(calculate, spec, {"ambition": 3}, name="high")

    assert run.inputs == {"SCENARIOS selection!D20": 3}
    assert run.outputs == {"ghg": 30}
    frame = outputs_frame(run)
    assert frame.loc[0, "name"] == "ghg"
    assert frame.loc[0, "value"] == 30


def test_output_table_frame_renders_declared_table_values() -> None:
    spec = FableCalculatorSpec(
        output_tables=[
            OutputTable(
                name="food_results",
                label="Results_Diets",
                sheet="FOOD",
                range_ref="A1:B2",
                cell_refs=(("FOOD!A2", "FOOD!B2"),),
                row_labels=("Calories",),
                column_labels=("Metric", "2030"),
            )
        ]
    )
    run = run_scenario(lambda inputs=None: {"FOOD!A2": "Calories", "FOOD!B2": 2600}, spec)

    frame = output_table_frame(run, "food_results")

    assert frame.loc["Calories", "Metric"] == "Calories"
    assert frame.loc["Calories", "2030"] == 2600
    assert frame.attrs["sheet"] == "FOOD"
