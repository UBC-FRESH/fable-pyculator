#!/usr/bin/env python
"""Run the opt-in FABLE benchmark evidence orchestration command."""

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
            fable_benchmark_run_paths,
            package_fable_benchmark_evidence,
            write_fable_benchmark_summary,
        )

        paths = fable_benchmark_run_paths(
            workbook_version=args.workbook_version,
            repo_root=repo_root,
            artifact_dir=args.artifact_dir,
            output_dir=args.output_dir,
        )
        summary = package_fable_benchmark_evidence(
            workbook_version=args.workbook_version,
            repo_root=repo_root,
            artifact_dir=args.artifact_dir,
            output_dir=args.output_dir,
            mode=args.mode,
            require_artifacts=args.require_artifacts,
            output_ref_strategy=args.output_ref_strategy,
            workbook_path=args.workbook_path,
            run_namespace=args.run_namespace,
            bundle_path=args.bundle,
            include_scenario_bundle_summary=args.include_scenario_bundle_summary,
        )
        payload = write_fable_benchmark_summary(summary, paths)
    except Exception as exc:  # noqa: BLE001
        return _fail(f"{type(exc).__name__}: {exc}", json_output=args.json_output)

    emit_relative_paths = args.artifact_dir is None and args.output_dir is None
    return _emit(
        _script_payload(payload, paths, repo_root, emit_relative_paths=emit_relative_paths),
        json_output=args.json_output,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package compact FABLE benchmark evidence and optionally prepare/run FreshForge."
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument("--workbook-version", default="2021", help="FABLE workbook version. Defaults to 2021.")
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="Input/generated artifact directory. Defaults to tmp/generated-models/fable-{version}.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Compact evidence output directory. Defaults to tmp/validation-evidence/fable-{version}.",
    )
    parser.add_argument(
        "--mode",
        choices=("evidence-only", "freshforge-plan", "freshforge-run"),
        default="evidence-only",
        help="Benchmark orchestration mode. Defaults to evidence-only.",
    )
    parser.add_argument(
        "--require-artifacts",
        action="store_true",
        help="Fail if expected local artifacts are missing. Defaults to skipped evidence.",
    )
    parser.add_argument(
        "--output-ref-strategy",
        default="output-columns",
        choices=("output-columns", "headline-only", "table", "flavour-tags", "all-columns"),
        help="FreshForge preparation output-ref strategy. Defaults to output-columns.",
    )
    parser.add_argument(
        "--workbook-path",
        default=None,
        help="Source workbook path for FreshForge plan/run modes. Defaults to tmp/private-workbooks/{version}_Open_FABLECalculator.xlsx.",
    )
    parser.add_argument("--bundle", default=None, help="Optional scenario bundle path to mention in the benchmark summary.")
    parser.add_argument(
        "--include-scenario-bundle-summary",
        action="store_true",
        help="Ingest a compact scenario-bundle FreshForge summary beside the bundle when present.",
    )
    parser.add_argument("--run-namespace", default=None, help="FreshForge run namespace for explicit run mode.")
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
        "mode": payload["mode"],
        "evidence_backend": payload["evidence_backend"],
        "evidence_status": payload["evidence_status"],
        "equivalence_status": payload["equivalence_status"],
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
        "validation_summary_json": _display_path(
            paths.validation_summary_json_path,
            repo_root,
            relative=emit_relative_paths,
        ),
        "missing_artifacts": payload["missing_artifacts"],
        "comparison": payload["comparison"],
        "freshforge": payload["freshforge"],
        "scenario_bundle": payload["scenario_bundle"],
    }


def _emit(payload: dict[str, Any], *, json_output: bool) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("FABLE benchmark evidence")
        print(f"Mode: {payload['mode']}")
        print(f"Evidence backend: {payload['evidence_backend']}")
        print(f"Evidence status: {payload['evidence_status']}")
        print(f"Equivalence status: {payload['equivalence_status']}")
        print(f"Benchmark summary JSON: {payload['benchmark_summary_json']}")
        print(f"Benchmark summary Markdown: {payload['benchmark_summary_markdown']}")
        if payload["missing_artifacts"]:
            print("Missing artifacts:")
            for name in payload["missing_artifacts"]:
                print(f"- {name}")
    return 0


def _fail(message: str, *, json_output: bool) -> int:
    payload = {"ok": False, "error": message}
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)
    return 1


def _display_path(path: Path, repo_root: Path, *, relative: bool) -> str:
    if not relative:
        return path.as_posix()
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
