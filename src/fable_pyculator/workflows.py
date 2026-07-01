"""FreshForge workflow helpers for FABLE generated-model builds.

The functions in this module turn workbook-derived FABLE Pyculator metadata into the explicit
artifact files that Modelwright needs. They do not generate Python models directly; they prepare the
output-ref lists, cached-workbook validation scenarios, and FreshForge workflow documents that hand
the generic generation and validation stages back to Modelwright.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
import fnmatch
import json
from pathlib import Path
import re
from typing import Any

from openpyxl import load_workbook

from fable_pyculator.spec import FableCalculatorSpec


DEFAULT_2021_ARTIFACT_DIR = Path("tmp/generated-models/fable-2021")
DEFAULT_2021_WORKFLOW_FILENAME = "freshforge-modelwright-run-workflow.json"


@dataclass(frozen=True)
class FableFreshForgeBuildPaths:
    """Version-specific artifact paths for a FABLE Modelwright/FreshForge build."""

    workbook_path: Path
    artifact_dir: Path
    output_refs_path: Path
    workflow_path: Path
    contract_path: Path
    expressions_path: Path
    constants_path: Path
    inference_result_path: Path
    generation_result_path: Path
    generated_model_path: Path
    generated_values_path: Path
    validation_scenario_path: Path
    evaluation_report_path: Path


def freshforge_2021_build_paths(
    *,
    repo_root: str | Path = ".",
    workbook_path: str | Path = "tmp/private-workbooks/2021_Open_FABLECalculator.xlsx",
    artifact_dir: str | Path = DEFAULT_2021_ARTIFACT_DIR,
    workflow_filename: str = DEFAULT_2021_WORKFLOW_FILENAME,
) -> FableFreshForgeBuildPaths:
    """Return the default 2021 FABLE FreshForge build artifact layout.

    Paths are resolved under ``repo_root`` so notebooks can run from VSCode's notebook directory or
    from the repository root while still writing artifacts to the same ignored ``tmp/`` location.
    """

    root = Path(repo_root)
    artifact_root = root / artifact_dir
    return FableFreshForgeBuildPaths(
        workbook_path=root / workbook_path,
        artifact_dir=artifact_root,
        output_refs_path=artifact_root / "output_refs.json",
        workflow_path=artifact_root / workflow_filename,
        contract_path=artifact_root / "contract.json",
        expressions_path=artifact_root / "expressions.json",
        constants_path=artifact_root / "constants.json",
        inference_result_path=artifact_root / "inference-result.json",
        generation_result_path=artifact_root / "generation-result.json",
        generated_model_path=artifact_root / "generated_fable_2021_model.py",
        generated_values_path=artifact_root / "generated-values.json",
        validation_scenario_path=artifact_root / "validation-scenario.json",
        evaluation_report_path=artifact_root / "evaluation-report.json",
    )


def derive_output_refs(
    spec: FableCalculatorSpec,
    *,
    column_flavour_tags: str | Sequence[str] | None = "OUTPUT-*",
    table_names: Sequence[str] | None = None,
) -> tuple[str, ...]:
    """Derive sorted workbook cell refs from discovered output-table metadata.

    ``column_flavour_tags`` accepts exact tags, the ``DATA``/``OUTPUT`` family aliases, and trailing
    wildcard patterns such as ``OUTPUT-*``. Passing ``None`` selects every column in the selected
    output tables.
    """

    selected_table_names = set(table_names) if table_names is not None else None
    known_table_names = {table.name for table in spec.output_tables}
    if selected_table_names is not None:
        unknown = sorted(selected_table_names - known_table_names)
        if unknown:
            raise KeyError(f"unknown output table name(s): {', '.join(unknown)}")
    patterns = _column_flavour_patterns(column_flavour_tags)
    refs: set[str] = set()
    for table in spec.output_tables:
        if selected_table_names is not None and table.name not in selected_table_names:
            continue
        for column_index in _matching_column_indexes(table.column_flavour_tags, patterns):
            refs.update(row[column_index] for row in table.cell_refs)
    return tuple(sorted(refs))


def write_output_refs(path: str | Path, output_refs: Iterable[str]) -> tuple[str, ...]:
    """Write sorted unique output refs as stable JSON and return the written refs."""

    refs = tuple(sorted(set(output_refs)))
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(list(refs), indent=2) + "\n", encoding="utf-8")
    return refs


def build_cached_workbook_validation_scenario(
    workbook_path: str | Path,
    output_refs: Iterable[str],
    *,
    generated_model_path: str | Path,
    scenario_id: str,
    description: str,
    source_workbook: str | Path | None = None,
    generated_model: str | Path | None = None,
    numeric_tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Build a Modelwright validation scenario from cached workbook output values.

    Blank cached outputs are skipped because they are not comparable evidence. Numeric outputs get
    the supplied tolerance; text, boolean, and spreadsheet error values use exact matching.
    """

    cached_workbook = load_workbook(workbook_path, data_only=True, read_only=True)
    validation_outputs: list[dict[str, Any]] = []
    for cell_ref in output_refs:
        sheet_name, coordinate = cell_ref.split("!", maxsplit=1)
        value = cached_workbook[sheet_name][coordinate].value
        kind = _cached_value_kind(value)
        if kind == "blank":
            continue
        output: dict[str, Any] = {"cell_ref": cell_ref, "kind": kind}
        if kind == "number":
            output["tolerance"] = numeric_tolerance
        validation_outputs.append(output)
    return {
        "scenario_id": scenario_id,
        "description": description,
        "source_workbook": str(source_workbook if source_workbook is not None else workbook_path),
        "generated_model": str(generated_model if generated_model is not None else generated_model_path),
        "oracle": {"backend": "cached_workbook"},
        "inputs": [],
        "outputs": validation_outputs,
        "comparison": {
            "default_numeric_tolerance": numeric_tolerance,
            "text": "exact",
            "boolean": "exact",
        },
    }


