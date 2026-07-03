"""Editable FABLE scenario-definition table surfaces.

This module turns discovered ``SCENARIOS definition`` metadata into a conservative patch surface.
It never mutates source workbooks; valid patches become generated-model input overrides keyed by
normalized workbook cell references.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any

from modelwright.references import normalize_cell_reference

from fable_pyculator.spec import FableCalculatorSpec, ScenarioDefinitionTable


JsonScalar = str | int | float | bool | None
EDITABLE_ROLE_TAG = "DIRECT"
READ_ONLY_ROLE_TAGS = ("AUX", "CALC", "SCEN")


@dataclass(frozen=True)
class ScenarioDefinitionEditableCell:
    """One editable cell from a FABLE ``SCENARIOS definition`` table."""

    table_name: str
    table_label: str | None
    sheet: str
    cell_ref: str
    row_label: str
    column_label: str
    column_role_tag: str | None
    original_value: object
    scenario_locations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        return {
            "table_name": self.table_name,
            "table_label": self.table_label,
            "sheet": self.sheet,
            "cell_ref": self.cell_ref,
            "row_label": self.row_label,
            "column_label": self.column_label,
            "column_role_tag": self.column_role_tag,
            "original_value": self.original_value,
            "scenario_locations": list(self.scenario_locations),
        }


@dataclass(frozen=True)
class ScenarioDefinitionEdit:
    """One requested scenario-definition cell edit."""

    value: JsonScalar
    cell_ref: str | None = None
    table: str | None = None
    row_label: str | None = None
    column_label: str | None = None

    def __post_init__(self) -> None:
        if not _is_json_scalar(self.value):
            raise ValueError("scenario definition edit values must be JSON/YAML scalar values")
        if self.cell_ref is not None:
            object.__setattr__(self, "cell_ref", _normalize_full_cell_ref(self.cell_ref))
        has_cell = self.cell_ref is not None
        selector_fields = (self.table, self.row_label, self.column_label)
        has_selector = any(value is not None for value in selector_fields)
        if has_cell == has_selector:
            raise ValueError("scenario definition edit must use either cell_ref or table/row_label/column_label")
        if has_selector and not all(value is not None for value in selector_fields):
            raise ValueError("table, row_label, and column_label are all required for selector edits")

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        payload: dict[str, Any] = {"value": self.value}
        if self.cell_ref is not None:
            payload["cell_ref"] = self.cell_ref
        else:
            payload.update(
                {
                    "table": self.table,
                    "row_label": self.row_label,
                    "column_label": self.column_label,
                }
            )
        return payload


@dataclass(frozen=True)
class ScenarioDefinitionPatch:
    """Versioned collection of scenario-definition edits."""

    version: int
    patch_id: str
    edits: tuple[ScenarioDefinitionEdit, ...]
    workbook_version: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        if self.version != 1:
            raise ValueError(f"unsupported scenario definition patch version: {self.version!r}")
        _require_slug(self.patch_id, "patch_id")
        object.__setattr__(self, "edits", tuple(self.edits))
        if not self.edits:
            raise ValueError("scenario definition patch must contain at least one edit")

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        payload: dict[str, Any] = {
            "version": self.version,
            "patch_id": self.patch_id,
            "edits": [edit.to_dict() for edit in self.edits],
        }
        if self.workbook_version is not None:
            payload["workbook_version"] = self.workbook_version
        if self.description is not None:
            payload["description"] = self.description
        return payload


@dataclass(frozen=True)
class ScenarioDefinitionPatchResult:
    """Validated scenario-definition patch and generated-model input mapping."""

    patch: ScenarioDefinitionPatch
    edits: tuple[dict[str, Any], ...]
    inputs: dict[str, JsonScalar]
    editable_cell_count: int
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-serializable representation."""

        return {
            "patch": self.patch.to_dict(),
            "edits": list(self.edits),
            "inputs": self.inputs,
            "editable_cell_count": self.editable_cell_count,
            "notes": list(self.notes),
        }


