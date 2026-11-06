from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from fable_pyculator.notebook import NotebookLoopResult
from fable_pyculator.spec import (
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    OutputTable,
    SelectionControl,
    SelectionOption,
)
from fable_pyculator.web import service
from fable_pyculator.web.app import create_app, is_loopback, validate_bind
from fable_pyculator.web.artifacts import artifact_paths, materialize_generated_model
from fable_pyculator.web.service import PortalConfig
from fable_pyculator.web.spec_io import spec_from_payload, spec_summary, spec_to_payload


def _spec() -> FableCalculatorSpec:
    return FableCalculatorSpec(
        selection_controls=[
            SelectionControl(
                name="gdp_scen",
                label="GDP projections",
                table_name="GDP_Scen",
                sheet="SCENARIOS selection",
                range_ref="A1:C3",
                code_header="GDP_SCEN",
                options=(
                    SelectionOption("SSP1", "SSP1", "SCENARIOS selection!A2"),
                    SelectionOption("SSP2", "SSP2", "SCENARIOS selection!A3", selected=True),
                ),
                location="S.1",
            )
        ],
        output_tables=[
            OutputTable(
                name="ghg_results",
                label="ResultsGHG",
                sheet="GHG",
                range_ref="A1:B2",
                cell_refs=(("GHG!A2", "GHG!B2"),),
                row_labels=("2030",),
                column_labels=("Year", "TotalCO2e"),
                column_flavour_tags=("DIRECT", "OUTPUT-8"),
            )
        ],
        headline_series=[
            HeadlineSeries(
                name="ghg_total_co2e",
                label="Total GHG emissions",
                group="GHG",
                sheet="GHG",
                table_name="ResultsGHG",
                points=(HeadlinePoint(2030, ("GHG!B2",)),),
                unit="MtCO2e",
            )
        ],
        workbook_id="2021",
        provenance="tmp/private-workbooks/2021_Open_FABLECalculator.xlsx",
    )


def _fake_result() -> NotebookLoopResult:
    headline = pd.DataFrame(
        [
            {
                "name": "ghg_total_co2e",
                "label": "Total GHG emissions",
                "group": "GHG",
                "year": 2020,
                "value": 10.0,
                "unit": "MtCO2e",
            },
            {
                "name": "ghg_total_co2e",
                "label": "Total GHG emissions",
                "group": "GHG",
                "year": 2030,
                "value": 7.5,
                "unit": "MtCO2e",
            },
        ]
    )
    headline.attrs.update({"label": "Total GHG emissions", "unit": "MtCO2e", "group": "GHG", "sheet": "GHG"})
    table = pd.DataFrame({"Year": [2030], "TotalCO2e": [7.5]})
    table.attrs.update({"label": "ResultsGHG", "sheet": "GHG", "range_ref": "A1:B2"})
    return NotebookLoopResult(
        run=SimpleNamespace(inputs={"SCENARIOS selection!A2": "x", "SCENARIOS selection!A3": None}),
        output_tables={"ghg_results": table},
        headline_frames={"ghg_total_co2e": headline},
        headline_figures={},
    )


def _config(tmp_path: Path) -> PortalConfig:
    paths = artifact_paths(tmp_path, "2021")
    paths.workbook.parent.mkdir(parents=True, exist_ok=True)
    paths.workbook.write_bytes(b"fake workbook")
    paths.generated_model.parent.mkdir(parents=True, exist_ok=True)
    paths.generated_model.write_text("# fake model\n", encoding="utf-8")
    return PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2021",))


def _wait(client: TestClient, job_id: str) -> dict[str, object]:
    for _ in range(200):
        payload = client.get(f"/api/jobs/{job_id}").json()
        if payload["status"] in {"ok", "error"}:
            return payload
        import time

        time.sleep(0.01)
    raise AssertionError("job did not finish")


def test_spec_roundtrip_preserves_controls_and_tables() -> None:
    spec = _spec()

    payload = spec_to_payload(spec)
    restored = spec_from_payload(payload)
    summary = spec_summary(restored)

    assert restored.input_mapping({"gdp_scen": "SSP1"}) == {
        "SCENARIOS selection!A2": "x",
        "SCENARIOS selection!A3": None,
    }
    assert summary["counts"]["selection_controls"] == 1
    assert summary["output_tables"][0]["column_flavour_tags"] == ["DIRECT", "OUTPUT-8"]
    assert restored.headline_series[0].points[0].cell_refs == ("GHG!B2",)


def test_artifact_summary_names_missing_files(tmp_path: Path) -> None:
    config = _config(tmp_path)
    app = create_app(config)
    with TestClient(app) as client:
        payload = client.get("/api/artifacts/2021").json()
        shell = client.get("/")
        script = client.get("/static/app.js")
        styles = client.get("/static/styles.css")

    assert payload["can_prepare"] is True
    assert payload["files"]["workbook"]["exists"] is True
    assert payload["files"]["compressed_model"]["exists"] is False
    assert "compressed_model" in payload["missing"]
    assert shell.status_code == 200
    assert "FABLE Pyculator" in shell.text
    assert script.status_code == 200
    assert "waitForJob" in script.text
    assert styles.status_code == 200
    assert "--green" in styles.text


