#!/usr/bin/env python
"""Prepare and optionally run the 2021 FABLE FreshForge rebuild workflow."""

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
    table_names = tuple(args.table_name) if args.table_name else None
    column_flavour_tags: str | tuple[str, ...] | None
    if args.all_columns:
        column_flavour_tags = None
    else:
        requested_tags = args.column_flavour_tag or ["OUTPUT-*"]
        if len(requested_tags) == 1:
            column_flavour_tags = requested_tags[0]
        else:
            column_flavour_tags = tuple(requested_tags)

    try:
        plan = _prepare_rebuild(
            repo_root=repo_root,
            workbook_path=args.workbook_path,
            artifact_dir=args.artifact_dir,
            workflow_filename=args.workflow_filename,
            column_flavour_tags=column_flavour_tags,
            table_names=table_names,
            module_name=args.module_name,
            workflow_id=args.workflow_id,
            workflow_name=args.workflow_name,
            workflow_description=args.workflow_description,
            scenario_id=args.scenario_id,
            scenario_description=args.scenario_description,
            numeric_tolerance=args.numeric_tolerance,
        )
    except Exception as exc:  # noqa: BLE001
        return _fail(f"{type(exc).__name__}: {exc}", json_output=args.json_output)

    run_payload: dict[str, Any] | None = None
    if args.run:
        try:
            run_payload = _run_freshforge(plan.paths.workflow_path, workdir=repo_root)
        except Exception as exc:  # noqa: BLE001
            return _fail(f"FreshForge run failed: {type(exc).__name__}: {exc}", json_output=args.json_output)
        if not run_payload["ok"]:
            return _emit(_summary(plan, repo_root, run_payload=run_payload), args.json_output, exit_code=1)

    return _emit(_summary(plan, repo_root, run_payload=run_payload), args.json_output)


def _prepare_rebuild(**kwargs: Any) -> Any:
    from fable_pyculator import prepare_2021_freshforge_rebuild

    return prepare_2021_freshforge_rebuild(**kwargs)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare the 2021 FABLE output refs, cached-workbook validation scenario, and "
            "Modelwright FreshForge workflow. Use --run to execute the FreshForge workflow."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument(
        "--workbook-path",
        default="tmp/private-workbooks/2021_Open_FABLECalculator.xlsx",
        help="2021 workbook path, relative to repo root unless absolute.",
    )
    parser.add_argument(
        "--artifact-dir",
        default="tmp/generated-models/fable-2021",
        help="Ignored artifact directory, relative to repo root unless absolute.",
    )
    parser.add_argument(
        "--workflow-filename",
        default="freshforge-modelwright-run-workflow.json",
        help="FreshForge workflow JSON filename inside the artifact directory.",
    )
    parser.add_argument(
        "--column-flavour-tag",
        action="append",
        default=None,
        help=(
            "Output-table column flavour tag filter. May be repeated. Supports exact tags, DATA/OUTPUT "
            "family aliases, and trailing-star wildcards. Defaults to OUTPUT-*."
        ),
    )
    parser.add_argument(
        "--all-columns",
        action="store_true",
        help="Use every output-table column instead of filtering by column flavour tag.",
    )
    parser.add_argument(
        "--table-name",
        action="append",
        default=[],
        help="Restrict output refs to one output table name. May be repeated.",
    )
    parser.add_argument("--module-name", default="generated_fable_2021_model")
    parser.add_argument("--workflow-id", default="fable_2021_modelwright_run")
    parser.add_argument("--workflow-name", default="FABLE 2021 Modelwright FreshForge run")
    parser.add_argument(
        "--workflow-description",
        default="FreshForge graph for rebuilding the 2021 FABLE generated model.",
    )
    parser.add_argument("--scenario-id", default="fable-c-2021-freshforge-rebuild")
    parser.add_argument(
        "--scenario-description",
        default="Cached-workbook validation slice derived from FABLE Pyculator output refs.",
    )
    parser.add_argument("--numeric-tolerance", type=float, default=1e-9)
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute the FreshForge workflow after writing artifacts. Omit for plan-only preparation.",
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


def _run_freshforge(workflow_path: Path, *, workdir: Path) -> dict[str, Any]:
    try:
        from fable_pyculator.workbook import suppress_benign_openpyxl_warnings
        from freshforge.execution import run_workflow
        from freshforge.loading import load_workflow
    except ImportError as exc:
        raise RuntimeError(
            "FreshForge is not installed in the active environment. Install FreshForge before using --run."
        ) from exc

    spec, diagnostics = load_workflow(workflow_path)
    if spec is None:
        return {"ok": False, "run": None, "diagnostics": [diagnostic.to_dict() for diagnostic in diagnostics]}
    with suppress_benign_openpyxl_warnings():
        result = run_workflow(spec, diagnostics=diagnostics, workdir=workdir)
    return {"ok": result.ok, "run": result.to_dict()}


def _summary(plan: Any, repo_root: Path, *, run_payload: dict[str, Any] | None) -> dict[str, Any]:
    paths = plan.paths

    def rel(path: Path) -> str:
        try:
            return str(path.relative_to(repo_root))
        except ValueError:
            return str(path)

    return {
        "ok": run_payload["ok"] if run_payload is not None else True,
        "mode": "run" if run_payload is not None else "plan",
        "output_ref_count": len(plan.output_refs),
        "comparable_output_count": plan.comparable_output_count,
        "artifacts": {
            "workbook": rel(paths.workbook_path),
            "artifact_dir": rel(paths.artifact_dir),
            "output_refs": rel(paths.output_refs_path),
            "validation_scenario": rel(paths.validation_scenario_path),
            "workflow": rel(paths.workflow_path),
            "contract": rel(paths.contract_path),
            "expressions": rel(paths.expressions_path),
            "constants": rel(paths.constants_path),
            "generated_model": rel(paths.generated_model_path),
            "generated_values": rel(paths.generated_values_path),
            "evaluation_report": rel(paths.evaluation_report_path),
        },
        "run": run_payload,
    }


def _emit(payload: dict[str, Any], json_output: bool, *, exit_code: int = 0) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("FABLE 2021 FreshForge rebuild")
        print(f"Mode: {payload['mode']}")
        print(f"Output refs: {payload['output_ref_count']:,}")
        print(f"Comparable validation outputs: {payload['comparable_output_count']:,}")
        print("Artifacts:")
        for label, path in payload["artifacts"].items():
            print(f"- {label}: {path}")
        if payload["mode"] == "plan":
            print("\nPlan-only preparation complete. Re-run with --run to execute FreshForge.")
        elif payload["ok"]:
            print("\nFreshForge run completed successfully.")
        else:
            print("\nFreshForge run failed.")
    return exit_code


def _fail(message: str, *, json_output: bool) -> int:
    payload = {"ok": False, "error": message}
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
