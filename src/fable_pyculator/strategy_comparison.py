"""Compare FABLE output-ref strategies before generated-model rebuilds.

This module prepares compact, local comparison artifacts for different FABLE output-ref boundaries.
It does not run FreshForge or Modelwright and does not claim generated-model equivalence.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

import yaml

from fable_pyculator.spec import FableCalculatorSpec
from fable_pyculator.workflows import (
    DEFAULT_WORKFLOW_FILENAME,
    OutputRefStrategy,
    build_cached_workbook_validation_scenario,
    build_modelwright_freshforge_workflow,
    derive_output_refs_for_strategy,
    fable_freshforge_build_paths,
    write_freshforge_workflow,
    write_output_refs,
    write_validation_scenario,
)


@dataclass(frozen=True)
class OutputRefStrategyCase:
    """One named output-ref boundary to compare."""

    case_id: str
    strategy: OutputRefStrategy
    label: str
    column_flavour_tags: str | tuple[str, ...] | None = "OUTPUT-*"
    table_names: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "table_names", tuple(self.table_names))
        if isinstance(self.column_flavour_tags, list):
            object.__setattr__(self, "column_flavour_tags", tuple(self.column_flavour_tags))

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON representation."""

        return {
            "case_id": self.case_id,
            "strategy": self.strategy,
            "label": self.label,
            "column_flavour_tags": self.column_flavour_tags,
            "table_names": list(self.table_names),
            "description": self.description,
        }


@dataclass(frozen=True)
class OutputRefStrategyComparisonPaths:
    """Path layout for one strategy-comparison run."""

    workbook_version: str
    output_dir: Path
    summary_json_path: Path
    summary_markdown_path: Path

    def case_dir(self, case_id: str) -> Path:
        """Return the per-case artifact directory."""

        return self.output_dir / case_id

    def output_refs_path(self, case_id: str) -> Path:
        """Return the per-case output refs JSON path."""

        return self.case_dir(case_id) / "output_refs.json"

    def workflow_path(self, case_id: str) -> Path:
        """Return the per-case FreshForge workflow JSON path."""

        return self.case_dir(case_id) / DEFAULT_WORKFLOW_FILENAME

    @property
    def matrix_path(self) -> Path:
        """Return the default FreshForge matrix YAML path."""

        return self.output_dir / "strategy-matrix.yaml"

    @property
    def matrix_template_path(self) -> Path:
        """Return the default FreshForge matrix workflow-template YAML path."""

        return self.output_dir / "strategy-matrix-workflow-template.yaml"


