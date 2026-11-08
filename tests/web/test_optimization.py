from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from fable_pyculator.web.app import create_app
from fable_pyculator.web.service import PortalConfig


def _write_frontier(repo_root: Path) -> None:
    path = repo_root / "examples" / "optimization" / "fable_2024" / "frontier.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "artifact_version": 1,
                "version": "2024",
                "title": "Test frontier",
                "generated_at": "2026-11-07T00:00:00+00:00",
                "boundary": "local test",
                "points": [
                    {"id": "p000", "origin": "Phase 40", "front": True, "objectives": {}, "selections": {}},
                    {"id": "p001", "origin": "Phase 37", "front": False, "objectives": {}, "selections": {}},
                ],
                "pareto_ids": ["p000"],
            }
        ),
        encoding="utf-8",
    )


def test_optimization_frontier_api(tmp_path: Path) -> None:
    _write_frontier(tmp_path)
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        listing = client.get("/api/optimization/frontiers")
        detail = client.get("/api/optimization/frontiers/2024")
        missing = client.get("/api/optimization/frontiers/1999")

    assert listing.status_code == 200
    assert listing.json()[0]["version"] == "2024"
    assert listing.json()[0]["point_count"] == 2
    assert listing.json()[0]["pareto_count"] == 1
    assert listing.json()[0]["origins"] == {"Phase 37": 1, "Phase 40": 1}
    assert detail.status_code == 200
    assert detail.json()["title"] == "Test frontier"
    assert missing.status_code == 404


