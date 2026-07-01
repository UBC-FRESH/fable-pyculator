"""Compact validation-evidence extraction for FABLE generated-model artifacts.

The helpers in this module summarize existing local Modelwright/FreshForge artifacts without copying
raw workbooks, raw generated values, raw reports, or generated Python source into tracked-friendly
evidence. A summary may claim ``pass`` only when explicit comparable-output, match, and mismatch
counts prove zero mismatches.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationEvidencePaths:
    """Local artifact and compact evidence paths for one FABLE workbook version."""

    artifact_dir: Path
    output_dir: Path
    inference_result_path: Path
    generation_result_path: Path
    generated_values_path: Path
    validation_scenario_path: Path
    evaluation_report_path: Path
    summary_json_path: Path
    summary_markdown_path: Path


@dataclass(frozen=True)
class ValidationEvidenceSummary:
    """Sanitized validation evidence summary suitable for sharing or uploading."""

    workbook_version: str
    evidence_status: str
    equivalence_status: str
    missing_artifacts: tuple[str, ...]
    artifacts: dict[str, str]
    stages: dict[str, dict[str, Any]]
    comparison: dict[str, Any]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        return {
            "workbook_version": self.workbook_version,
            "evidence_status": self.evidence_status,
            "equivalence_status": self.equivalence_status,
            "missing_artifacts": list(self.missing_artifacts),
            "artifacts": self.artifacts,
            "stages": self.stages,
            "comparison": self.comparison,
            "notes": list(self.notes),
        }


def fable_validation_evidence_paths(
    *,
    workbook_version: str = "2021",
    repo_root: str | Path = ".",
    artifact_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> ValidationEvidencePaths:
    """Return default validation-evidence input and output paths."""

    root = Path(repo_root)
    artifacts = Path(artifact_dir) if artifact_dir is not None else Path(f"tmp/generated-models/fable-{workbook_version}")
    output = Path(output_dir) if output_dir is not None else Path(f"tmp/validation-evidence/fable-{workbook_version}")
    artifact_root = artifacts if artifacts.is_absolute() else root / artifacts
    output_root = output if output.is_absolute() else root / output
    return ValidationEvidencePaths(
        artifact_dir=artifact_root,
        output_dir=output_root,
        inference_result_path=artifact_root / "inference-result.json",
        generation_result_path=artifact_root / "generation-result.json",
        generated_values_path=artifact_root / "generated-values.json",
        validation_scenario_path=artifact_root / "validation-scenario.json",
        evaluation_report_path=artifact_root / "evaluation-report.json",
        summary_json_path=output_root / "summary.json",
        summary_markdown_path=output_root / "summary.md",
    )


def extract_validation_evidence(
    paths: ValidationEvidencePaths,
    *,
    workbook_version: str,
    require_artifacts: bool = False,
) -> ValidationEvidenceSummary:
    """Extract sanitized evidence from existing local artifacts."""

    required_paths = {
        "inference_result": paths.inference_result_path,
        "generation_result": paths.generation_result_path,
        "generated_values": paths.generated_values_path,
        "validation_scenario": paths.validation_scenario_path,
        "evaluation_report": paths.evaluation_report_path,
    }
    missing = tuple(name for name, path in required_paths.items() if not path.exists())
    if missing and require_artifacts:
        raise FileNotFoundError(f"missing validation artifact(s): {', '.join(missing)}")

    artifacts = {
        "artifact_dir": paths.artifact_dir.as_posix(),
        "inference_result": paths.inference_result_path.as_posix(),
        "generation_result": paths.generation_result_path.as_posix(),
        "generated_values": paths.generated_values_path.as_posix(),
        "validation_scenario": paths.validation_scenario_path.as_posix(),
        "evaluation_report": paths.evaluation_report_path.as_posix(),
        "summary_json": paths.summary_json_path.as_posix(),
        "summary_markdown": paths.summary_markdown_path.as_posix(),
    }
    if missing:
        return ValidationEvidenceSummary(
            workbook_version=str(workbook_version),
            evidence_status="skipped",
            equivalence_status="incomplete",
            missing_artifacts=missing,
            artifacts=artifacts,
            stages={},
            comparison=_comparison_status({}),
            notes=("Validation artifacts are absent; no evidence was extracted.",),
        )

    inference = _load_json(paths.inference_result_path)
    generation = _load_json(paths.generation_result_path)
    generated_values = _load_json(paths.generated_values_path)
    validation_scenario = _load_json(paths.validation_scenario_path)
    evaluation = _load_json(paths.evaluation_report_path)
    comparison_counts = _extract_comparison_counts(evaluation)
    comparison = _comparison_status(comparison_counts)

    stages = {
        "inference": _inference_stage(inference),
        "generation": _generation_stage(generation),
        "generated_execution": _generated_values_stage(generated_values),
        "validation_scenario": _validation_scenario_stage(validation_scenario),
        "evaluation": _evaluation_stage(evaluation),
    }
    diagnostics_total = sum(int(stage.get("diagnostic_count", 0)) for stage in stages.values())
    evidence_status = "complete" if comparison["status"] in {"pass", "fail"} else "incomplete"
    notes: list[str] = []
    if comparison["status"] == "incomplete":
        notes.append("Explicit comparable-output, match, and mismatch counts were not found.")
    if diagnostics_total:
        notes.append(f"Stage diagnostics were reported: {diagnostics_total}.")

    return ValidationEvidenceSummary(
        workbook_version=str(workbook_version),
        evidence_status=evidence_status,
        equivalence_status=comparison["status"],
        missing_artifacts=(),
        artifacts=artifacts,
        stages=stages,
        comparison=comparison,
        notes=tuple(notes),
    )


def write_validation_evidence(summary: ValidationEvidenceSummary, paths: ValidationEvidencePaths) -> dict[str, Any]:
    """Write compact JSON and Markdown validation-evidence summaries."""

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    payload = summary.to_dict()
    paths.summary_json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    paths.summary_markdown_path.write_text(_summary_markdown(summary), encoding="utf-8")
    return payload


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _inference_stage(data: dict[str, Any]) -> dict[str, Any]:
    contract = data.get("contract", {})
    return {
        "available": True,
        "inferred": bool(data.get("inferred", False)),
        "diagnostic_count": len(data.get("diagnostics", [])),
        "constants_count": len(data.get("constants", {})),
        "expressions_count": len(data.get("expressions", {})),
        "input_ref_count": len(contract.get("input_refs", [])) if isinstance(contract, dict) else None,
        "output_ref_count": len(contract.get("output_refs", [])) if isinstance(contract, dict) else None,
    }


def _generation_stage(data: dict[str, Any]) -> dict[str, Any]:
    source_code = data.get("source_code")
    return {
        "available": True,
        "generated": bool(data.get("generated", False)),
        "diagnostic_count": len(data.get("diagnostics", [])),
        "source_size_bytes": len(source_code.encode("utf-8")) if isinstance(source_code, str) else None,
    }


def _generated_values_stage(data: dict[str, Any]) -> dict[str, Any]:
    output_values = data.get("output_values", {})
    contract = data.get("contract", {})
    return {
        "available": True,
        "executed": bool(data.get("executed", False)),
        "diagnostic_count": len(data.get("diagnostics", [])),
        "output_value_count": len(output_values) if isinstance(output_values, dict) else None,
        "contract_output_ref_count": len(contract.get("output_refs", [])) if isinstance(contract, dict) else None,
    }


def _validation_scenario_stage(data: dict[str, Any]) -> dict[str, Any]:
    outputs = data.get("outputs", [])
    kinds: dict[str, int] = {}
    if isinstance(outputs, list):
        for output in outputs:
            if isinstance(output, dict):
                kind = str(output.get("kind", "unknown"))
                kinds[kind] = kinds.get(kind, 0) + 1
    return {
        "available": True,
        "scenario_id": data.get("scenario_id"),
        "input_count": len(data.get("inputs", [])),
        "output_count": len(outputs) if isinstance(outputs, list) else None,
        "output_kinds": kinds,
        "diagnostic_count": 0,
    }


def _evaluation_stage(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "available": True,
        "scenario_id": data.get("scenario_id"),
        "diagnostic_count": len(data.get("diagnostics", [])),
        "has_cached_validation_report": data.get("cached_validation_report") is not None,
        "has_oracle_validation_report": data.get("oracle_validation_report") is not None,
        "comparison_counts_found": bool(_extract_comparison_counts(data)),
    }


def _extract_comparison_counts(data: Any) -> dict[str, int]:
    return {
        key: value
        for key, value in {
            "comparable_output_count": _find_count(data, _COMPARABLE_KEYS),
            "match_count": _find_count(data, _MATCH_KEYS),
            "mismatch_count": _find_count(data, _MISMATCH_KEYS),
            "non_comparable_count": _find_count(data, _NON_COMPARABLE_KEYS),
        }.items()
        if value is not None
    }


def _comparison_status(counts: dict[str, int]) -> dict[str, Any]:
    comparable = counts.get("comparable_output_count")
    matches = counts.get("match_count")
    mismatches = counts.get("mismatch_count")
    status = "incomplete"
    if comparable is not None and matches is not None and mismatches is not None:
        status = "pass" if comparable == matches and mismatches == 0 else "fail"
    return {
        "status": status,
        "comparable_output_count": comparable,
        "match_count": matches,
        "mismatch_count": mismatches,
        "non_comparable_count": counts.get("non_comparable_count"),
    }


def _find_count(value: Any, keys: set[str]) -> int | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in keys and isinstance(item, int) and not isinstance(item, bool):
                return item
        for item in value.values():
            found = _find_count(item, keys)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_count(item, keys)
            if found is not None:
                return found
    return None


def _summary_markdown(summary: ValidationEvidenceSummary) -> str:
    comparison = summary.comparison
    lines = [
        f"# FABLE {summary.workbook_version} Validation Evidence",
        "",
        f"- evidence status: `{summary.evidence_status}`",
        f"- equivalence status: `{summary.equivalence_status}`",
        f"- comparable outputs: `{comparison.get('comparable_output_count')}`",
        f"- matches: `{comparison.get('match_count')}`",
        f"- mismatches: `{comparison.get('mismatch_count')}`",
        f"- non-comparable outputs: `{comparison.get('non_comparable_count')}`",
        "",
        "## Stage Summary",
        "",
    ]
    if summary.missing_artifacts:
        lines.extend(["Missing artifacts:", *[f"- `{name}`" for name in summary.missing_artifacts], ""])
    for name, stage in summary.stages.items():
        lines.append(f"- `{name}`: {json.dumps(stage, sort_keys=True)}")
    if summary.notes:
        lines.extend(["", "## Notes", "", *[f"- {note}" for note in summary.notes]])
    return "\n".join(lines).rstrip() + "\n"


_COMPARABLE_KEYS = {
    "comparable_output_count",
    "comparable_outputs",
    "comparable_cached_outputs",
    "total_comparable_outputs",
}
_MATCH_KEYS = {
    "match_count",
    "matches",
    "matched_outputs",
    "generated_output_matches",
}
_MISMATCH_KEYS = {
    "mismatch_count",
    "mismatches",
    "mismatched_outputs",
}
_NON_COMPARABLE_KEYS = {
    "non_comparable_count",
    "non_comparable_outputs",
    "non_comparable_cached_blank_formula_outputs",
}
