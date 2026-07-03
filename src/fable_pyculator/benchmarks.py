"""Opt-in FABLE benchmark evidence orchestration.

This module packages compact benchmark evidence from local generated-model artifacts and, when
requested, prepares or runs the existing FreshForge/Modelwright rebuild workflow. It is intentionally
conservative: no workflow runs unless the caller opts in, no source workbooks or raw reports are
copied, and equivalence is reported only from explicit comparison counts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Literal

from fable_pyculator.validation import (
    extract_validation_evidence,
    fable_validation_evidence_paths,
    write_validation_evidence,
)
from fable_pyculator.workflows import DEFAULT_WORKFLOW_FILENAME, OutputRefStrategy, prepare_freshforge_rebuild

BenchmarkMode = Literal["evidence-only", "freshforge-plan", "freshforge-run"]
EvidenceBackend = Literal["modelwright", "fable-local"]
MatrixEvidenceBackend = Literal["modelwright"]


@dataclass(frozen=True)
class FableBenchmarkRunPaths:
    """Path contract for one opt-in FABLE benchmark evidence run."""

    workbook_version: str
    artifact_dir: Path
    output_dir: Path
    benchmark_summary_json_path: Path
    benchmark_summary_markdown_path: Path
    validation_summary_json_path: Path
    validation_summary_markdown_path: Path
    workflow_path: Path
    freshforge_run_summary_path: Path


@dataclass(frozen=True)
class FableBenchmarkRunSummary:
    """Compact benchmark orchestration summary safe for docs or CI artifacts."""

    workbook_version: str
    mode: BenchmarkMode
    evidence_backend: EvidenceBackend
    evidence_status: str
    equivalence_status: str
    missing_artifacts: tuple[str, ...]
    comparison: dict[str, Any]
    paths: dict[str, str]
    freshforge: dict[str, Any] = field(default_factory=dict)
    scenario_bundle: dict[str, Any] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        return {
            "workbook_version": self.workbook_version,
            "mode": self.mode,
            "evidence_backend": self.evidence_backend,
            "evidence_status": self.evidence_status,
            "equivalence_status": self.equivalence_status,
            "missing_artifacts": list(self.missing_artifacts),
            "comparison": self.comparison,
            "paths": self.paths,
            "freshforge": self.freshforge,
            "scenario_bundle": self.scenario_bundle,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class FableBenchmarkMatrixEvidencePaths:
    """Path contract for FABLE-facing benchmark matrix evidence packaging."""

    workbook_version: str
    evidence_id: str
    output_dir: Path
    artifact_root: Path
    matrix_run_path: Path | None
    matrix_summary_path: Path | None
    modelwright_summary_json_path: Path
    modelwright_summary_markdown_path: Path
    benchmark_summary_json_path: Path
    benchmark_summary_markdown_path: Path


@dataclass(frozen=True)
class FableBenchmarkMatrixEvidenceSummary:
    """Compact FABLE-facing summary of a generated-model benchmark matrix."""

    workbook_version: str
    evidence_backend: MatrixEvidenceBackend
    evidence_id: str
    evidence_status: str
    equivalence_status: str
    case_count: int
    complete_count: int
    incomplete_count: int
    skipped_count: int
    pass_count: int
    fail_count: int
    diagnostic_count: int
    error_count: int
    warning_count: int
    paths: dict[str, str | None]
    modelwright_summary: dict[str, Any]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        return {
            "workbook_version": self.workbook_version,
            "evidence_backend": self.evidence_backend,
            "evidence_id": self.evidence_id,
            "evidence_status": self.evidence_status,
            "equivalence_status": self.equivalence_status,
            "case_count": self.case_count,
            "complete_count": self.complete_count,
            "incomplete_count": self.incomplete_count,
            "skipped_count": self.skipped_count,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "diagnostic_count": self.diagnostic_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "paths": self.paths,
            "modelwright_summary": _sanitize_compact_payload(self.modelwright_summary),
            "notes": list(self.notes),
        }


def fable_benchmark_run_paths(
    *,
    workbook_version: str = "2021",
    repo_root: str | Path = ".",
    artifact_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> FableBenchmarkRunPaths:
    """Return default paths for a version-specific FABLE benchmark evidence run."""

    version = _normalize_workbook_version(workbook_version)
    root = Path(repo_root)
    artifact = Path(artifact_dir) if artifact_dir is not None else Path(f"tmp/generated-models/fable-{version}")
    output = Path(output_dir) if output_dir is not None else Path(f"tmp/validation-evidence/fable-{version}")
    artifact_root = artifact if artifact.is_absolute() else root / artifact
    output_root = output if output.is_absolute() else root / output
    return FableBenchmarkRunPaths(
        workbook_version=version,
        artifact_dir=artifact_root,
        output_dir=output_root,
        benchmark_summary_json_path=output_root / "benchmark-summary.json",
        benchmark_summary_markdown_path=output_root / "benchmark-summary.md",
        validation_summary_json_path=output_root / "summary.json",
        validation_summary_markdown_path=output_root / "summary.md",
        workflow_path=artifact_root / DEFAULT_WORKFLOW_FILENAME,
        freshforge_run_summary_path=output_root / "freshforge-run-summary.json",
    )


def fable_benchmark_matrix_evidence_paths(
    *,
    workbook_version: str = "2021",
    repo_root: str | Path = ".",
    matrix_run_path: str | Path | None = None,
    matrix_summary_path: str | Path | None = None,
    artifact_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    evidence_id: str | None = None,
) -> FableBenchmarkMatrixEvidencePaths:
    """Return default paths for FABLE benchmark matrix evidence packaging."""

    version = _normalize_workbook_version(workbook_version)
    root = Path(repo_root)
    strategy_root = root / f"tmp/strategy-comparisons/fable-{version}"
    default_matrix_run = strategy_root / "matrix-run-summary.json"
    matrix_run = _absolute_path(root, matrix_run_path) if matrix_run_path is not None else None
    matrix_summary = _absolute_path(root, matrix_summary_path) if matrix_summary_path is not None else None
    if matrix_run is None and matrix_summary is None and default_matrix_run.exists():
        matrix_run = default_matrix_run
    artifact = _absolute_path(root, artifact_root) if artifact_root is not None else strategy_root
    output = _absolute_path(root, output_dir) if output_dir is not None else root / f"tmp/validation-evidence/fable-{version}/matrix"
    resolved_evidence_id = evidence_id or f"fable-{version}-strategy-matrix"
    return FableBenchmarkMatrixEvidencePaths(
        workbook_version=version,
        evidence_id=resolved_evidence_id,
        output_dir=output,
        artifact_root=artifact,
        matrix_run_path=matrix_run,
        matrix_summary_path=matrix_summary,
        modelwright_summary_json_path=output / "summary.json",
        modelwright_summary_markdown_path=output / "summary.md",
        benchmark_summary_json_path=output / "benchmark-matrix-summary.json",
        benchmark_summary_markdown_path=output / "benchmark-matrix-summary.md",
    )


def package_fable_benchmark_evidence(
    *,
    workbook_version: str = "2021",
    repo_root: str | Path = ".",
    artifact_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    mode: BenchmarkMode = "evidence-only",
    require_artifacts: bool = False,
    output_ref_strategy: OutputRefStrategy = "output-columns",
    workbook_path: str | Path | None = None,
    run_namespace: str | None = None,
    bundle_path: str | Path | None = None,
    include_scenario_bundle_summary: bool = False,
) -> FableBenchmarkRunSummary:
    """Package benchmark evidence and optionally prepare or run the FreshForge rebuild workflow.

    ``mode="evidence-only"`` only summarizes existing artifacts. ``freshforge-plan`` prepares the
    build workflow when the source workbook is available. ``freshforge-run`` additionally executes
    that workflow through FreshForge and records a compact run summary. Missing local artifacts are
    reported as skipped evidence unless ``require_artifacts`` is true.
    """

    if mode not in {"evidence-only", "freshforge-plan", "freshforge-run"}:
        raise ValueError(f"unsupported benchmark mode: {mode}")

    version = _normalize_workbook_version(workbook_version)
    root = Path(repo_root).resolve()
    paths = fable_benchmark_run_paths(
        workbook_version=version,
        repo_root=root,
        artifact_dir=artifact_dir,
        output_dir=output_dir,
    )
    backend, evidence_payload = _extract_and_write_evidence(
        paths,
        workbook_version=version,
        require_artifacts=require_artifacts,
    )
    freshforge = _freshforge_payload(
        mode=mode,
        workbook_version=version,
        repo_root=root,
        artifact_dir=paths.artifact_dir,
        workbook_path=workbook_path,
        output_ref_strategy=output_ref_strategy,
        run_namespace=run_namespace,
        require_artifacts=require_artifacts,
        summary_path=paths.freshforge_run_summary_path,
    )
    scenario_bundle = _scenario_bundle_payload(
        bundle_path=bundle_path,
        include_scenario_bundle_summary=include_scenario_bundle_summary,
    )
    notes = list(_payload_notes(evidence_payload))
    if mode == "freshforge-plan" and freshforge.get("status") == "skipped":
        notes.append("FreshForge plan mode skipped because required local workbook artifacts are absent.")
    if mode == "freshforge-run":
        notes.append("FreshForge run mode is explicit and requires restored local workbook artifacts.")

    return FableBenchmarkRunSummary(
        workbook_version=version,
        mode=mode,
        evidence_backend=backend,
        evidence_status=str(evidence_payload.get("evidence_status", "incomplete")),
        equivalence_status=str(evidence_payload.get("equivalence_status", "incomplete")),
        missing_artifacts=tuple(str(item) for item in evidence_payload.get("missing_artifacts", ())),
        comparison=dict(evidence_payload.get("comparison", {})),
        paths=_path_payload(paths),
        freshforge=freshforge,
        scenario_bundle=scenario_bundle,
        notes=tuple(notes),
    )


def package_fable_benchmark_matrix_evidence(
    *,
    workbook_version: str = "2021",
    repo_root: str | Path = ".",
    matrix_run_path: str | Path | None = None,
    matrix_summary_path: str | Path | None = None,
    artifact_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    evidence_id: str | None = None,
    require_evidence: bool = False,
) -> FableBenchmarkMatrixEvidenceSummary:
    """Package compact FABLE benchmark matrix evidence through Modelwright.

    This wrapper supplies FABLE-C path defaults and public-facing summary text. Generic matrix
    aggregation remains in Modelwright.
    """

    paths = fable_benchmark_matrix_evidence_paths(
        workbook_version=workbook_version,
        repo_root=repo_root,
        matrix_run_path=matrix_run_path,
        matrix_summary_path=matrix_summary_path,
        artifact_root=artifact_root,
        output_dir=output_dir,
        evidence_id=evidence_id,
    )
    if paths.matrix_run_path is None and paths.matrix_summary_path is None:
        raise FileNotFoundError(
            "matrix evidence packaging requires --matrix-run or --matrix-summary; "
            f"no default matrix run summary exists at {paths.artifact_root / 'matrix-run-summary.json'}"
        )
    modelwright_api = _modelwright_matrix_evidence_api()
    if modelwright_api is None:
        raise RuntimeError(
            "Modelwright with Phase 38 matrix evidence aggregation support is required "
            "for FABLE benchmark matrix evidence packaging."
        )
    modelwright_paths, modelwright_extract, modelwright_write = modelwright_api
    generic_paths = modelwright_paths(
        evidence_id=paths.evidence_id,
        output_dir=paths.output_dir,
        matrix_run_path=paths.matrix_run_path,
        matrix_summary_path=paths.matrix_summary_path,
        artifact_root=paths.artifact_root,
    )
    summary = modelwright_extract(generic_paths, require_evidence=require_evidence)
    written = modelwright_write(summary, generic_paths)
    payload = _sanitize_compact_payload(dict(written.get("summary", summary.to_dict())))
    notes = tuple(str(note) for note in payload.get("notes", ()))
    notes = (
        *notes,
        "FABLE wrapper around Modelwright generic matrix evidence; no equivalence claim without explicit counts.",
    )
    return FableBenchmarkMatrixEvidenceSummary(
        workbook_version=paths.workbook_version,
        evidence_backend="modelwright",
        evidence_id=str(payload.get("evidence_id", paths.evidence_id)),
        evidence_status=str(payload.get("evidence_status", "incomplete")),
        equivalence_status=str(payload.get("equivalence_status", "incomplete")),
        case_count=int(payload.get("case_count", 0) or 0),
        complete_count=int(payload.get("complete_count", 0) or 0),
        incomplete_count=int(payload.get("incomplete_count", 0) or 0),
        skipped_count=int(payload.get("skipped_count", 0) or 0),
        pass_count=int(payload.get("pass_count", 0) or 0),
        fail_count=int(payload.get("fail_count", 0) or 0),
        diagnostic_count=int(payload.get("diagnostic_count", 0) or 0),
        error_count=int(payload.get("error_count", 0) or 0),
        warning_count=int(payload.get("warning_count", 0) or 0),
        paths=_matrix_path_payload(paths),
        modelwright_summary=payload,
        notes=notes,
    )


def write_fable_benchmark_matrix_evidence(
    summary: FableBenchmarkMatrixEvidenceSummary,
    paths: FableBenchmarkMatrixEvidencePaths | None = None,
) -> dict[str, Any]:
    """Write compact FABLE-facing JSON and Markdown matrix evidence summaries."""

    resolved_paths = paths or fable_benchmark_matrix_evidence_paths(workbook_version=summary.workbook_version)
    resolved_paths.output_dir.mkdir(parents=True, exist_ok=True)
    payload = summary.to_dict()
    resolved_paths.benchmark_summary_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    resolved_paths.benchmark_summary_markdown_path.write_text(
        _benchmark_matrix_markdown(summary),
        encoding="utf-8",
    )
    return payload


def write_fable_benchmark_summary(
    summary: FableBenchmarkRunSummary,
    paths: FableBenchmarkRunPaths | None = None,
) -> dict[str, Any]:
    """Write compact JSON and Markdown benchmark summaries."""

    resolved_paths = paths or fable_benchmark_run_paths(workbook_version=summary.workbook_version)
    resolved_paths.output_dir.mkdir(parents=True, exist_ok=True)
    payload = summary.to_dict()
    resolved_paths.benchmark_summary_json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    resolved_paths.benchmark_summary_markdown_path.write_text(_benchmark_markdown(summary), encoding="utf-8")
    return payload


def _extract_and_write_evidence(
    paths: FableBenchmarkRunPaths,
    *,
    workbook_version: str,
    require_artifacts: bool,
) -> tuple[EvidenceBackend, dict[str, Any]]:
    modelwright_api = _modelwright_evidence_api()
    if modelwright_api is not None:
        validation_evidence_paths, modelwright_extract, modelwright_write = modelwright_api
        modelwright_paths = validation_evidence_paths(
            evidence_id=f"fable-{workbook_version}",
            artifact_dir=paths.artifact_dir,
            output_dir=paths.output_dir,
            validation_scenario_path=paths.artifact_dir / "validation-scenario.json",
        )
        summary = modelwright_extract(modelwright_paths, require_artifacts=require_artifacts)
        written = modelwright_write(summary, modelwright_paths)
        return "modelwright", dict(written.get("summary", summary.to_dict()))

    fable_paths = fable_validation_evidence_paths(
        workbook_version=workbook_version,
        artifact_dir=paths.artifact_dir,
        output_dir=paths.output_dir,
    )
    summary = extract_validation_evidence(
        fable_paths,
        workbook_version=workbook_version,
        require_artifacts=require_artifacts,
    )
    return "fable-local", write_validation_evidence(summary, fable_paths)


def _freshforge_payload(
    *,
    mode: BenchmarkMode,
    workbook_version: str,
    repo_root: Path,
    artifact_dir: Path,
    workbook_path: str | Path | None,
    output_ref_strategy: OutputRefStrategy,
    run_namespace: str | None,
    require_artifacts: bool,
    summary_path: Path,
) -> dict[str, Any]:
    if mode == "evidence-only":
        return {"status": "not-requested"}

    workbook = Path(workbook_path) if workbook_path is not None else repo_root / (
        f"tmp/private-workbooks/{workbook_version}_Open_FABLECalculator.xlsx"
    )
    workbook = workbook if workbook.is_absolute() else repo_root / workbook
    if not workbook.exists():
        if require_artifacts or mode == "freshforge-run":
            raise FileNotFoundError(f"{workbook_version} FABLE workbook not found: {workbook}")
        return {
            "status": "skipped",
            "reason": "missing-workbook",
            "workbook_path": workbook.as_posix(),
            "output_ref_strategy": output_ref_strategy,
        }

    plan = prepare_freshforge_rebuild(
        workbook_version=workbook_version,
        repo_root=repo_root,
        workbook_path=workbook,
        artifact_dir=artifact_dir,
        output_ref_strategy=output_ref_strategy,
    )
    payload: dict[str, Any] = {
        "status": "planned",
        "workflow_path": plan.paths.workflow_path.as_posix(),
        "output_refs_path": plan.paths.output_refs_path.as_posix(),
        "output_ref_count": len(plan.output_refs),
        "comparable_output_count": plan.comparable_output_count,
        "output_ref_strategy": output_ref_strategy,
        "run_namespace": run_namespace,
    }
    if mode == "freshforge-plan":
        return payload

    try:
        from freshforge.execution import run_workflow  # type: ignore[import-untyped]
        from freshforge.validation import validate_workflow_document  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError("FreshForge is required for benchmark FreshForge run mode.") from exc

    spec, diagnostics = validate_workflow_document(plan.workflow)
    if spec is None:
        raise RuntimeError("FreshForge could not validate the benchmark workflow.")
    run_result = run_workflow(
        spec,
        diagnostics=diagnostics,
        workdir=repo_root,
        run_namespace=run_namespace,
    )
    summary_payload = {"run": run_result.to_dict(), "summary": run_result.summary().to_dict()}
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload.update(
        {
            "status": "ran",
            "run_status": summary_payload["summary"].get("status"),
            "run_summary_path": summary_path.as_posix(),
            "run_summary": summary_payload["summary"],
        }
    )
    return payload


def _scenario_bundle_payload(
    *,
    bundle_path: str | Path | None,
    include_scenario_bundle_summary: bool,
) -> dict[str, Any]:
    if bundle_path is None:
        return {}
    bundle = Path(bundle_path)
    payload: dict[str, Any] = {"bundle_path": bundle.as_posix()}
    if include_scenario_bundle_summary:
        summary_path = bundle.parent / "freshforge-run-summary.json"
        payload["summary_path"] = summary_path.as_posix()
        if summary_path.exists():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            payload["summary"] = _compact_freshforge_summary(summary)
        else:
            payload["summary_status"] = "missing"
    return payload


def _modelwright_evidence_api() -> tuple[Any, Any, Any] | None:
    try:
        from modelwright.evidence import (  # type: ignore[import-untyped]
            extract_validation_evidence as modelwright_extract,
            validation_evidence_paths,
            write_validation_evidence as modelwright_write,
        )
    except (ImportError, AttributeError):
        return None
    return validation_evidence_paths, modelwright_extract, modelwright_write


def _modelwright_matrix_evidence_api() -> tuple[Any, Any, Any] | None:
    try:
        from modelwright.evidence import (  # type: ignore[import-untyped]
            extract_matrix_evidence,
            matrix_evidence_paths,
            write_matrix_evidence,
        )
    except (ImportError, AttributeError):
        return None
    return matrix_evidence_paths, extract_matrix_evidence, write_matrix_evidence


def _compact_freshforge_summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary", payload)
    if not isinstance(summary, dict):
        return {}
    return {
        key: summary.get(key)
        for key in (
            "workflow_id",
            "run_namespace",
            "status",
            "node_counts",
            "diagnostic_counts",
            "artifact_count",
        )
        if key in summary
    }


def _matrix_path_payload(paths: FableBenchmarkMatrixEvidencePaths) -> dict[str, str | None]:
    return {
        "artifact_root": paths.artifact_root.as_posix(),
        "output_dir": paths.output_dir.as_posix(),
        "matrix_run": paths.matrix_run_path.as_posix() if paths.matrix_run_path is not None else None,
        "matrix_summary": paths.matrix_summary_path.as_posix() if paths.matrix_summary_path is not None else None,
        "modelwright_summary_json": paths.modelwright_summary_json_path.as_posix(),
        "modelwright_summary_markdown": paths.modelwright_summary_markdown_path.as_posix(),
        "benchmark_summary_json": paths.benchmark_summary_json_path.as_posix(),
        "benchmark_summary_markdown": paths.benchmark_summary_markdown_path.as_posix(),
    }


def _path_payload(paths: FableBenchmarkRunPaths) -> dict[str, str]:
    return {
        "artifact_dir": paths.artifact_dir.as_posix(),
        "output_dir": paths.output_dir.as_posix(),
        "validation_summary_json": paths.validation_summary_json_path.as_posix(),
        "validation_summary_markdown": paths.validation_summary_markdown_path.as_posix(),
        "benchmark_summary_json": paths.benchmark_summary_json_path.as_posix(),
        "benchmark_summary_markdown": paths.benchmark_summary_markdown_path.as_posix(),
        "workflow": paths.workflow_path.as_posix(),
        "freshforge_run_summary": paths.freshforge_run_summary_path.as_posix(),
    }


def _payload_notes(payload: dict[str, Any]) -> tuple[str, ...]:
    notes = payload.get("notes", ())
    if isinstance(notes, list | tuple):
        return tuple(str(note) for note in notes)
    return ()


def _benchmark_markdown(summary: FableBenchmarkRunSummary) -> str:
    comparison = summary.comparison
    lines = [
        f"# FABLE {summary.workbook_version} Benchmark Evidence",
        "",
        f"- mode: `{summary.mode}`",
        f"- evidence backend: `{summary.evidence_backend}`",
        f"- evidence status: `{summary.evidence_status}`",
        f"- equivalence status: `{summary.equivalence_status}`",
        f"- comparable outputs: `{comparison.get('comparable_output_count')}`",
        f"- matches: `{comparison.get('match_count')}`",
        f"- mismatches: `{comparison.get('mismatch_count')}`",
        "",
    ]
    if summary.freshforge:
        lines.extend(["## FreshForge", "", f"```json\n{json.dumps(summary.freshforge, indent=2, sort_keys=True)}\n```", ""])
    if summary.missing_artifacts:
        lines.extend(["## Missing Artifacts", "", *[f"- `{name}`" for name in summary.missing_artifacts], ""])
    if summary.notes:
        lines.extend(["## Notes", "", *[f"- {note}" for note in summary.notes], ""])
    return "\n".join(lines).rstrip() + "\n"


def _benchmark_matrix_markdown(summary: FableBenchmarkMatrixEvidenceSummary) -> str:
    lines = [
        f"# FABLE {summary.workbook_version} Benchmark Matrix Evidence",
        "",
        f"- evidence backend: `{summary.evidence_backend}`",
        f"- evidence status: `{summary.evidence_status}`",
        f"- equivalence status: `{summary.equivalence_status}`",
        f"- cases: `{summary.case_count}`",
        f"- complete: `{summary.complete_count}`",
        f"- incomplete: `{summary.incomplete_count}`",
        f"- skipped: `{summary.skipped_count}`",
        f"- pass: `{summary.pass_count}`",
        f"- fail: `{summary.fail_count}`",
        "",
        "Equivalence is `pass` only when Modelwright matrix evidence contains explicit comparable, match, and mismatch counts proving zero mismatches.",
        "",
    ]
    cases = summary.modelwright_summary.get("cases", ())
    if cases:
        lines.extend(
            [
                "## Cases",
                "",
                "| Case | Evidence | Equivalence | Comparable | Matches | Mismatches |",
                "| --- | --- | --- | ---: | ---: | ---: |",
            ]
        )
        for case in cases:
            if not isinstance(case, dict):
                continue
            lines.append(
                "| "
                f"`{case.get('case_id')}` | "
                f"`{case.get('evidence_status')}` | "
                f"`{case.get('equivalence_status')}` | "
                f"{case.get('comparable_output_count')} | "
                f"{case.get('match_count')} | "
                f"{case.get('mismatch_count')} |"
            )
        lines.append("")
    if summary.notes:
        lines.extend(["## Notes", "", *[f"- {note}" for note in summary.notes], ""])
    return "\n".join(lines).rstrip() + "\n"


def _sanitize_compact_payload(value: Any) -> Any:
    raw_keys = {
        "source_code",
        "output_values",
        "workbook_contents",
        "workbook_data",
        "generated_values",
        "validation_report",
        "mismatches",
    }
    if isinstance(value, dict):
        return {
            str(key): _sanitize_compact_payload(item)
            for key, item in value.items()
            if str(key) not in raw_keys
        }
    if isinstance(value, list):
        return [_sanitize_compact_payload(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize_compact_payload(item) for item in value)
    return value


def _absolute_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _normalize_workbook_version(workbook_version: str) -> str:
    version = str(workbook_version).strip()
    if not version:
        raise ValueError("workbook_version must not be empty")
    return version
