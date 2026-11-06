#!/usr/bin/env python
"""Repair the broken 2024 FABLE ``ResultsLand[TOTAL]`` formula in a local workbook.

Both the working and pristine 2024 Canada workbooks contain ``SUMIFS(#REF!, ...)`` in
``LAND!AA17:AA27``. The intended missing correction is ``calc_land_cor[CalcLoggedForest]``: subtracting
that column reproduces the workbook's own valid ``calc_land_cor[TotallandFin]`` total exactly.

This script edits the xlsx XML directly so formulas and cached values are repaired without asking
openpyxl to rewrite the whole workbook and drop cached formula results.

Examples::

    python scripts/repair_fable_2024_land_total.py
    python scripts/repair_fable_2024_land_total.py --check
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.utils.cell import range_boundaries

__all__ = ["main", "repair_workbook"]

_TARGET_HEADER = "TOTAL"
_TOTAL_SHEET = "LAND"
_TOTAL_TABLE = "ResultsLand"
_CALC_SHEET = "4_calc_land"
_CALC_TABLE = "calc_land_cor"
_CALC_HEADER = "TotallandFin"


def main(argv: list[str] | None = None) -> int:
    """Run the workbook repair."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workbook",
        type=Path,
        default=Path("tmp/private-workbooks/2024_Open_FABLECalculator.xlsx"),
        help="2024 workbook to repair.",
    )
    parser.add_argument("--check", action="store_true", help="Report status without writing.")
    parser.add_argument("--no-backup", action="store_true", help="Do not write a .bak copy.")
    args = parser.parse_args(argv)

    if not args.workbook.is_file():
        print(f"workbook not found: {args.workbook}")
        return 2
    try:
        result = repair_workbook(args.workbook, write=not args.check, backup=not args.no_backup)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"repair failed: {error}")
        return 1
    print(f"{result['status']}: {result['cells']} cell(s), cached totals: {result['totals']}")
    return 0


def repair_workbook(path: Path, *, write: bool = True, backup: bool = True) -> dict[str, object]:
    """Repair the 2024 LAND TOTAL formulas and cached values."""

    totals = _cached_totals(path)
    if not totals:
        raise ValueError("could not find ResultsLand[TOTAL] cells")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        target_name = None
        patched_data = None
        patched_count = 0
        for name in names:
            if not (name.startswith("xl/worksheets/sheet") and name.endswith(".xml")):
                continue
            data = archive.read(name).decode("utf-8")
            if _TOTAL_SHEET not in data and "calc_land_cor[Year]" not in data:
                continue
            if "SUMIFS(#REF!,calc_land_cor[Year]" not in data:
                continue
            patched_data, patched_count = _repair_sheet_xml(data, totals)
            target_name = name
            break
        if target_name is None:
            return {
                "status": "already repaired or formula not found",
                "cells": 0,
                "totals": len(totals),
            }
        if write:
            if backup:
                backup_path = path.with_suffix(path.suffix + ".bak")
                if not backup_path.exists():
                    shutil.copy2(path, backup_path)
            temporary = path.with_name(path.name + ".tmp")
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as output:
                for name in names:
                    data = patched_data if name == target_name else archive.read(name)
                    output.writestr(name, data)
            os.replace(temporary, path)
    return {
        "status": "repaired" if write else "needs repair",
        "cells": patched_count,
        "totals": len(totals),
    }


def _cached_totals(path: Path) -> dict[str, float]:
    """Map LAND TOTAL cell coordinates to cached calc_land_cor[TotallandFin] values."""

    workbook = load_workbook(path, data_only=True, read_only=False)
    try:
        land = workbook[_TOTAL_SHEET]
        calc = workbook[_CALC_SHEET]
        land_table = land.tables[_TOTAL_TABLE]
        calc_table = calc.tables[_CALC_TABLE]
        land_min_col, land_min_row, land_max_col, land_max_row = range_boundaries(land_table.ref)
        calc_min_col, calc_min_row, calc_max_col, calc_max_row = range_boundaries(calc_table.ref)
        land_headers = {
            _text(land.cell(land_min_row, column).value): column for column in range(land_min_col, land_max_col + 1)
        }
        calc_headers = {
            _text(calc.cell(calc_min_row, column).value): column for column in range(calc_min_col, calc_max_col + 1)
        }
        land_year_col = land_headers["Year"]
        land_total_col = land_headers[_TARGET_HEADER]
        calc_year_col = calc_headers["Year"]
        calc_total_col = calc_headers[_CALC_HEADER]
        calc_by_year = {
            calc.cell(row, calc_year_col).value: calc.cell(row, calc_total_col).value
            for row in range(calc_min_row + 1, calc_max_row + 1)
        }
        totals: dict[str, float] = {}
        for row in range(land_min_row + 1, land_max_row + 1):
            year = land.cell(row, land_year_col).value
            value = calc_by_year.get(year)
            if isinstance(value, int | float):
                totals[f"{land.cell(row, land_total_col).coordinate}"] = float(value)
        return totals
    finally:
        workbook.close()


def _repair_sheet_xml(xml: str, totals: dict[str, float]) -> tuple[str, int]:
    """Replace broken TOTAL formulas and cached error values in one worksheet XML."""

    pattern = re.compile(r'<c r="(?P<coordinate>AA(?:1[7-9]|2[0-7]))"(?P<attrs>[^>]*)>(?P<body>.*?)</c>')

    def replacement(match: re.Match[str]) -> str:
        coordinate = match.group("coordinate")
        if coordinate not in totals:
            return match.group(0)
        attrs = re.sub(r'\s+t="e"', "", match.group("attrs"))
        body = match.group("body").replace(
            "SUMIFS(#REF!,calc_land_cor[Year]",
            "SUMIFS(calc_land_cor[CalcLoggedForest],calc_land_cor[Year]",
        )
        body = body.replace("<v>#REF!</v>", f"<v>{totals[coordinate]}</v>")
        return f'<c r="{coordinate}"{attrs}>{body}</c>'

    return pattern.subn(replacement, xml)


def _text(value: object) -> str:
    return str(value or "")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
