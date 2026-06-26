from __future__ import annotations

import os
from pathlib import Path

import pytest

from fable_pyculator import curate_default_headline_series


WORKBOOK_ROOT = Path("tmp/private-workbooks")


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
def test_2020_headline_series_match_initial_curation_contract() -> None:
    series = curate_default_headline_series(workbook_path("2020_Open_FABLECalculator.xlsx"))

    assert [item.name for item in series] == [
        "food_total_kcal_feas",
        "land_total_area",
        "ghg_total_co2e",
        "water_total_footprint",
    ]
    assert [point.year for point in series[0].points] == list(range(2000, 2055, 5))
    assert all(len(item.points) == 11 for item in series)
    assert all(len(point.cell_refs) == 6 for point in series[3].points)
    assert series[3].aggregation == "sum"
