"""JSON serialization for prepared FABLE specs.

Building a spec from a real FABLE workbook is expensive. The portal prepares it once, writes the
typed declaration to a cache under the ignored runtime directory, and reloads it on the next start.
Only declaration metadata is cached; generated values are never cached here.
"""

from __future__ import annotations

import datetime as dt
import math
from typing import Any

from fable_pyculator.spec import (
    FableCalculatorSpec,
    HeadlinePoint,
    HeadlineSeries,
    OutputIndicator,
    OutputTable,
    ScenarioDefinitionTable,
    ScenarioParameter,
    SelectionControl,
    SelectionOption,
)

__all__ = ["spec_from_payload", "spec_summary", "spec_to_payload"]


def jsonable(value: Any) -> Any:
    """Convert workbook values and numpy-like scalars to JSON-safe values."""

    if value is None or isinstance(value, str | bool | int):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dt.datetime | dt.date | dt.time):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [jsonable(item) for item in value]
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return jsonable(item())
        except (TypeError, ValueError):
            pass
    return str(value)


def spec_to_payload(spec: FableCalculatorSpec) -> dict[str, Any]:
    """Serialize a spec to a stable JSON-ready payload."""

    return {
        "parameters": [
            {
                "name": parameter.name,
                "label": parameter.label,
                "cell_ref": parameter.cell_ref,
                "kind": parameter.kind,
                "unit": parameter.unit,
                "description": parameter.description,
                "default": jsonable(parameter.default),
                "choices": [jsonable(choice) for choice in parameter.choices],
                "source": parameter.source,
            }
            for parameter in spec.parameters
        ],
        "selection_controls": [
            {
                "name": control.name,
                "label": control.label,
                "table_name": control.table_name,
                "sheet": control.sheet,
                "range_ref": control.range_ref,
                "code_header": control.code_header,
                "location": control.location,
                "description": control.description,
                "default": control.default,
                "options": [
                    {
                        "value": option.value,
                        "label": option.label,
                        "selection_cell_ref": option.selection_cell_ref,
                        "description": option.description,
                        "selected": option.selected,
                    }
                    for option in control.options
                ],
            }
            for control in spec.selection_controls
        ],
        "scenario_definition_tables": [
            {
                "name": table.name,
                "sheet": table.sheet,
                "range_ref": table.range_ref,
                "cell_refs": [list(row) for row in table.cell_refs],
                "row_labels": list(table.row_labels),
                "column_labels": list(table.column_labels),
                "values": [[jsonable(value) for value in row] for row in table.values],
                "column_role_tags": list(table.column_role_tags),
                "raw_column_role_tags": list(table.raw_column_role_tags),
                "column_role_tag_refs": list(table.column_role_tag_refs),
                "scenario_locations": list(table.scenario_locations),
                "scenario_location_refs": list(table.scenario_location_refs),
                "label": table.label,
                "description": table.description,
            }
            for table in spec.scenario_definition_tables
        ],
        "outputs": [
            {
                "name": output.name,
                "label": output.label,
                "cell_ref": output.cell_ref,
                "unit": output.unit,
                "group": output.group,
                "description": output.description,
            }
            for output in spec.outputs
        ],
        "output_tables": [
            {
                "name": table.name,
                "sheet": table.sheet,
                "range_ref": table.range_ref,
                "cell_refs": [list(row) for row in table.cell_refs],
                "row_labels": list(table.row_labels),
                "column_labels": list(table.column_labels),
                "values": [[jsonable(value) for value in row] for row in table.values],
                "column_flavour_tags": list(table.column_flavour_tags),
                "raw_column_flavour_tags": list(table.raw_column_flavour_tags),
                "column_flavour_tag_refs": list(table.column_flavour_tag_refs),
                "label": table.label,
                "description": table.description,
            }
            for table in spec.output_tables
        ],
        "headline_series": [
            {
                "name": series.name,
                "label": series.label,
                "group": series.group,
                "sheet": series.sheet,
                "table_name": series.table_name,
                "points": [
                    {"year": jsonable(point.year), "cell_refs": list(point.cell_refs)} for point in series.points
                ],
                "unit": series.unit,
                "description": series.description,
                "aggregation": series.aggregation,
            }
            for series in spec.headline_series
        ],
        "workbook_id": spec.workbook_id,
        "provenance": spec.provenance,
    }


