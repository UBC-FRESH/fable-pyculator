#!/usr/bin/env python
"""Compare FABLE output-ref strategy boundaries."""

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
    include_workflows = args.include_workflows or args.include_matrix or args.matrix_plan or args.matrix_run
    try:
        spec = _build_spec(
            workbook_version=args.workbook_version,
            workbook_path=args.workbook_path,
            repo_root=repo_root,
        )
        result = _compare(
            spec,
            workbook_version=args.workbook_version,
            workbook_path=args.workbook_path or f"tmp/private-workbooks/{args.workbook_version}_Open_FABLECalculator.xlsx",
            repo_root=repo_root,
            output_dir=args.output_dir,
            selected_case_ids=tuple(args.strategy) if args.strategy else None,
            include_workflows=include_workflows,
            include_existing_evidence=args.include_existing_evidence,
        )
        payload = _write(result)
        matrix_payload = None
        if args.include_matrix or args.matrix_plan or args.matrix_run:
            matrix_result = _build_matrix(result, matrix_path=args.matrix_path)
            matrix_payload = _write_matrix(matrix_result)
            payload["matrix"] = matrix_payload
        if args.matrix_plan:
            if matrix_payload is None:
                raise RuntimeError("matrix plan requested but no matrix was written")
            payload["matrix_plan"] = _plan_matrix(matrix_payload["paths"]["matrix_path"])
        if args.matrix_run:
            if matrix_payload is None:
                raise RuntimeError("matrix run requested but no matrix was written")
            payload["matrix_run"] = _run_matrix(
                matrix_payload["paths"]["matrix_path"],
                workdir=args.workdir or repo_root,
                fail_fast=args.fail_fast,
            )
    except Exception as exc:  # noqa: BLE001
        return _fail(f"{type(exc).__name__}: {exc}", json_output=args.json_output)
    return _emit(payload, json_output=args.json_output)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare FABLE output-ref strategies without running FreshForge or Modelwright."
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument("--workbook-version", default="2021", help="FABLE workbook version. Defaults to 2021.")
    parser.add_argument(
        "--workbook-path",
        default=None,
        help="Workbook path. Defaults to tmp/private-workbooks/{version}_Open_FABLECalculator.xlsx.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Comparison output directory. Defaults to tmp/strategy-comparisons/fable-{version}.",
    )
    parser.add_argument(
        "--strategy",
        action="append",
        default=[],
        help="Restrict to one default strategy case id. May be repeated.",
    )
    parser.add_argument(
        "--include-workflows",
        action="store_true",
        help="Also write per-strategy FreshForge workflow JSON files.",
    )
    parser.add_argument(
        "--include-matrix",
        action="store_true",
        help="Also write a FreshForge matrix YAML document for the compared strategy cases.",
    )
    parser.add_argument(
        "--matrix-plan",
        action="store_true",
        help="Write and plan the FreshForge strategy matrix without running it.",
    )
    parser.add_argument(
        "--matrix-run",
        action="store_true",
        help="Write and explicitly run the FreshForge strategy matrix.",
    )
    parser.add_argument(
        "--matrix-path",
        default=None,
        help="FreshForge matrix YAML path. Defaults to strategy-matrix.yaml under the comparison output directory.",
    )
    parser.add_argument(
        "--workdir",
        type=Path,
        default=None,
        help="FreshForge matrix run workdir. Defaults to the repository root.",
    )
    parser.add_argument("--fail-fast", action="store_true", help="Stop matrix execution after the first failed case.")
    parser.add_argument(
        "--include-existing-evidence",
        action="store_true",
        help="Include compact evidence summaries from existing per-strategy artifacts when available.",
    )
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


def _build_spec(*, workbook_version: str, workbook_path: str | None, repo_root: Path) -> Any:
    from fable_pyculator import build_notebook_spec

    path = Path(workbook_path or f"tmp/private-workbooks/{workbook_version}_Open_FABLECalculator.xlsx")
    workbook = path if path.is_absolute() else repo_root / path
    return build_notebook_spec(workbook, workbook_id=f"fable-c-{workbook_version}")


def _compare(*args: Any, **kwargs: Any) -> Any:
    from fable_pyculator import compare_output_ref_strategies

    return compare_output_ref_strategies(*args, **kwargs)


def _write(result: Any) -> dict[str, Any]:
    from fable_pyculator import write_output_ref_strategy_comparison

    return write_output_ref_strategy_comparison(result)


def _build_matrix(result: Any, *, matrix_path: str | None) -> Any:
    from fable_pyculator import build_output_ref_strategy_matrix

    return build_output_ref_strategy_matrix(result, matrix_path=matrix_path)


def _write_matrix(result: Any) -> dict[str, Any]:
    from fable_pyculator import write_output_ref_strategy_matrix

    return write_output_ref_strategy_matrix(result)


def _plan_matrix(matrix_path: str) -> dict[str, Any]:
    from fable_pyculator import plan_output_ref_strategy_matrix

    return plan_output_ref_strategy_matrix(matrix_path)


def _run_matrix(matrix_path: str, *, workdir: Path, fail_fast: bool) -> dict[str, Any]:
    from fable_pyculator import run_output_ref_strategy_matrix

    return run_output_ref_strategy_matrix(matrix_path, workdir=workdir, fail_fast=fail_fast)


def _emit(payload: dict[str, Any], *, json_output: bool) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("FABLE output-ref strategy comparison")
        print(f"Workbook version: {payload['workbook_version']}")
        print(f"Summary JSON: {payload['summary_json_path']}")
        print(f"Summary Markdown: {payload['summary_markdown_path']}")
        if "matrix" in payload:
            print(f"Matrix YAML: {payload['matrix']['paths']['matrix_path']}")
        print("Strategies:")
        for entry in payload["entries"]:
            print(
                f"- {entry['case']['case_id']}: "
                f"{entry['output_ref_count']:,} refs; "
                f"{entry['comparable_output_count']:,} comparable cached outputs"
            )
        if "matrix_plan" in payload:
            print(f"Matrix plan ok: {payload['matrix_plan']['ok']}")
        if "matrix_run" in payload:
            print(f"Matrix run ok: {payload['matrix_run']['ok']}")
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
