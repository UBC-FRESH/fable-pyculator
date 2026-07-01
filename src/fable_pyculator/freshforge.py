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
                "Plan-only provider for FABLE workbook surface discovery, output-ref derivation, "
                "and notebook workflow orchestration around Modelwright-generated models."
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
