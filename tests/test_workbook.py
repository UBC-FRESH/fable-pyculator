from __future__ import annotations

import warnings

from fable_pyculator.workbook import suppress_benign_openpyxl_warnings


def test_suppress_benign_openpyxl_warnings_hides_known_fable_workbook_noise() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with suppress_benign_openpyxl_warnings():
            warnings.warn_explicit(
                "wmf image format is not supported so the image is being dropped",
                UserWarning,
                filename="openpyxl/reader/drawings.py",
                lineno=67,
                module="openpyxl.reader.drawings",
            )
            warnings.warn_explicit(
                "Data Validation extension is not supported and will be removed",
                UserWarning,
                filename="openpyxl/worksheet/_reader.py",
                lineno=329,
                module="openpyxl.worksheet._reader",
            )

    assert caught == []


def test_suppress_benign_openpyxl_warnings_preserves_unexpected_warnings() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with suppress_benign_openpyxl_warnings():
            warnings.warn_explicit(
                "A different workbook warning",
                UserWarning,
                filename="openpyxl/reader/excel.py",
                lineno=1,
                module="openpyxl.reader.excel",
            )

    assert len(caught) == 1
    assert str(caught[0].message) == "A different workbook warning"
