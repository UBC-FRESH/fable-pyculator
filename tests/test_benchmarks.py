from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import pytest

from fable_pyculator.benchmarks import (
    FableBenchmarkRunSummary,
    fable_benchmark_run_paths,
    package_fable_benchmark_evidence,
    write_fable_benchmark_summary,
)


def test_fable_benchmark_run_paths_are_version_specific(tmp_path: Path) -> None:
    paths_2020 = fable_benchmark_run_paths(workbook_version="2020", repo_root=tmp_path)
    paths_2021 = fable_benchmark_run_paths(workbook_version="2021", repo_root=tmp_path)
    paths_2022 = fable_benchmark_run_paths(workbook_version="2022", repo_root=tmp_path)

    assert paths_2020.artifact_dir == tmp_path / "tmp/generated-models/fable-2020"
    assert paths_2021.output_dir == tmp_path / "tmp/validation-evidence/fable-2021"
    assert paths_2022.benchmark_summary_json_path == tmp_path / "tmp/validation-evidence/fable-2022/benchmark-summary.json"


def test_package_benchmark_evidence_falls_back_to_fable_local(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import fable_pyculator.benchmarks as benchmarks

    monkeypatch.setattr(benchmarks, "_modelwright_evidence_api", lambda: None)

    summary = package_fable_benchmark_evidence(workbook_version="2021", repo_root=tmp_path)

    assert summary.evidence_backend == "fable-local"
    assert summary.evidence_status == "skipped"
    assert summary.equivalence_status == "incomplete"
    assert "inference_result" in summary.missing_artifacts
    assert summary.freshforge == {"status": "not-requested"}


def test_package_benchmark_evidence_prefers_modelwright_backend(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    import fable_pyculator.benchmarks as benchmarks

    calls: dict[str, Any] = {}

    def fake_paths(**kwargs: Any) -> _FakeEvidencePaths:
        calls["paths"] = kwargs
        return _FakeEvidencePaths(summary_json_path=tmp_path / "summary.json")

    def fake_extract(paths: _FakeEvidencePaths, *, require_artifacts: bool = False) -> _FakeEvidenceSummary:
        calls["require_artifacts"] = require_artifacts
        return _FakeEvidenceSummary()

    def fake_write(summary: _FakeEvidenceSummary, paths: _FakeEvidencePaths) -> dict[str, Any]:
        return {"summary": summary.to_dict()}

    monkeypatch.setattr(benchmarks, "_modelwright_evidence_api", lambda: (fake_paths, fake_extract, fake_write))

    summary = package_fable_benchmark_evidence(workbook_version="2021", repo_root=tmp_path)

    assert summary.evidence_backend == "modelwright"
    assert summary.evidence_status == "complete"
    assert summary.equivalence_status == "pass"
    assert summary.comparison["mismatch_count"] == 0
    assert calls["paths"]["evidence_id"] == "fable-2021"
    assert calls["require_artifacts"] is False


def test_package_benchmark_evidence_require_artifacts_fails(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="missing validation"):
        package_fable_benchmark_evidence(workbook_version="2021", repo_root=tmp_path, require_artifacts=True)


def test_freshforge_plan_mode_skips_missing_workbook_without_requirement(tmp_path: Path) -> None:
    summary = package_fable_benchmark_evidence(
        workbook_version="2021",
        repo_root=tmp_path,
        mode="freshforge-plan",
    )

    assert summary.freshforge["status"] == "skipped"
    assert summary.freshforge["reason"] == "missing-workbook"
    assert any("FreshForge plan mode skipped" in note for note in summary.notes)


def test_freshforge_run_mode_requires_workbook(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="2021 FABLE workbook not found"):
        package_fable_benchmark_evidence(
            workbook_version="2021",
            repo_root=tmp_path,
            mode="freshforge-run",
        )


def test_scenario_bundle_summary_ingestion_is_compact(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.yaml"
    bundle.write_text("version: 1\n", encoding="utf-8")
    summary_path = tmp_path / "freshforge-run-summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "summary": {
                    "workflow_id": "demo",
                    "run_namespace": "test/run",
                    "status": "succeeded",
                    "node_counts": {"succeeded": 2},
                    "diagnostic_counts": {"error": 0},
                    "artifact_count": 4,
                    "raw_node_payload": {"should": "not appear"},
                }
            }
        ),
        encoding="utf-8",
    )

    summary = package_fable_benchmark_evidence(
        workbook_version="2021",
        repo_root=tmp_path,
        bundle_path=bundle,
        include_scenario_bundle_summary=True,
    )

    assert summary.scenario_bundle["summary"]["workflow_id"] == "demo"
    assert "raw_node_payload" not in json.dumps(summary.to_dict())


def test_write_fable_benchmark_summary_is_stable_and_sanitized(tmp_path: Path) -> None:
    paths = fable_benchmark_run_paths(workbook_version="2021", repo_root=tmp_path)
    summary = FableBenchmarkRunSummary(
        workbook_version="2021",
        mode="evidence-only",
        evidence_backend="fable-local",
        evidence_status="complete",
        equivalence_status="pass",
        missing_artifacts=(),
        comparison={"comparable_output_count": 2, "match_count": 2, "mismatch_count": 0},
        paths={"artifact_dir": "tmp/generated-models/fable-2021"},
        notes=("Compact summary only.",),
    )

    payload = write_fable_benchmark_summary(summary, paths)

    assert payload["equivalence_status"] == "pass"
    assert paths.benchmark_summary_json_path.exists()
    markdown = paths.benchmark_summary_markdown_path.read_text(encoding="utf-8")
    assert "# FABLE 2021 Benchmark Evidence" in markdown
    assert "source_code" not in json.dumps(payload)
    assert "output_values" not in json.dumps(payload)
    assert "Open_FABLECalculator.xlsx" not in json.dumps(payload)


@dataclass(frozen=True)
class _FakeEvidencePaths:
    summary_json_path: Path


class _FakeEvidenceSummary:
    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": "fable-2021",
            "evidence_status": "complete",
            "equivalence_status": "pass",
            "missing_artifacts": [],
            "comparison": {
                "comparable_output_count": 2,
                "match_count": 2,
                "mismatch_count": 0,
            },
            "notes": ["Generated by fake modelwright evidence backend."],
        }
