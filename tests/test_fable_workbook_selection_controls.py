from __future__ import annotations

import os
from pathlib import Path

import pytest

from fable_pyculator import discover_selection_controls


WORKBOOK_ROOT = Path("tmp/private-workbooks")
EXPECTED_2020_SELECTIONS = [
    ("S.1", "GDP_Scen", "A19:C22", 3, "SSP2"),
    ("S.2", "Pop_Scen", "A27:C41", 14, "SSP1"),
    ("S.3", "Diet_scen", "A46:D52", 6, "EATLancetAverage"),
    ("S.4.", "Scen_foodloss", "A57:D60", 3, "Current"),
    ("S.5", "Scen_imports", "A65:D68", 3, "I2"),
    ("S.6", "Scen_exports", "A73:D76", 3, "E1"),
    ("S.7", "Live_scen", "A81:D85", 4, "BAUGrowth"),
    ("S.8", "Crop_scen", "A90:D94", 4, "HighGrowth"),
    ("S.9", "Land_Scen", "A99:D102", 3, "FreeExpansion"),
    ("S.10", "Affor_scen", "A107:D109", 2, "NoAffor"),
    ("S.11", "FixTrade_Scen", "A114:D116", 2, "No"),
    ("S.12", "PopActivity_Scen", "A121:D124", 3, "Middle"),
    ("S.13", "ClimateChange_Scen", "A129:D146", 17, "rcp6p0_hadgem2-es_n_GEPIC"),
    ("S.14", "PA_Scen", "A150:D152", 2, "NoChange"),
    ("S.15", "PostHarvestLoss_Scen", "A156:D158", 2, "Reduced"),
    ("S.16", "Biofuel_scen", "A162:D164", 2, "OECD_AGLINK"),
]


def workbook_tests_enabled() -> bool:
    return os.environ.get("FABLE_PYCULATOR_RUN_WORKBOOK_TESTS") == "1"


def workbook_path(filename: str) -> Path:
    path = WORKBOOK_ROOT / filename
    if not workbook_tests_enabled():
        pytest.skip("set FABLE_PYCULATOR_RUN_WORKBOOK_TESTS=1 to run workbook-backed tests")
    if not path.exists():
        pytest.skip(f"local workbook artifact is missing: {path}")
    return path


@pytest.mark.workbook
def test_2020_selection_controls_match_expected_s1_to_s16_contract() -> None:
    controls = discover_selection_controls(workbook_path("2020_Open_FABLECalculator.xlsx"))

    assert [
        (control.location, control.table_name, control.range_ref, len(control.options), control.default)
        for control in controls
    ] == EXPECTED_2020_SELECTIONS
    for control in controls:
        assert sum(1 for option in control.options if option.selected) == 1


@pytest.mark.workbook
def test_2021_selection_controls_share_2020_contract_with_known_default_difference() -> None:
    controls = discover_selection_controls(workbook_path("2021_Open_FABLECalculator.xlsx"))

    observed = [
        (control.location, control.table_name, control.range_ref, len(control.options), control.default)
        for control in controls
    ]
    expected = [
        ("S.10", "Affor_scen", "A107:D109", 2, "BonnChallenge")
        if row[1] == "Affor_scen"
        else row
        for row in EXPECTED_2020_SELECTIONS
    ]
    assert observed == expected


@pytest.mark.workbook
def test_2019_selection_controls_are_older_twelve_control_structure() -> None:
    controls = discover_selection_controls(workbook_path("2019_Open_FABLECalculator.xlsx"))

    assert len(controls) == 12
    assert [control.location for control in controls] == [
        "S.1",
        "S.2",
        "S.3",
        "S.4.",
        "S.5",
        "S.6",
        "S.7",
        "S.8",
        "S.9",
        "S.10",
        "S.12",
        "S.13",
    ]

