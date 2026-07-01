from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

from fable_pyculator import FableFreshForgeBuildPaths, FableFreshForgeRebuildPlan


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
