from __future__ import annotations

import json
from pathlib import Path

from freshforge.providers import ProviderRegistry
from freshforge.validation import validate_workflow_document

from fable_pyculator import (
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    OutputTable,
    ScenarioBundle,
    ScenarioBundleFreshForgePaths,
    ScenarioCase,
    SelectionControl,
    SelectionOption,
    fable_scenario_bundle_freshforge_paths,
    prepare_scenario_bundle_freshforge_workflow,
    run_scenario_bundle_freshforge_workflow,
    write_scenario_bundle_freshforge_summary,
)
from fable_pyculator.freshforge import provider_factory
from fable_pyculator.scenarios import ScenarioBundleRenderOptions


def test_prepare_scenario_bundle_freshforge_workflow_creates_deterministic_nodes(tmp_path: Path) -> None:
    bundle_path = _write_bundle(tmp_path)
    paths = fable_scenario_bundle_freshforge_paths(
        workbook_version="2021",
        bundle_id="ssp-demo",
        repo_root=tmp_path,
    )

    plan = prepare_scenario_bundle_freshforge_workflow(
        _bundle(),
        bundle_path=bundle_path,
        workbook_path=tmp_path / "workbook.xlsx",
        generated_model_path=tmp_path / "generated.py",
        paths=paths,
        repo_root=tmp_path,
        spec=_spec(),
        run_namespace="scenario/ssp-demo",
    )

    assert plan.run_namespace == "scenario/ssp-demo"
    assert [node["id"] for node in plan.workflow["nodes"]] == [
        "prepare_bundle",
        "scenario_ssp1",
        "scenario_ssp2",
        "bundle_manifest",
    ]
    assert plan.workflow["nodes"][2]["artifacts"]["scenario_summary"] == "scenarios/ssp2/scenario.json"
    assert paths.workflow_path.exists()
    spec, diagnostics = validate_workflow_document(plan.workflow)
    assert spec is not None
    assert not any(diagnostic.severity.value == "error" for diagnostic in diagnostics)


