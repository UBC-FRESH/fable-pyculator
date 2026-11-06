from __future__ import annotations

import pandas as pd
import pytest

from fable_pyculator.web.service import _extend_frame_to_2070, _trend_value


def test_extend_year_rows_uses_2035_to_2050_linear_trend() -> None:
    frame = pd.DataFrame(
        {
            "Year": [2035, 2040, 2045, 2050],
            "value": [10.0, 20.0, 30.0, 40.0],
            "label": ["x", "x", "x", "x"],
        }
    )

    extended = _extend_frame_to_2070(frame)

    assert list(extended["Year"]) == [2035, 2040, 2045, 2050, 2055, 2060, 2065, 2070]
    assert extended["value"].tolist() == pytest.approx([10, 20, 30, 40, 50, 60, 70, 80])
    assert extended["label"].tolist()[-4:] == ["x", "x", "x", "x"]
    assert "trend extension" in extended.attrs["extension_note"]


def test_extend_year_columns_uses_recent_trend() -> None:
    frame = pd.DataFrame(
        {
            "Item": ["A"],
            "2035": [10.0],
            "2040": [20.0],
            "2045": [30.0],
            "2050": [40.0],
        }
    )

    extended = _extend_frame_to_2070(frame)

    assert "2055" in extended.columns
    assert "2070" in extended.columns
    assert extended.loc[0, "2070"] == pytest.approx(80.0)
    assert "trend extension" in extended.attrs["extension_note"]


def test_multi_row_per_year_table_is_not_extended() -> None:
    frame = pd.DataFrame(
        {
            "Year": [2050, 2050, 2050],
            "Product": ["A", "B", "C"],
            "value": [1.0, 2.0, 3.0],
        }
    )

    extended = _extend_frame_to_2070(frame)

    assert len(extended) == len(frame)
    assert "multiple rows per year" in extended.attrs["extension_note"]


def test_trend_value_uses_last_value_when_only_one_point() -> None:
    assert _trend_value([(2050, 3.5)], 2070) == 3.5


def test_trend_value_handles_flat_series() -> None:
    assert _trend_value([(2035, 2.0), (2050, 2.0)], 2070) == pytest.approx(2.0)


def test_extended_headline_rows_do_not_reuse_native_cell_refs() -> None:
    frame = pd.DataFrame(
        {
            "year": [2035, 2040, 2045, 2050],
            "value": [1.0, 2.0, 3.0, 4.0],
            "cell_refs": [("FOOD!A1",), ("FOOD!A2",), ("FOOD!A3",), ("FOOD!A4",)],
            "description": [None, None, None, None],
        }
    )

    extended = _extend_frame_to_2070(frame)

    assert extended.iloc[-1]["cell_refs"] == ()
    assert extended.iloc[-1]["description"] == "Trend extension (non-native)"


def test_extend_grouped_rows_appends_each_product_series() -> None:
    rows = []
    for product, offset in (("A", 0.0), ("B", 100.0)):
        for year, value in zip((2035, 2040, 2045, 2050), (1.0, 2.0, 3.0, 4.0), strict=True):
            rows.append({"PRODUCT": product, "YEAR": year, "value": value + offset})
    frame = pd.DataFrame(rows)

    extended = _extend_frame_to_2070(frame)

    assert len(extended) == 16
    product_a = extended[extended["PRODUCT"] == "A"]
    product_b = extended[extended["PRODUCT"] == "B"]
    assert product_a["YEAR"].tolist()[-4:] == [2055, 2060, 2065, 2070]
    assert product_a["value"].tolist()[-4:] == pytest.approx([5.0, 6.0, 7.0, 8.0])
    assert product_b["value"].tolist()[-4:] == pytest.approx([105.0, 106.0, 107.0, 108.0])
    assert "trend extension" in extended.attrs["extension_note"]
