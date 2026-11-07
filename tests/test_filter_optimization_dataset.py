from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "filter_optimization_dataset.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("filter_optimization_dataset", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_filter_dataset_keeps_valid_and_rejects_invalid(tmp_path: Path) -> None:
    module = _load_module()
    rules = tmp_path / "rules.yaml"
    rules.write_text(
        """
rules:
  - id: HARD-001
    family: test
    severity: error
    confidence: high
    status: proposed
    when:
      switch: a
      in: [bad]
    message: bad
    review_question: n/a
""",
        encoding="utf-8",
    )
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"spec": {"scenario_definition_tables": []}}), encoding="utf-8")
    dataset = tmp_path / "dataset.json"
    dataset.write_text(
        json.dumps(
            {
                "samples": [
                    {"sample_id": "ok", "selections": {"a": "ok"}, "objectives": {"x": 1}},
                    {"sample_id": "bad", "selections": {"a": "bad"}, "objectives": {"x": 2}},
                ]
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "filtered.json"

    code = module.main(
        [
            "--dataset",
            str(dataset),
            "--rules",
            str(rules),
            "--spec",
            str(spec),
            "--mode",
            "draft_enforced",
            "--output",
            str(output),
        ]
    )

    assert code == 0
    filtered = json.loads(output.read_text(encoding="utf-8"))
    assert [sample["sample_id"] for sample in filtered["samples"]] == ["ok"]
    assert filtered["rejected_count"] == 1
    assert filtered["provisional"] is True


def test_filter_dataset_help() -> None:
    import subprocess

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--rules" in result.stdout
    assert "--mode" in result.stdout
