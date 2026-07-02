from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from fable_pyculator.freshforge import FABLE_PYCULATOR_PROVIDER_ID, provider_factory


EXAMPLE_PATH = Path("examples/freshforge/fable_2021_notebook_workflow.yaml")
EXPECTED_PLAN_ORDER = [
    "discover_notebook_spec",
    "derive_output_refs",
    "prepare_validation_scenario",
    "build_modelwright_workflow",
    "plan_notebook_loop",
]


def _registry_with_fable_pyculator_provider():
    from freshforge.providers import ProviderRegistry

    registry = ProviderRegistry()
    registry.register(provider_factory())
    return registry


def test_provider_factory_returns_fable_pyculator_provider() -> None:
    provider = provider_factory()

    assert provider.__class__.__name__ == "FablePyculatorFreshForgeProvider"
    assert FABLE_PYCULATOR_PROVIDER_ID == "fable_pyculator"


def test_provider_metadata_serializes_deterministically() -> None:
    pytest.importorskip("freshforge")
    metadata = provider_factory().metadata()

    assert metadata.to_dict() == {
        "id": "fable_pyculator",
        "version": "0.1.0a4",
        "node_types": [
            {
                "id": "notebook_spec_discover",
                "inputs": [],
                "outputs": ["notebook_spec"],
                "parameters": ["workbook", "workbook_id"],
                "artifacts": ["spec_summary"],
                "name": "Discover notebook spec",
                "description": "Declare FABLE workbook-surface discovery into a notebook-facing spec.",
            },
            {
                "id": "output_refs_derive",
                "inputs": ["notebook_spec"],
                "outputs": ["output_refs"],
                "parameters": ["column_flavour_tags"],
                "artifacts": ["output_refs"],
                "name": "Derive output refs",
                "description": "Declare output-ref derivation from FABLE output-table flavour metadata.",
            },
            {
                "id": "validation_scenario_prepare",
                "inputs": ["output_refs"],
                "outputs": ["validation_scenario"],
                "parameters": ["scenario_id", "source_workbook", "generated_model"],
                "artifacts": ["validation_scenario"],
                "name": "Prepare validation scenario",
                "description": "Declare cached-workbook validation scenario preparation for selected output refs.",
            },
            {
                "id": "modelwright_workflow_build",
                "inputs": ["output_refs", "validation_scenario"],
                "outputs": ["modelwright_workflow"],
                "parameters": ["workflow_id", "module_name"],
                "artifacts": ["modelwright_workflow"],
                "name": "Build Modelwright workflow",
                "description": "Declare construction of a downstream Modelwright FreshForge workflow document.",
            },
            {
                "id": "notebook_loop_plan",
                "inputs": ["notebook_spec", "generated_model"],
                "outputs": ["notebook_loop_result"],
                "parameters": ["scenario_name"],
                "artifacts": ["notebook_result_summary"],
                "name": "Plan notebook loop",
                "description": "Declare a notebook loop around a matching workbook spec and generated model.",
            },
            {
                "id": "scenario_bundle_prepare",
                "inputs": [],
                "outputs": ["bundle"],
                "parameters": ["bundle_path", "workbook_path", "workbook_id"],
                "artifacts": ["normalized_bundle", "prepare_summary"],
                "name": "Prepare scenario bundle",
                "description": "Validate a scenario bundle and write normalized bundle metadata.",
            },
            {
                "id": "scenario_run",
                "inputs": ["bundle"],
                "outputs": ["scenario_result"],
                "parameters": [
                    "bundle_path",
                    "workbook_path",
                    "workbook_id",
                    "generated_model_path",
                    "module_name",
                    "scenario_id",
                ],
                "artifacts": [
                    "scenario_summary",
                    "scenario_inputs",
                    "output_tables",
                    "headline_frames",
                    "headline_figures",
                ],
                "name": "Run scenario bundle case",
                "description": "Run one scenario bundle case against a matching generated model.",
            },
            {
                "id": "scenario_bundle_manifest",
                "inputs": [],
                "outputs": ["manifest"],
                "parameters": ["bundle_path"],
                "artifacts": ["manifest"],
                "name": "Write scenario bundle manifest",
                "description": "Assemble a scenario-bundle manifest from completed scenario run nodes.",
            },
        ],
        "name": "FABLE Pyculator notebook workflow provider",
        "description": (
            "Provider for FABLE workbook surface discovery, output-ref derivation, "
            "scenario-bundle orchestration, and notebook workflows around Modelwright-generated models."
        ),
    }


def test_pyproject_declares_freshforge_entry_point_without_direct_dependency() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    entry_points = pyproject["project"]["entry-points"]["freshforge.providers"]
    assert entry_points["fable_pyculator"] == "fable_pyculator.freshforge:provider_factory"
    optional = pyproject["project"]["optional-dependencies"]
    assert "freshforge" not in optional
    assert "freshforge" not in "\n".join(pyproject["project"]["dependencies"])


def test_fable_pyculator_import_does_not_import_freshforge_eagerly() -> None:
    script = "import sys; import fable_pyculator; print('freshforge' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "False"


def test_example_workflow_validates_and_plans() -> None:
    pytest.importorskip("freshforge")
    from freshforge.loading import load_workflow
    from freshforge.planning import create_run_plan
    from freshforge.validation import validate_workflow_with_providers

    spec, load_diagnostics = load_workflow(EXAMPLE_PATH)
    assert spec is not None
    assert load_diagnostics == []

    diagnostics = validate_workflow_with_providers(
        spec,
        registry=_registry_with_fable_pyculator_provider(),
        structural_diagnostics=load_diagnostics,
    )
    assert diagnostics == []

    plan = create_run_plan(
        spec,
        diagnostics=diagnostics,
        registry=_registry_with_fable_pyculator_provider(),
    )
    assert not plan.has_errors
    assert [node.id for node in plan.nodes] == EXPECTED_PLAN_ORDER
    assert {node.provider_id for node in plan.nodes} == {"fable_pyculator"}


def test_missing_required_parameter_returns_provider_diagnostic() -> None:
    pytest.importorskip("freshforge")
    from freshforge.loading import load_workflow_document
    from freshforge.validation import validate_workflow_document, validate_workflow_with_providers

    document = load_workflow_document(EXAMPLE_PATH)
    del document["nodes"][0]["parameters"]["workbook"]
    spec, structural = validate_workflow_document(document)

    assert spec is not None
    diagnostics = validate_workflow_with_providers(
        spec,
        registry=_registry_with_fable_pyculator_provider(),
        structural_diagnostics=structural,
    )

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "fable_pyculator.parameters.missing"
    }
    assert diagnostics[0].location == "nodes[0].parameters.workbook"
