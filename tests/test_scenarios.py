from __future__ import annotations

import json
from pathlib import Path

import pytest

from fable_pyculator import (
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    NotebookLoopResult,
    OutputTable,
    ScenarioBundle,
    ScenarioBundleRunResult,
    ScenarioCase,
    SelectionControl,
    SelectionOption,
    fable_scenario_bundle_artifact_paths,
    load_scenario_bundle,
    run_scenario_bundle,
    validate_scenario_bundle,
    write_scenario_bundle_artifacts,
)
from fable_pyculator.scenarios import ScenarioBundleRenderOptions


def test_load_scenario_bundle_accepts_json_and_yaml(tmp_path: Path) -> None:
    json_path = tmp_path / "bundle.json"
    yaml_path = tmp_path / "bundle.yaml"
    payload = _bundle_payload()
    json_path.write_text(json.dumps(payload), encoding="utf-8")
    yaml_path.write_text(
        "version: 1\n"
        "bundle_id: ssp-demo\n"
        "workbook_version: '2021'\n"
        "render:\n"
        "  output_table_names:\n"
        "    - ghg_resultsghg\n"
        "  output_table_column_flavour_tags: OUTPUT-*\n"
        "scenarios:\n"
        "  - scenario_id: ssp1\n"
        "    selections:\n"
        "      gdp_scen: SSP1\n",
        encoding="utf-8",
    )

    json_bundle = load_scenario_bundle(json_path)
    yaml_bundle = load_scenario_bundle(yaml_path)

    assert json_bundle.bundle_id == "ssp-demo"
    assert json_bundle.render.output_table_names == ("ghg_resultsghg",)
    assert json_bundle.render.output_table_column_flavour_tags == "OUTPUT-*"
    assert yaml_bundle.bundle_id == "ssp-demo"
    assert yaml_bundle.scenarios[0].selections == {"gdp_scen": "SSP1"}


def test_validate_scenario_bundle_rejects_schema_and_selection_errors() -> None:
    spec = _spec()

    with pytest.raises(ValueError, match="path-safe slug"):
        validate_scenario_bundle(
            ScenarioBundle(
                version=1,
                bundle_id="bad/bundle",
                workbook_version="2021",
                scenarios=(ScenarioCase("ssp1", {"gdp_scen": "SSP1"}),),
            ),
            spec,
        )

    with pytest.raises(ValueError, match="at least one scenario"):
        validate_scenario_bundle(ScenarioBundle(version=1, bundle_id="empty", workbook_version="2021", scenarios=()), spec)

    with pytest.raises(ValueError, match="duplicate"):
        validate_scenario_bundle(
            ScenarioBundle(
                version=1,
                bundle_id="duplicate",
                workbook_version="2021",
                scenarios=(
                    ScenarioCase("ssp1", {"gdp_scen": "SSP1"}),
                    ScenarioCase("ssp1", {"gdp_scen": "SSP2"}),
                ),
            ),
            spec,
        )

    with pytest.raises(KeyError, match="unknown"):
        validate_scenario_bundle(
            ScenarioBundle(
                version=1,
                bundle_id="unknown",
                workbook_version="2021",
                scenarios=(ScenarioCase("ssp1", {"missing": "SSP1"}),),
            ),
            spec,
        )

    with pytest.raises(KeyError, match="SSP9"):
        validate_scenario_bundle(
            ScenarioBundle(
                version=1,
                bundle_id="invalid-option",
                workbook_version="2021",
                scenarios=(ScenarioCase("ssp9", {"gdp_scen": "SSP9"}),),
            ),
            spec,
        )


def test_fable_scenario_bundle_artifact_paths_are_version_general(tmp_path: Path) -> None:
    paths_2020 = fable_scenario_bundle_artifact_paths(
        workbook_version="2020",
        bundle_id="ssp-demo",
        repo_root=tmp_path,
    )
    paths_2022 = fable_scenario_bundle_artifact_paths(
        workbook_version="2022",
        bundle_id="future-demo",
        repo_root=tmp_path,
    )

    assert paths_2020.output_dir == tmp_path / "tmp/scenario-runs/fable-2020/ssp-demo"
    assert paths_2020.normalized_bundle_path.name == "bundle.json"
    assert paths_2020.scenario_dir("ssp1") == tmp_path / "tmp/scenario-runs/fable-2020/ssp-demo/scenarios/ssp1"
    assert paths_2022.output_dir == tmp_path / "tmp/scenario-runs/fable-2022/future-demo"


def test_run_scenario_bundle_runs_each_selection_case_and_renders_subsets() -> None:
    result = run_scenario_bundle(_calculate, _spec(), _bundle())

    assert set(result.scenario_results) == {"ssp1", "ssp2"}
    assert result.scenario_results["ssp1"].run.inputs == {
        "SCENARIOS selection!A20": "x",
        "SCENARIOS selection!A21": None,
    }
    assert result.scenario_results["ssp2"].output_tables["ghg_resultsghg"].loc["2030", "TotalCO2e"] == 84
    assert set(result.scenario_results["ssp1"].output_tables) == {"ghg_resultsghg"}
    assert set(result.scenario_results["ssp1"].headline_frames) == {"ghg_total_co2e"}


def test_write_scenario_bundle_artifacts_writes_manifest_tables_and_optional_figures(tmp_path: Path) -> None:
    result = run_scenario_bundle(_calculate, _spec(), _bundle())
    ssp1 = result.scenario_results["ssp1"]
    result_with_figure = ScenarioBundleRunResult(
        bundle=result.bundle,
        render=result.render,
        scenario_results={
            **result.scenario_results,
            "ssp1": NotebookLoopResult(
                run=ssp1.run,
                output_tables=ssp1.output_tables,
                headline_frames=ssp1.headline_frames,
                headline_figures={"ghg_total_co2e": _FakeFigure()},
            ),
        },
    )
    paths = fable_scenario_bundle_artifact_paths(
        workbook_version="2021",
        bundle_id="ssp-demo",
        repo_root=tmp_path,
    )

    manifest = write_scenario_bundle_artifacts(result_with_figure, paths)

    assert manifest["scenario_count"] == 2
    assert paths.normalized_bundle_path.exists()
    assert paths.manifest_path.exists()
    assert (paths.scenario_dir("ssp1") / "scenario_inputs.csv").exists()
    assert (paths.scenario_dir("ssp1") / "output_tables" / "ghg_resultsghg.csv").exists()
    assert (paths.scenario_dir("ssp1") / "headline_frames" / "ghg_total_co2e.csv").exists()
    assert (paths.scenario_dir("ssp1") / "headline_figures" / "ghg_total_co2e.png").read_text(
        encoding="utf-8"
    ) == "fake figure\n"
    assert json.loads(paths.normalized_bundle_path.read_text(encoding="utf-8"))["bundle_id"] == "ssp-demo"


def _bundle_payload() -> dict[str, object]:
    return {
        "version": 1,
        "bundle_id": "ssp-demo",
        "workbook_version": "2021",
        "render": {
            "output_table_names": ["ghg_resultsghg"],
            "output_table_column_flavour_tags": "OUTPUT-*",
            "headline_series_names": ["ghg_total_co2e"],
            "include_figures": False,
        },
        "scenarios": [
            {
                "scenario_id": "ssp1",
                "label": "SSP1",
                "selections": {"gdp_scen": "SSP1"},
            },
            {
                "scenario_id": "ssp2",
                "label": "SSP2",
                "selections": {"gdp_scen": "SSP2"},
            },
        ],
    }


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


class _FakeFigure:
    def savefig(self, path: Path) -> None:
        path.write_text("fake figure\n", encoding="utf-8")
