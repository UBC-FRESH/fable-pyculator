"""Typed notebook declarations for FABLE Calculator wrapper specs.

This module is deliberately declarative. The records here describe the workbook-backed surfaces that
FABLE Pyculator can expose in notebooks: high-level scenario selections, scenario-definition tables,
canonical output tables, and curated headline series. They do not execute Excel formulas and they do
not claim that every workbook cell has been converted into a stable public API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Literal

from modelwright.references import normalize_cell_reference


ControlKind = Literal["number", "text", "choice", "boolean"]
HeadlineAggregation = Literal["value", "sum"]
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
    """One scalar FABLE Calculator input exposed as a notebook scenario value.

    A parameter maps a friendly Python name to a generated-model cell reference. This record is for
    curated scalar controls; discovered FABLE-C selection tables should normally use
    :class:`SelectionControl` instead.
    """

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
    """One scalar output cell rendered from a generated Modelwright model."""

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
    """One rectangular output table on a canonical FABLE output sheet.

    ``column_flavour_tags`` stores output-sheet flavour metadata such as ``DIRECT``, ``DATA-5``, or
    ``OUTPUT-8``. That vocabulary belongs to output tables only; scenario-definition input tables use
    ``column_role_tags`` instead.
    """

    name: str
    sheet: str
    range_ref: str
    cell_refs: tuple[tuple[str, ...], ...]
    row_labels: tuple[str, ...]
    column_labels: tuple[str, ...]
    values: tuple[tuple[object, ...], ...] | list[list[object]] | tuple[()] = ()
    column_flavour_tags: tuple[str | None, ...] | list[str | None] = ()
    raw_column_flavour_tags: tuple[str | None, ...] | list[str | None] = ()
    column_flavour_tag_refs: tuple[str | None, ...] | list[str | None] = ()
    label: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "cell_refs", tuple(tuple(row) for row in self.cell_refs))
        object.__setattr__(self, "row_labels", tuple(self.row_labels))
        object.__setattr__(self, "column_labels", tuple(self.column_labels))
        object.__setattr__(self, "values", tuple(tuple(row) for row in self.values))
        object.__setattr__(self, "column_flavour_tags", tuple(self.column_flavour_tags))
        object.__setattr__(self, "raw_column_flavour_tags", tuple(self.raw_column_flavour_tags))
        object.__setattr__(self, "column_flavour_tag_refs", tuple(self.column_flavour_tag_refs))
        column_count = len(self.column_labels)
        if self.values:
            if len(self.values) != len(self.row_labels):
                raise ValueError(
                    f"output table {self.name!r} has {len(self.values)} value rows "
                    f"for {len(self.row_labels)} row labels"
                )
            for index, row in enumerate(self.values):
                if len(row) != column_count:
                    raise ValueError(
                        f"output table {self.name!r} value row {index} has {len(row)} values "
                        f"for {column_count} columns"
                    )
        for field_name in ("column_flavour_tags", "raw_column_flavour_tags", "column_flavour_tag_refs"):
            values = getattr(self, field_name)
            if values and len(values) != column_count:
                raise ValueError(
                    f"output table {self.name!r} has {len(values)} {field_name} values "
                    f"for {column_count} columns"
                )


@dataclass(frozen=True)
class ScenarioDefinitionTable:
    """One native table on the FABLE ``SCENARIOS definition`` sheet.

    These records make definition tables inspectable in notebooks. ``column_role_tags`` preserves
    workbook role/source markers such as ``DIRECT``, ``SCEN``, ``CALC``, and ``DATA-1``. The
    ``scenario_locations`` field stores workbook markers such as ``S.3.C`` that help users browse
    related definition tables. The table is not yet an editable widget contract.
    """

    name: str
    sheet: str
    range_ref: str
    cell_refs: tuple[tuple[str, ...], ...]
    row_labels: tuple[str, ...]
    column_labels: tuple[str, ...]
    values: tuple[tuple[object, ...], ...] | list[list[object]] | list[tuple[object, ...]] = ()
    column_role_tags: tuple[str | None, ...] | list[str | None] = ()
    raw_column_role_tags: tuple[str | None, ...] | list[str | None] = ()
    column_role_tag_refs: tuple[str | None, ...] | list[str | None] = ()
    scenario_locations: tuple[str, ...] | list[str] = ()
    scenario_location_refs: tuple[str, ...] | list[str] = ()
    label: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        cell_refs = tuple(tuple(_normalize_full_cell_ref(cell_ref) for cell_ref in row) for row in self.cell_refs)
        values = tuple(tuple(row) for row in self.values)
        object.__setattr__(self, "cell_refs", cell_refs)
        object.__setattr__(self, "row_labels", tuple(self.row_labels))
        object.__setattr__(self, "column_labels", tuple(self.column_labels))
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "column_role_tags", tuple(self.column_role_tags))
        object.__setattr__(self, "raw_column_role_tags", tuple(self.raw_column_role_tags))
        object.__setattr__(self, "column_role_tag_refs", tuple(self.column_role_tag_refs))
        object.__setattr__(
            self,
            "scenario_locations",
            tuple(_normalize_scenario_definition_location(location) for location in self.scenario_locations),
        )
        object.__setattr__(
            self,
            "scenario_location_refs",
            tuple(_normalize_full_cell_ref(cell_ref) for cell_ref in self.scenario_location_refs),
        )
        row_count = len(self.row_labels)
        column_count = len(self.column_labels)
        if len(cell_refs) != row_count:
            raise ValueError(
                f"scenario definition table {self.name!r} has {len(cell_refs)} cell rows "
                f"for {row_count} row labels"
            )
        if values and len(values) != row_count:
            raise ValueError(
                f"scenario definition table {self.name!r} has {len(values)} value rows "
                f"for {row_count} row labels"
            )
        for row in cell_refs:
            if len(row) != column_count:
                raise ValueError(
                    f"scenario definition table {self.name!r} has a cell row with {len(row)} "
                    f"cells for {column_count} columns"
                )
        for row in values:
            if len(row) != column_count:
                raise ValueError(
                    f"scenario definition table {self.name!r} has a value row with {len(row)} "
                    f"values for {column_count} columns"
                )
        for field_name in ("column_role_tags", "raw_column_role_tags", "column_role_tag_refs"):
            field_values = getattr(self, field_name)
            if field_values and len(field_values) != column_count:
                raise ValueError(
                    f"scenario definition table {self.name!r} has {len(field_values)} {field_name} "
                    f"values for {column_count} columns"
                )
        if self.scenario_location_refs and len(self.scenario_location_refs) != len(self.scenario_locations):
            raise ValueError(
                f"scenario definition table {self.name!r} has {len(self.scenario_location_refs)} "
                f"scenario_location_refs for {len(self.scenario_locations)} scenario_locations"
            )


@dataclass(frozen=True)
class HeadlinePoint:
    """One year/value point in a curated headline output series."""

    year: int | str
    cell_refs: tuple[str, ...] | list[str]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "cell_refs",
            tuple(_normalize_full_cell_ref(cell_ref) for cell_ref in self.cell_refs),
        )


@dataclass(frozen=True)
class HeadlineSeries:
    """One curated notebook headline series built from FABLE output tables.

    A series is intentionally narrower than a full output table. It describes the source table,
    source cell references, units, and aggregation rule needed to render a compact analyst-facing
    time series.
    """

    name: str
    label: str
    group: str
    sheet: str
    table_name: str
    points: tuple[HeadlinePoint, ...] | list[HeadlinePoint]
    unit: str | None = None
    description: str | None = None
    aggregation: HeadlineAggregation = "value"

    def __post_init__(self) -> None:
        points = tuple(self.points)
        _require_unique("headline year", (str(point.year) for point in points))
        object.__setattr__(self, "points", points)


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
    """One mutually exclusive FABLE scenario selection table.

    FABLE-C selection tables use a first-column ``x`` marker. Selecting one option means placing
    ``x`` in that option's marker cell and clearing all other marker cells in the same table.
    """

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
        """Return generated-model overrides that place one ``x`` in this table.

        The returned mapping is keyed by normalized full cell references. It clears unselected marker
        cells with ``None`` because Modelwright scenarios accept explicit cell inputs, not workbook UI
        gestures.
        """

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
    """Notebook-facing declaration of FABLE scenario inputs and outputs.

    The spec is the central object passed to FABLE Pyculator control, execution, and rendering
    helpers. It keeps input declarations, discovered definition-table metadata, output declarations,
    and workbook provenance together while preserving their distinct semantics.
    """

    parameters: tuple[ScenarioParameter, ...] | list[ScenarioParameter] = field(default_factory=tuple)
    selection_controls: tuple[SelectionControl, ...] | list[SelectionControl] = field(default_factory=tuple)
    scenario_definition_tables: tuple[ScenarioDefinitionTable, ...] | list[ScenarioDefinitionTable] = field(
        default_factory=tuple
    )
    outputs: tuple[OutputIndicator, ...] | list[OutputIndicator] = field(default_factory=tuple)
    output_tables: tuple[OutputTable, ...] | list[OutputTable] = field(default_factory=tuple)
    headline_series: tuple[HeadlineSeries, ...] | list[HeadlineSeries] = field(default_factory=tuple)
    workbook_id: str | None = None
    provenance: str | None = None

    def __post_init__(self) -> None:
        parameters = tuple(self.parameters)
        selection_controls = tuple(self.selection_controls)
        scenario_definition_tables = tuple(self.scenario_definition_tables)
        outputs = tuple(self.outputs)
        output_tables = tuple(self.output_tables)
        headline_series = tuple(self.headline_series)
        _require_unique("parameter", (parameter.name for parameter in parameters))
        _require_unique("selection control", (control.name for control in selection_controls))
        _require_unique("scenario definition table", (table.name for table in scenario_definition_tables))
        _require_unique("output", (output.name for output in outputs))
        _require_unique("output table", (table.name for table in output_tables))
        _require_unique("headline series", (series.name for series in headline_series))
        overlap = set(parameter.name for parameter in parameters) & set(control.name for control in selection_controls)
        if overlap:
            raise ValueError(f"parameter and selection control names overlap: {', '.join(sorted(overlap))}")
        object.__setattr__(self, "parameters", parameters)
        object.__setattr__(self, "selection_controls", selection_controls)
        object.__setattr__(self, "scenario_definition_tables", scenario_definition_tables)
        object.__setattr__(self, "outputs", outputs)
        object.__setattr__(self, "output_tables", output_tables)
        object.__setattr__(self, "headline_series", headline_series)

    def input_mapping(self, values: dict[str, object]) -> dict[str, object]:
        """Convert friendly scenario values to generated-model cell inputs.

        Values may reference curated scalar parameters or discovered selection controls by name.
        Unknown names are rejected so notebook typos do not silently produce partial scenarios.
        """

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


def _normalize_scenario_definition_location(location: str) -> str:
    text = re.sub(r"\s+", "", str(location).strip()).upper().rstrip(".")
    if not re.match(r"^S\.\d+(?:\.[A-Z])?$", text):
        raise ValueError(f"expected a scenario definition location like 'S.3' or 'S.3.C', got {location!r}")
    return text


def _require_unique(kind: str, names: object) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for name in names:
        if name in seen:
            duplicates.add(name)
        seen.add(name)
    if duplicates:
        raise ValueError(f"duplicate {kind} name(s): {', '.join(sorted(duplicates))}")
