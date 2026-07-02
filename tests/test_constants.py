from __future__ import annotations

from fable_pyculator import FABLE_OUTPUT_SURFACE_SHEETS, __version__


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


def test_package_version_matches_alpha_release_target() -> None:
    assert __version__ == "0.1.0a3"
