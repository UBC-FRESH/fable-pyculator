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


def test_build_artifact_marks_front_points_and_views() -> None:
    module = _load_module()
    points = [
        _point("a", 100.0, 50.0),
        _point("b", 90.0, 40.0),
        _point("c", 80.0, 60.0),
    ]
    front = module.pareto_front(points)
    front_unique = module._unique_objectives(front)
    ranked = module.weighted_ranking(points)
    payload = {
        "point_count": 3,
        "unique_point_count": 3,
        "pareto_count": len(front),
        "pareto_unique_count": len(front_unique),
        "input": [],
        "aspirations": module.DEFAULT_ASPIRATIONS,
        "weights": module.DEFAULT_WEIGHTS,
        "ranges": module._ranges(points),
        "food_first_cap_ghg": 110.0,
        "ghg_first_floor_food": 3000.0,
        "balanced": ranked[0],
        "food_first": points[0],
        "ghg_first": points[1],
        "food_first_views": [],
        "ghg_first_views": [],
    }

    artifact = module.build_artifact(
        payload=payload,
        unique_points=points,
        front=front,
        front_unique=front_unique,
        ranked=ranked,
        version="2024",
        title="test",
    )

    assert len(artifact["points"]) == 3
    assert sum(1 for point in artifact["points"] if point["front"]) == 2
    assert [dimension["key"] for dimension in artifact["dimensions"]] == [
        "food_total_kcal_feas",
        "ghg_total_co2e",
        "land_total_area",
        "goal",
    ]
    assert artifact["views"]["balanced"]["point_id"]
    assert artifact["views"]["food_first"]["point_id"]


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
