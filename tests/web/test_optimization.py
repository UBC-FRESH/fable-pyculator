from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fable_pyculator.web.app import create_app
from fable_pyculator.web.service import PortalConfig, PortalState


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
    assert 'id="optimization-shared-backup"' in shell.text
    assert 'id="optimization-shared-restore"' in shell.text
    assert 'id="optimization-shared-restore-file"' in shell.text
    assert 'id="optimization-shared-restore-confirm"' in shell.text
    assert 'id="optimization-shared-restore-mode"' in shell.text
    assert 'id="optimization-shared-restore-preview"' in shell.text
    assert 'id="optimization-shared-snapshot-now"' in shell.text
    assert 'id="optimization-shared-snapshot-refresh"' in shell.text
    assert 'id="optimization-shared-snapshots"' in shell.text
    assert 'id="optimization-shared-timeline"' in shell.text
    assert 'id="optimization-timeline-author"' in shell.text
    assert 'id="optimization-timeline-action"' in shell.text
    assert 'id="optimization-timeline-preset"' in shell.text
    assert 'id="optimization-timeline-window"' in shell.text
    assert 'id="optimization-timeline-recently-reviewed"' in shell.text
    assert 'id="optimization-review-workload"' in shell.text
    assert 'id="optimization-timeline-preset"' in shell.text
    assert 'id="optimization-timeline-preset-save"' in shell.text
    assert 'id="optimization-timeline-preset-load"' in shell.text
    assert 'id="optimization-timeline-preset-delete"' in shell.text
    assert 'id="optimization-timeline-preset-copy-link"' in shell.text
    assert 'id="optimization-timeline-preset-export"' in shell.text
    assert 'id="optimization-timeline-preset-import"' in shell.text
    assert 'id="optimization-shared-timeline-view"' in shell.text
    assert 'id="optimization-shared-timeline-save"' in shell.text
    assert 'id="optimization-shared-timeline-load"' in shell.text
    assert 'id="optimization-shared-timeline-delete"' in shell.text
    assert 'id="optimization-shared-timeline-author"' in shell.text
    assert 'id="optimization-shared-timeline-note"' in shell.text
    assert 'id="optimization-shared-timeline-review"' in shell.text
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
    assert "exportSharedLibraryBackup" in script.text
    assert "previewSharedLibraryRestore" in script.text
    assert "confirmSharedLibraryRestore" in script.text
    assert "requestSharedLibraryRestorePreview" in script.text
    assert "optimization/library/restore" in script.text
    assert "loadLibrarySnapshots" in script.text
    assert "renderLibrarySnapshots" in script.text
    assert "createLibrarySnapshot" in script.text
    assert "downloadLibrarySnapshot" in script.text
    assert "prepareLibrarySnapshotRestore" in script.text
    assert "optimization/snapshots" in script.text
    assert "timelineFilter" in script.text
    assert "Recently reviewed" in shell.text
    assert "renderReviewWorkload" in script.text
    assert "data-workload-author" in script.text
    assert "loadTimelinePresets" in script.text
    assert "applyTimelineFilter" in script.text
    assert "TIMELINE_PRESETS_KEY" in script.text
    assert "copyTimelineLink" in script.text
    assert "exportTimelinePresets" in script.text
    assert "opt_tl_author" in script.text
    assert "loadSharedTimelineViews" in script.text
    assert "saveSharedTimelineView" in script.text
    assert "optimization/timeline-views" in script.text
    assert "syncSharedTimelineMetadata" in script.text
    assert "pruneOptimizationHistory" in script.text
    assert "optimization/presets/prune" in script.text
    assert "loadRetentionPolicy" in script.text
    assert "optimization/retention" in script.text
    assert "history_retention_interval_minutes" in script.text
    assert "loadRetentionRuns" in script.text
    assert "optimization/retention/runs" in script.text
    assert "exportRetentionRunsCsv" in script.text
    assert "renderRetentionDetail" in script.text
    assert "resetPruneConfirmation" in script.text
    assert "Confirm prune" in script.text
    assert "exportRetentionDiffCsv" in script.text
    assert "retentionSelected" in script.text
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
            "/api/optimization/timeline-views",
            json={**_timeline_view_payload("Bad review"), "review_status": "approved"},
        )
        assert invalid_review.status_code == 400
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