def write_validation_scenario(path: str | Path, scenario: dict[str, Any]) -> dict[str, Any]:
    """Write a Modelwright validation scenario as stable JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    return scenario


def build_modelwright_freshforge_workflow(
    paths: FableFreshForgeBuildPaths,
    *,
    workdir: str | Path,
    workflow_id: str,
    name: str,
    description: str,
    module_name: str,
) -> dict[str, Any]:
    """Build a FreshForge workflow document for Modelwright generated-model stages."""

    root = Path(workdir)

    def rel(path: str | Path) -> str:
        return str(Path(path).relative_to(root))

    return {
        "workflow": {
            "id": workflow_id,
            "name": name,
            "description": description,
        },
        "nodes": [
            {
                "id": "infer_contract",
                "provider": "modelwright.model_infer_contract",
                "outputs": {
                    "generated_contract": "generated_contract",
                    "formula_expressions": "formula_expressions",
                    "input_constants": "input_constants",
                },
                "parameters": {
                    "workbook": rel(paths.workbook_path),
                    "module_name": module_name,
                },
                "artifacts": {
                    "output_refs": rel(paths.output_refs_path),
                    "contract": rel(paths.contract_path),
                    "expressions": rel(paths.expressions_path),
                    "constants": rel(paths.constants_path),
                    "inference_result": rel(paths.inference_result_path),
                },
            },
            {
                "id": "generate_model",
                "provider": "modelwright.model_generate",
                "needs": ["infer_contract"],
                "inputs": {
                    "generated_contract": "infer_contract.generated_contract",
                    "formula_expressions": "infer_contract.formula_expressions",
                    "input_constants": "infer_contract.input_constants",
                },
                "outputs": {"generated_model": module_name},
                "artifacts": {
                    "contract": rel(paths.contract_path),
                    "expressions": rel(paths.expressions_path),
                    "constants": rel(paths.constants_path),
                    "generated_model": rel(paths.generated_model_path),
                    "generation_result": rel(paths.generation_result_path),
                },
            },
            {
                "id": "execute_model",
                "provider": "modelwright.model_execute",
                "needs": ["generate_model"],
                "inputs": {
                    "generated_contract": "infer_contract.generated_contract",
                    "generated_model": "generate_model.generated_model",
                },
                "outputs": {"generated_values": "generated_values"},
                "artifacts": {
                    "contract": rel(paths.contract_path),
                    "generated_model": rel(paths.generated_model_path),
                    "generated_values": rel(paths.generated_values_path),
                },
            },
            {
                "id": "evaluate_model",
                "provider": "modelwright.validation_evaluate",
                "needs": ["execute_model"],
                "inputs": {
                    "generated_contract": "infer_contract.generated_contract",
                    "generated_model": "generate_model.generated_model",
                },
                "outputs": {"validation_report": "validation_report"},
                "parameters": {"scenario": rel(paths.validation_scenario_path)},
                "artifacts": {
                    "contract": rel(paths.contract_path),
                    "generated_model": rel(paths.generated_model_path),
                    "scenario": rel(paths.validation_scenario_path),
                    "evaluation_report": rel(paths.evaluation_report_path),
                },
            },
        ],
    }


def write_freshforge_workflow(path: str | Path, workflow: dict[str, Any]) -> dict[str, Any]:
    """Write a FreshForge workflow document as stable JSON."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
    return workflow


def _matching_column_indexes(
    column_flavour_tags: Sequence[str | None],
    patterns: tuple[str, ...] | None,
) -> tuple[int, ...]:
    if patterns is None:
        return tuple(range(len(column_flavour_tags)))
    indexes: list[int] = []
    for index, tag in enumerate(column_flavour_tags):
        if tag is None:
            continue
        normalized_tag = _normalize_column_flavour_tag(tag)
        if any(fnmatch.fnmatchcase(normalized_tag, pattern) for pattern in patterns):
            indexes.append(index)
    return tuple(indexes)


def _column_flavour_patterns(column_flavour_tags: str | Sequence[str] | None) -> tuple[str, ...] | None:
    if column_flavour_tags is None:
        return None
    values = (column_flavour_tags,) if isinstance(column_flavour_tags, str) else tuple(column_flavour_tags)
    return tuple(_normalize_column_flavour_pattern(value) for value in values)


def _normalize_column_flavour_pattern(value: str) -> str:
    text = _normalize_column_flavour_tag(value)
    if text in {"DATA", "OUTPUT"}:
        return f"{text}-*"
    return text


def _normalize_column_flavour_tag(value: str) -> str:
    text = re.sub(r"\s+", "", str(value).strip().upper())
    text = re.sub(r"^(DATA|OUTPUT)-", r"\1-", text)
    text = re.sub(r"^OUTPUT(\d)", r"OUTPUT-\1", text)
    return text


def _cached_value_kind(value: object) -> str:
    if isinstance(value, bool):
        return "boolean"
    if value is None:
        return "blank"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str) and value.startswith("#"):
        return "error"
    return "text"
