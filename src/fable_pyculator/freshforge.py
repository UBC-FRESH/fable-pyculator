"""FreshForge provider metadata for FABLE Pyculator notebook workflows.

This module is intentionally plan-only. It lets FreshForge validate and plan FABLE-specific notebook
workflow stages, while execution stays with notebooks, FABLE Pyculator helper APIs, and Modelwright's
generated-model provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FABLE_PYCULATOR_PROVIDER_ID = "fable_pyculator"
FABLE_PYCULATOR_PROVIDER_VERSION = "0.1.0a2"


@dataclass(frozen=True)
class _NodeContract:
    id: str
    name: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()


_NODE_CONTRACTS: tuple[_NodeContract, ...] = (
    _NodeContract(
        id="notebook_spec_discover",
        name="Discover notebook spec",
        description="Declare FABLE workbook-surface discovery into a notebook-facing spec.",
        outputs=("notebook_spec",),
        parameters=("workbook", "workbook_id"),
        artifacts=("spec_summary",),
    ),
    _NodeContract(
        id="output_refs_derive",
        name="Derive output refs",
        description="Declare output-ref derivation from FABLE output-table flavour metadata.",
        inputs=("notebook_spec",),
        outputs=("output_refs",),
        parameters=("column_flavour_tags",),
        artifacts=("output_refs",),
    ),
    _NodeContract(
        id="validation_scenario_prepare",
        name="Prepare validation scenario",
        description="Declare cached-workbook validation scenario preparation for selected output refs.",
        inputs=("output_refs",),
        outputs=("validation_scenario",),
        parameters=("scenario_id", "source_workbook", "generated_model"),
        artifacts=("validation_scenario",),
    ),
    _NodeContract(
        id="modelwright_workflow_build",
        name="Build Modelwright workflow",
        description="Declare construction of a downstream Modelwright FreshForge workflow document.",
        inputs=("output_refs", "validation_scenario"),
        outputs=("modelwright_workflow",),
        parameters=("workflow_id", "module_name"),
        artifacts=("modelwright_workflow",),
    ),
    _NodeContract(
        id="notebook_loop_plan",
        name="Plan notebook loop",
        description="Declare a notebook loop around a matching workbook spec and generated model.",
        inputs=("notebook_spec", "generated_model"),
        outputs=("notebook_loop_result",),
        parameters=("scenario_name",),
        artifacts=("notebook_result_summary",),
    ),
    _NodeContract(
        id="scenario_bundle_prepare",
        name="Prepare scenario bundle",
        description="Validate a scenario bundle and write normalized bundle metadata.",
        outputs=("bundle",),
        parameters=("bundle_path", "workbook_path", "workbook_id"),
        artifacts=("normalized_bundle", "prepare_summary"),
    ),
    _NodeContract(
        id="scenario_run",
        name="Run scenario bundle case",
        description="Run one scenario bundle case against a matching generated model.",
        inputs=("bundle",),
        outputs=("scenario_result",),
        parameters=(
            "bundle_path",
            "workbook_path",
            "workbook_id",
            "generated_model_path",
            "module_name",
            "scenario_id",
        ),
        artifacts=(
            "scenario_summary",
            "scenario_inputs",
            "output_tables",
            "headline_frames",
            "headline_figures",
        ),
    ),
    _NodeContract(
        id="scenario_bundle_manifest",
        name="Write scenario bundle manifest",
        description="Assemble a scenario-bundle manifest from completed scenario run nodes.",
        outputs=("manifest",),
        parameters=("bundle_path",),
        artifacts=("manifest",),
    ),
)


class FablePyculatorFreshForgeProvider:
    """FreshForge provider for plan-only FABLE Pyculator notebook workflow stages."""

    def metadata(self) -> Any:
        """Return FreshForge provider metadata."""
        node_type_metadata, provider_metadata = _freshforge_metadata_types()
        return provider_metadata(
            id=FABLE_PYCULATOR_PROVIDER_ID,
            version=FABLE_PYCULATOR_PROVIDER_VERSION,
            name="FABLE Pyculator notebook workflow provider",
            description=(
                "Provider for FABLE workbook surface discovery, output-ref derivation, "
                "scenario-bundle orchestration, and notebook workflows around Modelwright-generated models."
            ),
            node_types=tuple(
                node_type_metadata(
                    id=contract.id,
                    name=contract.name,
                    description=contract.description,
                    inputs=contract.inputs,
                    outputs=contract.outputs,
                    parameters=contract.parameters,
                    artifacts=contract.artifacts,
                )
                for contract in _NODE_CONTRACTS
            ),
        )

    def validate_node(
        self,
        node: Any,
        node_type: Any,
        *,
        location: str,
    ) -> tuple[Any, ...]:
        """Validate broad FABLE Pyculator node shape without executing notebook helpers."""
        diagnostic, severity = _freshforge_diagnostic_types()
        diagnostics: list[Any] = []
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.inputs),
                actual=node.inputs,
                field_name="inputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.outputs),
                actual=node.outputs,
                field_name="outputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.parameters),
                actual=node.parameters,
                field_name="parameters",
                location=location,
            )
        )
        artifacts = node.artifacts if isinstance(node.artifacts, dict) else {}
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.artifacts),
                actual=artifacts,
                field_name="artifacts",
                location=location,
            )
        )
        diagnostics.extend(
            _empty_parameter_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                parameters=node.parameters,
                required=tuple(node_type.parameters),
                location=location,
            )
        )
        return tuple(diagnostics)

    def run_node(
        self,
        node: Any,
        node_type: Any,
        *,
        context: Any,
    ) -> Any:
        """Execute Phase 19 scenario-bundle nodes while leaving Phase 9 nodes plan-only."""

        if node_type.id == "scenario_bundle_prepare":
            return _run_scenario_bundle_prepare(node, context)
        if node_type.id == "scenario_run":
            return _run_scenario(node, context)
        if node_type.id == "scenario_bundle_manifest":
            return _run_scenario_bundle_manifest(node, context)
        run_status, diagnostic, severity = _freshforge_run_types()
        return _provider_result(
            status=run_status.FAILED,
            diagnostics=(
                diagnostic(
                    severity=severity.ERROR,
                    code="fable_pyculator.execution.unsupported",
                    message=f"FABLE Pyculator node type '{node_type.id}' is plan-only.",
                    location=f"nodes.{node.id}",
                ),
            ),
        )


def provider_factory() -> FablePyculatorFreshForgeProvider:
    """Return the FABLE Pyculator FreshForge provider for entry-point discovery."""
    return FablePyculatorFreshForgeProvider()


def _freshforge_metadata_types() -> tuple[Any, Any]:
    try:
        from freshforge.providers import (  # type: ignore[import-untyped]
            NodeTypeMetadata,
            ProviderMetadata,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The FABLE Pyculator FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return NodeTypeMetadata, ProviderMetadata


def _freshforge_diagnostic_types() -> tuple[Any, Any]:
    try:
        from freshforge.records import (  # type: ignore[import-untyped]
            Diagnostic,
            DiagnosticSeverity,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The FABLE Pyculator FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return Diagnostic, DiagnosticSeverity


def _freshforge_run_types() -> tuple[Any, Any, Any]:
    try:
        from freshforge.records import (  # type: ignore[import-untyped]
            Diagnostic,
            DiagnosticSeverity,
            RunStatus,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The FABLE Pyculator FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return RunStatus, Diagnostic, DiagnosticSeverity


def _provider_result(
    *,
    status: Any,
    outputs: dict[str, Any] | None = None,
    artifacts: dict[str, Any] | None = None,
    diagnostics: tuple[Any, ...] = (),
    data: dict[str, Any] | None = None,
) -> Any:
    try:
        from freshforge.records import ProviderRunResult  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The FABLE Pyculator FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return ProviderRunResult(
        status=status,
        outputs=outputs or {},
        artifacts=artifacts or {},
        diagnostics=diagnostics,
        data=data or {},
    )


def _run_scenario_bundle_prepare(node: Any, context: Any) -> Any:
    run_status, diagnostic, severity = _freshforge_run_types()
    try:
        from fable_pyculator.notebook import build_notebook_spec
        from fable_pyculator.scenarios import load_scenario_bundle, validate_scenario_bundle
        from fable_pyculator.workbook import suppress_benign_openpyxl_warnings
        from freshforge.execution import artifact_paths  # type: ignore[import-untyped]

        paths = artifact_paths(node, context)
        bundle = load_scenario_bundle(node.parameters["bundle_path"])
        with suppress_benign_openpyxl_warnings():
            spec = build_notebook_spec(
                node.parameters["workbook_path"],
                workbook_id=node.parameters["workbook_id"],
            )
        validate_scenario_bundle(bundle, spec)
        normalized = _bundle_to_mapping(bundle)
        _write_json(paths["normalized_bundle"], normalized)
        summary = {
            "bundle_id": bundle.bundle_id,
            "workbook_version": bundle.workbook_version,
            "scenario_count": len(bundle.scenarios),
            "scenario_ids": [scenario.scenario_id for scenario in bundle.scenarios],
        }
        _write_json(paths["prepare_summary"], summary)
        return _provider_result(
            status=run_status.SUCCESS,
            outputs={"bundle": bundle.bundle_id},
            artifacts={key: str(path) for key, path in paths.items()},
            data={"summary": summary},
        )
    except Exception as exc:  # noqa: BLE001
        return _failed_provider_result(
            run_status=run_status,
            diagnostic=diagnostic,
            severity=severity,
            code="fable_pyculator.scenario_bundle_prepare.failed",
            message=f"Scenario-bundle preparation failed: {exc}",
            location=f"nodes.{node.id}",
        )


def _run_scenario(node: Any, context: Any) -> Any:
    run_status, diagnostic, severity = _freshforge_run_types()
    try:
        from fable_pyculator.notebook import build_notebook_spec, load_generated_model, run_notebook_loop
        from fable_pyculator.scenarios import load_scenario_bundle, validate_scenario_bundle, write_scenario_artifacts
        from fable_pyculator.workbook import suppress_benign_openpyxl_warnings
        from freshforge.execution import artifact_paths  # type: ignore[import-untyped]

        paths = artifact_paths(node, context)
        bundle = load_scenario_bundle(node.parameters["bundle_path"])
        with suppress_benign_openpyxl_warnings():
            spec = build_notebook_spec(
                node.parameters["workbook_path"],
                workbook_id=node.parameters["workbook_id"],
            )
        validate_scenario_bundle(bundle, spec)
        scenario_id = node.parameters["scenario_id"]
        scenario = _scenario_by_id(bundle, scenario_id)
        generated_model = load_generated_model(
            node.parameters["generated_model_path"],
            module_name=node.parameters["module_name"],
        )
        result = run_notebook_loop(
            generated_model,
            spec,
            scenario.selections,
            scenario_name=scenario.scenario_id,
            output_table_names=bundle.render.output_table_names,
            output_table_column_flavour_tags=bundle.render.output_table_column_flavour_tags,
            include_context_columns=bundle.render.include_context_columns,
            headline_series_names=bundle.render.headline_series_names,
            include_figures=bundle.render.include_figures,
        )
        output_dir = _context_output_dir(context)
        manifest_entry = write_scenario_artifacts(
            result,
            scenario,
            scenario_dir=paths["scenario_summary"].parent,
            output_dir=output_dir,
        )
        scenario_summary = {
            **manifest_entry,
            "status": "success",
            "output_table_count": len(result.output_tables),
            "headline_frame_count": len(result.headline_frames),
            "headline_figure_count": len(result.headline_figures),
        }
        _write_json(paths["scenario_summary"], scenario_summary)
        return _provider_result(
            status=run_status.SUCCESS,
            outputs={
                "scenario_result": scenario.scenario_id,
                "manifest_entry": manifest_entry,
            },
            artifacts={key: str(path) for key, path in paths.items()},
            data={"summary": scenario_summary},
        )
    except Exception as exc:  # noqa: BLE001
        return _failed_provider_result(
            run_status=run_status,
            diagnostic=diagnostic,
            severity=severity,
            code="fable_pyculator.scenario_run.failed",
            message=f"Scenario run failed: {exc}",
            location=f"nodes.{node.id}",
        )


def _run_scenario_bundle_manifest(node: Any, context: Any) -> Any:
    run_status, diagnostic, severity = _freshforge_run_types()
    try:
        from fable_pyculator.scenarios import load_scenario_bundle
        from freshforge.execution import artifact_paths  # type: ignore[import-untyped]

        paths = artifact_paths(node, context)
        bundle = load_scenario_bundle(node.parameters["bundle_path"])
        output_dir = _context_output_dir(context)
        scenario_entries = []
        for scenario in bundle.scenarios:
            outputs = context.completed_outputs.get(f"scenario_{scenario.scenario_id}", {})
            entry = outputs.get("manifest_entry")
            if isinstance(entry, dict):
                scenario_entries.append(entry)
        manifest = {
            "bundle_id": bundle.bundle_id,
            "workbook_version": bundle.workbook_version,
            "scenario_count": len(bundle.scenarios),
            "render": _render_to_mapping(bundle.render),
            "normalized_bundle": _relative_to(output_dir / "bundle.json", output_dir),
            "freshforge": {
                "workflow_id": context.workflow_id,
                "run_namespace": context.run_namespace,
                "scenario_node_count": len(scenario_entries),
            },
            "scenarios": scenario_entries,
        }
        _write_json(paths["manifest"], manifest)
        return _provider_result(
            status=run_status.SUCCESS,
            outputs={"manifest": str(paths["manifest"])},
            artifacts={key: str(path) for key, path in paths.items()},
            data={"summary": {"scenario_count": len(scenario_entries), "manifest": str(paths["manifest"])}},
        )
    except Exception as exc:  # noqa: BLE001
        return _failed_provider_result(
            run_status=run_status,
            diagnostic=diagnostic,
            severity=severity,
            code="fable_pyculator.scenario_bundle_manifest.failed",
            message=f"Scenario-bundle manifest failed: {exc}",
            location=f"nodes.{node.id}",
        )


def _failed_provider_result(
    *,
    run_status: Any,
    diagnostic: Any,
    severity: Any,
    code: str,
    message: str,
    location: str,
) -> Any:
    return _provider_result(
        status=run_status.FAILED,
        diagnostics=(
            diagnostic(
                severity=severity.ERROR,
                code=code,
                message=message,
                location=location,
            ),
        ),
    )


def _missing_key_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    required: tuple[str, ...],
    actual: dict[str, Any],
    field_name: str,
    location: str,
) -> tuple[Any, ...]:
    return tuple(
        diagnostic(
            severity=severity.ERROR,
            code=f"fable_pyculator.{field_name}.missing",
            message=(
                f"FABLE Pyculator node requires {field_name} key '{key}' for "
                "non-executing workflow planning."
            ),
            location=f"{location}.{field_name}.{key}",
        )
        for key in required
        if key not in actual
    )


def _empty_parameter_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    parameters: dict[str, Any],
    required: tuple[str, ...],
    location: str,
) -> tuple[Any, ...]:
    diagnostics: list[Any] = []
    for key in required:
        value = parameters.get(key)
        if isinstance(value, str) and not value.strip():
            diagnostics.append(
                diagnostic(
                    severity=severity.ERROR,
                    code="fable_pyculator.parameters.empty",
                    message=f"FABLE Pyculator node parameter '{key}' must be nonempty.",
                    location=f"{location}.parameters.{key}",
                )
            )
    return tuple(diagnostics)


def _scenario_by_id(bundle: Any, scenario_id: str) -> Any:
    for scenario in bundle.scenarios:
        if scenario.scenario_id == scenario_id:
            return scenario
    raise KeyError(f"scenario_id not found in bundle: {scenario_id}")


def _context_output_dir(context: Any) -> Any:
    from pathlib import Path

    if context.run_namespace is None:
        return Path(context.workdir)
    return Path(context.workdir) / context.run_namespace


def _bundle_to_mapping(bundle: Any) -> dict[str, Any]:
    return {
        "version": bundle.version,
        "bundle_id": bundle.bundle_id,
        "workbook_version": bundle.workbook_version,
        "description": bundle.description,
        "render": _render_to_mapping(bundle.render),
        "scenarios": [
            {
                "scenario_id": scenario.scenario_id,
                "label": scenario.label,
                "description": scenario.description,
                "selections": scenario.selections,
            }
            for scenario in bundle.scenarios
        ],
    }


def _render_to_mapping(render: Any) -> dict[str, Any]:
    return {
        "output_table_names": list(render.output_table_names) if render.output_table_names is not None else None,
        "output_table_column_flavour_tags": render.output_table_column_flavour_tags,
        "include_context_columns": render.include_context_columns,
        "headline_series_names": list(render.headline_series_names) if render.headline_series_names is not None else None,
        "include_figures": render.include_figures,
    }


def _relative_to(path: Any, root: Any) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _write_json(path: Any, payload: Any) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
