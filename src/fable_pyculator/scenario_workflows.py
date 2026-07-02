"""FreshForge orchestration helpers for FABLE scenario bundles."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import yaml

from fable_pyculator.scenarios import (
    ScenarioBundle,
    ScenarioBundleArtifactPaths,
    fable_scenario_bundle_artifact_paths,
    validate_scenario_bundle,
)
from fable_pyculator.workflows import fable_freshforge_build_paths


DEFAULT_SCENARIO_BUNDLE_WORKFLOW_FILENAME = "freshforge-scenario-bundle-workflow.json"
DEFAULT_SCENARIO_BUNDLE_RUN_SUMMARY_FILENAME = "freshforge-run-summary.json"
DEFAULT_SCENARIO_BUNDLE_MATRIX_FILENAME = "freshforge-scenario-bundle-matrix.yaml"
DEFAULT_SCENARIO_BUNDLE_MATRIX_TEMPLATE_FILENAME = "freshforge-scenario-bundle-matrix-template.yaml"
DEFAULT_SCENARIO_BUNDLE_MATRIX_SUMMARY_FILENAME = "freshforge-matrix-summary.json"


@dataclass(frozen=True)
class ScenarioBundleFreshForgePaths:
    """Ignored local paths for FreshForge-backed scenario-bundle orchestration."""

    scenario_paths: ScenarioBundleArtifactPaths
    workflow_path: Path
    run_summary_path: Path

    @property
    def output_dir(self) -> Path:
        """Return the scenario-bundle output root used as the FreshForge workdir."""

        return self.scenario_paths.output_dir

    def namespaced_run_summary_path(self, run_namespace: str | None = None) -> Path:
        """Return the run-summary path for a namespace-aware FreshForge run."""

        if run_namespace is None:
            return self.run_summary_path
        return self.output_dir / run_namespace / self.run_summary_path.name


@dataclass(frozen=True)
class ScenarioBundleFreshForgePlan:
    """Prepared FreshForge workflow for a FABLE scenario bundle."""

    bundle: ScenarioBundle
    paths: ScenarioBundleFreshForgePaths
    workflow: dict[str, Any]
    run_namespace: str | None = None


@dataclass(frozen=True)
class ScenarioBundleFreshForgeMatrixPaths:
    """Ignored local paths for FreshForge matrix scenario-bundle orchestration."""

    scenario_paths: ScenarioBundleArtifactPaths
    matrix_path: Path
    workflow_template_path: Path
    matrix_summary_path: Path

    @property
    def output_dir(self) -> Path:
        """Return the scenario-bundle output root used as the FreshForge matrix workdir."""

        return self.scenario_paths.output_dir


@dataclass(frozen=True)
class ScenarioBundleFreshForgeMatrixPlan:
    """Prepared FreshForge matrix for a FABLE scenario bundle."""

    bundle: ScenarioBundle
    paths: ScenarioBundleFreshForgeMatrixPaths
    matrix: dict[str, Any]
    workflow_template: dict[str, Any]
    case_count: int


def fable_scenario_bundle_freshforge_paths(
    *,
    workbook_version: str,
    bundle_id: str,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    workflow_path: str | Path | None = None,
    run_summary_path: str | Path | None = None,
) -> ScenarioBundleFreshForgePaths:
    """Return default paths for FreshForge-backed scenario-bundle orchestration."""

    scenario_paths = fable_scenario_bundle_artifact_paths(
        workbook_version=workbook_version,
        bundle_id=bundle_id,
        repo_root=repo_root,
        output_dir=output_dir,
    )
    workflow = (
        Path(workflow_path)
        if workflow_path is not None
        else scenario_paths.output_dir / DEFAULT_SCENARIO_BUNDLE_WORKFLOW_FILENAME
    )
    run_summary = (
        Path(run_summary_path)
        if run_summary_path is not None
        else scenario_paths.output_dir / DEFAULT_SCENARIO_BUNDLE_RUN_SUMMARY_FILENAME
    )
    root = Path(repo_root)
    return ScenarioBundleFreshForgePaths(
        scenario_paths=scenario_paths,
        workflow_path=workflow if workflow.is_absolute() else root / workflow,
        run_summary_path=run_summary if run_summary.is_absolute() else root / run_summary,
    )


def fable_scenario_bundle_freshforge_matrix_paths(
    *,
    workbook_version: str,
    bundle_id: str,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    matrix_path: str | Path | None = None,
    workflow_template_path: str | Path | None = None,
    matrix_summary_path: str | Path | None = None,
) -> ScenarioBundleFreshForgeMatrixPaths:
    """Return default paths for FreshForge matrix scenario-bundle orchestration."""

    scenario_paths = fable_scenario_bundle_artifact_paths(
        workbook_version=workbook_version,
        bundle_id=bundle_id,
        repo_root=repo_root,
        output_dir=output_dir,
    )
    matrix = (
        Path(matrix_path)
        if matrix_path is not None
        else scenario_paths.output_dir / DEFAULT_SCENARIO_BUNDLE_MATRIX_FILENAME
    )
    template = (
        Path(workflow_template_path)
        if workflow_template_path is not None
        else scenario_paths.output_dir / DEFAULT_SCENARIO_BUNDLE_MATRIX_TEMPLATE_FILENAME
    )
    summary = (
        Path(matrix_summary_path)
        if matrix_summary_path is not None
        else scenario_paths.output_dir / DEFAULT_SCENARIO_BUNDLE_MATRIX_SUMMARY_FILENAME
    )
    root = Path(repo_root)
    return ScenarioBundleFreshForgeMatrixPaths(
        scenario_paths=scenario_paths,
        matrix_path=matrix if matrix.is_absolute() else root / matrix,
        workflow_template_path=template if template.is_absolute() else root / template,
        matrix_summary_path=summary if summary.is_absolute() else root / summary,
    )


def prepare_scenario_bundle_freshforge_workflow(
    bundle: ScenarioBundle,
    *,
    bundle_path: str | Path,
    workbook_path: str | Path,
    generated_model_path: str | Path,
    paths: ScenarioBundleFreshForgePaths,
    repo_root: str | Path = ".",
    workbook_id: str | None = None,
    module_name: str | None = None,
    run_namespace: str | None = None,
    spec: Any | None = None,
) -> ScenarioBundleFreshForgePlan:
    """Write a FreshForge workflow for a FABLE scenario bundle without running it."""

    if spec is not None:
        validate_scenario_bundle(bundle, spec)
    root = Path(repo_root).resolve()
    bundle_source = _resolve_path(bundle_path, root)
    workbook = _resolve_path(workbook_path, root)
    generated_model = _resolve_path(generated_model_path, root)
    resolved_workbook_id = workbook_id or f"fable-c-{bundle.workbook_version}"
    resolved_module_name = module_name or f"fable_pyculator_generated_fable_{bundle.workbook_version}"
    workflow = build_scenario_bundle_freshforge_workflow(
        bundle,
        bundle_path=bundle_source,
        workbook_path=workbook,
        generated_model_path=generated_model,
        workbook_id=resolved_workbook_id,
        module_name=resolved_module_name,
    )
    _write_json(paths.workflow_path, workflow)
    return ScenarioBundleFreshForgePlan(
        bundle=bundle,
        paths=paths,
        workflow=workflow,
        run_namespace=run_namespace,
    )


def build_scenario_bundle_freshforge_workflow(
    bundle: ScenarioBundle,
    *,
    bundle_path: str | Path,
    workbook_path: str | Path,
    generated_model_path: str | Path,
    workbook_id: str,
    module_name: str,
) -> dict[str, Any]:
    """Build a FreshForge workflow document for one scenario bundle."""

    bundle_path_parameter = str(bundle_path)
    common_parameters = {
        "bundle_path": bundle_path_parameter,
        "workbook_path": str(workbook_path),
        "workbook_id": workbook_id,
        "generated_model_path": str(generated_model_path),
        "module_name": module_name,
    }
    nodes: list[dict[str, Any]] = [
        {
            "id": "prepare_bundle",
            "provider": "fable_pyculator.scenario_bundle_prepare",
            "outputs": {"bundle": "bundle"},
            "parameters": {
                "bundle_path": bundle_path_parameter,
                "workbook_path": str(workbook_path),
                "workbook_id": workbook_id,
            },
            "artifacts": {
                "normalized_bundle": "bundle.json",
                "prepare_summary": "prepare.json",
            },
        }
    ]
    for scenario in bundle.scenarios:
        nodes.append(
            {
                "id": f"scenario_{scenario.scenario_id}",
                "provider": "fable_pyculator.scenario_run",
                "needs": ["prepare_bundle"],
                "inputs": {"bundle": "prepare_bundle.bundle"},
                "outputs": {"scenario_result": scenario.scenario_id},
                "parameters": {
                    **common_parameters,
                    "scenario_id": scenario.scenario_id,
                },
                "artifacts": {
                    "scenario_summary": f"scenarios/{scenario.scenario_id}/scenario.json",
                    "scenario_inputs": f"scenarios/{scenario.scenario_id}/scenario_inputs.csv",
                    "output_tables": f"scenarios/{scenario.scenario_id}/output_tables",
                    "headline_frames": f"scenarios/{scenario.scenario_id}/headline_frames",
                    "headline_figures": f"scenarios/{scenario.scenario_id}/headline_figures",
                },
            }
        )
    nodes.append(
        {
            "id": "bundle_manifest",
            "provider": "fable_pyculator.scenario_bundle_manifest",
            "needs": [f"scenario_{scenario.scenario_id}" for scenario in bundle.scenarios],
            "inputs": {
                f"scenario_{scenario.scenario_id}": f"scenario_{scenario.scenario_id}.scenario_result"
                for scenario in bundle.scenarios
            },
            "outputs": {"manifest": "manifest"},
            "parameters": {
                "bundle_path": bundle_path_parameter,
            },
            "artifacts": {
                "manifest": "manifest.json",
            },
        }
    )
    return {
        "workflow": {
            "id": f"fable_{bundle.workbook_version}_{bundle.bundle_id}_scenario_bundle",
            "name": f"FABLE {bundle.workbook_version} scenario bundle: {bundle.bundle_id}",
            "description": "FreshForge-backed FABLE Pyculator scenario-bundle run.",
        },
        "parameters": {"bundle_path": bundle_path_parameter},
        "nodes": nodes,
    }

def prepare_scenario_bundle_freshforge_matrix(
    bundle: ScenarioBundle,
    *,
    bundle_path: str | Path,
    workbook_path: str | Path,
    generated_model_path: str | Path,
    paths: ScenarioBundleFreshForgeMatrixPaths,
    repo_root: str | Path = ".",
    workbook_id: str | None = None,
    module_name: str | None = None,
    spec: Any | None = None,
) -> ScenarioBundleFreshForgeMatrixPlan:
    """Write a FreshForge matrix for one scenario-bundle case per scenario."""

    if spec is not None:
        validate_scenario_bundle(bundle, spec)
    root = Path(repo_root).resolve()
    bundle_source = _resolve_path(bundle_path, root)
    workbook = _resolve_path(workbook_path, root)
    generated_model = _resolve_path(generated_model_path, root)
    resolved_workbook_id = workbook_id or f"fable-c-{bundle.workbook_version}"
    resolved_module_name = module_name or f"fable_pyculator_generated_fable_{bundle.workbook_version}"
    template = build_scenario_bundle_freshforge_matrix_template()
    matrix = build_scenario_bundle_freshforge_matrix(
        bundle,
        template_path=paths.workflow_template_path,
        matrix_path=paths.matrix_path,
        bundle_path=bundle_source,
        workbook_path=workbook,
        generated_model_path=generated_model,
        workbook_id=resolved_workbook_id,
        module_name=resolved_module_name,
    )
    _write_yaml(paths.workflow_template_path, template)
    _write_yaml(paths.matrix_path, matrix)
    return ScenarioBundleFreshForgeMatrixPlan(
        bundle=bundle,
        paths=paths,
        matrix=matrix,
        workflow_template=template,
        case_count=len(bundle.scenarios),
    )


def build_scenario_bundle_freshforge_matrix(
    bundle: ScenarioBundle,
    *,
    template_path: str | Path,
    matrix_path: str | Path,
    bundle_path: str | Path,
    workbook_path: str | Path,
    generated_model_path: str | Path,
    workbook_id: str,
    module_name: str,
) -> dict[str, Any]:
    """Build a FreshForge matrix document for one scenario bundle."""

    matrix_parent = Path(matrix_path).parent
    return {
        "matrix": {
            "id": f"fable_{bundle.workbook_version}_{bundle.bundle_id}_scenario_matrix",
            "name": f"FABLE {bundle.workbook_version} scenario matrix: {bundle.bundle_id}",
            "description": "FreshForge matrix for FABLE Pyculator scenario-bundle cases.",
            "workflow_template": _path_relative_to(Path(template_path), matrix_parent),
        },
        "cases": [
            {
                "id": scenario.scenario_id,
                "namespace": f"scenario/{scenario.scenario_id}",
                "variables": {
                    "scenario_id": scenario.scenario_id,
                    "scenario_label": scenario.label or scenario.scenario_id,
                    "bundle_path": str(bundle_path),
                    "workbook_path": str(workbook_path),
                    "workbook_id": workbook_id,
                    "generated_model_path": str(generated_model_path),
                    "module_name": module_name,
                },
            }
            for scenario in bundle.scenarios
        ],
    }


def build_scenario_bundle_freshforge_matrix_template() -> dict[str, Any]:
    """Build the FreshForge matrix workflow template for one scenario case."""

    return {
        "workflow": {
            "id": "fable_scenario_${matrix.scenario_id}",
            "name": "FABLE scenario ${matrix.scenario_label}",
            "description": "FreshForge-backed FABLE Pyculator scenario-bundle matrix case.",
        },
        "nodes": [
            {
                "id": "prepare_bundle",
                "provider": "fable_pyculator.scenario_bundle_prepare",
                "outputs": {"bundle": "bundle"},
                "parameters": {
                    "bundle_path": "${matrix.bundle_path}",
                    "workbook_path": "${matrix.workbook_path}",
                    "workbook_id": "${matrix.workbook_id}",
                },
                "artifacts": {
                    "normalized_bundle": "bundle.json",
                    "prepare_summary": "prepare.json",
                },
            },
            {
                "id": "scenario_${matrix.scenario_id}",
                "provider": "fable_pyculator.scenario_run",
                "needs": ["prepare_bundle"],
                "inputs": {"bundle": "prepare_bundle.bundle"},
                "outputs": {"scenario_result": "${matrix.scenario_id}"},
                "parameters": {
                    "bundle_path": "${matrix.bundle_path}",
                    "workbook_path": "${matrix.workbook_path}",
                    "workbook_id": "${matrix.workbook_id}",
                    "generated_model_path": "${matrix.generated_model_path}",
                    "module_name": "${matrix.module_name}",
                    "scenario_id": "${matrix.scenario_id}",
                },
                "artifacts": {
                    "scenario_summary": "scenarios/${matrix.scenario_id}/scenario.json",
                    "scenario_inputs": "scenarios/${matrix.scenario_id}/scenario_inputs.csv",
                    "output_tables": "scenarios/${matrix.scenario_id}/output_tables",
                    "headline_frames": "scenarios/${matrix.scenario_id}/headline_frames",
                    "headline_figures": "scenarios/${matrix.scenario_id}/headline_figures",
                },
            },
            {
                "id": "bundle_manifest",
                "provider": "fable_pyculator.scenario_bundle_manifest",
                "needs": ["scenario_${matrix.scenario_id}"],
                "inputs": {"scenario_${matrix.scenario_id}": "scenario_${matrix.scenario_id}.scenario_result"},
                "outputs": {"manifest": "manifest"},
                "parameters": {
                    "bundle_path": "${matrix.bundle_path}",
                },
                "artifacts": {
                    "manifest": "manifest.json",
                },
            },
        ],
    }
def run_scenario_bundle_freshforge_workflow(
    plan: ScenarioBundleFreshForgePlan,
    *,
    run_namespace: str | None = None,
    registry: Any | None = None,
) -> Any:
    """Run a prepared scenario-bundle FreshForge workflow."""

    try:
        from freshforge.execution import run_workflow  # type: ignore[import-untyped]
        from freshforge.validation import validate_workflow_document  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError("FreshForge is required for FreshForge-backed scenario-bundle runs.") from exc

    spec, diagnostics = validate_workflow_document(plan.workflow)
    if spec is None:
        raise RuntimeError("FreshForge could not validate the scenario-bundle workflow.")
    return run_workflow(
        spec,
        diagnostics=diagnostics,
        registry=registry,
        workdir=plan.paths.output_dir,
        run_namespace=run_namespace if run_namespace is not None else plan.run_namespace,
    )


def write_scenario_bundle_freshforge_summary(
    run_result: Any,
    paths: ScenarioBundleFreshForgePaths,
    *,
    run_namespace: str | None = None,
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Write a compact FreshForge run summary for a scenario-bundle workflow."""

    summary = run_result.summary()
    destination = (
        Path(path)
        if path is not None
        else paths.namespaced_run_summary_path(run_namespace or run_result.run_namespace)
    )
    payload = {
        "run": run_result.to_dict(),
        "summary": summary.to_dict(),
    }
    _write_json(destination, payload)
    return {
        "run_summary": str(destination),
        "status": summary.to_dict()["status"],
        "run_namespace": summary.to_dict()["run_namespace"],
        "node_count": summary.to_dict()["node_count"],
        "failed_count": summary.to_dict()["failed_count"],
        "error_count": summary.to_dict()["error_count"],
    }


