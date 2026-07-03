#!/usr/bin/env python
"""Package compact FABLE benchmark matrix evidence through Modelwright."""

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
            fable_benchmark_matrix_evidence_paths,
            package_fable_benchmark_matrix_evidence,
            write_fable_benchmark_matrix_evidence,
        )

        paths = fable_benchmark_matrix_evidence_paths(
            workbook_version=args.workbook_version,
            repo_root=repo_root,
            matrix_run_path=args.matrix_run,
            matrix_summary_path=args.matrix_summary,
            artifact_root=args.artifact_root,
            output_dir=args.output_dir,
            evidence_id=args.evidence_id,
        )
        summary = package_fable_benchmark_matrix_evidence(
            workbook_version=args.workbook_version,
            repo_root=repo_root,
            matrix_run_path=args.matrix_run,
            matrix_summary_path=args.matrix_summary,
            artifact_root=args.artifact_root,
            output_dir=args.output_dir,
            evidence_id=args.evidence_id,
            require_evidence=args.require_evidence,
        )
        payload = write_fable_benchmark_matrix_evidence(summary, paths)
    except Exception as exc:  # noqa: BLE001
        return _fail(f"{type(exc).__name__}: {exc}", json_output=args.json_output)

    emit_relative_paths = args.artifact_root is None and args.output_dir is None
    return _emit(
        _script_payload(payload, paths, repo_root, emit_relative_paths=emit_relative_paths),
        json_output=args.json_output,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package compact FABLE benchmark matrix evidence using Modelwright aggregation."
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument("--workbook-version", default="2021", help="FABLE workbook version. Defaults to 2021.")
    parser.add_argument("--matrix-run", default=None, help="FreshForge matrix run JSON path.")
    parser.add_argument("--matrix-summary", default=None, help="FreshForge matrix summary JSON path.")
    parser.add_argument(
        "--artifact-root",
        default=None,
        help="Per-case generated-model artifact root. Defaults to tmp/strategy-comparisons/fable-{version}.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Compact evidence output directory. Defaults to tmp/validation-evidence/fable-{version}/matrix.",
    )
    parser.add_argument(
        "--evidence-id",
        default=None,
        help="Evidence id. Defaults to fable-{version}-strategy-matrix.",
    )
    parser.add_argument(
        "--require-evidence",
        action="store_true",
        help="Fail if per-case evidence is missing. Defaults to skipped/incomplete evidence.",
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


def _script_payload(
    payload: dict[str, Any],
    paths: Any,
    repo_root: Path,
    *,
    emit_relative_paths: bool,
) -> dict[str, Any]:
    return {
        "ok": True,
        "workbook_version": payload["workbook_version"],
        "evidence_backend": payload["evidence_backend"],
        "evidence_id": payload["evidence_id"],
        "evidence_status": payload["evidence_status"],
        "equivalence_status": payload["equivalence_status"],
        "case_count": payload["case_count"],
        "complete_count": payload["complete_count"],
        "incomplete_count": payload["incomplete_count"],
        "skipped_count": payload["skipped_count"],
        "pass_count": payload["pass_count"],
        "fail_count": payload["fail_count"],
        "matrix_run": _display_path(paths.matrix_run_path, repo_root, relative=emit_relative_paths),
        "matrix_summary": _display_path(paths.matrix_summary_path, repo_root, relative=emit_relative_paths),
        "artifact_root": _display_path(paths.artifact_root, repo_root, relative=emit_relative_paths),
        "benchmark_summary_json": _display_path(
            paths.benchmark_summary_json_path,
            repo_root,
            relative=emit_relative_paths,
        ),
        "benchmark_summary_markdown": _display_path(
            paths.benchmark_summary_markdown_path,
            repo_root,
            relative=emit_relative_paths,
        ),
        "modelwright_summary_json": _display_path(
            paths.modelwright_summary_json_path,
            repo_root,
            relative=emit_relative_paths,
        ),
    }


def _display_path(path: Path | None, repo_root: Path, *, relative: bool) -> str | None:
    if path is None:
        return None
    if not relative:
        return path.as_posix()
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _emit(payload: dict[str, Any], *, json_output: bool) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("FABLE benchmark matrix evidence")
        print(f"Evidence backend: {payload['evidence_backend']}")
        print(f"Evidence status: {payload['evidence_status']}")
        print(f"Equivalence status: {payload['equivalence_status']}")
        print(f"Cases: {payload['case_count']}")
        print(f"Benchmark summary JSON: {payload['benchmark_summary_json']}")
        print(f"Modelwright summary JSON: {payload['modelwright_summary_json']}")
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
