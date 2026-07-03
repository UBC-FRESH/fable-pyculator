from __future__ import annotations

import json
from pathlib import Path

import pytest

from fable_pyculator import (
    FableCalculatorSpec,
    ScenarioDefinitionEdit,
    ScenarioDefinitionPatch,
    ScenarioDefinitionTable,
    SelectionControl,
    SelectionOption,
    editable_scenario_definition_cells,
    load_scenario_definition_patch,
    run_scenario,
    scenario_definition_input_mapping,
    validate_scenario_definition_patch,
    write_scenario_definition_patch,
)


def test_editable_scenario_definition_cells_are_direct_non_formula_cells() -> None:
    cells = editable_scenario_definition_cells(_definition_spec())

    assert [cell.cell_ref for cell in cells] == [
        "SCENARIOS definition!A4",
        "SCENARIOS definition!E4",
        "SCENARIOS definition!A5",
        "SCENARIOS definition!E5",
    ]
    assert cells[0].table_label == "DietTarget"
    assert cells[0].row_label == "Current"
    assert cells[0].column_label == "DietScen"
    assert cells[0].scenario_locations == ("S.3.C",)


def test_patch_resolves_cell_ref_and_selector_edits() -> None:
    patch = ScenarioDefinitionPatch(
        version=1,
        patch_id="diet-demo",
        edits=(
            ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!A4", value="Current"),
            ScenarioDefinitionEdit(table="DietTarget", row_label="Ambitious", column_label="DietScen", value="High"),
        ),
    )

    result = validate_scenario_definition_patch(_definition_spec(), patch)

    assert result.inputs == {
        "SCENARIOS definition!A4": "Current",
        "SCENARIOS definition!A5": "High",
    }
    assert result.edits[1]["cell"]["original_value"] == "Ambitious"