def plan_scenario_bundle_freshforge_matrix(plan: ScenarioBundleFreshForgeMatrixPlan) -> dict[str, Any]:
    """Plan a prepared FreshForge scenario-bundle matrix."""

    try:
        from freshforge.matrix import load_workflow_matrix, plan_workflow_matrix  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError("FreshForge with matrix support is required for scenario-bundle matrix planning.") from exc

    matrix, diagnostics = load_workflow_matrix(plan.paths.matrix_path)
    if matrix is None:
        return {"ok": False, "matrix": None, "diagnostics": [diagnostic.to_dict() for diagnostic in diagnostics]}
    matrix_plan = plan_workflow_matrix(matrix, diagnostics=diagnostics)
    return {"ok": matrix_plan.ok, "matrix": matrix.to_dict(), "plan": matrix_plan.to_dict()}


def run_scenario_bundle_freshforge_matrix(
    plan: ScenarioBundleFreshForgeMatrixPlan,
    *,
    registry: Any | None = None,
    fail_fast: bool = False,
) -> Any:
    """Run a prepared FreshForge scenario-bundle matrix."""

    try:
        from freshforge.matrix import load_workflow_matrix, run_workflow_matrix  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError("FreshForge with matrix support is required for scenario-bundle matrix runs.") from exc

    matrix, diagnostics = load_workflow_matrix(plan.paths.matrix_path)
    if matrix is None:
        raise RuntimeError("FreshForge could not validate the scenario-bundle matrix.")
    return run_workflow_matrix(
        matrix,
        diagnostics=diagnostics,
        registry=registry,
        workdir=plan.paths.output_dir,
        fail_fast=fail_fast,
    )


def write_scenario_bundle_freshforge_matrix_summary(
    run_result: Any,
    paths: ScenarioBundleFreshForgeMatrixPaths,
    *,
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Write a compact FreshForge matrix summary for a scenario-bundle matrix run."""

    summary = run_result.summary()
    destination = Path(path) if path is not None else paths.matrix_summary_path
    payload = {
        "run": run_result.to_dict(),
        "summary": summary.to_dict(),
    }
    _write_json(destination, payload)
    summary_dict = summary.to_dict()
    return {
        "matrix_summary": str(destination),
        "status": summary_dict["status"],
        "case_count": summary_dict["case_count"],
        "failed_count": summary_dict["failed_count"],
        "error_count": summary_dict["error_count"],
    }


def default_generated_model_path(
    *,
    workbook_version: str,
    repo_root: str | Path = ".",
) -> Path:
    """Return the default generated-model path for a scenario-bundle workflow."""

    return fable_freshforge_build_paths(workbook_version=workbook_version, repo_root=repo_root).generated_model_path


def _resolve_path(path: str | Path, root: Path) -> Path:
    value = Path(path)
    return value if value.is_absolute() else root / value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_yaml(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _path_relative_to(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
