#!/usr/bin/env python
"""Run a FABLE scenario bundle and write rendered result artifacts."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import datetime, timezone
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
        bundle = _load_bundle(args.bundle)
        workbook_version = args.workbook_version or bundle.workbook_version
        build_paths = _build_paths(
            workbook_version=workbook_version,
            repo_root=repo_root,
            workbook_path=args.workbook_path,
        )
        generated_model_path = _generated_model_path(
            workbook_version=workbook_version,
            repo_root=repo_root,
            value=args.generated_model_path,
        )
        artifact_paths = _artifact_paths(
            workbook_version=workbook_version,
            bundle_id=bundle.bundle_id,
            repo_root=repo_root,
            output_dir=args.output_dir,
        )
        freshforge_paths = _freshforge_paths(
            workbook_version=workbook_version,
            bundle_id=bundle.bundle_id,
            repo_root=repo_root,
            output_dir=args.output_dir,
            workflow_path=args.workflow_path,
            run_summary_path=args.run_summary_path,
        )
        spec = _build_spec(build_paths.workbook_path, workbook_version=workbook_version)
        _validate_bundle(bundle, spec)
        render_overrides = _render_overrides(args)
        if args.freshforge_plan or args.freshforge_run:
            run_namespace = args.run_namespace or (_timestamp_namespace() if args.freshforge_run else None)
            plan = _prepare_freshforge_workflow(
                bundle,
                bundle_path=args.bundle,
                workbook_path=build_paths.workbook_path,
                generated_model_path=generated_model_path,
                paths=freshforge_paths,
                repo_root=repo_root,
                spec=spec,
                run_namespace=run_namespace,
            )
            run_payload = None
            if args.freshforge_run:
                run_result = _run_freshforge_workflow(plan, run_namespace=run_namespace)
                run_payload = _write_freshforge_summary(
                    run_result,
                    freshforge_paths,
                    run_namespace=run_namespace,
                    path=args.run_summary_path,
                )
            return _emit(
                _summary(
                    bundle=bundle,
                    repo_root=repo_root,
                    workbook_path=build_paths.workbook_path,
                    generated_model_path=generated_model_path,
                    artifact_paths=artifact_paths,
                    mode="freshforge-run" if args.freshforge_run else "freshforge-plan",
                    render_overrides=render_overrides,
                    manifest=None,
                    freshforge={
                        "workflow": _rel(freshforge_paths.workflow_path, repo_root),
                        "run_namespace": run_namespace,
                        "run_summary": (
                            _rel(Path(run_payload["run_summary"]), repo_root)
                            if run_payload is not None
                            else _rel(freshforge_paths.namespaced_run_summary_path(run_namespace), repo_root)
                        ),
                        "run": run_payload,
                        "node_count": len(plan.workflow.get("nodes", [])),
                    },
                ),
                json_output=args.json_output,
            )
        if args.dry_run:
            return _emit(
                _summary(
                    bundle=bundle,
                    repo_root=repo_root,
                    workbook_path=build_paths.workbook_path,
                    generated_model_path=generated_model_path,
                    artifact_paths=artifact_paths,
                    mode="dry-run",
                    render_overrides=render_overrides,
                    manifest=None,
                    freshforge=None,
                ),
                json_output=args.json_output,
            )
        if not generated_model_path.exists():
            raise FileNotFoundError(f"generated model not found: {generated_model_path}")
        generated_model = _load_generated_model(
            generated_model_path,
            module_name=f"fable_pyculator_generated_fable_{workbook_version}",
        )
        run_result = _run_bundle(generated_model, spec, bundle, **render_overrides)
        manifest = _write_artifacts(run_result, artifact_paths)
    except Exception as exc:  # noqa: BLE001
        return _fail(f"{type(exc).__name__}: {exc}", json_output=args.json_output)

    return _emit(
        _summary(
            bundle=bundle,
            repo_root=repo_root,
            workbook_path=build_paths.workbook_path,
            generated_model_path=generated_model_path,
            artifact_paths=artifact_paths,
            mode="run",
            render_overrides=render_overrides,
            manifest=manifest,
            freshforge=None,
        ),
        json_output=args.json_output,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a JSON/YAML FABLE scenario bundle against an existing generated model."
    )
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument("--bundle", required=True, type=Path, help="Scenario bundle JSON/YAML file.")
    parser.add_argument(
        "--workbook-version",
        default=None,
        help="Override bundle workbook_version, such as 2020 or 2021.",
    )
    parser.add_argument(
        "--workbook-path",
        default=None,
        help="Workbook path. Defaults to tmp/private-workbooks/{version}_Open_FABLECalculator.xlsx.",
    )
    parser.add_argument(
        "--generated-model-path",
        default=None,
        help="Generated model path. Defaults to tmp/generated-models/fable-{version}/generated_fable_{version}_model.py.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Artifact output directory. Defaults to tmp/scenario-runs/fable-{version}/{bundle_id}.",
    )
    parser.add_argument("--output-table-name", action="append", default=None, help="Render one output table name.")
    parser.add_argument("--headline-series-name", action="append", default=None, help="Render one headline series name.")
    parser.add_argument(
        "--column-flavour-tag",
        action="append",
        default=None,
        help="Output-table column flavour tag filter. May be repeated.",
    )
    parser.add_argument("--include-figures", action="store_true", help="Write headline PNG figures.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report planned artifacts without running.")
    parser.add_argument("--freshforge-plan", action="store_true", help="Write and report a FreshForge workflow without running it.")
    parser.add_argument("--freshforge-run", action="store_true", help="Run the scenario bundle through FreshForge.")
    parser.add_argument("--run-namespace", default=None, help="FreshForge run namespace. Defaults to a timestamp for --freshforge-run.")
    parser.add_argument("--workflow-path", default=None, help="FreshForge workflow JSON path.")
    parser.add_argument("--run-summary-path", default=None, help="FreshForge run summary JSON path.")
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


def _load_bundle(path: Path) -> Any:
    from fable_pyculator import load_scenario_bundle

    return load_scenario_bundle(path)


def _build_paths(**kwargs: Any) -> Any:
    from fable_pyculator import fable_freshforge_build_paths

    return fable_freshforge_build_paths(**kwargs)


def _artifact_paths(**kwargs: Any) -> Any:
    from fable_pyculator import fable_scenario_bundle_artifact_paths

    return fable_scenario_bundle_artifact_paths(**kwargs)


def _freshforge_paths(**kwargs: Any) -> Any:
    from fable_pyculator import fable_scenario_bundle_freshforge_paths

    return fable_scenario_bundle_freshforge_paths(**kwargs)


def _build_spec(workbook_path: Path, *, workbook_version: str) -> Any:
    from fable_pyculator import build_notebook_spec
    from fable_pyculator.workbook import suppress_benign_openpyxl_warnings

    with suppress_benign_openpyxl_warnings():
        return build_notebook_spec(workbook_path, workbook_id=f"fable-c-{workbook_version}")


def _validate_bundle(bundle: Any, spec: Any) -> Any:
    from fable_pyculator import validate_scenario_bundle

    return validate_scenario_bundle(bundle, spec)


def _load_generated_model(path: Path, *, module_name: str) -> Any:
    from fable_pyculator import load_generated_model

    return load_generated_model(path, module_name=module_name)


def _run_bundle(generated_model: Any, spec: Any, bundle: Any, **kwargs: Any) -> Any:
    from fable_pyculator import run_scenario_bundle

    return run_scenario_bundle(generated_model, spec, bundle, **kwargs)


def _write_artifacts(run_result: Any, artifact_paths: Any) -> dict[str, Any]:
    from fable_pyculator import write_scenario_bundle_artifacts

    return write_scenario_bundle_artifacts(run_result, artifact_paths)


def _prepare_freshforge_workflow(bundle: Any, **kwargs: Any) -> Any:
    from fable_pyculator import prepare_scenario_bundle_freshforge_workflow

    return prepare_scenario_bundle_freshforge_workflow(bundle, **kwargs)


def _run_freshforge_workflow(plan: Any, **kwargs: Any) -> Any:
    from fable_pyculator import run_scenario_bundle_freshforge_workflow

    return run_scenario_bundle_freshforge_workflow(plan, **kwargs)


def _write_freshforge_summary(run_result: Any, paths: Any, **kwargs: Any) -> dict[str, Any]:
    from fable_pyculator import write_scenario_bundle_freshforge_summary

    return write_scenario_bundle_freshforge_summary(run_result, paths, **kwargs)


def _generated_model_path(
    *,
    workbook_version: str,
    repo_root: Path,
    value: str | Path | None,
) -> Path:
    if value is not None:
        path = Path(value)
        return path if path.is_absolute() else repo_root / path
    return repo_root / f"tmp/generated-models/fable-{workbook_version}/generated_fable_{workbook_version}_model.py"


def _render_overrides(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "output_table_names": tuple(args.output_table_name) if args.output_table_name is not None else None,
        "headline_series_names": tuple(args.headline_series_name) if args.headline_series_name is not None else None,
        "output_table_column_flavour_tags": (
            args.column_flavour_tag[0]
            if args.column_flavour_tag is not None and len(args.column_flavour_tag) == 1
            else tuple(args.column_flavour_tag)
            if args.column_flavour_tag is not None
            else None
        ),
        "include_figures": True if args.include_figures else None,
    }


def _summary(
    *,
    bundle: Any,
    repo_root: Path,
    workbook_path: Path,
    generated_model_path: Path,
    artifact_paths: Any,
    mode: str,
    render_overrides: dict[str, Any],
    manifest: dict[str, Any] | None,
    freshforge: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "ok": True,
        "mode": mode,
        "bundle_id": bundle.bundle_id,
        "workbook_version": bundle.workbook_version,
        "scenario_count": len(bundle.scenarios),
        "artifacts": {
            "workbook": _rel(workbook_path, repo_root),
            "generated_model": _rel(generated_model_path, repo_root),
            "output_dir": _rel(artifact_paths.output_dir, repo_root),
            "normalized_bundle": _rel(artifact_paths.normalized_bundle_path, repo_root),
            "manifest": _rel(artifact_paths.manifest_path, repo_root),
        },
        "render_overrides": {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in render_overrides.items()
            if value is not None
        },
        "manifest": manifest,
        "freshforge": freshforge,
    }


def _emit(payload: dict[str, Any], *, json_output: bool) -> int:
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("FABLE scenario bundle")
        print(f"Mode: {payload['mode']}")
        print(f"Bundle: {payload['bundle_id']}")
        print(f"Scenarios: {payload['scenario_count']}")
        print("Artifacts:")
        for label, path in payload["artifacts"].items():
            print(f"- {label}: {path}")
        if payload.get("freshforge") is not None:
            print("FreshForge:")
            print(f"- workflow: {payload['freshforge']['workflow']}")
            print(f"- namespace: {payload['freshforge']['run_namespace']}")
            print(f"- run summary: {payload['freshforge']['run_summary']}")
    return 0


def _fail(message: str, *, json_output: bool) -> int:
    payload = {"ok": False, "error": message}
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)
    return 1


def _rel(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _timestamp_namespace() -> str:
    return datetime.now(timezone.utc).strftime("run/%Y%m%dT%H%M%SZ")


if __name__ == "__main__":
    raise SystemExit(main())
