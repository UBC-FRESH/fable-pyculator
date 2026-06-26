from __future__ import annotations

import os
from pathlib import Path

import pytest

from fable_pyculator import discover_scenario_definition_tables


WORKBOOK_ROOT = Path("tmp/private-workbooks")
EXPECTED_2020_2021_TABLE_NAMES = [
    "ImplCoefOptions",
    "DietImplRates",
    "DietTarget",
    "DietScenDef",
    "FLScenTarget",
    "FoodLossTarget",
    "Product_ImpScen",
    "ImpScenTarget",
    "ImportDef",
    "product_Exports",
    "ExpScenTarget",
    "ExportDef",
    "LivePdtyTarget",
    "LivePdtyDef",
    "CropPdtyTarget",
    "CropPdtyDef",
    "LandScenTarget",
    "AfforTarget",
    "AfforScenDef",
    "FinalTradeAdj",
    "CCShifters",
    "PAtarget",
    "PAtarget_def",
    "PHLoss_target",
    "PHLossTarget_def",
    "BiofuelScen_def",
    "GdpPopTarget",
    "income_elas",
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
def test_2020_and_2021_scenario_definition_table_inventory_matches() -> None:
    tables_2020 = discover_scenario_definition_tables(workbook_path("2020_Open_FABLECalculator.xlsx"))
    tables_2021 = discover_scenario_definition_tables(workbook_path("2021_Open_FABLECalculator.xlsx"))

    assert {table.label for table in tables_2020} == set(EXPECTED_2020_2021_TABLE_NAMES)
    assert {table.label for table in tables_2021} == set(EXPECTED_2020_2021_TABLE_NAMES)


@pytest.mark.workbook
def test_2020_scenario_definition_tables_preserve_direct_and_scen_tags() -> None:
    tables = discover_scenario_definition_tables(workbook_path("2020_Open_FABLECalculator.xlsx"))
    diet_target = next(table for table in tables if table.label == "DietTarget")
    food_loss = next(table for table in tables if table.label == "FoodLossTarget")

    assert diet_target.range_ref == "AA28:AE79"
    assert diet_target.column_flavour_tags == ("DIRECT", "DIRECT", "CALC", "DATA-1", "CALC")
    assert diet_target.column_flavour_tag_refs[0] == "SCENARIOS definition!AA23"
    assert "SCEN" in food_loss.column_flavour_tags
    assert "DIRECT" in food_loss.column_flavour_tags