def test_freshforge_provider_runs_scenario_bundle_under_namespace(
    monkeypatch,
    tmp_path: Path,
) -> None:
    bundle_path = _write_bundle(tmp_path)
    workbook_path = tmp_path / "workbook.xlsx"
    generated_model_path = tmp_path / "generated.py"
    workbook_path.write_text("fake workbook\n", encoding="utf-8")
    generated_model_path.write_text("fake model\n", encoding="utf-8")
    paths = fable_scenario_bundle_freshforge_paths(
        workbook_version="2021",
        bundle_id="ssp-demo",
        repo_root=tmp_path,
    )
    plan = prepare_scenario_bundle_freshforge_workflow(
        _bundle(),
        bundle_path=bundle_path,
        workbook_path=workbook_path,
        generated_model_path=generated_model_path,
        paths=paths,
        repo_root=tmp_path,
        spec=_spec(),
    )

    import fable_pyculator.notebook as notebook

    monkeypatch.setattr(notebook, "build_notebook_spec", lambda *_, **__: _spec())
    monkeypatch.setattr(notebook, "load_generated_model", lambda *_, **__: _calculate)

    registry = ProviderRegistry()
    registry.register(provider_factory())
    result = run_scenario_bundle_freshforge_workflow(
        plan,
        run_namespace="scenario/test-run",
        registry=registry,
    )
    summary_payload = write_scenario_bundle_freshforge_summary(result, paths)

    output_root = paths.output_dir / "scenario" / "test-run"
    assert result.ok
    assert result.summary().run_namespace == "scenario/test-run"
    assert (output_root / "bundle.json").exists()
    assert (output_root / "scenarios" / "ssp1" / "scenario_inputs.csv").exists()
    assert (output_root / "scenarios" / "ssp2" / "output_tables" / "ghg_resultsghg.csv").exists()
    manifest = json.loads((output_root / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["freshforge"]["run_namespace"] == "scenario/test-run"
    assert [scenario["scenario_id"] for scenario in manifest["scenarios"]] == ["ssp1", "ssp2"]
    assert summary_payload["status"] == "success"
    assert (output_root / "freshforge-run-summary.json").exists()


def test_plan_only_provider_nodes_remain_unsupported_for_execution(tmp_path: Path) -> None:
    from freshforge.execution import run_workflow

    registry = ProviderRegistry()
    registry.register(provider_factory())
    spec, diagnostics = validate_workflow_document(
        {
            "workflow": {"id": "plan_only"},
            "nodes": [
                {
                    "id": "discover",
                    "provider": "fable_pyculator.notebook_spec_discover",
                    "outputs": {"notebook_spec": "spec"},
                    "parameters": {"workbook": "workbook.xlsx", "workbook_id": "fable-c-2021"},
                    "artifacts": {"spec_summary": "spec.json"},
                }
            ],
        }
    )
    assert spec is not None

    result = run_workflow(spec, diagnostics=diagnostics, registry=registry, workdir=tmp_path)

    assert not result.ok
    assert result.nodes[0].diagnostics[0].code == "fable_pyculator.execution.unsupported"


def test_fable_scenario_bundle_freshforge_paths_are_version_general(tmp_path: Path) -> None:
    paths = fable_scenario_bundle_freshforge_paths(
        workbook_version="2022",
        bundle_id="ssp-demo",
        repo_root=tmp_path,
    )

    assert isinstance(paths, ScenarioBundleFreshForgePaths)
    assert paths.output_dir == tmp_path / "tmp/scenario-runs/fable-2022/ssp-demo"
    assert paths.workflow_path.name == "freshforge-scenario-bundle-workflow.json"
    assert paths.namespaced_run_summary_path("scenario/test") == (
        tmp_path / "tmp/scenario-runs/fable-2022/ssp-demo/scenario/test/freshforge-run-summary.json"
    )


def _write_bundle(root: Path) -> Path:
    path = root / "bundle.yaml"
    path.write_text(
        "version: 1\n"
        "bundle_id: ssp-demo\n"
        "workbook_version: '2021'\n"
        "render:\n"
        "  output_table_names: [ghg_resultsghg]\n"
        "  output_table_column_flavour_tags: OUTPUT-*\n"
        "  headline_series_names: [ghg_total_co2e]\n"
        "  include_figures: false\n"
        "scenarios:\n"
        "  - scenario_id: ssp1\n"
        "    label: SSP1\n"
        "    selections: {gdp_scen: SSP1}\n"
        "  - scenario_id: ssp2\n"
        "    label: SSP2\n"
        "    selections: {gdp_scen: SSP2}\n",
        encoding="utf-8",
    )
    return path


def _bundle() -> ScenarioBundle:
    return ScenarioBundle(
        version=1,
        bundle_id="ssp-demo",
        workbook_version="2021",
        render=ScenarioBundleRenderOptions(
            output_table_names=("ghg_resultsghg",),
            output_table_column_flavour_tags="OUTPUT-*",
            headline_series_names=("ghg_total_co2e",),
            include_figures=False,
        ),
        scenarios=(
            ScenarioCase("ssp1", {"gdp_scen": "SSP1"}, label="SSP1"),
            ScenarioCase("ssp2", {"gdp_scen": "SSP2"}, label="SSP2"),
        ),
    )


def _spec() -> FableCalculatorSpec:
    return FableCalculatorSpec(
        selection_controls=[
            SelectionControl(
                name="gdp_scen",
                label="GDP projections",
                table_name="GDP_Scen",
                sheet="SCENARIOS selection",
                range_ref="A19:C21",
                code_header="GDP_SCEN",
                options=[
                    SelectionOption("SSP1", "SSP1", "SCENARIOS selection!A20"),
                    SelectionOption("SSP2", "SSP2", "SCENARIOS selection!A21"),
                ],
            )
        ],
        output_tables=[
            OutputTable(
                name="ghg_resultsghg",
                sheet="GHG",
                range_ref="A2:B3",
                cell_refs=(("GHG!A3", "GHG!B3"),),
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
                points=[HeadlinePoint(2030, ("GHG!B3",))],
            )
        ],
    )


def _calculate(inputs=None):
    inputs = inputs or {}
    value = 42 if inputs.get("SCENARIOS selection!A20") == "x" else 84
    return {
        "GHG!A3": 2030,
        "GHG!B3": value,
    }
