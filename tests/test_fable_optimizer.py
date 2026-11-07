from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("torch")
pytest.importorskip("numpy")

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fable_gpu_optimizer.py"


def _dataset(path: Path) -> Path:
    controls = [
        {"name": "a", "options": ["a1", "a2"], "default": "a1"},
        {"name": "b", "options": ["b1", "b2", "b3"], "default": "b2"},
        {"name": "c", "options": ["c1", "c2"], "default": "c1"},
    ]
    rows = []
    for index in range(24):
        choices = {
            "a": controls[0]["options"][index % 2],
            "b": controls[1]["options"][(index // 2) % 3],
            "c": controls[2]["options"][(index // 6) % 2],
        }
        rows.append(
            {
                "sample_id": f"sample_{index:03d}",
                "selections": choices,
                "objectives": {
                    "food": 100.0 + 10.0 * (choices["a"] == "a2") + 5.0 * (choices["b"] == "b3"),
                    "ghg": 50.0 - 8.0 * (choices["a"] == "a2") + 2.0 * (choices["c"] == "c2"),
                },
            }
        )
    payload = {"version": "test", "controls": controls, "samples": rows}
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_gpu_optimizer_merges_fixed_controls(tmp_path: Path) -> None:
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("fable_gpu_optimizer_fixed", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    dataset = json.loads(_dataset(tmp_path / "dataset.json").read_text(encoding="utf-8"))
    dataset["variable_controls"] = ["a", "b"]
    dataset["baseline_selections"] = {"a": "a1", "b": "b2", "c": "c1"}
    path = tmp_path / "dataset-fixed.json"
    path.write_text(json.dumps(dataset), encoding="utf-8")
    output = tmp_path / "result-fixed.json"

    code = module.main(
        [
            "--dataset",
            str(path),
            "--output",
            str(output),
            "--population",
            "16",
            "--generations",
            "3",
            "--epochs",
            "20",
            "--ensemble-size",
            "2",
            "--top-k",
            "2",
            "--device",
            "cpu",
            "--objective",
            "food:max:1.0",
            "--objective",
            "ghg:min:1.0",
        ]
    )

    assert code == 0
    result = json.loads(output.read_text(encoding="utf-8"))
    assert all(candidate["selections"]["c"] == "c1" for candidate in result["top_candidates"])


def test_gpu_optimizer_runs_on_synthetic_data(tmp_path: Path) -> None:
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("fable_gpu_optimizer", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    dataset = _dataset(tmp_path / "dataset.json")
    output = tmp_path / "result.json"
    code = module.main(
        [
            "--dataset",
            str(dataset),
            "--output",
            str(output),
            "--population",
            "32",
            "--generations",
            "5",
            "--epochs",
            "40",
            "--top-k",
            "3",
            "--device",
            "cpu",
            "--objective",
            "food:max:1.0",
            "--objective",
            "ghg:min:1.0",
        ]
    )

    assert code == 0
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["device"] == "cpu"
    assert 1 <= len(result["top_candidates"]) <= 3
    assert result["metrics"]["objective_names"] == ["food", "ghg"]
    assert all(candidate["selections"]["a"] in {"a1", "a2"} for candidate in result["top_candidates"])
