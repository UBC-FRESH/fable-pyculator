#!/usr/bin/env python
"""Repair the stale 2024 generated-model LAND TOTAL expressions.

The tracked 2024 generated model was produced from a workbook whose ``ResultsLand[TOTAL]`` formula
contained ``#REF!``. The repaired workbook shows that the missing subtraction was
``calc_land_cor[CalcLoggedForest]``. This script mechanically replaces the 11 generated expressions
for ``LAND!AA17:AA27`` with the recovered ``calc_land_cor[CalcLoggedForest]`` range.

It does not rebuild or reinterpret any other generated cell. Use
``scripts/repair_fable_2024_land_total.py`` for the source workbook.
"""

from __future__ import annotations

import argparse
import hashlib
import lzma
import os
import shutil
import sys
from pathlib import Path

__all__ = ["main", "repair_model"]

_ROWS = range(17, 28)


def main(argv: list[str] | None = None) -> int:
    """Run the generated-model repair."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("tmp/generated-models/fable-2024/generated_fable_2024_model.py"),
        help="Decompressed 2024 generated model to repair.",
    )
    parser.add_argument("--check", action="store_true", help="Report status without writing.")
    parser.add_argument("--no-backup", action="store_true", help="Do not write a .bak copy.")
    parser.add_argument(
        "--archive",
        type=Path,
        default=None,
        help="Optional .xz archive path to write from the repaired model.",
    )
    args = parser.parse_args(argv)

    if not args.model.is_file():
        print(f"model not found: {args.model}")
        return 2
    try:
        result = repair_model(args.model, write=not args.check, backup=not args.no_backup)
        if args.archive is not None and not args.check:
            _write_archive(args.model, args.archive)
    except (OSError, ValueError) as error:
        print(f"repair failed: {error}")
        return 1
    print(f"{result['status']}: {result['cells']} cell(s)")
    if args.archive is not None and not args.check:
        print(f"archive: {args.archive} sha256={_sha256(args.archive)}")
    return 0


def _write_archive(model: Path, archive: Path) -> None:
    """Write the repaired model to a compressed archive."""

    archive.parent.mkdir(parents=True, exist_ok=True)
    temporary = archive.with_name(archive.name + ".tmp")
    with model.open("rb") as source, lzma.open(temporary, "wb", preset=6) as target:
        shutil.copyfileobj(source, target)
    os.replace(temporary, archive)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def repair_model(path: Path, *, write: bool = True, backup: bool = True) -> dict[str, object]:
    """Replace the 11 ``LAND!AA17:AA27`` #REF! expressions."""

    source = path.read_text(encoding="utf-8")
    patched = source
    count = 0
    for row in _ROWS:
        old = f"_sf_sumifs('#REF!', (_range('4_calc_land', 5, 29, 5, 39), _sf_direct_reference(_get('LAND!K{row}'))))"
        new = (
            "_sf_sumifs(_range('4_calc_land', 37, 29, 37, 39), "
            "(_range('4_calc_land', 5, 29, 5, 39), "
            f"_sf_direct_reference(_get('LAND!K{row}'))))"
        )
        if old not in patched:
            if new in patched:
                continue
            raise ValueError(f"could not find LAND!AA{row} #REF! expression")
        patched = patched.replace(old, new, 1)
        count += 1
    leftover = patched.count("_sf_sumifs('#REF!'")
    if leftover:
        raise ValueError(f"{leftover} _sf_sumifs('#REF!') expression(s) remain")
    if count == 0 and patched == source:
        return {"status": "already repaired", "cells": 0}
    compile(patched, str(path), "exec")
    if write:
        if backup:
            backup_path = path.with_suffix(path.suffix + ".bak")
            if not backup_path.exists():
                shutil.copy2(path, backup_path)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(patched, encoding="utf-8")
        os.replace(temporary, path)
    return {"status": "repaired" if write else "needs repair", "cells": count}


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
