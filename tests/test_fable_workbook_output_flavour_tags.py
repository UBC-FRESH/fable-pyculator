from __future__ import annotations

import os
from pathlib import Path

import pytest

from fable_pyculator import discover_output_tables


WORKBOOK_ROOT = Path("tmp/private-workbooks")
EXPECTED_2020_2021_TAGS = {
    "AUX",
    "CALC",
    "DATA-1",
    "DATA-3.2",
    "DATA-4",
    "DATA-5",
    "DATA-9",
    "DIRECT",
    "OUTPUT-1",
    "OUTPUT-3",
    "OUTPUT-4",
    "OUTPUT-5",
    "OUTPUT-5,6",
    "OUTPUT-6",
    "OUTPUT-7",
    "OUTPUT-8",
    "OUTPUT-9",
}


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
def test_2020_and_2021_output_column_flavour_tag_inventory_matches() -> None:
    tags_2020 = _tag_inventory(workbook_path("2020_Open_FABLECalculator.xlsx"))
    tags_2021 = _tag_inventory(workbook_path("2021_Open_FABLECalculator.xlsx"))

    assert set(tags_2020) == EXPECTED_2020_2021_TAGS
    assert tags_2021 == tags_2020


@pytest.mark.workbook
def test_2020_ghg_output_eight_tags_preserve_raw_workbook_text() -> None:
    tables = discover_output_tables(workbook_path("2020_Open_FABLECalculator.xlsx"))
    ghg = next(table for table in tables if table.name == "ghg_resultsghg")

    assert "OUTPUT-8" in ghg.column_flavour_tags
    assert "OUTPUT - 8" in ghg.raw_column_flavour_tags
    assert all(
        raw_tag == "OUTPUT - 8"
        for raw_tag, tag in zip(ghg.raw_column_flavour_tags, ghg.column_flavour_tags, strict=True)
        if tag == "OUTPUT-8"
    )


def _tag_inventory(workbook_path: Path) -> dict[str, int]:
    inventory: dict[str, int] = {}
    for table in discover_output_tables(workbook_path):
        for tag in table.column_flavour_tags:
            if tag is None:
                continue
            inventory[tag] = inventory.get(tag, 0) + 1
    return inventory
