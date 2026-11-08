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
    assert three.status_code == 200
    assert "THREE" in three.text
    assert controls.status_code == 200
    assert "OrbitControls" in controls.text