def spec_from_payload(payload: dict[str, Any]) -> FableCalculatorSpec:
    """Reconstruct a spec from :func:`spec_to_payload` output."""

    return FableCalculatorSpec(
        parameters=[
            ScenarioParameter(
                name=str(item["name"]),
                label=str(item["label"]),
                cell_ref=str(item["cell_ref"]),
                kind=item.get("kind", "number"),
                unit=item.get("unit"),
                description=item.get("description"),
                default=item.get("default"),
                choices=tuple(item.get("choices", ())),
                source=item.get("source"),
            )
            for item in payload.get("parameters", [])
        ],
        selection_controls=[
            SelectionControl(
                name=str(item["name"]),
                label=str(item["label"]),
                table_name=str(item["table_name"]),
                sheet=str(item["sheet"]),
                range_ref=str(item["range_ref"]),
                code_header=str(item["code_header"]),
                options=tuple(
                    SelectionOption(
                        value=str(option["value"]),
                        label=option.get("label"),
                        selection_cell_ref=str(option["selection_cell_ref"]),
                        description=option.get("description"),
                        selected=bool(option.get("selected", False)),
                    )
                    for option in item.get("options", [])
                ),
                location=item.get("location"),
                description=item.get("description"),
            )
            for item in payload.get("selection_controls", [])
        ],
        scenario_definition_tables=[
            ScenarioDefinitionTable(
                name=str(item["name"]),
                sheet=str(item["sheet"]),
                range_ref=str(item["range_ref"]),
                cell_refs=tuple(tuple(row) for row in item.get("cell_refs", [])),
                row_labels=tuple(item.get("row_labels", [])),
                column_labels=tuple(item.get("column_labels", [])),
                values=tuple(tuple(row) for row in item.get("values", [])),
                column_role_tags=tuple(item.get("column_role_tags", [])),
                raw_column_role_tags=tuple(item.get("raw_column_role_tags", [])),
                column_role_tag_refs=tuple(item.get("column_role_tag_refs", [])),
                scenario_locations=tuple(item.get("scenario_locations", [])),
                scenario_location_refs=tuple(item.get("scenario_location_refs", [])),
                label=item.get("label"),
                description=item.get("description"),
            )
            for item in payload.get("scenario_definition_tables", [])
        ],
        outputs=[
            OutputIndicator(
                name=str(item["name"]),
                label=str(item["label"]),
                cell_ref=str(item["cell_ref"]),
                unit=item.get("unit"),
                group=item.get("group"),
                description=item.get("description"),
            )
            for item in payload.get("outputs", [])
        ],
        output_tables=[
            OutputTable(
                name=str(item["name"]),
                sheet=str(item["sheet"]),
                range_ref=str(item["range_ref"]),
                cell_refs=tuple(tuple(row) for row in item.get("cell_refs", [])),
                row_labels=tuple(item.get("row_labels", [])),
                column_labels=tuple(item.get("column_labels", [])),
                values=tuple(tuple(row) for row in item.get("values", [])),
                column_flavour_tags=tuple(item.get("column_flavour_tags", [])),
                raw_column_flavour_tags=tuple(item.get("raw_column_flavour_tags", [])),
                column_flavour_tag_refs=tuple(item.get("column_flavour_tag_refs", [])),
                label=item.get("label"),
                description=item.get("description"),
            )
            for item in payload.get("output_tables", [])
        ],
        headline_series=[
            HeadlineSeries(
                name=str(item["name"]),
                label=str(item["label"]),
                group=str(item["group"]),
                sheet=str(item["sheet"]),
                table_name=str(item["table_name"]),
                points=tuple(
                    HeadlinePoint(year=point["year"], cell_refs=tuple(point.get("cell_refs", [])))
                    for point in item.get("points", [])
                ),
                unit=item.get("unit"),
                description=item.get("description"),
                aggregation=item.get("aggregation", "value"),
            )
            for item in payload.get("headline_series", [])
        ],
        workbook_id=payload.get("workbook_id"),
        provenance=payload.get("provenance"),
    )


def spec_summary(spec: FableCalculatorSpec) -> dict[str, Any]:
    """Return the compact declaration metadata the browser needs."""

    return {
        "workbook_id": spec.workbook_id,
        "provenance": spec.provenance,
        "counts": {
            "parameters": len(spec.parameters),
            "selection_controls": len(spec.selection_controls),
            "scenario_definition_tables": len(spec.scenario_definition_tables),
            "outputs": len(spec.outputs),
            "output_tables": len(spec.output_tables),
            "headline_series": len(spec.headline_series),
        },
        "parameters": [
            {
                "name": parameter.name,
                "label": parameter.label,
                "kind": parameter.kind,
                "unit": parameter.unit,
                "description": parameter.description,
                "default": jsonable(parameter.default),
                "choices": [jsonable(choice) for choice in parameter.choices],
            }
            for parameter in spec.parameters
        ],
        "selection_controls": [
            {
                "name": control.name,
                "label": control.label,
                "location": control.location,
                "description": control.description,
                "default": control.default,
                "options": [
                    {
                        "value": option.value,
                        "label": option.label or option.value,
                        "description": option.description,
                    }
                    for option in control.options
                ],
            }
            for control in spec.selection_controls
        ],
        "outputs": [
            {
                "name": output.name,
                "label": output.label,
                "group": output.group,
                "unit": output.unit,
                "description": output.description,
            }
            for output in spec.outputs
        ],
        "output_tables": [
            {
                "name": table.name,
                "label": table.label,
                "sheet": table.sheet,
                "range_ref": table.range_ref,
                "row_count": len(table.row_labels),
                "column_count": len(table.column_labels),
                "column_flavour_tags": list(table.column_flavour_tags),
            }
            for table in spec.output_tables
        ],
        "headline_series": [
            {
                "name": series.name,
                "label": series.label,
                "group": series.group,
                "unit": series.unit,
                "description": series.description,
                "year_count": len(series.points),
                "years": [jsonable(point.year) for point in series.points],
            }
            for series in spec.headline_series
        ],
        "scenario_definition_tables": [
            {
                "name": table.name,
                "label": table.label,
                "sheet": table.sheet,
                "range_ref": table.range_ref,
                "row_count": len(table.row_labels),
                "column_count": len(table.column_labels),
                "scenario_locations": list(table.scenario_locations),
            }
            for table in spec.scenario_definition_tables
        ],
    }
