from __future__ import annotations

import pytest

from fable_pyculator import (
    FableCalculatorSpec,
    ScenarioControlSurface,
    ScenarioParameter,
    SelectionControl,
    SelectionOption,
)


def test_control_surface_reads_and_sets_values() -> None:
    spec = FableCalculatorSpec(
        parameters=[
            ScenarioParameter(
                name="ambition",
                label="Ambition",
                cell_ref="SCENARIOS selection!D20",
                kind="choice",
                default="baseline",
                choices=("baseline", "high"),
            ),
            ScenarioParameter(name="price", label="Price", cell_ref="SCENARIOS selection!D21", default=2.5),
        ],
    )

    surface = ScenarioControlSurface(spec)

    assert surface.values() == {"ambition": "baseline", "price": 2.5}
    surface.set_values({"ambition": "high", "price": 4})
    assert surface.values() == {"ambition": "high", "price": 4.0}


def test_control_surface_includes_selection_controls() -> None:
    surface = ScenarioControlSurface(
        FableCalculatorSpec(
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
                    ],
                    location="S.1",
                )
            ]
        )
    )

    assert surface.values() == {"gdp_scen": "SSP2"}
    surface.set_values({"gdp_scen": "SSP1"})
    assert surface.values() == {"gdp_scen": "SSP1"}


def test_control_surface_rejects_unknown_values() -> None:
    surface = ScenarioControlSurface(
        FableCalculatorSpec(
            parameters=[
                ScenarioParameter(name="ambition", label="Ambition", cell_ref="SCENARIOS selection!D20"),
            ],
        )
    )

    with pytest.raises(KeyError, match="unknown scenario parameter"):
        surface.set_values({"missing": 1})
