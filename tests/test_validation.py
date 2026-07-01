from __future__ import annotations

import json
from pathlib import Path

import pytest

from fable_pyculator import (
    extract_validation_evidence,
    fable_validation_evidence_paths,
    write_validation_evidence,
)


def test_extract_validation_evidence_reports_explicit_pass(tmp_path: Path) -> None:
    paths = fable_validation_evidence_paths(workbook_version="2021", repo_root=tmp_path)
    _write_artifacts(paths.artifact_dir, mismatches=0)

    summary = extract_validation_evidence(paths, workbook_version="2021")

    assert summary.evidence_status == "complete"
    assert summary.equivalence_status == "pass"
    assert summary.comparison["comparable_output_count"] == 2
    assert summary.comparison["match_count"] == 2
    assert summary.comparison["mismatch_count"] == 0
    assert summary.stages["inference"]["constants_count"] == 1
    assert summary.stages["generation"]["source_size_bytes"] == len("def calculate():\n".encode("utf-8"))
    assert summary.stages["generated_execution"]["output_value_count"] == 2
    assert summary.stages["validation_scenario"]["output_kinds"] == {"number": 1, "text": 1}


def test_extract_validation_evidence_reports_explicit_fail(tmp_path: Path) -> None:
    paths = fable_validation_evidence_paths(workbook_version="2021", repo_root=tmp_path)
    _write_artifacts(paths.artifact_dir, mismatches=1, matches=1)

    summary = extract_validation_evidence(paths, workbook_version="2021")

    assert summary.equivalence_status == "fail"
    assert summary.comparison["mismatch_count"] == 1


def test_extract_validation_evidence_reports_incomplete_without_comparison_counts(tmp_path: Path) -> None:
    paths = fable_validation_evidence_paths(workbook_version="2021", repo_root=tmp_path)
    _write_artifacts(paths.artifact_dir, include_comparison=False)

    summary = extract_validation_evidence(paths, workbook_version="2021")

    assert summary.evidence_status == "incomplete"
    assert summary.equivalence_status == "incomplete"
    assert "source_code" not in json.dumps(summary.to_dict())
    assert "GHG!B3" not in json.dumps(summary.to_dict())


def test_extract_validation_evidence_handles_missing_artifacts(tmp_path: Path) -> None:
    paths = fable_validation_evidence_paths(workbook_version="2022", repo_root=tmp_path)

    summary = extract_validation_evidence(paths, workbook_version="2022")

    assert summary.evidence_status == "skipped"
    assert summary.equivalence_status == "incomplete"
    assert "inference_result" in summary.missing_artifacts
    with pytest.raises(FileNotFoundError, match="missing validation artifact"):
        extract_validation_evidence(paths, workbook_version="2022", require_artifacts=True)


def test_write_validation_evidence_writes_stable_json_and_markdown(tmp_path: Path) -> None:
    paths = fable_validation_evidence_paths(workbook_version="2021", repo_root=tmp_path)
    _write_artifacts(paths.artifact_dir)
    summary = extract_validation_evidence(paths, workbook_version="2021")

    payload = write_validation_evidence(summary, paths)

    assert payload["equivalence_status"] == "pass"
    assert paths.summary_json_path.exists()
    assert paths.summary_markdown_path.exists()
    assert json.loads(paths.summary_json_path.read_text(encoding="utf-8"))["workbook_version"] == "2021"
    markdown = paths.summary_markdown_path.read_text(encoding="utf-8")
    assert "# FABLE 2021 Validation Evidence" in markdown
    assert "source_code" not in markdown
    assert "GHG!B3" not in markdown


def _write_artifacts(
    artifact_dir: Path,
    *,
    include_comparison: bool = True,
    matches: int = 2,
    mismatches: int = 0,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        artifact_dir / "inference-result.json",
        {
            "constants": {"Inputs!A1": 1},
            "contract": {"input_refs": ["Inputs!A1"], "output_refs": ["GHG!B3", "GHG!C3"]},
            "diagnostics": [],
            "expressions": {"GHG!B3": "1 + 1"},
            "inferred": True,
        },
    )
    _write_json(
        artifact_dir / "generation-result.json",
        {
            "contract": {"output_refs": ["GHG!B3", "GHG!C3"]},
            "diagnostics": [],
            "generated": True,
            "source_code": "def calculate():\n",
        },
    )
    _write_json(
        artifact_dir / "generated-values.json",
        {
            "contract": {"output_refs": ["GHG!B3", "GHG!C3"]},
            "diagnostics": [],
            "entrypoint": "calculate",
            "executed": True,
            "output_values": {"GHG!B3": 2, "GHG!C3": "ok"},
        },
    )
    _write_json(
        artifact_dir / "validation-scenario.json",
        {
            "scenario_id": "synthetic",
            "inputs": [],
            "outputs": [
                {"cell_ref": "GHG!B3", "kind": "number"},
                {"cell_ref": "GHG!C3", "kind": "text"},
            ],
        },
    )
    comparison = (
        {
            "comparison": {
                "comparable_output_count": 2,
                "match_count": matches,
                "mismatch_count": mismatches,
                "non_comparable_count": 1,
            }
        }
        if include_comparison
        else {}
    )
    _write_json(
        artifact_dir / "evaluation-report.json",
        {
            "diagnostics": [],
            "generated_execution": {"executed": True},
            "scenario_id": "synthetic",
            **comparison,
        },
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")
