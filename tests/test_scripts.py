from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

from fable_pyculator import (
    FableFreshForgeBuildPaths,
    FableFreshForgeRebuildPlan,
    ScenarioBundle,
    ScenarioBundleArtifactPaths,
    ScenarioCase,
)


def test_bootstrap_dev_env_script_documents_vscode_kernel() -> None:
    script = Path("scripts/bootstrap_dev_env.sh")

    result = subprocess.run(
        [str(script), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert os.access(script, os.X_OK)
    assert ".venv" in result.stdout
    assert "VSCode notebook kernel" in result.stdout
    assert "[dev,notebook,docs]" not in result.stdout


def test_build_fable_model_script_help_documents_plan_run_and_strategy_modes() -> None:
    script = Path("scripts/build_fable_model.py")

    result = subprocess.run(
        [str(script), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert os.access(script, os.X_OK)
    assert "--run" in result.stdout
    assert "--workbook-version" in result.stdout
    assert "--output-ref-strategy" in result.stdout
    assert "plan-only" in result.stdout
    assert "OUTPUT-*" in result.stdout


def test_build_fable_2021_model_script_remains_shortcut() -> None:
    script = Path("scripts/build_fable_2021_model.py")

    result = subprocess.run(
        [str(script), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert os.access(script, os.X_OK)
    assert "--workbook-version" in result.stdout


def test_build_fable_model_script_reports_missing_versioned_workbook(tmp_path: Path) -> None:
    script = Path("scripts/build_fable_model.py")

    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path), "--workbook-version", "2022", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert "2022 FABLE workbook not found" in payload["error"]


def test_build_fable_model_script_plan_mode_is_explicit(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module("build_fable_model", Path("scripts/build_fable_model.py"))
    plan = _fake_rebuild_plan(tmp_path)

    monkeypatch.setattr(module, "_prepare_rebuild", lambda **_: plan)

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--workbook-version",
            "2021",
            "--output-ref-strategy",
            "headline-only",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["mode"] == "plan"
    assert payload["output_ref_strategy"] == "headline-only"
    assert payload["output_ref_count"] == 2
    assert payload["comparable_output_count"] == 1
    assert payload["artifacts"]["workflow"] == "tmp/generated-models/fable-2021/workflow.json"
    assert payload["run"] is None


def test_run_fable_scenario_bundle_script_help_documents_bundle_mode() -> None:
    script = Path("scripts/run_fable_scenario_bundle.py")

    result = subprocess.run(
        [str(script), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert os.access(script, os.X_OK)
    assert "--bundle" in result.stdout
    assert "--dry-run" in result.stdout
    assert "--generated-model-path" in result.stdout


def test_run_fable_scenario_bundle_script_reports_missing_bundle(tmp_path: Path) -> None:
    script = Path("scripts/run_fable_scenario_bundle.py")

    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path), "--bundle", "missing.yaml", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert "scenario bundle not found" in payload["error"]


def test_run_fable_scenario_bundle_script_dry_run_is_explicit(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module("run_fable_scenario_bundle", Path("scripts/run_fable_scenario_bundle.py"))

    monkeypatch.setattr(module, "_load_bundle", lambda _: _fake_bundle())
    monkeypatch.setattr(module, "_build_paths", lambda **_: _fake_build_paths(tmp_path))
    monkeypatch.setattr(module, "_artifact_paths", lambda **_: _fake_bundle_paths(tmp_path))
    monkeypatch.setattr(module, "_build_spec", lambda *_, **__: object())
    monkeypatch.setattr(module, "_validate_bundle", lambda *_: None)

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--bundle",
            "bundle.yaml",
            "--dry-run",
            "--json",
            "--output-table-name",
            "ghg_resultsghg",
            "--column-flavour-tag",
            "OUTPUT-8",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["mode"] == "dry-run"
    assert payload["bundle_id"] == "ssp-demo"
    assert payload["scenario_count"] == 1
    assert payload["render_overrides"] == {
        "output_table_names": ["ghg_resultsghg"],
        "output_table_column_flavour_tags": "OUTPUT-8",
    }
    assert payload["manifest"] is None


def test_run_fable_scenario_bundle_script_reports_missing_generated_model(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module("run_fable_scenario_bundle_missing_model", Path("scripts/run_fable_scenario_bundle.py"))

    monkeypatch.setattr(module, "_load_bundle", lambda _: _fake_bundle())
    monkeypatch.setattr(module, "_build_paths", lambda **_: _fake_build_paths(tmp_path))
    monkeypatch.setattr(module, "_artifact_paths", lambda **_: _fake_bundle_paths(tmp_path))
    monkeypatch.setattr(module, "_build_spec", lambda *_, **__: object())
    monkeypatch.setattr(module, "_validate_bundle", lambda *_: None)

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--bundle",
            "bundle.yaml",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.err)
    assert exit_code == 1
    assert payload["ok"] is False
    assert "generated model not found" in payload["error"]


def _load_script_module(module_name: str, script: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fake_rebuild_plan(root: Path) -> FableFreshForgeRebuildPlan:
    artifact_dir = root / "tmp" / "generated-models" / "fable-2021"
    paths = FableFreshForgeBuildPaths(
        workbook_path=root / "tmp" / "private-workbooks" / "2021_Open_FABLECalculator.xlsx",
        artifact_dir=artifact_dir,
        output_refs_path=artifact_dir / "output_refs.json",
        workflow_path=artifact_dir / "workflow.json",
        contract_path=artifact_dir / "contract.json",
        expressions_path=artifact_dir / "expressions.json",
        constants_path=artifact_dir / "constants.json",
        inference_result_path=artifact_dir / "inference-result.json",
        generation_result_path=artifact_dir / "generation-result.json",
        generated_model_path=artifact_dir / "generated_fable_2021_model.py",
        generated_values_path=artifact_dir / "generated-values.json",
        validation_scenario_path=artifact_dir / "validation-scenario.json",
        evaluation_report_path=artifact_dir / "evaluation-report.json",
    )
    return FableFreshForgeRebuildPlan(
        paths=paths,
        output_refs=("GHG!B3", "GHG!D3"),
        validation_scenario={"outputs": [{"cell_ref": "GHG!B3"}]},
        workflow={"workflow": {"id": "demo"}, "nodes": []},
    )


def _fake_bundle() -> ScenarioBundle:
    return ScenarioBundle(
        version=1,
        bundle_id="ssp-demo",
        workbook_version="2021",
        scenarios=(ScenarioCase("ssp1", {"gdp_scen": "SSP1"}),),
    )


def _fake_bundle_paths(root: Path) -> ScenarioBundleArtifactPaths:
    output_dir = root / "tmp" / "scenario-runs" / "fable-2021" / "ssp-demo"
    return ScenarioBundleArtifactPaths(
        output_dir=output_dir,
        normalized_bundle_path=output_dir / "bundle.json",
        manifest_path=output_dir / "manifest.json",
    )


def _fake_build_paths(root: Path) -> FableFreshForgeBuildPaths:
    artifact_dir = root / "tmp" / "generated-models" / "fable-2021"
    return FableFreshForgeBuildPaths(
        workbook_path=root / "tmp" / "private-workbooks" / "2021_Open_FABLECalculator.xlsx",
        artifact_dir=artifact_dir,
        output_refs_path=artifact_dir / "output_refs.json",
        workflow_path=artifact_dir / "workflow.json",
        contract_path=artifact_dir / "contract.json",
        expressions_path=artifact_dir / "expressions.json",
        constants_path=artifact_dir / "constants.json",
        inference_result_path=artifact_dir / "inference-result.json",
        generation_result_path=artifact_dir / "generation-result.json",
        generated_model_path=artifact_dir / "generated_fable_2021_model.py",
        generated_values_path=artifact_dir / "generated-values.json",
        validation_scenario_path=artifact_dir / "validation-scenario.json",
        evaluation_report_path=artifact_dir / "evaluation-report.json",
    )
