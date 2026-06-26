from __future__ import annotations

import pytest

from fable_pyculator import (
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    OutputIndicator,
    OutputTable,
    ScenarioDefinitionTable,
    ScenarioParameter,
    headline_frame,
    headline_frames,
    output_table_frame,
    outputs_frame,
    plot_headline,
    run_scenario,
    scenario_definition_table_frame,
    scenario_definition_tables,
    scenario_definition_tables_for_location,
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


def test_output_table_frame_filters_by_column_flavour_tags() -> None:
    spec = FableCalculatorSpec(
        output_tables=[
            OutputTable(
                name="ghg_results",
                label="ResultsGHG",
                sheet="GHG",
                range_ref="A2:D3",
                cell_refs=(("GHG!A3", "GHG!B3", "GHG!C3", "GHG!D3"),),
                row_labels=("2030",),
                column_labels=("Year", "Hist", "TotalCO2e", "LandSeq"),
                column_flavour_tags=("DIRECT", "DATA-5", "OUTPUT-8", "CALC"),
                raw_column_flavour_tags=("DIRECT", "DATA-5", "OUTPUT - 8", "CALC"),
                column_flavour_tag_refs=("GHG!A1", "GHG!B1", "GHG!C1", "GHG!D1"),
            )
        ]
    )
    run = run_scenario(
        lambda inputs=None: {
            "GHG!A3": 2030,
            "GHG!B3": 12,
            "GHG!C3": 42,
            "GHG!D3": -2,
        },
        spec,
    )

    frame = output_table_frame(run, "ghg_results", column_flavour_tags="OUTPUT - 8")
    exact_frame = output_table_frame(
        run,
        "ghg_results",
        column_flavour_tags="OUTPUT-8",
        include_context_columns=False,
    )
    multi_tag_frame = output_table_frame(
        run,
        "ghg_results",
        column_flavour_tags=("DATA-5", "CALC"),
    )

    assert list(frame.columns) == ["Year", "TotalCO2e"]
    assert frame.loc["2030", "TotalCO2e"] == 42
    assert list(exact_frame.columns) == ["TotalCO2e"]
    assert list(multi_tag_frame.columns) == ["Year", "Hist", "LandSeq"]
    assert frame.attrs["selected_column_flavour_tags"] == ("OUTPUT-8",)
    assert frame.attrs["matched_column_flavour_tags"] == ("OUTPUT-8",)
    assert frame.attrs["column_flavour_tags"] == ["DIRECT", "DATA-5", "OUTPUT-8", "CALC"]
    assert frame.attrs["raw_column_flavour_tags"] == ["DIRECT", "DATA-5", "OUTPUT - 8", "CALC"]
    assert frame.attrs["selected_cell_refs"] == [["GHG!A3", "GHG!C3"]]


def test_output_table_frame_filters_by_prefix_and_wildcard_column_flavour_tags() -> None:
    spec = FableCalculatorSpec(
        output_tables=[
            OutputTable(
                name="mixed_results",
                label="MixedResults",
                sheet="GHG",
                range_ref="A2:F3",
                cell_refs=(("GHG!A3", "GHG!B3", "GHG!C3", "GHG!D3", "GHG!E3", "GHG!F3"),),
                row_labels=("2030",),
                column_labels=("Year", "FAO", "Scenario", "TotalCO2e", "LandSeq", "Water"),
                column_flavour_tags=("DIRECT", "DATA-5", "DATA-9", "OUTPUT-8", "CALC", "OUTPUT-9"),
            )
        ]
    )
    run = run_scenario(
        lambda inputs=None: {
            "GHG!A3": 2030,
            "GHG!B3": 12,
            "GHG!C3": 15,
            "GHG!D3": 42,
            "GHG!E3": -2,
            "GHG!F3": 6,
        },
        spec,
    )

    data_family = output_table_frame(run, "mixed_results", column_flavour_tags="DATA")
    data_wildcard = output_table_frame(run, "mixed_results", column_flavour_tags="DATA*")
    output_wildcard = output_table_frame(
        run,
        "mixed_results",
        column_flavour_tags="OUTPUT-*",
        include_context_columns=False,
    )

    assert list(data_family.columns) == ["Year", "FAO", "Scenario"]
    assert list(data_wildcard.columns) == ["Year", "FAO", "Scenario"]
    assert list(output_wildcard.columns) == ["TotalCO2e", "Water"]
    assert data_family.attrs["selected_column_flavour_tags"] == ("DATA",)
    assert data_family.attrs["matched_column_flavour_tags"] == ("DATA-5", "DATA-9")
    assert data_wildcard.attrs["selected_column_flavour_tags"] == ("DATA*",)
    assert output_wildcard.attrs["selected_column_flavour_tags"] == ("OUTPUT-*",)
    assert output_wildcard.attrs["matched_column_flavour_tags"] == ("OUTPUT-8", "OUTPUT-9")


def test_output_table_frame_reports_missing_or_unknown_column_flavour_tags() -> None:
    missing_metadata_spec = FableCalculatorSpec(
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
    missing_metadata_run = run_scenario(
        lambda inputs=None: {"FOOD!A2": "Calories", "FOOD!B2": 2600},
        missing_metadata_spec,
    )

    with pytest.raises(ValueError, match="does not have column flavour metadata"):
        output_table_frame(missing_metadata_run, "food_results", column_flavour_tags="OUTPUT-1")

    unknown_tag_spec = FableCalculatorSpec(
        output_tables=[
            OutputTable(
                name="ghg_results",
                label="ResultsGHG",
                sheet="GHG",
                range_ref="A2:B3",
                cell_refs=(("GHG!A3", "GHG!B3"),),
                row_labels=("2030",),
                column_labels=("Year", "TotalCO2e"),
                column_flavour_tags=("DIRECT", "OUTPUT-8"),
            )
        ]
    )
    unknown_tag_run = run_scenario(lambda inputs=None: {"GHG!A3": 2030, "GHG!B3": 42}, unknown_tag_spec)

    with pytest.raises(KeyError, match="OUTPUT-1"):
        output_table_frame(unknown_tag_run, "ghg_results", column_flavour_tags="OUTPUT-1")

    with pytest.raises(KeyError, match="OUTPUT-9"):
        output_table_frame(unknown_tag_run, "ghg_results", column_flavour_tags="OUTPUT-9*")

    with pytest.raises(ValueError, match="SCEN"):
        output_table_frame(unknown_tag_run, "ghg_results", column_flavour_tags="SCEN")


def test_scenario_definition_table_frame_renders_workbook_values() -> None:
    spec = FableCalculatorSpec(
        scenario_definition_tables=[
            ScenarioDefinitionTable(
                name="scenarios_definition_diettarget",
                label="DietTarget",
                sheet="SCENARIOS definition",
                range_ref="A2:C3",
                cell_refs=(
                    (
                        "SCENARIOS definition!A3",
                        "SCENARIOS definition!B3",
                        "SCENARIOS definition!C3",
                    ),
                ),
                row_labels=("Current",),
                column_labels=("DietScen", "PROD_GROUP", "target"),
                values=(("Current", "CEREALS", 2500),),
                column_role_tags=("DIRECT", "SCEN", "DATA-1"),
                raw_column_role_tags=("DIRECT", "SCEN", "DATA - 1"),
                column_role_tag_refs=(
                    "SCENARIOS definition!A1",
                    "SCENARIOS definition!B1",
                    "SCENARIOS definition!C1",
                ),
                scenario_locations=("S.3.C",),
                scenario_location_refs=("SCENARIOS definition!A1",),
            )
        ]
    )

    frame = scenario_definition_table_frame(spec, "DietTarget")
    frames = scenario_definition_tables(spec)

    assert frame.loc["Current", "target"] == 2500
    assert frames["scenarios_definition_diettarget"].loc["Current", "PROD_GROUP"] == "CEREALS"
    assert frame.attrs["sheet"] == "SCENARIOS definition"
    assert frame.attrs["column_role_tags"] == ["DIRECT", "SCEN", "DATA-1"]
    assert frame.attrs["scenario_locations"] == ["S.3.C"]
    assert frame.attrs["cell_refs"] == [
        [
            "SCENARIOS definition!A3",
            "SCENARIOS definition!B3",
            "SCENARIOS definition!C3",
        ]
    ]


def test_scenario_definition_tables_for_location_matches_family_and_exact_markers() -> None:
    spec = FableCalculatorSpec(
        scenario_definition_tables=[
            ScenarioDefinitionTable(
                name="scenarios_definition_diettarget",
                label="DietTarget",
                sheet="SCENARIOS definition",
                range_ref="A2:B3",
                cell_refs=(("SCENARIOS definition!A3", "SCENARIOS definition!B3"),),
                row_labels=("Current",),
                column_labels=("DietScen", "target"),
                values=(("Current", 2500),),
                scenario_locations=("S.3.C",),
            ),
            ScenarioDefinitionTable(
                name="scenarios_definition_foodloss",
                label="FoodLossTarget",
                sheet="SCENARIOS definition",
                range_ref="D2:E3",
                cell_refs=(("SCENARIOS definition!D3", "SCENARIOS definition!E3"),),
                row_labels=("Current",),
                column_labels=("FoodLossScen", "target"),
                values=(("Current", 0.1),),
                scenario_locations=("S.4.B",),
            ),
        ]
    )

    family_frames = scenario_definition_tables_for_location(spec, "S.3")
    exact_frames = scenario_definition_tables_for_location(spec, "S.3.c")
    no_family_frames = scenario_definition_tables_for_location(spec, "S.3", include_family=False)

    assert set(family_frames) == {"scenarios_definition_diettarget"}
    assert set(exact_frames) == {"scenarios_definition_diettarget"}
    assert no_family_frames == {}


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
