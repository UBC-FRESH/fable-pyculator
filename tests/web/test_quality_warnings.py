from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import pytest

from fable_pyculator.web.service import _ghg_cached_mismatch, _quality_warnings


def _spec(*, land_component: bool = False, water: bool = True):
    series = [
        SimpleNamespace(name="land_total_area", label="Total land area", description=None),
        SimpleNamespace(name="ghg_total_co2e", label="Total GHG emissions", description=None),
    ]
    if land_component:
        series[0] = SimpleNamespace(
            name="land_total_area",
            label="Total land area (component sum)",
            description="matches calc_land_cor[TotallandFin]",
        )
    if water:
        series.append(SimpleNamespace(name="water_total_footprint", label="Water", description=None))
    return SimpleNamespace(headline_series=series)


def test_quality_warnings_cover_extension_land_water_and_unextended_tables() -> None:
    warnings = _quality_warnings(
        version="2024",
        spec=_spec(land_component=True, water=False),
        horizon=2070,
        headline_frames={},
        table_frames={},
        table_summaries=[
            {
                "name": "production_resultsprod",
                "label": "ResultsProd",
                "extension_note": "This table has multiple rows per year; 2055-2070 trend extension was not applied.",
            }
        ],
    )

    codes = {warning["code"] for warning in warnings}
    assert "trend_extension_2070" in codes
    assert "land_component_sum" in codes
    assert "water_unavailable_2024" in codes
    assert "tables_not_extended" in codes


def test_ghg_cached_mismatch_reports_largest_difference() -> None:
    headline = pd.DataFrame(
        {
            "year": [2045, 2050],
            "value": [180.7579, 186.5172],
        }
    )
    table = pd.DataFrame(
        {
            "Year": [2045, 2050],
            "TotalCO2e": [180.7579, 107.6262],
        }
    )

    mismatch = _ghg_cached_mismatch(
        {"ghg_total_co2e": headline},
        {"ghg_resultsghg": table},
    )

    assert mismatch is not None
    years, maximum, max_year = mismatch
    assert years == [2050]
    assert maximum == pytest.approx(78.891)
    assert max_year == 2050


def test_quality_warnings_are_empty_for_clean_native_run() -> None:
    warnings = _quality_warnings(
        version="2021",
        spec=_spec(),
        horizon=2050,
        headline_frames={},
        table_frames={},
        table_summaries=[],
    )

    assert warnings == []


def test_ghg_mismatch_can_use_cached_spec_table_without_rendering_it() -> None:
    headline = pd.DataFrame({"year": [2045, 2050], "value": [180.7579, 186.5172]})
    spec = SimpleNamespace(
        headline_series=[],
        output_tables=[
            SimpleNamespace(
                name="ghg_resultsghg",
                column_labels=("Year", "TotalCO2e"),
                values=((2045, 180.7579), (2050, 107.6262)),
            )
        ],
    )

    mismatch = _ghg_cached_mismatch(
        {"ghg_total_co2e": headline},
        {},
        spec=spec,
    )

    assert mismatch is not None
    assert mismatch[0] == [2050]
    assert mismatch[2] == 2050


def test_2021_ghg_mismatch_uses_generic_warning() -> None:
    headline = pd.DataFrame({"year": [2050], "value": [186.5172]})
    table = pd.DataFrame({"Year": [2050], "TotalCO2e": [107.6262]})

    warnings = _quality_warnings(
        version="2021",
        spec=_spec(),
        horizon=2050,
        headline_frames={"ghg_total_co2e": headline},
        table_frames={"ghg_resultsghg": table},
        table_summaries=[],
    )

    codes = {warning["code"] for warning in warnings}
    assert "ghg_cached_mismatch" in codes