@dataclass(frozen=True)
class OutputRefStrategyComparisonEntry:
    """Compact comparison result for one strategy case."""

    case: OutputRefStrategyCase
    output_ref_count: int
    comparable_output_count: int
    output_refs_path: Path
    workflow_path: Path | None
    run_namespace: str
    evidence_source: str | None = None
    evidence_summary: dict[str, Any] | None = None
    freshforge_run_summary: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON representation."""

        return {
            "case": self.case.to_dict(),
            "output_ref_count": self.output_ref_count,
            "comparable_output_count": self.comparable_output_count,
            "output_refs_path": str(self.output_refs_path),
            "workflow_path": str(self.workflow_path) if self.workflow_path is not None else None,
            "run_namespace": self.run_namespace,
            "evidence_source": self.evidence_source,
            "evidence_summary": self.evidence_summary,
            "freshforge_run_summary": self.freshforge_run_summary,
        }


@dataclass(frozen=True)
class OutputRefStrategyComparisonResult:
    """Collection of compared FABLE output-ref strategies."""

    workbook_version: str
    paths: OutputRefStrategyComparisonPaths
    entries: tuple[OutputRefStrategyComparisonEntry, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON representation."""

        return {
            "workbook_version": self.workbook_version,
            "output_dir": str(self.paths.output_dir),
            "summary_json_path": str(self.paths.summary_json_path),
            "summary_markdown_path": str(self.paths.summary_markdown_path),
            "entries": [entry.to_dict() for entry in self.entries],
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class OutputRefStrategyMatrixPaths:
    """Path layout for a FreshForge matrix built from a strategy comparison."""

    workbook_version: str
    output_dir: Path
    matrix_path: Path
    workflow_template_path: Path

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON representation."""

        return {
            "workbook_version": self.workbook_version,
            "output_dir": str(self.output_dir),
            "matrix_path": str(self.matrix_path),
            "workflow_template_path": str(self.workflow_template_path),
        }


@dataclass(frozen=True)
class OutputRefStrategyMatrixResult:
    """Prepared FreshForge matrix artifacts for strategy comparison cases."""

    workbook_version: str
    paths: OutputRefStrategyMatrixPaths
    matrix: dict[str, Any]
    workflow_template: dict[str, Any]
    case_count: int
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON representation."""

        return {
            "workbook_version": self.workbook_version,
            "paths": self.paths.to_dict(),
            "matrix": self.matrix,
            "workflow_template": self.workflow_template,
            "case_count": self.case_count,
            "notes": list(self.notes),
        }


def output_ref_strategy_comparison_paths(
    *,
    workbook_version: str = "2021",
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> OutputRefStrategyComparisonPaths:
    """Return default output-ref strategy comparison paths."""

    version = _normalize_workbook_version(workbook_version)
    root = Path(repo_root)
    output = Path(output_dir) if output_dir is not None else Path(f"tmp/strategy-comparisons/fable-{version}")
    output_root = output if output.is_absolute() else root / output
    return OutputRefStrategyComparisonPaths(
        workbook_version=version,
        output_dir=output_root,
        summary_json_path=output_root / "summary.json",
        summary_markdown_path=output_root / "summary.md",
    )


def default_output_ref_strategy_cases() -> tuple[OutputRefStrategyCase, ...]:
    """Return deterministic default strategy cases for FABLE-C output tables."""

    return (
        OutputRefStrategyCase(
            case_id="output-columns",
            strategy="output-columns",
            label="All OUTPUT-* columns",
            column_flavour_tags="OUTPUT-*",
            description="Default generated-model boundary using all workbook output columns.",
        ),
        OutputRefStrategyCase(
            case_id="headline-only",
            strategy="headline-only",
            label="Curated headline refs",
            column_flavour_tags=None,
            description="Narrow validation slice using curated FABLE Pyculator headline series.",
        ),
        OutputRefStrategyCase(
            case_id="ghg-output-columns",
            strategy="table",
            label="GHG OUTPUT-* columns",
            column_flavour_tags="OUTPUT-*",
            table_names=("ghg_resultsghg",),
            description="GHG output table restricted to workbook output columns.",
        ),
        OutputRefStrategyCase(
            case_id="ghg-output-8",
            strategy="table",
            label="GHG OUTPUT-8 columns",
            column_flavour_tags="OUTPUT-8",
            table_names=("ghg_resultsghg",),
            description="GHG output table restricted to the OUTPUT-8 flavour.",
        ),
        OutputRefStrategyCase(
            case_id="all-columns",
            strategy="all-columns",
            label="All output-table columns",
            column_flavour_tags=None,
            description="Broadest discovered output-table boundary, including context and support columns.",
        ),
    )


def compare_output_ref_strategies(
    spec: FableCalculatorSpec,
    *,
    workbook_version: str = "2021",
    workbook_path: str | Path,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    cases: Sequence[OutputRefStrategyCase] | None = None,
    selected_case_ids: Sequence[str] | None = None,
    include_workflows: bool = False,
    include_existing_evidence: bool = False,
) -> OutputRefStrategyComparisonResult:
    """Compare output-ref strategies and write per-case preparation artifacts."""

    version = _normalize_workbook_version(workbook_version)
    root = Path(repo_root).resolve()
    workbook = Path(workbook_path)
    workbook_full_path = workbook if workbook.is_absolute() else root / workbook
    if not workbook_full_path.exists():
        raise FileNotFoundError(f"FABLE workbook not found: {workbook_full_path}")

    paths = output_ref_strategy_comparison_paths(workbook_version=version, repo_root=root, output_dir=output_dir)
    case_list = _selected_cases(cases or default_output_ref_strategy_cases(), selected_case_ids)
    entries: list[OutputRefStrategyComparisonEntry] = []
    for case in case_list:
        output_refs = derive_output_refs_for_strategy(
            spec,
            strategy=case.strategy,
            column_flavour_tags=case.column_flavour_tags,
            table_names=case.table_names or None,
        )
        output_refs_path = paths.output_refs_path(case.case_id)
        write_output_refs(output_refs_path, output_refs)
        build_paths = fable_freshforge_build_paths(
            workbook_version=version,
            repo_root=root,
            workbook_path=workbook_full_path,
            artifact_dir=paths.case_dir(case.case_id),
            workflow_filename=DEFAULT_WORKFLOW_FILENAME,
        )
        validation_scenario = build_cached_workbook_validation_scenario(
            workbook_full_path,
            output_refs,
            generated_model_path=build_paths.generated_model_path,
            scenario_id=f"fable-c-{version}-{case.case_id}",
            description=f"Output-ref strategy comparison case: {case.label}",
            source_workbook=workbook_full_path,
            generated_model=build_paths.generated_model_path,
        )
        write_validation_scenario(build_paths.validation_scenario_path, validation_scenario)
        workflow_path = None
        if include_workflows:
            workflow = build_modelwright_freshforge_workflow(
                build_paths,
                workdir=root,
                workflow_id=f"fable_{version}_{case.case_id}_modelwright_run",
                name=f"FABLE {version} {case.label}",
                description=f"Modelwright workflow for FABLE output-ref strategy {case.case_id}.",
                module_name=f"generated_fable_{version}_{_safe_identifier(case.case_id)}_model",
            )
            workflow_path = paths.workflow_path(case.case_id)
            write_freshforge_workflow(workflow_path, workflow)
        evidence_source, evidence_summary = _existing_evidence_summary(
            case_dir=paths.case_dir(case.case_id),
            workbook_version=version,
            include_existing_evidence=include_existing_evidence,
        )
        entries.append(
            OutputRefStrategyComparisonEntry(
                case=case,
                output_ref_count=len(output_refs),
                comparable_output_count=len(validation_scenario.get("outputs", ())),
                output_refs_path=output_refs_path,
                workflow_path=workflow_path,
                run_namespace=f"strategy/{case.case_id}",
                evidence_source=evidence_source,
                evidence_summary=evidence_summary,
            )
        )

    return OutputRefStrategyComparisonResult(
        workbook_version=version,
        paths=paths,
        entries=tuple(entries),
        notes=(
            "Strategy comparison prepares workflow boundaries only; it is not a generated-model equivalence claim.",
        ),
    )


def write_output_ref_strategy_comparison(result: OutputRefStrategyComparisonResult) -> dict[str, Any]:
    """Write compact JSON and Markdown strategy-comparison summaries."""

    result.paths.output_dir.mkdir(parents=True, exist_ok=True)
    payload = result.to_dict()
    result.paths.summary_json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result.paths.summary_markdown_path.write_text(_comparison_markdown(result), encoding="utf-8")
    return payload


def build_output_ref_strategy_matrix(
    result: OutputRefStrategyComparisonResult,
    *,
    matrix_path: str | Path | None = None,
) -> OutputRefStrategyMatrixResult:
    """Build a FreshForge matrix document for prepared strategy-comparison workflows.

    Matrix creation is FreshForge-free. Planning and running the written matrix require FreshForge to
    be installed separately.
    """

    paths = _matrix_paths(result, matrix_path=matrix_path)
    missing_workflows = [
        entry.case.case_id
        for entry in result.entries
        if entry.workflow_path is None or not entry.workflow_path.exists()
    ]
    if missing_workflows:
        raise FileNotFoundError(
            "strategy matrix requires per-case workflow files; rerun comparison with "
            f"include_workflows=True for: {', '.join(missing_workflows)}"
        )

    template = _strategy_matrix_workflow_template(result)
    matrix = {
        "matrix": {
            "id": f"fable_{result.workbook_version}_output_ref_strategies",
            "name": f"FABLE {result.workbook_version} output-ref strategy matrix",
            "description": "FreshForge matrix for comparing FABLE output-ref strategy rebuild boundaries.",
            "workflow_template": _path_relative_to(paths.workflow_template_path, paths.matrix_path.parent),
        },
        "cases": [_strategy_matrix_case(entry, workbook_version=result.workbook_version) for entry in result.entries],
    }
    return OutputRefStrategyMatrixResult(
        workbook_version=result.workbook_version,
        paths=paths,
        matrix=matrix,
        workflow_template=template,
        case_count=len(result.entries),
        notes=(
            "FreshForge matrix creation prepares repeated runs only; it is not a generated-model equivalence claim.",
        ),
    )


def write_output_ref_strategy_matrix(result: OutputRefStrategyMatrixResult) -> dict[str, Any]:
    """Write a FreshForge strategy matrix and workflow template as YAML."""

    result.paths.output_dir.mkdir(parents=True, exist_ok=True)
    result.paths.workflow_template_path.parent.mkdir(parents=True, exist_ok=True)
    result.paths.workflow_template_path.write_text(
        yaml.safe_dump(result.workflow_template, sort_keys=False),
        encoding="utf-8",
    )
    result.paths.matrix_path.write_text(
        yaml.safe_dump(result.matrix, sort_keys=False),
        encoding="utf-8",
    )
    return result.to_dict()


def plan_output_ref_strategy_matrix(matrix_path: str | Path) -> dict[str, Any]:
    """Plan a FreshForge strategy matrix and return a serializable payload."""

    try:
        from freshforge.matrix import load_workflow_matrix, plan_workflow_matrix
    except ImportError as exc:  # pragma: no cover - exercised by callers without FreshForge
        raise RuntimeError("FreshForge with matrix support is required to plan strategy matrices.") from exc

    matrix, diagnostics = load_workflow_matrix(matrix_path)
    if matrix is None:
        return {
            "ok": False,
            "matrix": None,
            "diagnostics": [diagnostic.to_dict() for diagnostic in diagnostics],
        }
    plan = plan_workflow_matrix(matrix, diagnostics=diagnostics)
    return {"ok": plan.ok, "matrix": matrix.to_dict(), "plan": plan.to_dict()}


def run_output_ref_strategy_matrix(
    matrix_path: str | Path,
    *,
    workdir: str | Path | None = None,
    fail_fast: bool = False,
) -> dict[str, Any]:
    """Run a FreshForge strategy matrix and return a serializable payload."""

    try:
        from freshforge.matrix import load_workflow_matrix, run_workflow_matrix
    except ImportError as exc:  # pragma: no cover - exercised by callers without FreshForge
        raise RuntimeError("FreshForge with matrix support is required to run strategy matrices.") from exc

    matrix, diagnostics = load_workflow_matrix(matrix_path)
    if matrix is None:
        return {
            "ok": False,
            "matrix": None,
            "diagnostics": [diagnostic.to_dict() for diagnostic in diagnostics],
        }
    run = run_workflow_matrix(matrix, diagnostics=diagnostics, workdir=workdir, fail_fast=fail_fast)
    return {
        "ok": run.ok,
        "matrix": matrix.to_dict(),
        "run": run.to_dict(),
        "summary": run.summary().to_dict(),
    }


def _selected_cases(
    cases: Sequence[OutputRefStrategyCase],
    selected_case_ids: Sequence[str] | None,
) -> tuple[OutputRefStrategyCase, ...]:
    if selected_case_ids is None:
        return tuple(cases)
    case_by_id = {case.case_id: case for case in cases}
    unknown = sorted(set(selected_case_ids) - set(case_by_id))
    if unknown:
        raise KeyError(f"unknown strategy case id(s): {', '.join(unknown)}")
    return tuple(case_by_id[case_id] for case_id in selected_case_ids)


def _existing_evidence_summary(
    *,
    case_dir: Path,
    workbook_version: str,
    include_existing_evidence: bool,
) -> tuple[str | None, dict[str, Any] | None]:
    if not include_existing_evidence:
        return None, None
    try:
        from modelwright.evidence import extract_validation_evidence, validation_evidence_paths

        paths = validation_evidence_paths(
            evidence_id=f"fable-{workbook_version}-{case_dir.name}",
            artifact_dir=case_dir,
            output_dir=case_dir / "validation-evidence",
        )
        summary = extract_validation_evidence(paths)
        return "modelwright", summary.to_dict()
    except ImportError:
        from fable_pyculator.validation import extract_validation_evidence, fable_validation_evidence_paths

        paths = fable_validation_evidence_paths(
            workbook_version=workbook_version,
            artifact_dir=case_dir,
            output_dir=case_dir / "validation-evidence",
        )
        summary = extract_validation_evidence(paths, workbook_version=workbook_version)
        return "fable-local", summary.to_dict()


def _comparison_markdown(result: OutputRefStrategyComparisonResult) -> str:
    lines = [
        f"# FABLE {result.workbook_version} Output-Ref Strategy Comparison",
        "",
        "| Strategy | Output refs | Comparable cached outputs | Namespace |",
        "| --- | ---: | ---: | --- |",
    ]
    for entry in result.entries:
        lines.append(
            "| "
            f"`{entry.case.case_id}` | "
            f"{entry.output_ref_count} | "
            f"{entry.comparable_output_count} | "
            f"`{entry.run_namespace}` |"
        )
    if result.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in result.notes)
    return "\n".join(lines).rstrip() + "\n"


def _matrix_paths(
    result: OutputRefStrategyComparisonResult,
    *,
    matrix_path: str | Path | None,
) -> OutputRefStrategyMatrixPaths:
    selected_matrix_path = Path(matrix_path) if matrix_path is not None else result.paths.matrix_path
    if not selected_matrix_path.is_absolute():
        selected_matrix_path = result.paths.output_dir / selected_matrix_path
    template_path = selected_matrix_path.parent / "strategy-matrix-workflow-template.yaml"
    return OutputRefStrategyMatrixPaths(
        workbook_version=result.workbook_version,
        output_dir=result.paths.output_dir,
        matrix_path=selected_matrix_path,
        workflow_template_path=template_path,
    )


def _strategy_matrix_case(entry: OutputRefStrategyComparisonEntry, *, workbook_version: str) -> dict[str, Any]:
    workflow_path = entry.workflow_path
    if workflow_path is None:  # pragma: no cover - guarded by caller
        raise ValueError(f"strategy case {entry.case.case_id} does not have a workflow path")
    case_dir = workflow_path.parent
    return {
        "id": entry.case.case_id,
        "namespace": entry.run_namespace,
        "variables": {
            "case_id": entry.case.case_id,
            "case_label": entry.case.label,
            "workflow_path": str(workflow_path),
            "workbook": _existing_artifact_value(workflow_path, "infer_contract", "parameters", "workbook"),
            "module_name": f"generated_fable_{workbook_version}_{_safe_identifier(entry.case.case_id)}_model",
            "output_refs": str(case_dir / "output_refs.json"),
            "contract": str(case_dir / "contract.json"),
            "expressions": str(case_dir / "expressions.json"),
            "constants": str(case_dir / "constants.json"),
            "inference_result": str(case_dir / "inference-result.json"),
            "generation_result": str(case_dir / "generation-result.json"),
            "generated_model": str(case_dir / f"generated_fable_{workbook_version}_model.py"),
            "generated_values": str(case_dir / "generated-values.json"),
            "validation_scenario": str(case_dir / "validation-scenario.json"),
            "evaluation_report": str(case_dir / "evaluation-report.json"),
        },
    }


def _strategy_matrix_workflow_template(result: OutputRefStrategyComparisonResult) -> dict[str, Any]:
    return {
        "workflow": {
            "id": f"fable_{result.workbook_version}_${{matrix.case_id}}_modelwright_run",
            "name": f"FABLE {result.workbook_version} ${{matrix.case_label}}",
            "description": "Modelwright workflow for FABLE output-ref strategy ${matrix.case_id}.",
        },
        "nodes": [
            {
                "id": "infer_contract",
                "provider": "modelwright.model_infer_contract",
                "outputs": {
                    "generated_contract": "generated_contract",
                    "formula_expressions": "formula_expressions",
                    "input_constants": "input_constants",
                },
                "parameters": {
                    "workbook": "${matrix.workbook}",
                    "module_name": "${matrix.module_name}",
                },
                "artifacts": {
                    "output_refs": "${matrix.output_refs}",
                    "contract": "${matrix.contract}",
                    "expressions": "${matrix.expressions}",
                    "constants": "${matrix.constants}",
                    "inference_result": "${matrix.inference_result}",
                },
            },
            {
                "id": "generate_model",
                "provider": "modelwright.model_generate",
                "needs": ["infer_contract"],
                "inputs": {
                    "generated_contract": "infer_contract.generated_contract",
                    "formula_expressions": "infer_contract.formula_expressions",
                    "input_constants": "infer_contract.input_constants",
                },
                "outputs": {"generated_model": "${matrix.module_name}"},
                "artifacts": {
                    "contract": "${matrix.contract}",
                    "expressions": "${matrix.expressions}",
                    "constants": "${matrix.constants}",
                    "generated_model": "${matrix.generated_model}",
                    "generation_result": "${matrix.generation_result}",
                },
            },
            {
                "id": "execute_model",
                "provider": "modelwright.model_execute",
                "needs": ["generate_model"],
                "inputs": {
                    "generated_contract": "infer_contract.generated_contract",
                    "generated_model": "generate_model.generated_model",
                },
                "outputs": {"generated_values": "generated_values"},
                "artifacts": {
                    "contract": "${matrix.contract}",
                    "generated_model": "${matrix.generated_model}",
                    "generated_values": "${matrix.generated_values}",
                },
            },
            {
                "id": "evaluate_model",
                "provider": "modelwright.validation_evaluate",
                "needs": ["execute_model"],
                "inputs": {
                    "generated_contract": "infer_contract.generated_contract",
                    "generated_model": "generate_model.generated_model",
                },
                "outputs": {"validation_report": "validation_report"},
                "parameters": {"scenario": "${matrix.validation_scenario}"},
                "artifacts": {
                    "contract": "${matrix.contract}",
                    "generated_model": "${matrix.generated_model}",
                    "scenario": "${matrix.validation_scenario}",
                    "evaluation_report": "${matrix.evaluation_report}",
                },
            },
        ],
    }


def _existing_artifact_value(path: Path, node_id: str, section: str, key: str) -> str:
    workflow = json.loads(path.read_text(encoding="utf-8"))
    for node in workflow.get("nodes", ()):
        if node.get("id") == node_id:
            value = node.get(section, {}).get(key)
            if isinstance(value, str):
                return value
    raise KeyError(f"could not find {node_id}.{section}.{key} in {path}")


def _path_relative_to(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _safe_identifier(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value).strip("_")


def _normalize_workbook_version(workbook_version: str) -> str:
    text = str(workbook_version).strip()
    if not text:
        raise ValueError("workbook_version must not be empty")
    return text