def editable_scenario_definition_cells(
    spec: FableCalculatorSpec,
    *,
    role_tag: str = EDITABLE_ROLE_TAG,
) -> tuple[ScenarioDefinitionEditableCell, ...]:
    """Return editable non-formula scenario-definition cells for ``spec``."""

    editable_role = _canonical_role_tag(role_tag)
    cells: list[ScenarioDefinitionEditableCell] = []
    for table in spec.scenario_definition_tables:
        for row_index, row_label in enumerate(table.row_labels):
            for column_index, column_label in enumerate(table.column_labels):
                tag = _table_role_tag(table, column_index)
                value = table.values[row_index][column_index] if table.values else None
                if tag == editable_role and not _is_formula_value(value):
                    cells.append(
                        ScenarioDefinitionEditableCell(
                            table_name=table.name,
                            table_label=table.label,
                            sheet=table.sheet,
                            cell_ref=table.cell_refs[row_index][column_index],
                            row_label=row_label,
                            column_label=column_label,
                            column_role_tag=tag,
                            original_value=value,
                            scenario_locations=tuple(table.scenario_locations),
                        )
                    )
    return tuple(cells)


def load_scenario_definition_patch(path: str | Path) -> ScenarioDefinitionPatch:
    """Load a scenario-definition patch from JSON, YAML, or YML."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"scenario definition patch not found: {source}")
    if source.suffix.casefold() == ".json":
        data = json.loads(source.read_text(encoding="utf-8"))
    elif source.suffix.casefold() in {".yaml", ".yml"}:
        import yaml

        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"unsupported scenario definition patch format: {source.suffix}")
    return _patch_from_mapping(_require_mapping(data, "scenario definition patch"))


def write_scenario_definition_patch(path: str | Path, patch: ScenarioDefinitionPatch) -> dict[str, Any]:
    """Write a normalized scenario-definition patch as JSON."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = patch.to_dict()
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def validate_scenario_definition_patch(
    spec: FableCalculatorSpec,
    patch: ScenarioDefinitionPatch,
) -> ScenarioDefinitionPatchResult:
    """Validate ``patch`` against ``spec`` and return generated-model inputs."""

    editable_cells = editable_scenario_definition_cells(spec)
    cell_by_ref = {cell.cell_ref: cell for cell in editable_cells}
    inputs: dict[str, JsonScalar] = {}
    resolved_edits: list[dict[str, Any]] = []
    for edit in patch.edits:
        cell = _resolve_edit(edit, spec=spec, editable_cells=editable_cells, cell_by_ref=cell_by_ref)
        if cell.cell_ref in inputs:
            raise ValueError(f"duplicate scenario definition edit target: {cell.cell_ref}")
        inputs[cell.cell_ref] = edit.value
        resolved_edits.append(
            {
                "cell": cell.to_dict(),
                "value": edit.value,
            }
        )
    return ScenarioDefinitionPatchResult(
        patch=patch,
        edits=tuple(resolved_edits),
        inputs=inputs,
        editable_cell_count=len(editable_cells),
        notes=(
            "Scenario-definition patches produce generated-model input overrides; source workbooks are not mutated.",
        ),
    )


def scenario_definition_input_mapping(
    spec: FableCalculatorSpec,
    patch: ScenarioDefinitionPatch | Mapping[str, Any] | str | Path | None,
) -> dict[str, JsonScalar]:
    """Return generated-model input overrides for a validated scenario-definition patch."""

    if patch is None:
        return {}
    loaded_patch = _coerce_patch(patch)
    return validate_scenario_definition_patch(spec, loaded_patch).inputs


