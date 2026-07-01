#!/usr/bin/env python
"""Package compact FABLE validation evidence from restored local artifacts."""

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
        paths = _paths(
            workbook_version=args.workbook_version,
            repo_root=repo_root,
            artifact_dir=args.artifact_dir,
            output_dir=args.output_dir,
        )
        summary = _extract(
            paths,
            workbook_version=args.workbook_version,
            require_artifacts=args.require_artifacts,
        )
        payload = _write(summary, paths)
    except Exception as exc:  # noqa: BLE001
        return _fail(f"{type(exc).__name__}: {exc}", json_output=args.json_output)

    emit_relative_paths = args.artifact_dir is None and args.output_dir is None
    return _emit(
        _script_payload(payload, paths, repo_root, emit_relative_paths=emit_relative_paths),
        json_output=args.json_output,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package compact FABLE validation evidence from existing local generated-model artifacts."
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument("--workbook-version", default="2021", help="FABLE workbook version. Defaults to 2021.")
    parser.add_argument(
        "--artifact-dir",
        default=None,
        help="Input artifact directory. Defaults to tmp/generated-models/fable-{version}.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory. Defaults to tmp/validation-evidence/fable-{version}.",
    )
    parser.add_argument(
        "--require-artifacts",
        action="store_true",
        help="Fail if expected input artifacts are missing. Defaults to skipped evidence.",
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


def _paths(**kwargs: Any) -> Any:
    from fable_pyculator import fable_validation_evidence_paths

    return fable_validation_evidence_paths(**kwargs)


def _extract(paths: Any, *, workbook_version: str, require_artifacts: bool) -> Any:
    from fable_pyculator import extract_validation_evidence

    return extract_validation_evidence(paths, workbook_version=workbook_version, require_artifacts=require_artifacts)


def _write(summary: Any, paths: Any) -> dict[str, Any]:
    from fable_pyculator import write_validation_evidence

    return write_validation_evidence(summary, paths)


def _script_payload(
    payload: dict[str, Any],
    paths: Any,
    repo_root: Path,
    *,
    emit_relative_paths: bool,
) -> dict[str, Any]:
    return {
        "ok": True,
        "evidence_status": payload["evidence_status"],
        "equivalence_status": payload["equivalence_status"],
        "workbook_version": payload["workbook_version"],
        "summary_json": _display_path(paths.summary_json_path, repo_root, relative=emit_relative_paths),
        "summary_markdown": _display_path(paths.summary_markdown_path, repo_root, relative=emit_relative_paths),
        "missing_artifacts": payload["missing_artifacts"],
        "comparison": payload["comparison"],
    }


def _emit(payload: dict[str, Any], *, json_output: bool) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("FABLE validation evidence")
        print(f"Evidence status: {payload['evidence_status']}")
        print(f"Equivalence status: {payload['equivalence_status']}")
        print(f"Summary JSON: {payload['summary_json']}")
        print(f"Summary Markdown: {payload['summary_markdown']}")
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
