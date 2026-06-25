from __future__ import annotations

import pytest

from fable_pyculator import FableCalculatorSpec, OutputIndicator, ScenarioParameter, SelectionControl, SelectionOption


def test_spec_maps_named_parameters_to_cell_refs() -> None:
    spec = FableCalculatorSpec(
        parameters=[
            ScenarioParameter(name="ambition", label="Ambition", cell_ref="SCENARIOS selection!D20"),
        ],
        outputs=[
            OutputIndicator(name="ghg", label="GHG", cell_ref="SCENARIOS selection!D22"),
        ],
    )

    assert spec.input_mapping({"ambition": 2}) == {"SCENARIOS selection!D20": 2}


def test_spec_rejects_unknown_parameter_values() -> None:
    spec = FableCalculatorSpec(
        parameters=[
            ScenarioParameter(name="ambition", label="Ambition", cell_ref="SCENARIOS selection!D20"),
        ],
    )

    with pytest.raises(KeyError, match="unknown scenario parameter"):
        spec.input_mapping({"missing": 2})


def test_spec_rejects_duplicate_names() -> None:
    with pytest.raises(ValueError, match="duplicate parameter"):
        FableCalculatorSpec(
            parameters=[
                ScenarioParameter(name="ambition", label="Ambition", cell_ref="SCENARIOS selection!D20"),
                ScenarioParameter(name="ambition", label="Ambition 2", cell_ref="SCENARIOS selection!D21"),
            ],
        )


def test_spec_maps_selection_controls_to_x_marker_cells() -> None:
    spec = FableCalculatorSpec(
        selection_controls=[
            SelectionControl(
                name="gdp_scen",
                label="GDP projections",
                table_name="GDP_Scen",
                sheet="SCENARIOS selection",
                range_ref="A19:C22",
                code_header="GDP_SCEN",
                options=[
                    SelectionOption("SSP1", "SSP1", "SCENARIOS selection!A20"),
                    SelectionOption("SSP2", "SSP2", "SCENARIOS selection!A21", selected=True),
                    SelectionOption("SSP3", "SSP3", "SCENARIOS selection!A22"),
                ],
                location="S.1",
            )
        ]
    )

    assert spec.input_mapping({"gdp_scen": "SSP1"}) == {
        "SCENARIOS selection!A20": "x",
        "SCENARIOS selection!A21": None,
        "SCENARIOS selection!A22": None,
    }
