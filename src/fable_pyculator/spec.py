"""Typed FABLE Pyculator notebook declarations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from modelwright.references import normalize_cell_reference


ControlKind = Literal["number", "text", "choice", "boolean"]
FABLE_OUTPUT_SURFACE_SHEETS = (
    "FOOD",
    "PRODUCTION",
    "TRADE",
    "BIODIVERSITY",
    "LAND",
    "GHG",
    "WATER",
)


@dataclass(frozen=True)
class ScenarioParameter:
    """One FABLE Calculator input parameter exposed to a notebook scenario."""

    name: str
    label: str
    cell_ref: str
    kind: ControlKind = "number"
    unit: str | None = None
    description: str | None = None
    default: object = None
    choices: tuple[object, ...] = ()
    source: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "cell_ref", _normalize_full_cell_ref(self.cell_ref))
        object.__setattr__(self, "choices", tuple(self.choices))


@dataclass(frozen=True)
class OutputIndicator:
    """One FABLE Calculator output indicator rendered from a generated model."""

    name: str
    label: str
    cell_ref: str
    unit: str | None = None
    group: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "cell_ref", _normalize_full_cell_ref(self.cell_ref))


@dataclass(frozen=True)
class OutputTable:
    """One rectangular table on a canonical FABLE output sheet."""

    name: str
    sheet: str
    range_ref: str
    cell_refs: tuple[tuple[str, ...], ...]
    row_labels: tuple[str, ...]
    column_labels: tuple[str, ...]
    label: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "cell_refs", tuple(tuple(row) for row in self.cell_refs))
        object.__setattr__(self, "row_labels", tuple(self.row_labels))
        object.__setattr__(self, "column_labels", tuple(self.column_labels))


@dataclass(frozen=True)
class SelectionOption:
    """One selectable row in a FABLE scenario selection table."""

    value: str
    label: str | None
    selection_cell_ref: str
    description: str | None = None
    selected: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", str(self.value))
        object.__setattr__(self, "selection_cell_ref", _normalize_full_cell_ref(self.selection_cell_ref))


@dataclass(frozen=True)
class SelectionControl:
    """One mutually-exclusive FABLE scenario selection table."""

    name: str
    label: str
    table_name: str
    sheet: str
    range_ref: str
    code_header: str
    options: tuple[SelectionOption, ...] | list[SelectionOption]
    location: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        options = tuple(self.options)
        _require_unique("selection option", (option.value for option in options))
        selected = [option for option in options if option.selected]
        if len(selected) > 1:
            raise ValueError(f"selection control {self.name!r} has more than one selected option")
        object.__setattr__(self, "options", options)

    @property
    def default(self) -> str | None:
        for option in self.options:
            if option.selected:
                return option.value
        return self.options[0].value if self.options else None

    def input_mapping(self, selected_value: object) -> dict[str, object]:
        """Return generated-model overrides that place one ``x`` in this table."""

        selected = str(selected_value)
        values = {option.value for option in self.options}
        if selected not in values:
            raise KeyError(f"unknown option {selected!r} for selection control {self.name!r}")
        return {
            option.selection_cell_ref: "x" if option.value == selected else None
            for option in self.options
        }


@dataclass(frozen=True)
class FableCalculatorSpec:
    """Notebook-facing declaration of FABLE scenario parameters and outputs."""

    parameters: tuple[ScenarioParameter, ...] | list[ScenarioParameter] = field(default_factory=tuple)
    selection_controls: tuple[SelectionControl, ...] | list[SelectionControl] = field(default_factory=tuple)
    outputs: tuple[OutputIndicator, ...] | list[OutputIndicator] = field(default_factory=tuple)
    output_tables: tuple[OutputTable, ...] | list[OutputTable] = field(default_factory=tuple)
    workbook_id: str | None = None
    provenance: str | None = None

    def __post_init__(self) -> None:
        parameters = tuple(self.parameters)
        selection_controls = tuple(self.selection_controls)
        outputs = tuple(self.outputs)
        output_tables = tuple(self.output_tables)
        _require_unique("parameter", (parameter.name for parameter in parameters))
        _require_unique("selection control", (control.name for control in selection_controls))
        _require_unique("output", (output.name for output in outputs))
        _require_unique("output table", (table.name for table in output_tables))
        overlap = set(parameter.name for parameter in parameters) & set(control.name for control in selection_controls)
        if overlap:
            raise ValueError(f"parameter and selection control names overlap: {', '.join(sorted(overlap))}")
        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(self, "selection_controls", selection_controls)
        object.__setattr__(self, "outputs", outputs)
        object.__setattr__(self, "output_tables", output_tables)

    def input_mapping(self, values: dict[str, object]) -> dict[str, object]:
        """Convert scenario values keyed by parameter name to generated-model cell inputs."""

        parameters_by_name = {parameter.name: parameter for parameter in self.parameters}
        controls_by_name = {control.name: control for control in self.selection_controls}
        known_names = set(parameters_by_name) | set(controls_by_name)
        unknown = sorted(set(values) - known_names)
        if unknown:
            raise KeyError(f"unknown scenario parameter(s): {', '.join(unknown)}")
        inputs = {
            parameters_by_name[name].cell_ref: value
            for name, value in values.items()
            if name in parameters_by_name
        }
        for name, value in values.items():
            control = controls_by_name.get(name)
            if control is not None:
                inputs.update(control.input_mapping(value))
        return inputs


def _normalize_full_cell_ref(cell_ref: str) -> str:
    normalized = normalize_cell_reference(cell_ref)
    if normalized.kind != "cell" or normalized.sheet is None:
        raise ValueError(f"expected a full cell reference like 'Sheet!A1', got {cell_ref!r}")
    return normalized.normalized


def _require_unique(kind: str, names: object) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for name in names:
        if name in seen:
            duplicates.add(name)
        seen.add(name)
    if duplicates:
        raise ValueError(f"duplicate {kind} name(s): {', '.join(sorted(duplicates))}")
