from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace

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


def test_run_fable_benchmark_evidence_script_help_documents_modes() -> None:
    script = Path("scripts/run_fable_benchmark_evidence.py")

    result = subprocess.run(
        [str(script), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert os.access(script, os.X_OK)
    assert "--mode" in result.stdout
    assert "freshforge-plan" in result.stdout
    assert "--output-ref-strategy" in result.stdout


def test_run_fable_benchmark_evidence_script_default_json_skips_missing_artifacts(tmp_path: Path) -> None:
    script = Path("scripts/run_fable_benchmark_evidence.py")

    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["mode"] == "evidence-only"
    assert payload["evidence_status"] == "skipped"
    assert payload["equivalence_status"] == "incomplete"
    assert payload["benchmark_summary_json"] == "tmp/validation-evidence/fable-2021/benchmark-summary.json"


def test_run_fable_benchmark_evidence_script_requires_artifacts(tmp_path: Path) -> None:
    script = Path("scripts/run_fable_benchmark_evidence.py")

    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path), "--require-artifacts", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert "missing validation" in payload["error"]


def test_run_fable_benchmark_evidence_script_freshforge_plan_skips_missing_workbook(tmp_path: Path) -> None:
    script = Path("scripts/run_fable_benchmark_evidence.py")

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(tmp_path),
            "--mode",
            "freshforge-plan",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["freshforge"]["status"] == "skipped"
    assert payload["freshforge"]["reason"] == "missing-workbook"


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
    assert "--freshforge-plan" in result.stdout
    assert "--freshforge-run" in result.stdout
    assert "--freshforge-matrix-plan" in result.stdout
    assert "--freshforge-matrix-run" in result.stdout


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


def test_run_fable_scenario_bundle_script_matrix_plan_is_explicit(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module("run_fable_scenario_bundle_matrix_plan", Path("scripts/run_fable_scenario_bundle.py"))
    matrix_paths = SimpleNamespace(
        matrix_path=tmp_path / "matrix.yaml",
        workflow_template_path=tmp_path / "template.yaml",
        matrix_summary_path=tmp_path / "matrix-summary.json",
    )
    matrix_plan = SimpleNamespace(case_count=1)

    monkeypatch.setattr(module, "_load_bundle", lambda _: _fake_bundle())
    monkeypatch.setattr(module, "_build_paths", lambda **_: _fake_build_paths(tmp_path))
    monkeypatch.setattr(module, "_generated_model_path", lambda **_: tmp_path / "generated.py")
    monkeypatch.setattr(module, "_artifact_paths", lambda **_: _fake_bundle_paths(tmp_path))
    monkeypatch.setattr(module, "_freshforge_paths", lambda **_: _fake_freshforge_paths(tmp_path))
    monkeypatch.setattr(module, "_freshforge_matrix_paths", lambda **_: matrix_paths)
    monkeypatch.setattr(module, "_build_spec", lambda *_, **__: object())
    monkeypatch.setattr(module, "_validate_bundle", lambda *_: None)
    monkeypatch.setattr(module, "_prepare_freshforge_matrix", lambda bundle, **_: matrix_plan)
    monkeypatch.setattr(module, "_plan_freshforge_matrix", lambda plan: {"ok": True, "case_count": plan.case_count})

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--bundle",
            "bundle.yaml",
            "--freshforge-matrix-plan",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["mode"] == "freshforge-matrix-plan"
    assert payload["freshforge"]["matrix"] == "matrix.yaml"
    assert payload["freshforge"]["case_count"] == 1
    assert payload["freshforge"]["plan"]["ok"] is True


def test_run_fable_scenario_bundle_script_matrix_run_reports_summary(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module("run_fable_scenario_bundle_matrix_run", Path("scripts/run_fable_scenario_bundle.py"))
    matrix_paths = SimpleNamespace(
        matrix_path=tmp_path / "matrix.yaml",
        workflow_template_path=tmp_path / "template.yaml",
        matrix_summary_path=tmp_path / "matrix-summary.json",
    )
    matrix_plan = SimpleNamespace(case_count=2)
    seen: dict[str, object] = {}

    def fake_run(plan, *, fail_fast):  # type: ignore[no-untyped-def]
        seen["fail_fast"] = fail_fast
        return object()

    monkeypatch.setattr(module, "_load_bundle", lambda _: _fake_bundle())
    monkeypatch.setattr(module, "_build_paths", lambda **_: _fake_build_paths(tmp_path))
    monkeypatch.setattr(module, "_generated_model_path", lambda **_: tmp_path / "generated.py")
    monkeypatch.setattr(module, "_artifact_paths", lambda **_: _fake_bundle_paths(tmp_path))
    monkeypatch.setattr(module, "_freshforge_paths", lambda **_: _fake_freshforge_paths(tmp_path))
    monkeypatch.setattr(module, "_freshforge_matrix_paths", lambda **_: matrix_paths)
    monkeypatch.setattr(module, "_build_spec", lambda *_, **__: object())
    monkeypatch.setattr(module, "_validate_bundle", lambda *_: None)
    monkeypatch.setattr(module, "_prepare_freshforge_matrix", lambda bundle, **_: matrix_plan)
    monkeypatch.setattr(module, "_plan_freshforge_matrix", lambda plan: {"ok": True})
    monkeypatch.setattr(module, "_run_freshforge_matrix", fake_run)
    monkeypatch.setattr(
        module,
        "_write_freshforge_matrix_summary",
        lambda result, paths, **_: {"status": "success", "case_count": 2, "matrix_summary": str(paths.matrix_summary_path)},
    )

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--bundle",
            "bundle.yaml",
            "--freshforge-matrix-run",
            "--fail-fast",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert seen == {"fail_fast": True}
    assert payload["mode"] == "freshforge-matrix-run"
    assert payload["freshforge"]["run"]["status"] == "success"
    assert payload["manifest"] is None


def test_run_fable_scenario_bundle_script_freshforge_plan_is_explicit(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module("run_fable_scenario_bundle_plan", Path("scripts/run_fable_scenario_bundle.py"))
    freshforge_paths = _fake_freshforge_paths(tmp_path)

    monkeypatch.setattr(module, "_load_bundle", lambda _: _fake_bundle())
    monkeypatch.setattr(module, "_build_paths", lambda **_: _fake_build_paths(tmp_path))
    monkeypatch.setattr(module, "_artifact_paths", lambda **_: _fake_bundle_paths(tmp_path))
    monkeypatch.setattr(module, "_freshforge_paths", lambda **_: freshforge_paths)
    monkeypatch.setattr(module, "_build_spec", lambda *_, **__: object())
    monkeypatch.setattr(module, "_validate_bundle", lambda *_: None)
    monkeypatch.setattr(
        module,
        "_prepare_freshforge_workflow",
        lambda *_, **__: SimpleNamespace(workflow={"nodes": [{"id": "prepare_bundle"}]}),
    )

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--bundle",
            "bundle.yaml",
            "--freshforge-plan",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["mode"] == "freshforge-plan"
    assert payload["freshforge"]["workflow"] == "tmp/scenario-runs/fable-2021/ssp-demo/workflow.json"
    assert payload["freshforge"]["run_namespace"] is None
    assert payload["freshforge"]["node_count"] == 1


def test_run_fable_scenario_bundle_script_freshforge_run_reports_summary(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module("run_fable_scenario_bundle_run", Path("scripts/run_fable_scenario_bundle.py"))
    freshforge_paths = _fake_freshforge_paths(tmp_path)
    seen: dict[str, object] = {}

    monkeypatch.setattr(module, "_load_bundle", lambda _: _fake_bundle())
    monkeypatch.setattr(module, "_build_paths", lambda **_: _fake_build_paths(tmp_path))
    monkeypatch.setattr(module, "_artifact_paths", lambda **_: _fake_bundle_paths(tmp_path))
    monkeypatch.setattr(module, "_freshforge_paths", lambda **_: freshforge_paths)
    monkeypatch.setattr(module, "_build_spec", lambda *_, **__: object())
    monkeypatch.setattr(module, "_validate_bundle", lambda *_: None)
    monkeypatch.setattr(
        module,
        "_prepare_freshforge_workflow",
        lambda *_, **__: SimpleNamespace(workflow={"nodes": [{"id": "prepare_bundle"}, {"id": "scenario_ssp1"}]}),
    )
    monkeypatch.setattr(module, "_run_freshforge_workflow", lambda *_, **kwargs: seen.setdefault("run", kwargs))
    monkeypatch.setattr(
        module,
        "_write_freshforge_summary",
        lambda *_, **__: {
            "run_summary": str(tmp_path / "tmp/scenario-runs/fable-2021/ssp-demo/test/run/run-summary.json"),
            "status": "success",
            "run_namespace": "test/run",
            "node_count": 2,
            "failed_count": 0,
            "error_count": 0,
        },
    )

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--bundle",
            "bundle.yaml",
            "--freshforge-run",
            "--run-namespace",
            "test/run",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert seen == {"run": {"run_namespace": "test/run"}}
    assert payload["mode"] == "freshforge-run"
    assert payload["freshforge"]["run"]["status"] == "success"
    assert payload["freshforge"]["run_namespace"] == "test/run"


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


def test_package_fable_validation_evidence_script_help_documents_artifact_modes() -> None:
    script = Path("scripts/package_fable_validation_evidence.py")

    result = subprocess.run(
        [str(script), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert os.access(script, os.X_OK)
    assert "--workbook-version" in result.stdout
    assert "--artifact-dir" in result.stdout
    assert "--require-artifacts" in result.stdout


def test_package_fable_validation_evidence_script_skips_missing_artifacts(tmp_path: Path) -> None:
    script = Path("scripts/package_fable_validation_evidence.py")

    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path), "--workbook-version", "2022", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["evidence_status"] == "skipped"
    assert payload["equivalence_status"] == "incomplete"
    assert "inference_result" in payload["missing_artifacts"]


def test_package_fable_validation_evidence_script_requires_missing_artifacts(tmp_path: Path) -> None:
    script = Path("scripts/package_fable_validation_evidence.py")

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(tmp_path),
            "--workbook-version",
            "2022",
            "--require-artifacts",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stderr)
    assert result.returncode == 1
    assert payload["ok"] is False
    assert "missing validation artifact" in payload["error"]


def test_package_fable_validation_evidence_script_accepts_custom_dirs(tmp_path: Path) -> None:
    script = Path("scripts/package_fable_validation_evidence.py")
    artifact_dir = tmp_path / "artifacts"
    output_dir = tmp_path / "evidence"

    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--repo-root",
            str(tmp_path),
            "--workbook-version",
            "2022",
            "--artifact-dir",
            str(artifact_dir),
            "--output-dir",
            str(output_dir),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["summary_json"] == str(output_dir / "summary.json")
    assert (output_dir / "summary.json").exists()


def test_compare_fable_output_ref_strategies_script_help_documents_compare_mode() -> None:
    script = Path("scripts/compare_fable_output_ref_strategies.py")

    result = subprocess.run(
        [str(script), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert os.access(script, os.X_OK)
    assert "--strategy" in result.stdout
    assert "--include-workflows" in result.stdout
    assert "--include-matrix" in result.stdout
    assert "--matrix-plan" in result.stdout
    assert "--matrix-run" in result.stdout
    assert "--include-existing-evidence" in result.stdout


def test_compare_fable_output_ref_strategies_script_reports_missing_workbook(tmp_path: Path) -> None:
    script = Path("scripts/compare_fable_output_ref_strategies.py")

    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(tmp_path), "--workbook-version", "2022", "--json"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert "No such file" in payload["error"] or "not found" in payload["error"]


def test_compare_fable_output_ref_strategies_script_outputs_json(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module(
        "compare_fable_output_ref_strategies",
        Path("scripts/compare_fable_output_ref_strategies.py"),
    )
    payload = {
        "workbook_version": "2021",
        "summary_json_path": str(tmp_path / "summary.json"),
        "summary_markdown_path": str(tmp_path / "summary.md"),
        "entries": [
            {
                "case": {"case_id": "output-columns"},
                "output_ref_count": 3,
                "comparable_output_count": 3,
            },
            {
                "case": {"case_id": "headline-only"},
                "output_ref_count": 2,
                "comparable_output_count": 2,
            },
        ],
    }

    spec_marker = object()
    seen: dict[str, object] = {}

    def fake_compare(*args, **kwargs):  # type: ignore[no-untyped-def]
        seen["spec"] = args[0]
        seen["selected_case_ids"] = kwargs["selected_case_ids"]
        return object()

    monkeypatch.setattr(module, "_build_spec", lambda **_: spec_marker)
    monkeypatch.setattr(module, "_compare", fake_compare)
    monkeypatch.setattr(module, "_write", lambda _: payload)

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--workbook-version",
            "2021",
            "--strategy",
            "output-columns",
            "--strategy",
            "headline-only",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert seen == {"spec": spec_marker, "selected_case_ids": ("output-columns", "headline-only")}
    assert json.loads(captured.out)["entries"][1]["case"]["case_id"] == "headline-only"


def test_compare_fable_output_ref_strategies_script_writes_matrix_json(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module(
        "compare_fable_output_ref_strategies_matrix",
        Path("scripts/compare_fable_output_ref_strategies.py"),
    )
    payload = {
        "workbook_version": "2021",
        "summary_json_path": str(tmp_path / "summary.json"),
        "summary_markdown_path": str(tmp_path / "summary.md"),
        "entries": [],
    }
    matrix_payload = {
        "case_count": 1,
        "paths": {"matrix_path": str(tmp_path / "strategy-matrix.yaml")},
    }
    seen: dict[str, object] = {}

    def fake_compare(*args, **kwargs):  # type: ignore[no-untyped-def]
        seen["include_workflows"] = kwargs["include_workflows"]
        return object()

    monkeypatch.setattr(module, "_build_spec", lambda **_: object())
    monkeypatch.setattr(module, "_compare", fake_compare)
    monkeypatch.setattr(module, "_write", lambda _: dict(payload))
    monkeypatch.setattr(module, "_build_matrix", lambda result, matrix_path=None: ("matrix", matrix_path))
    monkeypatch.setattr(module, "_write_matrix", lambda _: matrix_payload)

    exit_code = module.main(
        [
            "--repo-root",
            str(tmp_path),
            "--workbook-version",
            "2021",
            "--include-matrix",
            "--matrix-path",
            "custom-matrix.yaml",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert seen == {"include_workflows": True}
    output = json.loads(captured.out)
    assert output["matrix"]["case_count"] == 1


def test_compare_fable_output_ref_strategies_script_matrix_plan_json(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module(
        "compare_fable_output_ref_strategies_plan",
        Path("scripts/compare_fable_output_ref_strategies.py"),
    )
    matrix_path = str(tmp_path / "strategy-matrix.yaml")
    monkeypatch.setattr(module, "_build_spec", lambda **_: object())
    monkeypatch.setattr(module, "_compare", lambda *_, **__: object())
    monkeypatch.setattr(module, "_write", lambda _: {"workbook_version": "2021", "entries": []})
    monkeypatch.setattr(module, "_build_matrix", lambda result, matrix_path=None: object())
    monkeypatch.setattr(module, "_write_matrix", lambda _: {"paths": {"matrix_path": matrix_path}, "case_count": 1})
    monkeypatch.setattr(module, "_plan_matrix", lambda path: {"ok": True, "path": path})

    exit_code = module.main(["--repo-root", str(tmp_path), "--matrix-plan", "--json"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["matrix_plan"] == {"ok": True, "path": matrix_path}


def test_compare_fable_output_ref_strategies_script_matrix_run_is_explicit(
    monkeypatch,
    capsys,
    tmp_path: Path,
) -> None:
    module = _load_script_module(
        "compare_fable_output_ref_strategies_run",
        Path("scripts/compare_fable_output_ref_strategies.py"),
    )
    matrix_path = str(tmp_path / "strategy-matrix.yaml")
    seen: dict[str, object] = {}

    def fake_run(path, *, workdir, fail_fast):  # type: ignore[no-untyped-def]
        seen["path"] = path
        seen["workdir"] = str(workdir)
        seen["fail_fast"] = fail_fast
        return {"ok": False, "summary": {"status": "failed"}}

    monkeypatch.setattr(module, "_build_spec", lambda **_: object())
    monkeypatch.setattr(module, "_compare", lambda *_, **__: object())
    monkeypatch.setattr(module, "_write", lambda _: {"workbook_version": "2021", "entries": []})
    monkeypatch.setattr(module, "_build_matrix", lambda result, matrix_path=None: object())
    monkeypatch.setattr(module, "_write_matrix", lambda _: {"paths": {"matrix_path": matrix_path}, "case_count": 1})
    monkeypatch.setattr(module, "_run_matrix", fake_run)

    exit_code = module.main(
        ["--repo-root", str(tmp_path), "--matrix-run", "--fail-fast", "--workdir", str(tmp_path / "runs"), "--json"]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert seen == {"path": matrix_path, "workdir": str(tmp_path / "runs"), "fail_fast": True}
    assert json.loads(captured.out)["matrix_run"]["summary"]["status"] == "failed"


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


def _fake_freshforge_paths(root: Path) -> SimpleNamespace:
    output_dir = root / "tmp" / "scenario-runs" / "fable-2021" / "ssp-demo"
    return SimpleNamespace(
        output_dir=output_dir,
        workflow_path=output_dir / "workflow.json",
        namespaced_run_summary_path=lambda namespace=None: output_dir
        / (namespace or "")
        / "freshforge-run-summary.json",
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
