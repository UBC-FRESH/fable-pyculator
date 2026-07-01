"""Workbook loading helpers for FABLE Calculator workbooks."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
import warnings
from typing import Any

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook


BENIGN_OPENPYXL_WARNING_PATTERNS = (
    r"wmf image format is not supported so the image is being dropped",
    r"Data Validation extension is not supported and will be removed",
)


def load_fable_workbook(path: str | Path, **kwargs: Any) -> Workbook:
    """Load a FABLE workbook while suppressing known irrelevant OpenPyXL warnings.

    The public FABLE-C workbooks include workbook features that FABLE Pyculator does not use for
    scenario control discovery, output-table discovery, notebook rendering, or generated-model
    rebuild preparation. OpenPyXL warns when it drops unsupported WMF images or data-validation
    extension metadata; those warnings are benign for this package's workbook surfaces.
    """

    with suppress_benign_openpyxl_warnings():
        return load_workbook(path, **kwargs)


@contextmanager
def suppress_benign_openpyxl_warnings() -> Iterator[None]:
    """Suppress only the known benign OpenPyXL warnings seen in FABLE workbooks."""

    with warnings.catch_warnings():
        for pattern in BENIGN_OPENPYXL_WARNING_PATTERNS:
            warnings.filterwarnings(
                "ignore",
                message=pattern,
                category=UserWarning,
                module=r"openpyxl\..*",
            )
        yield
