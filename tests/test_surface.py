from __future__ import annotations

from fable_pyculator import (
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    OutputIndicator,
    OutputTable,
    ScenarioParameter,
    headline_frame,
    headline_frames,
    output_table_frame,
    outputs_frame,
    plot_headline,
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


def test_headline_frame_renders_value_and_sum_series() -> None:
    spec = FableCalculatorSpec(
        headline_series=[
            HeadlineSeries(
                name="food_total_kcal_feas",
                label="Feasible total kilocalorie consumption",
                group="FOOD",
                sheet="FOOD",
                table_name="Total_results_diets",
                points=[
                    HeadlinePoint(year=2030, cell_refs=["FOOD!C2"]),
                    HeadlinePoint(year=2050, cell_refs=["FOOD!C3"]),
                ],
                unit="kcal/cap/day",
            ),
            HeadlineSeries(
                name="water_total_footprint",
                label="Total water footprint",
                group="WATER",
                sheet="WATER",
                table_name="TotalResultsWF",
                points=[HeadlinePoint(year=2030, cell_refs=["WATER!C2", "WATER!D2", "WATER!E2"])],
                aggregation="sum",
            ),
        ]
    )
    run = run_scenario(
        lambda inputs=None: {
            "FOOD!C2": 2500,
            "FOOD!C3": 2600,
            "WATER!C2": 1,
            "WATER!D2": 2,
            "WATER!E2": 3,
        },
        spec,
    )

    food_frame = headline_frame(run, "food_total_kcal_feas")
    all_frames = headline_frames(run)
    water_frame = all_frames["water_total_footprint"]

    assert list(food_frame["year"]) == [2030, 2050]
    assert list(food_frame["value"]) == [2500, 2600]
    assert water_frame.loc[0, "value"] == 6
    assert water_frame.attrs["aggregation"] == "sum"


def test_plot_headline_returns_line_figure() -> None:
    spec = FableCalculatorSpec(
        headline_series=[
            HeadlineSeries(
                name="ghg_total_co2e",
                label="Total GHG emissions",
                group="GHG",
                sheet="GHG",
                table_name="ResultsGHG",
                points=[
                    HeadlinePoint(year=2030, cell_refs=["GHG!B2"]),
                    HeadlinePoint(year=2050, cell_refs=["GHG!B3"]),
                ],
            )
        ]
    )
    run = run_scenario(lambda inputs=None: {"GHG!B2": 42, "GHG!B3": 30}, spec)

    figure = plot_headline(run, "ghg_total_co2e")

    assert figure.axes[0].get_title() == "Total GHG emissions"
    assert len(figure.axes[0].lines) == 1
    figure.clf()
