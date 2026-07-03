#!/usr/bin/env python
"""Validate a FABLE scenario-definition patch without mutating workbooks."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import sys
from typing import Any

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line wrapper."""

    args = _parser().parse_args(argv)
    repo_root = _repo_root(args.repo_root)
    try:
        from fable_pyculator import (
            build_notebook_spec,
            editable_scenario_definition_cells,
            load_scenario_definition_patch,
            validate_scenario_definition_patch,
        )

        patch = load_scenario_definition_patch(args.patch)
        workbook_path = _workbook_path(
            repo_root=repo_root,
            workbook_version=args.workbook_version,
            workbook_path=args.workbook_path,
        )
        spec = build_notebook_spec(workbook_path, workbook_id=f"fable-c-{args.workbook_version}")
        result = validate_scenario_definition_patch(spec, patch)
        payload = {
            "ok": True,
            "workbook_version": args.workbook_version,
            "workbook_path": _display_path(workbook_path, repo_root),
            "patch": result.patch.to_dict(),
            "editable_cell_count": result.editable_cell_count,
            "edit_count": len(result.edits),
            "inputs": result.inputs,
            "edits": list(result.edits),
            "sample_editable_cells": [
                cell.to_dict()
                for cell in editable_scenario_definition_cells(spec)[: args.sample_limit]
            ],
            "notes": list(result.notes),
        }
    except Exception as exc:  # noqa: BLE001
        return _fail(f"{type(exc).__name__}: {exc}", json_output=args.json_output)
    return _emit(payload, json_output=args.json_output)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a FABLE scenario-definition patch and report generated-model inputs."
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument("--patch", required=True, help="Scenario-definition patch JSON/YAML path.")
    parser.add_argument("--workbook-version", default="2021", help="FABLE workbook version. Defaults to 2021.")
    parser.add_argument(
        "--workbook-path",
        default=None,
        help="Workbook path. Defaults to tmp/private-workbooks/{version}_Open_FABLECalculator.xlsx.",
    )
    parser.add_argument("--sample-limit", type=int, default=5, help="Editable-cell sample size for JSON output.")
    parser.add_argument("--json", dest="json_output", action="store_true", help="Emit machine-readable JSON.")
    return parser


def _repo_root(value: Path | None) -> Path:
    if value is not None:
        return value.resolve()
    start = Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "src" / "fable_pyculator").exists():
            return candidate
    raise RuntimeError("Could not find the fable-pyculator repository root.")


def _workbook_path(*, repo_root: Path, workbook_version: str, workbook_path: str | None) -> Path:
    path = Path(workbook_path or f"tmp/private-workbooks/{workbook_version}_Open_FABLECalculator.xlsx")
    return path if path.is_absolute() else repo_root / path


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _emit(payload: dict[str, Any], *, json_output: bool) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("FABLE scenario-definition patch")
        print(f"Workbook version: {payload['workbook_version']}")
        print(f"Patch id: {payload['patch']['patch_id']}")
        print(f"Editable cells: {payload['editable_cell_count']}")
        print(f"Validated edits: {payload['edit_count']}")
        print("No source workbook was mutated.")
    return 0


def _fail(message: str, *, json_output: bool) -> int:
    payload = {"ok": False, "error": message}
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
