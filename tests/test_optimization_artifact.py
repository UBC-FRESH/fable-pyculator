from __future__ import annotations

import json
from pathlib import Path

ARTIFACT = Path(__file__).resolve().parents[1] / "examples" / "optimization" / "fable_2024" / "frontier.json"


def test_tracked_optimization_artifact_is_complete_and_consistent() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["version"] == "2024"
    assert payload["artifact_version"] == 1
    assert len(payload["points"]) == 160
    assert sum(1 for point in payload["points"] if point["front"]) == 29
    assert len(payload["pareto_ids"]) == 15
    assert [dimension["key"] for dimension in payload["dimensions"]] == [
        "food_total_kcal_feas",
        "ghg_total_co2e",
        "land_total_area",
        "goal",
    ]

    point_ids = {point["id"] for point in payload["points"]}
    assert len(point_ids) == len(payload["points"])
    assert all(point_id in point_ids for point_id in payload["pareto_ids"])
    for view in (
        payload["views"]["balanced"],
        payload["views"]["food_first"],
        payload["views"]["ghg_first"],
        *payload["views"]["food_first_views"],
        *payload["views"]["ghg_first_views"],
    ):
        assert view["point_id"] in point_ids

    for point in payload["points"]:
        assert set(point["objectives"]) == {
            "food_total_kcal_feas",
            "ghg_total_co2e",
            "land_total_area",
        }
        assert point["selections"]
        assert point["origin"] in {"Phase 37", "Phase 38", "Phase 39", "Phase 40", "Other"}
