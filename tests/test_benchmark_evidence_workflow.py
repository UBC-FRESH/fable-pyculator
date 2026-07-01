from __future__ import annotations

from pathlib import Path

import yaml


def test_benchmark_evidence_workflow_is_manual_and_uploads_only_summaries() -> None:
    workflow = yaml.safe_load(Path(".github/workflows/benchmark-evidence.yml").read_text(encoding="utf-8"))

    assert "workflow_dispatch" in workflow[True]
    assert "pull_request" not in workflow[True]
    assert "push" not in workflow[True]
    steps = workflow["jobs"]["package-evidence"]["steps"]
    upload = next(step for step in steps if step.get("name") == "Upload compact evidence summaries")
    path_value = upload["with"]["path"]
    assert "tmp/validation-evidence/**" in path_value
    assert "tmp/generated-models" not in path_value
    assert "tmp/private-workbooks" not in path_value
