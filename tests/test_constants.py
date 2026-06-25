from __future__ import annotations

from fable_pyculator import FABLE_OUTPUT_SURFACE_SHEETS


def test_fable_output_surface_sheet_order_is_canonical() -> None:
    assert FABLE_OUTPUT_SURFACE_SHEETS == (
        "FOOD",
        "PRODUCTION",
        "TRADE",
        "BIODIVERSITY",
        "LAND",
        "GHG",
        "WATER",
    )
