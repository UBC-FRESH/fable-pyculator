#!/usr/bin/env python
"""Smoke-test the Abdulateef-facing 2021 notebook loop path."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import sys
import time
from typing import Any

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line smoke check."""

    args = _parser().parse_args(argv)
    repo_root = _repo_root(args.repo_root)
    workbook_path = _resolve(repo_root, args.workbook_path)
    generated_model_path = _resolve(repo_root, args.generated_model_path)
    missing = _missing_artifacts(
        workbook_path=workbook_path,
        generated_model_path=generated_model_path,
    )
    if missing:
        payload = _base_payload(
            repo_root=repo_root,
            workbook_path=workbook_path,
            generated_model_path=generated_model_path,
            status="skipped",
            elapsed_seconds=0.0,
        )
        payload["missing_artifacts"] = missing
        return _emit(payload, json_output=args.json_output, exit_code=0)

    start = time.monotonic()
    try:
        from fable_pyculator import run_2021_notebook_loop

        result = run_2021_notebook_loop(
            {args.selection_name: args.selection_value},
            workbook_path=workbook_path,
            generated_model_path=generated_model_path,
            output_table_column_flavour_tags=args.output_table_column_flavour_tags,
            include_figures=False,
        )
        table = result.output_tables[args.proof_table]
        proof_columns = list(dict.fromkeys(args.proof_context_column or ["PRODUCT", "YEAR"]))
        missing_columns = [column for column in proof_columns if column not in table.columns]
        missing_values = {
            column: bool(table[column].head(args.proof_rows).isna().any())
            for column in proof_columns
            if column in table.columns
        }
        proof_ok = not missing_columns and not any(missing_values.values())
        status = "passed" if proof_ok else "failed"
        payload = _base_payload(
            repo_root=repo_root,
            workbook_path=workbook_path,
            generated_model_path=generated_model_path,
            status=status,
            elapsed_seconds=time.monotonic() - start,
        )
        payload.update(
            {
                "selection": {args.selection_name: args.selection_value},
                "output_table_column_flavour_tags": args.output_table_column_flavour_tags,
                "rendered_tables": sorted(result.output_tables),
                "skipped_output_tables": result.skipped_output_tables,
                "proof": {
                    "table": args.proof_table,
                    "context_columns": proof_columns,
                    "checked_rows": args.proof_rows,
                    "missing_columns": missing_columns,
                    "missing_values": missing_values,
                    "ok": proof_ok,
                },
            }
        )
        return _emit(payload, json_output=args.json_output, exit_code=0 if proof_ok else 1)
    except Exception as exc:  # noqa: BLE001
        payload = _base_payload(
            repo_root=repo_root,
            workbook_path=workbook_path,
            generated_model_path=generated_model_path,
            status="failed",
            elapsed_seconds=time.monotonic() - start,
        )
        payload["error"] = f"{type(exc).__name__}: {exc}"
        return _emit(payload, json_output=args.json_output, exit_code=1, stderr=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Smoke-test the 2021 FABLE Pyculator notebook loop and context-column rendering."
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument(
        "--workbook-path",
        type=Path,
        default=Path("tmp/private-workbooks/2021_Open_FABLECalculator.xlsx"),
        help="2021 source workbook path. Defaults to tmp/private-workbooks/2021_Open_FABLECalculator.xlsx.",
    )
    parser.add_argument(
        "--generated-model-path",
        type=Path,
        default=Path("tmp/generated-models/fable-2021/generated_fable_2021_model.py"),
        help="2021 generated model path. Defaults to tmp/generated-models/fable-2021/generated_fable_2021_model.py.",
    )
    parser.add_argument("--selection-name", default="gdp_scen", help="Selection control name. Defaults to gdp_scen.")
    parser.add_argument("--selection-value", default="SSP1", help="Selection value. Defaults to SSP1.")
    parser.add_argument(
        "--output-table-column-flavour-tags",
        default="OUTPUT-*",
        help="Output table flavour filter. Defaults to OUTPUT-*.",
    )
    parser.add_argument("--proof-table", default="trade_resultstrade", help="Output table used for context proof.")
    parser.add_argument(
        "--proof-context-column",
        action="append",
        default=None,
        help="Context column that must be present and populated. May be repeated.",
    )
    parser.add_argument("--proof-rows", type=int, default=5, help="Number of top rows to inspect. Defaults to 5.")
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


def _resolve(repo_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else repo_root / path


def _missing_artifacts(*, workbook_path: Path, generated_model_path: Path) -> list[str]:
    missing = []
    if not workbook_path.exists():
        missing.append("workbook_path")
    if not generated_model_path.exists():
        missing.append("generated_model_path")
    return missing


def _base_payload(
    *,
    repo_root: Path,
    workbook_path: Path,
    generated_model_path: Path,
    status: str,
    elapsed_seconds: float,
) -> dict[str, Any]:
    return {
        "ok": status == "passed",
        "status": status,
        "workbook_path": _display_path(workbook_path, repo_root),
        "generated_model_path": _display_path(generated_model_path, repo_root),
        "elapsed_seconds": round(elapsed_seconds, 3),
        "missing_artifacts": [],
    }


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _emit(
    payload: dict[str, Any],
    *,
    json_output: bool,
    exit_code: int,
    stderr: bool = False,
) -> int:
    stream = sys.stderr if stderr else sys.stdout
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stream)
    else:
        print(f"2021 notebook loop smoke: {payload['status']}", file=stream)
        print(f"Workbook: {payload['workbook_path']}", file=stream)
        print(f"Generated model: {payload['generated_model_path']}", file=stream)
        if payload["missing_artifacts"]:
            print("Missing artifacts:", file=stream)
            for name in payload["missing_artifacts"]:
                print(f"- {name}", file=stream)
        if "proof" in payload:
            print(f"Context proof: {'passed' if payload['proof']['ok'] else 'failed'}", file=stream)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