def _resolve_edit(
    edit: ScenarioDefinitionEdit,
    *,
    spec: FableCalculatorSpec,
    editable_cells: tuple[ScenarioDefinitionEditableCell, ...],
    cell_by_ref: dict[str, ScenarioDefinitionEditableCell],
) -> ScenarioDefinitionEditableCell:
    if edit.cell_ref is not None:
        editable = cell_by_ref.get(edit.cell_ref)
        if editable is not None:
            return editable
        _raise_read_only_or_unknown_cell(edit.cell_ref, spec)
    assert edit.table is not None and edit.row_label is not None and edit.column_label is not None
    matches = [
        cell
        for cell in editable_cells
        if (cell.table_name == edit.table or cell.table_label == edit.table)
        and cell.row_label == edit.row_label
        and cell.column_label == edit.column_label
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ValueError(
            "ambiguous scenario definition edit selector: "
            f"{edit.table!r}, {edit.row_label!r}, {edit.column_label!r}"
        )
    _raise_read_only_or_unknown_selector(edit, spec)
    raise AssertionError("unreachable")


def _raise_read_only_or_unknown_cell(cell_ref: str, spec: FableCalculatorSpec) -> None:
    for table in spec.scenario_definition_tables:
        for row_index, row in enumerate(table.cell_refs):
            for column_index, candidate in enumerate(row):
                if candidate != cell_ref:
                    continue
                tag = _table_role_tag(table, column_index)
                value = table.values[row_index][column_index] if table.values else None
                if _is_formula_value(value):
                    raise ValueError(f"scenario definition cell {cell_ref} is read-only because it contains a formula")
                raise ValueError(
                    f"scenario definition cell {cell_ref} is read-only because column role tag is {tag!r}"
                )
    raise KeyError(f"unknown scenario definition cell: {cell_ref}")


def _raise_read_only_or_unknown_selector(edit: ScenarioDefinitionEdit, spec: FableCalculatorSpec) -> None:
    found_table = False
    found_row = False
    found_column = False
    for table in spec.scenario_definition_tables:
        if table.name != edit.table and table.label != edit.table:
            continue
        found_table = True
        if edit.row_label in table.row_labels:
            found_row = True
        if edit.column_label in table.column_labels:
            found_column = True
        if found_row and found_column:
            row_index = table.row_labels.index(str(edit.row_label))
            column_index = table.column_labels.index(str(edit.column_label))
            cell_ref = table.cell_refs[row_index][column_index]
            _raise_read_only_or_unknown_cell(cell_ref, spec)
    if not found_table:
        raise KeyError(f"unknown scenario definition table: {edit.table!r}")
    if not found_row:
        raise KeyError(f"unknown scenario definition row label {edit.row_label!r} in table {edit.table!r}")
    if not found_column:
        raise KeyError(f"unknown scenario definition column label {edit.column_label!r} in table {edit.table!r}")
    raise KeyError(
        "unknown scenario definition edit selector: "
        f"{edit.table!r}, {edit.row_label!r}, {edit.column_label!r}"
    )


def _patch_from_mapping(data: Mapping[str, Any]) -> ScenarioDefinitionPatch:
    edits = _require_sequence(data.get("edits"), "scenario definition patch edits")
    return ScenarioDefinitionPatch(
        version=int(data.get("version", 0)),
        patch_id=str(data.get("patch_id", "")),
        workbook_version=str(data["workbook_version"]) if data.get("workbook_version") is not None else None,
        description=str(data["description"]) if data.get("description") is not None else None,
        edits=tuple(_edit_from_mapping(_require_mapping(item, "scenario definition edit")) for item in edits),
    )


def _edit_from_mapping(data: Mapping[str, Any]) -> ScenarioDefinitionEdit:
    if "value" not in data:
        raise ValueError("scenario definition edit is missing required value")
    return ScenarioDefinitionEdit(
        cell_ref=str(data["cell_ref"]) if data.get("cell_ref") is not None else None,
        table=str(data["table"]) if data.get("table") is not None else None,
        row_label=str(data["row_label"]) if data.get("row_label") is not None else None,
        column_label=str(data["column_label"]) if data.get("column_label") is not None else None,
        value=data["value"],
    )


def _coerce_patch(patch: ScenarioDefinitionPatch | Mapping[str, Any] | str | Path) -> ScenarioDefinitionPatch:
    if isinstance(patch, ScenarioDefinitionPatch):
        return patch
    if isinstance(patch, str | Path):
        return load_scenario_definition_patch(patch)
    return _patch_from_mapping(_require_mapping(patch, "scenario definition patch"))


def _table_role_tag(table: ScenarioDefinitionTable, column_index: int) -> str | None:
    if not table.column_role_tags:
        return None
    tag = table.column_role_tags[column_index]
    return _canonical_role_tag(tag) if tag is not None else None


def _canonical_role_tag(tag: str | None) -> str | None:
    if tag is None:
        return None
    return re.sub(r"\s+", "", str(tag).strip().upper()).replace("DATA-", "DATA-")


def _normalize_full_cell_ref(cell_ref: str) -> str:
    normalized = normalize_cell_reference(cell_ref)
    if normalized.kind != "cell" or normalized.sheet is None:
        raise ValueError(f"expected a full cell reference like 'Sheet!A1', got {cell_ref!r}")
    return normalized.normalized


def _is_formula_value(value: object) -> bool:
    return isinstance(value, str) and value.startswith("=")


def _is_json_scalar(value: object) -> bool:
    return value is None or isinstance(value, str | int | float | bool)


def _require_slug(value: str, field_name: str) -> None:
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]*$", value):
        raise ValueError(f"{field_name} must be a path-safe slug")


def _require_mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    return value


def _require_sequence(value: object, name: str) -> list[Any] | tuple[Any, ...]:
    if not isinstance(value, list | tuple):
        raise ValueError(f"{name} must be a list")
    return value
