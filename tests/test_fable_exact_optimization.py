from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fable_exact_optimization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("fable_exact_optimization", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sample(sample_id: str, food: float, ghg: float, land: float) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "selections": {"id": sample_id},
        "objectives": {
            "food_total_kcal_feas": food,
            "ghg_total_co2e": ghg,
            "land_total_area": land,
        },
    }


def test_pareto_front_maximizes_food_and_minimizes_ghg_and_land() -> None:
    module = _load_module()
    samples = [
        _sample("a", 100.0, 50.0, 100.0),
        _sample("b", 90.0, 40.0, 100.0),
        _sample("c", 80.0, 60.0, 100.0),
        _sample("d", 100.0, 60.0, 100.0),
    ]

    front = module.pareto_front(samples)

    assert [row["sample_id"] for row in front] == ["a", "b"]


def test_weighted_ranking_prefers_higher_food_and_lower_ghg() -> None:
    module = _load_module()
    samples = [
        _sample("bad", 10.0, 100.0, 100.0),
        _sample("good", 100.0, 10.0, 100.0),
    ]

    ranked = module.weighted_ranking(samples)

    assert [row["sample_id"] for row in ranked] == ["good", "bad"]


def test_help() -> None:
    import subprocess

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--controls" in result.stdout
    assert "--rule-mode" in result.stdout