def test_materialize_generated_model_from_approved_archive(tmp_path: Path) -> None:
    import lzma

    paths = artifact_paths(tmp_path, "2024")
    paths.compressed_model.parent.mkdir(parents=True, exist_ok=True)
    with lzma.open(paths.compressed_model, "wb") as handle:
        handle.write(b"# generated model\n")

    result = materialize_generated_model(tmp_path, "2024")

    assert result["materialized"] is True
    assert paths.generated_model.read_text(encoding="utf-8") == "# generated model\n"
    second = materialize_generated_model(tmp_path, "2024")
    assert second["materialized"] is False


def test_portal_prepare_run_and_compare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = _config(tmp_path)
    spec = _spec()
    monkeypatch.setattr(service, "build_notebook_spec", lambda *_args, **_kwargs: spec)
    monkeypatch.setattr(service, "load_generated_model", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(service, "run_notebook_loop", lambda *_args, **_kwargs: _fake_result())
    (tmp_path / "tmp" / "validation-evidence" / "fable-2021").mkdir(parents=True)
    (tmp_path / "tmp" / "validation-evidence" / "fable-2021" / "summary.json").write_text(
        '{"workbook_version": "2021", "evidence_status": "complete", '
        '"equivalence_status": "pass", "comparison": {"status": "pass", '
        '"comparable_output_count": 10, "match_count": 10, "mismatch_count": 0}, '
        '"stages": {}, "notes": []}',
        encoding="utf-8",
    )

    app = create_app(config)
    with TestClient(app) as client:
        health = client.get("/api/health").json()
        assert health["status"] == "ok"
        assert client.get("/").status_code == 200

        prepared = _wait(client, client.post("/api/models/2021/prepare").json()["job_id"])
        assert prepared["status"] == "ok"
        assert prepared["result"]["summary"]["counts"]["selection_controls"] == 1

        summary = client.get("/api/models/2021/spec").json()["summary"]
        assert summary["selection_controls"][0]["default"] == "SSP2"

        first = _wait(
            client,
            client.post(
                "/api/runs",
                json={"version": "2021", "name": "SSP1 run", "selections": {"gdp_scen": "SSP1"}},
            ).json()["job_id"],
        )
        second = _wait(
            client,
            client.post(
                "/api/runs",
                json={"version": "2021", "name": "SSP2 run", "selections": {"gdp_scen": "SSP2"}},
            ).json()["job_id"],
        )
        run_id = first["result"]["run_id"]
        assert first["result"]["headline_summary"][0]["last_value"] == 7.5
        assert first["result"]["provenance"]["portal_version"]
        assert first["result"]["provenance"]["workbook"]["exists"] is True
        assert client.get(f"/api/runs/{run_id}/tables/ghg_results").json()["rows"][0]["TotalCO2e"] == 7.5

        compared = client.post(
            "/api/compare",
            json={"run_ids": [run_id, second["result"]["run_id"]]},
        ).json()
        assert len(compared["runs"]) == 2
        assert compared["series"][0]["years"] == [2020, 2030]

        validation = client.get("/api/validation/2021").json()
        assert validation["available"] is True
        assert validation["summary"]["equivalence_status"] == "pass"

        assert client.post("/api/assistant", json={"message": "hello"}).status_code == 403


def test_prepare_reuses_cached_spec_across_app_instances(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = _config(tmp_path)
    spec = _spec()
    monkeypatch.setattr(service, "build_notebook_spec", lambda *_args, **_kwargs: spec)
    monkeypatch.setattr(service, "load_generated_model", lambda *_args, **_kwargs: object())

    with TestClient(create_app(config)) as client:
        first = _wait(client, client.post("/api/models/2021/prepare").json()["job_id"])
    assert first["status"] == "ok"

    def fail_build(*_args, **_kwargs):
        raise AssertionError("cached spec should have been reused")

    monkeypatch.setattr(service, "build_notebook_spec", fail_build)
    with TestClient(create_app(config)) as client:
        second = _wait(client, client.post("/api/models/2021/prepare").json()["job_id"])
        summary = client.get("/api/models/2021/spec").json()["summary"]
    assert second["status"] == "ok"
    assert summary["counts"]["output_tables"] == 1


def test_run_auto_prepares_when_needed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = _config(tmp_path)
    spec = _spec()
    monkeypatch.setattr(service, "build_notebook_spec", lambda *_args, **_kwargs: spec)
    monkeypatch.setattr(service, "load_generated_model", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(service, "run_notebook_loop", lambda *_args, **_kwargs: _fake_result())

    app = create_app(config)
    with TestClient(app) as client:
        job = client.post(
            "/api/runs",
            json={"version": "2021", "name": "auto-prepare", "selections": {"gdp_scen": "SSP1"}},
        ).json()
        finished = _wait(client, job["job_id"])

    assert finished["status"] == "ok"
    assert finished["result"]["version"] == "2021"


def test_bind_guard_allows_only_loopback_by_default() -> None:
    assert is_loopback("127.0.0.1")
    assert is_loopback("localhost")
    validate_bind("127.0.0.1", allow_remote=False)
    with pytest.raises(ValueError, match="Refusing non-loopback"):
        validate_bind("0.0.0.0", allow_remote=False)
    validate_bind("0.0.0.0", allow_remote=True)
