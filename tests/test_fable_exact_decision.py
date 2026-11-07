from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fable_exact_decision.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("fable_exact_decision", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _point(sample_id: str, food: float, ghg: float, land: float = 100.0) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "selections": {"id": sample_id},
        "objectives": {
            "food_total_kcal_feas": food,
            "ghg_total_co2e": ghg,
            "land_total_area": land,
        },
    }


def test_pareto_front_uses_food_max_ghg_min_and_ignores_constant_land() -> None:
    module = _load_module()
    points = [
        _point("a", 100.0, 50.0),
        _point("b", 90.0, 40.0),
        _point("c", 80.0, 60.0),
        _point("d", 100.0, 60.0),
    ]

    front = module.pareto_front(points)

    assert [point["sample_id"] for point in front] == ["a", "b"]


def test_food_first_and_ghg_first_respect_caps_and_floors() -> None:
    module = _load_module()
    points = [
        _point("a", 100.0, 50.0),
        _point("b", 90.0, 40.0),
        _point("c", 80.0, 60.0),
    ]

    assert module.select_food_first(points, 45.0)["sample_id"] == "b"
    assert module.select_ghg_first(points, 95.0)["sample_id"] == "a"
    assert module.select_food_first(points, 10.0) is None
    assert module.select_ghg_first(points, 101.0) is None


def test_dedupe_points_keeps_first_selection() -> None:
    module = _load_module()
    points = [_point("a", 100.0, 50.0), _point("a", 100.0, 50.0), _point("b", 90.0, 40.0)]

    unique = module._dedupe_points(points)

    assert [point["sample_id"] for point in unique] == ["a", "b"]


def test_help() -> None:
    import subprocess

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--food-ghg-cap" in result.stdout
    assert "--ghg-food-floor" in result.stdout