def test_optimization_page_and_vendor_assets_are_served(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        shell = client.get("/")
        script = client.get("/static/app.js")
        three = client.get("/static/vendor/three/three.module.js")
        controls = client.get("/static/vendor/three/OrbitControls.js")

    assert shell.status_code == 200
    assert 'data-page="optimization"' in shell.text
    assert 'id="page-optimization"' in shell.text
    assert 'id="pareto-canvas"' in shell.text
    assert 'id="pareto-x"' in shell.text
    assert 'id="pareto-load"' in shell.text
    assert 'id="pareto-tooltip"' in shell.text
    assert 'id="pareto-ranges"' in shell.text
    assert 'id="pareto-warning-free"' in shell.text
    assert 'id="pareto-copy-link"' in shell.text
    assert 'id="pareto-download-csv"' in shell.text
    assert 'id="parallel-chart"' in shell.text
    assert 'id="parallel-count"' in shell.text
    assert 'id="pareto-reference"' in shell.text
    assert 'id="pareto-clear-reference"' in shell.text
    assert 'id="pareto-delta"' in shell.text
    assert 'id="parallel-clear-brush"' in shell.text
    assert 'id="parallel-brush-label"' in shell.text
    assert 'id="optimization-preset"' in shell.text
    assert 'id="optimization-preset-save"' in shell.text
    assert 'id="optimization-preset-load"' in shell.text
    assert 'id="optimization-preset-delete"' in shell.text
    assert 'id="optimization-preset-export"' in shell.text
    assert 'id="optimization-preset-import"' in shell.text
    assert 'id="optimization-preset-file"' in shell.text
    assert 'id="optimization-preset-copy-link"' in shell.text
    assert 'id="optimization-shared-preset"' in shell.text
    assert 'id="optimization-shared-save"' in shell.text
    assert 'id="optimization-shared-load"' in shell.text
    assert 'id="optimization-shared-delete"' in shell.text
    assert 'id="optimization-shared-author"' in shell.text
    assert 'id="optimization-shared-note"' in shell.text
    assert 'id="optimization-shared-review"' in shell.text
    assert 'id="optimization-shared-filter"' in shell.text
    assert 'id="optimization-shared-summary"' in shell.text
    assert 'id="optimization-shared-mark-reviewed"' in shell.text
    assert 'id="optimization-shared-history"' in shell.text
    assert 'id="optimization-shared-audit"' in shell.text
    assert 'id="optimization-shared-export"' in shell.text
    assert 'id="optimization-shared-export-csv"' in shell.text
    assert 'id="optimization-shared-timeline"' in shell.text
    assert script.status_code == 200
    assert "drawOptimization" in script.text
    assert "loadOptimizationPointInWorkbench" in script.text
    assert "optimization/frontiers" in script.text
    assert "updateOptimizationSelectionMarker" in script.text
    assert "optimizationLegendHtml" in script.text
    assert "updateOptimizationRangeNote" in script.text
    assert "persistOptimizationState" in script.text
    assert "restoreOptimizationState" in script.text
    assert "downloadOptimizationCsv" in script.text
    assert "drawParallelCoordinates" in script.text
    assert "PARALLEL_AXES" in script.text
    assert "setOptimizationReference" in script.text
    assert "renderOptimizationDelta" in script.text
    assert "opt_reference" in script.text
    assert "beginParallelBrush" in script.text
    assert "clearOptimizationBrush" in script.text
    assert "parallelBrushMatches" in script.text
    assert "opt_brush" in script.text
    assert "opt_brushes" in script.text
    assert "removeOptimizationBrush" in script.text
    assert "brushes: []" in script.text
    assert "loadOptimizationPresets" in script.text
    assert "applyOptimizationPreset" in script.text
    assert "localStorage" in script.text
    assert "exportOptimizationPresets" in script.text
    assert "importOptimizationPresets" in script.text
    assert "normalizeImportedPreset" in script.text
    assert "copyOptimizationPresetLink" in script.text
    assert "opt_preset" in script.text
    assert "loadSharedOptimizationPresets" in script.text
    assert "saveSharedOptimizationPreset" in script.text
    assert "deleteSharedOptimizationPreset" in script.text
    assert "syncSharedPresetMetadata" in script.text
    assert "review_status" in script.text
    assert "markSharedOptimizationPresetReviewed" in script.text
    assert "sharedFilter" in script.text
    assert "renderSharedPresetHistory" in script.text
    assert "renderSharedAudit" in script.text
    assert "exportSharedOptimizationPresets" in script.text
    assert "renderSharedTimeline" in script.text
    assert "exportSharedAuditCsv" in script.text
    assert three.status_code == 200
    assert "THREE" in three.text
    assert controls.status_code == 200
    assert "OrbitControls" in controls.text


def _preset_payload(name: str, review_status: str = "reviewed") -> dict[str, object]:
    return {
        "name": name,
        "author": "Reviewer",
        "note": "Team view",
        "review_status": review_status,
        "state": {
            "version": "2024",
            "x": "food_total_kcal_feas",
            "y": "ghg_total_co2e",
            "z": "goal",
            "colour": "front",
            "size": "uniform",
            "floor_dimension": "goal",
            "floor": 0,
            "front": True,
            "warning_free": True,
            "brushes": [{"axisKey": "diet_scen", "start": 0.25, "end": 0.6}],
            "reference": "p012",
            "point": "p001",
        },
    }


def test_shared_optimization_preset_api_round_trip(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        assert client.get("/api/optimization/presets").json() == []
        created = client.post("/api/optimization/presets", json=_preset_payload("Shared view"))
        assert created.status_code == 200
        assert created.json()["name"] == "Shared view"
        listing = client.get("/api/optimization/presets").json()
        assert len(listing) == 1
        assert listing[0]["state"]["brushes"][0]["axisKey"] == "diet_scen"
        assert listing[0]["author"] == "Reviewer"
        assert listing[0]["note"] == "Team view"
        assert listing[0]["review_status"] == "reviewed"
        assert listing[0]["history"][-1]["action"] == "created"

        replaced = client.post("/api/optimization/presets", json=_preset_payload("Shared view"))
        assert replaced.status_code == 200
        assert len(client.get("/api/optimization/presets").json()) == 1

        invalid = client.post("/api/optimization/presets", json={"name": "Bad", "state": {}})
        assert invalid.status_code == 400
        invalid_review = client.post(
            "/api/optimization/presets",
            json={**_preset_payload("Bad review"), "review_status": "approved"},
        )
        assert invalid_review.status_code == 400

        deleted = client.delete("/api/optimization/presets/Shared view")
        assert deleted.status_code == 200
        assert client.get("/api/optimization/presets").json() == []
        assert client.delete("/api/optimization/presets/Shared view").status_code == 404


def test_shared_optimization_presets_survive_app_restart(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        assert client.post("/api/optimization/presets", json=_preset_payload("Persistent")).status_code == 200
    with TestClient(create_app(config)) as client:
        listing = client.get("/api/optimization/presets").json()
    assert [preset["name"] for preset in listing] == ["Persistent"]


def test_shared_preset_history_records_review(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        created = client.post(
            "/api/optimization/presets",
            json=_preset_payload("History view", review_status="draft"),
        ).json()
        assert created["history"][-1]["action"] == "created"

        reviewed = client.post(
            "/api/optimization/presets",
            json=_preset_payload("History view", review_status="reviewed"),
        ).json()
        assert reviewed["history"][-1]["action"] == "reviewed"
        assert len(reviewed["history"]) == 2

    with TestClient(create_app(config)) as client:
        listing = client.get("/api/optimization/presets").json()
    assert [event["action"] for event in listing[0]["history"]] == ["created", "reviewed"]