def test_patch_rejects_read_only_role_tags_and_formula_cells() -> None:
    spec = _definition_spec()

    with pytest.raises(ValueError, match="SCEN"):
        validate_scenario_definition_patch(
            spec,
            ScenarioDefinitionPatch(
                version=1,
                patch_id="scen-readonly",
                edits=(ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!B4", value="CEREALS"),),
            ),
        )

    with pytest.raises(ValueError, match="formula"):
        validate_scenario_definition_patch(
            spec,
            ScenarioDefinitionPatch(
                version=1,
                patch_id="formula-readonly",
                edits=(ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!D4", value=10),),
            ),
        )


def test_patch_rejects_unknown_duplicate_ambiguous_and_invalid_edits() -> None:
    spec = _definition_spec()

    with pytest.raises(KeyError, match="unknown scenario definition cell"):
        validate_scenario_definition_patch(
            spec,
            ScenarioDefinitionPatch(
                version=1,
                patch_id="unknown-cell",
                edits=(ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!Z99", value=1),),
            ),
        )

    with pytest.raises(ValueError, match="duplicate"):
        validate_scenario_definition_patch(
            spec,
            ScenarioDefinitionPatch(
                version=1,
                patch_id="duplicate-cell",
                edits=(
                    ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!A4", value="A"),
                    ScenarioDefinitionEdit(table="DietTarget", row_label="Current", column_label="DietScen", value="B"),
                ),
            ),
        )

    with pytest.raises(ValueError, match="ambiguous"):
        validate_scenario_definition_patch(
            _ambiguous_definition_spec(),
            ScenarioDefinitionPatch(
                version=1,
                patch_id="ambiguous-selector",
                edits=(ScenarioDefinitionEdit(table="DietTarget", row_label="Current", column_label="DietScen", value="A"),),
            ),
        )

    with pytest.raises(ValueError, match="path-safe slug"):
        ScenarioDefinitionPatch(version=1, patch_id="bad id", edits=(ScenarioDefinitionEdit(cell_ref="A!A1", value=1),))

    with pytest.raises(ValueError, match="unsupported"):
        ScenarioDefinitionPatch(version=2, patch_id="demo", edits=(ScenarioDefinitionEdit(cell_ref="A!A1", value=1),))

    with pytest.raises(ValueError, match="scalar"):
        ScenarioDefinitionEdit(cell_ref="A!A1", value={"nested": "no"})  # type: ignore[arg-type]


def test_patch_load_write_and_input_mapping(tmp_path: Path) -> None:
    patch = ScenarioDefinitionPatch(
        version=1,
        patch_id="diet-demo",
        workbook_version="2021",
        edits=(ScenarioDefinitionEdit(table="DietTarget", row_label="Current", column_label="DietScen", value="Low"),),
    )
    path = tmp_path / "patch.json"

    payload = write_scenario_definition_patch(path, patch)
    loaded = load_scenario_definition_patch(path)
    mapping = scenario_definition_input_mapping(_definition_spec(), loaded)

    assert payload["patch_id"] == "diet-demo"
    assert mapping == {"SCENARIOS definition!A4": "Low"}

    yaml_path = tmp_path / "patch.yaml"
    yaml_path.write_text(
        "version: 1\npatch_id: yaml-demo\nedits:\n- cell_ref: SCENARIOS definition!A5\n  value: Medium\n",
        encoding="utf-8",
    )
    yaml_mapping = scenario_definition_input_mapping(_definition_spec(), yaml_path)
    assert yaml_mapping == {"SCENARIOS definition!A5": "Medium"}


def test_run_scenario_merges_definition_patch_inputs_and_rejects_conflicts() -> None:
    spec = FableCalculatorSpec(
        selection_controls=[
            SelectionControl(
                name="diet_scen",
                label="Diet scenario",
                table_name="DietScenSelection",
                sheet="SCENARIOS selection",
                range_ref="A1:B2",
                code_header="DietScen",
                options=[
                    SelectionOption("Current", "Current", "SCENARIOS definition!A4"),
                    SelectionOption("Ambitious", "Ambitious", "SCENARIOS definition!A5"),
                ],
            )
        ],
        scenario_definition_tables=_definition_spec().scenario_definition_tables,
    )
    patch = ScenarioDefinitionPatch(
        version=1,
        patch_id="diet-demo",
        edits=(ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!E5", value="patched"),),
    )

    run = run_scenario(lambda inputs=None: {"OUT!A1": 1}, spec, {"diet_scen": "Current"}, scenario_definition_patch=patch)

    assert run.inputs["SCENARIOS definition!A4"] == "x"
    assert run.inputs["SCENARIOS definition!A5"] is None
    assert run.inputs["SCENARIOS definition!E5"] == "patched"

    conflicting_patch = ScenarioDefinitionPatch(
        version=1,
        patch_id="diet-conflict",
        edits=(ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!A4", value="patched"),),
    )
    with pytest.raises(ValueError, match="conflict"):
        run_scenario(
            lambda inputs=None: {},
            spec,
            {"diet_scen": "Current"},
            scenario_definition_patch=conflicting_patch,
        )


def test_patch_to_dict_is_json_serializable() -> None:
    result = validate_scenario_definition_patch(
        _definition_spec(),
        ScenarioDefinitionPatch(
            version=1,
            patch_id="diet-demo",
            edits=(ScenarioDefinitionEdit(cell_ref="SCENARIOS definition!A4", value="Current"),),
        ),
    )

    assert json.loads(json.dumps(result.to_dict()))["inputs"] == {"SCENARIOS definition!A4": "Current"}


def _definition_spec() -> FableCalculatorSpec:
    return FableCalculatorSpec(
        scenario_definition_tables=[
            ScenarioDefinitionTable(
                name="scenarios_definition_diettarget",
                label="DietTarget",
                sheet="SCENARIOS definition",
                range_ref="A3:E5",
                cell_refs=(
                    (
                        "SCENARIOS definition!A4",
                        "SCENARIOS definition!B4",
                        "SCENARIOS definition!C4",
                        "SCENARIOS definition!D4",
                        "SCENARIOS definition!E4",
                    ),
                    (
                        "SCENARIOS definition!A5",
                        "SCENARIOS definition!B5",
                        "SCENARIOS definition!C5",
                        "SCENARIOS definition!D5",
                        "SCENARIOS definition!E5",
                    ),
                ),
                row_labels=("Current", "Ambitious"),
                column_labels=("DietScen", "PROD_GROUP", "target", "diff", "EditableValue"),
                values=(
                    ("Current", "CEREALS", 2500, "=C4-2400", "baseline"),
                    ("Ambitious", "CEREALS", 2600, "=C5-2400", "target"),
                ),
                column_role_tags=("DIRECT", "SCEN", "DATA-1", "CALC", "DIRECT"),
                scenario_locations=("S.3.C",),
            )
        ]
    )


def _ambiguous_definition_spec() -> FableCalculatorSpec:
    table = _definition_spec().scenario_definition_tables[0]
    return FableCalculatorSpec(
        scenario_definition_tables=[
            table,
            ScenarioDefinitionTable(
                name="scenarios_definition_diettarget_copy",
                label="DietTarget",
                sheet="SCENARIOS definition",
                range_ref="F3:F4",
                cell_refs=(("SCENARIOS definition!F4",),),
                row_labels=("Current",),
                column_labels=("DietScen",),
                values=(("Copy",),),
                column_role_tags=("DIRECT",),
            ),
        ]
    )
