from __future__ import annotations

import builtins
import json
from pathlib import Path

from openpyxl import Workbook

from fable_pyculator import (
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    OutputTable,
    compare_output_ref_strategies,
    default_output_ref_strategy_cases,
    output_ref_strategy_comparison_paths,
    write_output_ref_strategy_comparison,
)


def test_default_output_ref_strategy_cases_are_deterministic() -> None:
    cases = default_output_ref_strategy_cases()

    assert [case.case_id for case in cases] == [
        "output-columns",
        "headline-only",
        "ghg-output-columns",
        "ghg-output-8",
        "all-columns",
    ]
    assert cases[3].column_flavour_tags == "OUTPUT-8"
    assert cases[3].table_names == ("ghg_resultsghg",)


def test_output_ref_strategy_comparison_paths_are_versioned(tmp_path: Path) -> None:
    paths = output_ref_strategy_comparison_paths(workbook_version="2022", repo_root=tmp_path)

    assert paths.output_dir == tmp_path / "tmp/strategy-comparisons/fable-2022"
    assert paths.output_refs_path("headline-only") == (
        tmp_path / "tmp/strategy-comparisons/fable-2022/headline-only/output_refs.json"
    )
    assert paths.workflow_path("headline-only").name == "freshforge-modelwright-run-workflow.json"


def test_compare_output_ref_strategies_writes_counts_and_artifacts(tmp_path: Path) -> None:
    workbook_path = _workbook(tmp_path)

    result = compare_output_ref_strategies(
        _spec(),
        workbook_version="2021",
        workbook_path=workbook_path,
        repo_root=tmp_path,
        selected_case_ids=("output-columns", "headline-only", "ghg-output-8", "all-columns"),
        include_workflows=True,
    )

    entries = {entry.case.case_id: entry for entry in result.entries}
    assert entries["output-columns"].output_ref_count == 3
    assert entries["output-columns"].comparable_output_count == 3
    assert entries["headline-only"].output_ref_count == 2
    assert entries["ghg-output-8"].output_ref_count == 1
    assert entries["all-columns"].output_ref_count == 6
    assert entries["all-columns"].comparable_output_count == 6
    assert entries["ghg-output-8"].run_namespace == "strategy/ghg-output-8"
    assert json.loads(entries["ghg-output-8"].output_refs_path.read_text(encoding="utf-8")) == ["GHG!B3"]
    assert entries["ghg-output-8"].workflow_path is not None
    assert entries["ghg-output-8"].workflow_path.exists()


def test_compare_output_ref_strategies_rejects_unknown_case(tmp_path: Path) -> None:
    workbook_path = _workbook(tmp_path)

    try:
        compare_output_ref_strategies(
            _spec(),
            workbook_version="2021",
            workbook_path=workbook_path,
            repo_root=tmp_path,
            selected_case_ids=("missing",),
        )
    except KeyError as error:
        assert "missing" in str(error)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("expected KeyError")


def test_write_output_ref_strategy_comparison_is_stable(tmp_path: Path) -> None:
    result = compare_output_ref_strategies(
        _spec(),
        workbook_version="2021",
        workbook_path=_workbook(tmp_path),
        repo_root=tmp_path,
        selected_case_ids=("headline-only",),
    )

    payload = write_output_ref_strategy_comparison(result)

    assert payload["entries"][0]["case"]["case_id"] == "headline-only"
    assert result.paths.summary_json_path.exists()
    assert result.paths.summary_markdown_path.exists()
    assert "Strategy comparison" in result.paths.summary_markdown_path.read_text(encoding="utf-8")


def test_existing_evidence_falls_back_to_fable_local_when_modelwright_evidence_is_unavailable(
    monkeypatch,
    tmp_path: Path,
) -> None:
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # type: ignore[no-untyped-def]
        if name == "modelwright.evidence":
            raise ImportError("modelwright evidence unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = compare_output_ref_strategies(
        _spec(),
        workbook_version="2021",
        workbook_path=_workbook(tmp_path),
        repo_root=tmp_path,
        selected_case_ids=("headline-only",),
        include_existing_evidence=True,
    )

    entry = result.entries[0]
    assert entry.evidence_source == "fable-local"
    assert entry.evidence_summary is not None
    assert entry.evidence_summary["evidence_status"] == "skipped"


def _workbook(tmp_path: Path) -> Path:
    workbook_path = tmp_path / "tmp/private-workbooks/2021_Open_FABLECalculator.xlsx"
    workbook_path.parent.mkdir(parents=True)
    workbook = Workbook()
    ghg = workbook.active
    ghg.title = "GHG"
    ghg["A3"] = 2030
    ghg["B3"] = 42
    ghg["C3"] = 7
    ghg["D3"] = 84
    land = workbook.create_sheet("LAND")
    land["A3"] = 2030
    land["B3"] = 12
    workbook.save(workbook_path)
    return workbook_path


def _spec() -> FableCalculatorSpec:
    return FableCalculatorSpec(
        output_tables=(
            OutputTable(
                name="ghg_resultsghg",
                sheet="GHG",
                range_ref="A2:D3",
                cell_refs=(("GHG!A3", "GHG!B3", "GHG!C3", "GHG!D3"),),
                row_labels=("2030",),
                column_labels=("Year", "TotalCO2e", "Data", "OtherOutput"),
                column_flavour_tags=("DIRECT", "OUTPUT - 8", "DATA-1", "OUTPUT-9"),
            ),
            OutputTable(
                name="land_resultsland",
                sheet="LAND",
                range_ref="A2:B3",
                cell_refs=(("LAND!A3", "LAND!B3"),),
                row_labels=("2030",),
                column_labels=("Year", "Area"),
                column_flavour_tags=("DIRECT", "OUTPUT-4"),
            ),
        ),
        headline_series=(
            HeadlineSeries(
                name="ghg_total_co2e",
                label="Total GHG emissions",
                group="GHG",
                sheet="GHG",
                table_name="ResultsGHG",
                points=(HeadlinePoint(year=2030, cell_refs=("GHG!B3",)),),
            ),
            HeadlineSeries(
                name="land_total_area",
                label="Total land area",
                group="LAND",
                sheet="LAND",
                table_name="ResultsLand",
                points=(HeadlinePoint(year=2030, cell_refs=("LAND!B3",)),),
            ),
        ),
    )