def _timeline_view_payload(name: str) -> dict[str, object]:
    return {
        "name": name,
        "author": "Hisham",
        "note": "Team timeline",
        "review_status": "reviewed",
        "filter": {"author": "Hisham", "action": "reviewed", "preset": "Team view", "window": "7d"},
    }


def test_shared_timeline_view_api_round_trip(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        assert client.get("/api/optimization/timeline-views").json() == []
        created = client.post("/api/optimization/timeline-views", json=_timeline_view_payload("My reviews"))
        assert created.status_code == 200
        listing = client.get("/api/optimization/timeline-views").json()
        assert listing[0]["filter"]["window"] == "7d"
        assert listing[0]["filter"]["action"] == "reviewed"
        assert listing[0]["author"] == "Hisham"
        assert listing[0]["note"] == "Team timeline"
        assert listing[0]["review_status"] == "reviewed"

        invalid = client.post(
            "/api/optimization/timeline-views",
            json={"name": "Bad", "filter": {"window": "year"}},
        )
        assert invalid.status_code == 400

        assert client.delete("/api/optimization/timeline-views/My reviews").status_code == 200
        assert client.get("/api/optimization/timeline-views").json() == []


def test_shared_timeline_views_survive_app_restart(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        assert (
            client.post("/api/optimization/timeline-views", json=_timeline_view_payload("Persistent")).status_code
            == 200
        )
    with TestClient(create_app(config)) as client:
        listing = client.get("/api/optimization/timeline-views").json()
    assert [view["name"] for view in listing] == ["Persistent"]


def test_shared_library_backup_round_trip(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        client.post("/api/optimization/presets", json=_preset_payload("Team view"))
        client.post("/api/optimization/timeline-views", json=_timeline_view_payload("Team timeline"))
        bundle = client.get("/api/optimization/library").json()

        assert bundle["schema"] == "fable-pyculator.optimization-library"
        assert bundle["schema_version"] == 1
        assert bundle["presets"][0]["history"][-1]["action"] == "created"
        assert bundle["timeline_views"][0]["filter"]["window"] == "7d"

        assert client.delete("/api/optimization/presets/Team view").status_code == 200
        assert client.delete("/api/optimization/timeline-views/Team timeline").status_code == 200

        preview = client.post(
            "/api/optimization/library/restore",
            json={
                "presets": bundle["presets"],
                "timeline_views": bundle["timeline_views"],
                "mode": "replace",
                "dry_run": True,
            },
        )
        assert preview.status_code == 200
        assert preview.json()["dry_run"] is True
        assert preview.json()["changed"] is True
        assert preview.json()["presets"]["added"] == 1
        assert client.get("/api/optimization/presets").json() == []
        assert client.get("/api/optimization/timeline-views").json() == []

        restored = client.post(
            "/api/optimization/library/restore",
            json={
                "presets": bundle["presets"],
                "timeline_views": bundle["timeline_views"],
                "mode": "replace",
                "dry_run": False,
            },
        )
        assert restored.status_code == 200
        assert restored.json()["dry_run"] is False
        assert restored.json()["presets"]["result"] == 1
        assert restored.json()["timeline_views"]["result"] == 1
        presets = client.get("/api/optimization/presets").json()
        views = client.get("/api/optimization/timeline-views").json()
        assert presets[0]["name"] == "Team view"
        assert presets[0]["state"]["point"] == "p001"
        assert presets[0]["history"][-1]["action"] == "created"
        assert views[0]["name"] == "Team timeline"
        assert views[0]["filter"]["action"] == "reviewed"


def test_shared_library_merge_preview_and_rejections(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    existing = _preset_payload("Existing")
    incoming_existing = _preset_payload("Existing")
    incoming_existing["note"] = "From backup"
    incoming_existing["history"] = [
        {
            "at": "2000-01-01T00:00:00+00:00",
            "action": "updated",
            "author": "Backup",
            "note": "Restored",
            "review_status": "reviewed",
        }
    ]
    incoming_new = _preset_payload("New")
    with TestClient(create_app(config)) as client:
        client.post("/api/optimization/presets", json=existing)
        client.post("/api/optimization/timeline-views", json=_timeline_view_payload("Existing view"))
        payload = {
            "presets": [incoming_existing, incoming_new],
            "timeline_views": [_timeline_view_payload("New view")],
            "mode": "merge",
        }

        preview = client.post("/api/optimization/library/restore", json={**payload, "dry_run": True})
        assert preview.status_code == 200
        assert preview.json()["presets"]["added"] == 1
        assert preview.json()["presets"]["replaced"] == 1
        assert preview.json()["presets"]["removed"] == 0
        assert preview.json()["timeline_views"]["added"] == 1
        assert client.get("/api/optimization/presets").json()[0]["note"] == "Team view"

        applied = client.post("/api/optimization/library/restore", json={**payload, "dry_run": False})
        assert applied.status_code == 200
        listed = client.get("/api/optimization/presets").json()
        assert [preset["name"] for preset in listed] == ["Existing", "New"]
        existing_preset = next(preset for preset in listed if preset["name"] == "Existing")
        assert existing_preset["note"] == "From backup"
        assert [event["action"] for event in existing_preset["history"]] == ["updated", "created"]

        duplicate = client.post(
            "/api/optimization/library/restore",
            json={
                "presets": [incoming_new, incoming_new],
                "timeline_views": [],
                "mode": "merge",
                "dry_run": True,
            },
        )
        assert duplicate.status_code == 400

        invalid = client.post(
            "/api/optimization/library/restore",
            json={"presets": [{"name": "Bad", "state": {}}], "timeline_views": [], "mode": "merge"},
        )
        assert invalid.status_code == 400

        replace = client.post(
            "/api/optimization/library/restore",
            json={
                "presets": [incoming_new],
                "timeline_views": [_timeline_view_payload("New view")],
                "mode": "replace",
                "dry_run": False,
            },
        )
        assert replace.status_code == 200
        assert replace.json()["presets"]["removed"] == 1
        assert [preset["name"] for preset in client.get("/api/optimization/presets").json()] == ["New"]
        assert [view["name"] for view in client.get("/api/optimization/timeline-views").json()] == ["New view"]


def test_shared_library_merge_does_not_silently_drop_entries(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2024",))
    with TestClient(create_app(config)) as client:
        for index in range(20):
            response = client.post("/api/optimization/presets", json=_preset_payload(f"Preset {index}"))
            assert response.status_code == 200
        response = client.post(
            "/api/optimization/library/restore",
            json={
                "presets": [_preset_payload("Overflow")],
                "timeline_views": [],
                "mode": "merge",
                "dry_run": True,
            },
        )
    assert response.status_code == 400
    assert "use replace" in response.json()["detail"]


def test_library_snapshot_api_round_trip(tmp_path: Path) -> None:
    config = PortalConfig(
        repo_root=tmp_path,
        runtime_dir=tmp_path / "runtime",
        versions=("2024",),
        library_snapshot_keep=2,
    )
    with TestClient(create_app(config)) as client:
        client.post("/api/optimization/presets", json=_preset_payload("Snapshot view"))
        client.post("/api/optimization/timeline-views", json=_timeline_view_payload("Snapshot timeline"))
        created = client.post("/api/optimization/snapshots")
        assert created.status_code == 200
        assert created.json()["presets"] == 1
        assert created.json()["timeline_views"] == 1
        first = created.json()["name"]

        second = client.post("/api/optimization/snapshots").json()["name"]
        third = client.post("/api/optimization/snapshots").json()["name"]
        listing = client.get("/api/optimization/snapshots").json()
        assert [item["name"] for item in listing] == [third, second]
        assert all(item["bytes"] > 0 for item in listing)

        bundle = client.get(f"/api/optimization/snapshots/{third}").json()
        assert bundle["schema"] == "fable-pyculator.optimization-library"
        assert bundle["snapshot_source"] == "manual"
        assert bundle["presets"][0]["history"][-1]["action"] == "created"

        assert client.delete("/api/optimization/presets/Snapshot view").status_code == 200
        assert client.delete("/api/optimization/timeline-views/Snapshot timeline").status_code == 200
        preview = client.post(
            f"/api/optimization/snapshots/{third}/restore",
            json={"mode": "replace", "dry_run": True},
        )
        assert preview.status_code == 200
        assert preview.json()["snapshot"] == third
        assert preview.json()["presets"]["added"] == 1
        assert client.get("/api/optimization/presets").json() == []
        applied = client.post(
            f"/api/optimization/snapshots/{third}/restore",
            json={"mode": "replace", "dry_run": False},
        )
        assert applied.status_code == 200
        assert [preset["name"] for preset in client.get("/api/optimization/presets").json()] == ["Snapshot view"]
        assert [view["name"] for view in client.get("/api/optimization/timeline-views").json()] == ["Snapshot timeline"]

        assert client.get(f"/api/optimization/snapshots/{first}").status_code == 404
        assert client.get("/api/optimization/snapshots/bad-name").status_code == 400
        assert client.delete(f"/api/optimization/snapshots/{third}").status_code == 200
        assert client.get(f"/api/optimization/snapshots/{third}").status_code == 404


def test_library_snapshot_config_validation(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="library_snapshot_keep"):
        PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", library_snapshot_keep=0)
    with pytest.raises(ValueError, match="library_snapshot_interval_minutes"):
        PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", library_snapshot_interval_minutes=-1)


def test_library_snapshot_scheduler_starts_and_stops(tmp_path: Path) -> None:
    config = PortalConfig(
        repo_root=tmp_path,
        runtime_dir=tmp_path / "runtime",
        versions=("2024",),
        library_snapshot_interval_minutes=1,
    )
    state = PortalState(config)
    try:
        assert state._snapshot_thread is not None
        assert state._snapshot_thread.is_alive()
        snapshot = state.create_library_snapshot(source="scheduled")
        assert snapshot["source"] == "scheduled"
        assert state.library_snapshots()[0]["source"] == "scheduled"
    finally:
        state.close()
    assert not state._snapshot_thread.is_alive()


def test_prune_shared_preset_history_preserves_latest(tmp_path: Path) -> None:
    from datetime import UTC, datetime, timedelta

    runtime = tmp_path / "runtime"
    runtime.mkdir(parents=True)
    now = datetime.now(UTC)
    old = (now - timedelta(days=90)).isoformat(timespec="seconds")
    recent = now.isoformat(timespec="seconds")
    state = {
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
        "brushes": [],
        "reference": None,
        "point": None,
    }
    (runtime / "optimization-presets.json").write_text(
        json.dumps(
            [
                {
                    "name": "Old history",
                    "saved_at": recent,
                    "author": "Hisham",
                    "note": "",
                    "review_status": "draft",
                    "state": state,
                    "history": [
                        {"at": old, "action": "created", "author": "Hisham", "note": "", "review_status": "draft"},
                        {
                            "at": recent,
                            "action": "reviewed",
                            "author": "Hisham",
                            "note": "",
                            "review_status": "reviewed",
                        },
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    config = PortalConfig(repo_root=tmp_path, runtime_dir=runtime, versions=("2024",))
    with TestClient(create_app(config)) as client:
        preview = client.post("/api/optimization/presets/prune", json={"days": 30, "dry_run": True}).json()
        assert preview["days"] == 30
        assert preview["dry_run"] is True
        assert preview["removed"] == 1
        assert preview["kept"] == 1
        assert preview["presets_touched"] == 1
        assert preview["presets_total"] == 1
        assert preview["source"] == "manual"
        assert preview["details"][0]["preset"] == "Old history"
        assert preview["details"][0]["removed"][0]["action"] == "created"
        assert [event["action"] for event in preview["details"][0]["before"]] == ["created", "reviewed"]
        assert [event["action"] for event in preview["details"][0]["after"]] == ["reviewed"]
        assert len(client.get("/api/optimization/presets").json()[0]["history"]) == 2

        pruned = client.post("/api/optimization/presets/prune", json={"days": 30, "dry_run": False}).json()
        assert pruned["removed"] == 1
        history = client.get("/api/optimization/presets").json()[0]["history"]
    assert len(history) == 1
    assert history[0]["action"] == "reviewed"


def test_startup_retention_prunes_and_logs(tmp_path: Path) -> None:
    from datetime import UTC, datetime, timedelta

    runtime = tmp_path / "runtime"
    runtime.mkdir(parents=True)
    now = datetime.now(UTC)
    old = (now - timedelta(days=90)).isoformat(timespec="seconds")
    recent = now.isoformat(timespec="seconds")
    state = {
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
        "brushes": [],
        "reference": None,
        "point": None,
    }
    (runtime / "optimization-presets.json").write_text(
        json.dumps(
            [
                {
                    "name": "Startup history",
                    "saved_at": recent,
                    "author": "Hisham",
                    "note": "",
                    "review_status": "draft",
                    "state": state,
                    "history": [
                        {"at": old, "action": "created", "author": "Hisham", "note": "", "review_status": "draft"},
                        {
                            "at": recent,
                            "action": "reviewed",
                            "author": "Hisham",
                            "note": "",
                            "review_status": "reviewed",
                        },
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )
    config = PortalConfig(
        repo_root=tmp_path,
        runtime_dir=runtime,
        versions=("2024",),
        history_retention_days=30,
    )
    with TestClient(create_app(config)) as client:
        history = client.get("/api/optimization/presets").json()[0]["history"]
        policy = client.get("/api/optimization/retention").json()
    assert len(history) == 1
    assert history[0]["action"] == "reviewed"
    assert policy["history_retention_days"] == 30
    assert policy["last"]["source"] == "startup"
    assert policy["last"]["removed"] == 1
    assert (runtime / "retention-log.jsonl").is_file()


def test_startup_retention_dry_run_is_non_destructive(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir(parents=True)
    config = PortalConfig(
        repo_root=tmp_path,
        runtime_dir=runtime,
        versions=("2024",),
        history_retention_days=30,
        history_retention_dry_run=True,
    )
    with TestClient(create_app(config)) as client:
        policy = client.get("/api/optimization/retention").json()
    assert policy["history_retention_dry_run"] is True
    assert policy["last"]["dry_run"] is True


def test_scheduled_retention_thread_starts_and_stops(tmp_path: Path) -> None:
    from fable_pyculator.web.service import PortalState

    config = PortalConfig(
        repo_root=tmp_path,
        runtime_dir=tmp_path / "runtime",
        versions=("2024",),
        history_retention_days=30,
        history_retention_interval_minutes=1,
    )
    state = PortalState(config)
    try:
        assert state._retention_thread is not None
        assert state._retention_thread.is_alive()
        status = state.retention_status()
        assert status["history_retention_interval_minutes"] == 1
        assert status["next_run_at"]
    finally:
        state.close()
    assert not state._retention_thread.is_alive()


def test_retention_runs_endpoint_returns_newest_first(tmp_path: Path) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir(parents=True)
    rows = [
        {
            "days": 30,
            "dry_run": True,
            "removed": 0,
            "kept": 2,
            "presets_touched": 0,
            "presets_total": 1,
            "source": "startup",
            "at": "2026-01-01T00:00:00+00:00",
        },
        {
            "days": 30,
            "dry_run": False,
            "removed": 1,
            "kept": 1,
            "presets_touched": 1,
            "presets_total": 1,
            "source": "scheduled",
            "at": "2026-01-02T00:00:00+00:00",
        },
    ]
    (runtime / "retention-log.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    config = PortalConfig(repo_root=tmp_path, runtime_dir=runtime, versions=("2024",))
    with TestClient(create_app(config)) as client:
        runs = client.get("/api/optimization/retention/runs?limit=1").json()
    assert len(runs) == 1
    assert runs[0]["source"] == "scheduled"
    assert runs[0]["at"].startswith("2026-01-02")
