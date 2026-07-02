from __future__ import annotations

from pathlib import Path

import yaml


def test_benchmark_evidence_workflow_is_manual_and_uploads_only_summaries() -> None:
    workflow = yaml.safe_load(Path(".github/workflows/benchmark-evidence.yml").read_text(encoding="utf-8"))

    assert "workflow_dispatch" in workflow[True]
    assert "pull_request" not in workflow[True]
    assert "push" not in workflow[True]
    inputs = workflow[True]["workflow_dispatch"]["inputs"]
    assert inputs["mode"]["options"] == ["evidence-only", "freshforge-plan", "freshforge-run"]
    assert inputs["output_ref_strategy"]["default"] == "output-columns"
    assert inputs["require_artifacts"]["default"] is False
    steps = workflow["jobs"]["package-evidence"]["steps"]
    upload = next(step for step in steps if step.get("name") == "Upload compact evidence summaries")
    path_value = upload["with"]["path"]
    assert "tmp/validation-evidence/**" in path_value
    assert "tmp/benchmark-evidence-summary.json" in path_value
    forbidden_paths = (
        "tmp/generated-models",
        "tmp/private-workbooks",
        "tmp/scenario-runs",
        "generated_fable_",
        "evaluation-report.json",
        "generated-values.json",
    )
    for forbidden in forbidden_paths:
        assert forbidden not in path_value
