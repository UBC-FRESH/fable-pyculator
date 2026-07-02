"""Scenario-bundle helpers for repeated FABLE Pyculator notebook runs.

Scenario bundles are a small analyst-facing layer over the existing notebook loop. They load named
selection-control scenarios from JSON or YAML, validate them against a workbook-derived
``FableCalculatorSpec``, run each scenario against an already available generated model, and write
rendered table/headline artifacts under ignored local paths.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import re
from types import ModuleType
from typing import Any

from fable_pyculator.notebook import NotebookLoopResult, run_notebook_loop
from fable_pyculator.spec import FableCalculatorSpec
from fable_pyculator.surface import scenario_frame


@dataclass(frozen=True)
class ScenarioCase:
    """One named scenario inside a scenario bundle."""

    scenario_id: str
    selections: dict[str, object]
    label: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class ScenarioBundleRenderOptions:
    """Output rendering options shared by all scenarios in a bundle."""

    output_table_names: tuple[str, ...] | None = None
    output_table_column_flavour_tags: str | tuple[str, ...] | None = None
    include_context_columns: bool = True
    headline_series_names: tuple[str, ...] | None = None
    include_figures: bool = False


@dataclass(frozen=True)
class ScenarioBundle:
    """A version-aware collection of named FABLE selection-control scenarios."""

    version: int
    bundle_id: str
    workbook_version: str
    scenarios: tuple[ScenarioCase, ...]
    render: ScenarioBundleRenderOptions = ScenarioBundleRenderOptions()
    description: str | None = None


@dataclass(frozen=True)
class ScenarioBundleArtifactPaths:
    """Ignored local output paths for a scenario-bundle run."""

    output_dir: Path
    normalized_bundle_path: Path
    manifest_path: Path

    def scenario_dir(self, scenario_id: str) -> Path:
        """Return the output directory for one scenario id."""

        return self.output_dir / "scenarios" / scenario_id


@dataclass(frozen=True)
class ScenarioBundleRunResult:
    """Rendered results from running every scenario in a bundle."""

    bundle: ScenarioBundle
    render: ScenarioBundleRenderOptions
    scenario_results: dict[str, NotebookLoopResult]


def load_scenario_bundle(path: str | Path) -> ScenarioBundle:
    """Load a scenario bundle from JSON, YAML, or YML."""

    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"scenario bundle not found: {source}")
    if source.suffix.casefold() == ".json":
        data = json.loads(source.read_text(encoding="utf-8"))
    elif source.suffix.casefold() in {".yaml", ".yml"}:
        import yaml

        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"unsupported scenario bundle format: {source.suffix}")
    return _scenario_bundle_from_mapping(_require_mapping(data, "scenario bundle"))


def validate_scenario_bundle(bundle: ScenarioBundle, spec: FableCalculatorSpec) -> ScenarioBundle:
    """Validate bundle ids and selection-control values against a FABLE spec."""

    if bundle.version != 1:
        raise ValueError(f"unsupported scenario bundle version: {bundle.version!r}")
    _require_slug(bundle.bundle_id, "bundle_id")
    if not bundle.scenarios:
        raise ValueError("scenario bundle must contain at least one scenario")
    scenario_ids = [scenario.scenario_id for scenario in bundle.scenarios]
    duplicates = sorted({scenario_id for scenario_id in scenario_ids if scenario_ids.count(scenario_id) > 1})
    if duplicates:
        raise ValueError(f"duplicate scenario_id value(s): {', '.join(duplicates)}")

    controls = {control.name: control for control in spec.selection_controls}
    for scenario in bundle.scenarios:
        _require_slug(scenario.scenario_id, "scenario_id")
        unknown = sorted(set(scenario.selections) - set(controls))
        if unknown:
            raise KeyError(
                f"scenario {scenario.scenario_id!r} contains unknown selection control(s): "
                f"{', '.join(unknown)}"
            )
        for name, value in scenario.selections.items():
            controls[name].input_mapping(value)
    return bundle


def fable_scenario_bundle_artifact_paths(
    *,
    workbook_version: str,
    bundle_id: str,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
) -> ScenarioBundleArtifactPaths:
    """Return the default ignored artifact paths for a scenario-bundle run."""

    _require_slug(bundle_id, "bundle_id")
    root = Path(repo_root)
    output = Path(output_dir) if output_dir is not None else Path(f"tmp/scenario-runs/fable-{workbook_version}/{bundle_id}")
    output_root = output if output.is_absolute() else root / output
    return ScenarioBundleArtifactPaths(
        output_dir=output_root,
        normalized_bundle_path=output_root / "bundle.json",
        manifest_path=output_root / "manifest.json",
    )


def run_scenario_bundle(
    generated_model: ModuleType | object,
    spec: FableCalculatorSpec,
    bundle: ScenarioBundle,
    *,
    output_table_names: Sequence[str] | None = None,
    output_table_column_flavour_tags: str | Sequence[str] | None = None,
    include_context_columns: bool | None = None,
    headline_series_names: Sequence[str] | None = None,
    include_figures: bool | None = None,
) -> ScenarioBundleRunResult:
    """Run every scenario in ``bundle`` using the existing notebook-loop renderer."""

    validate_scenario_bundle(bundle, spec)
    render = _effective_render_options(
        bundle.render,
        output_table_names=output_table_names,
        output_table_column_flavour_tags=output_table_column_flavour_tags,
        include_context_columns=include_context_columns,
        headline_series_names=headline_series_names,
        include_figures=include_figures,
    )
    results = {
        scenario.scenario_id: run_notebook_loop(
            generated_model,
            spec,
            scenario.selections,
            scenario_name=scenario.scenario_id,
            output_table_names=render.output_table_names,
            output_table_column_flavour_tags=render.output_table_column_flavour_tags,
            include_context_columns=render.include_context_columns,
            headline_series_names=render.headline_series_names,
            include_figures=render.include_figures,
        )
        for scenario in bundle.scenarios
    }
    return ScenarioBundleRunResult(bundle=bundle, render=render, scenario_results=results)


def write_scenario_bundle_artifacts(
    run_result: ScenarioBundleRunResult,
    paths: ScenarioBundleArtifactPaths,
) -> dict[str, Any]:
    """Write normalized bundle metadata and rendered scenario artifacts."""

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    bundle_payload = _bundle_to_mapping(run_result.bundle, render=run_result.render)
    _write_json(paths.normalized_bundle_path, bundle_payload)

    scenarios: list[dict[str, Any]] = []
    for scenario in run_result.bundle.scenarios:
        result = run_result.scenario_results[scenario.scenario_id]
        scenarios.append(
            write_scenario_artifacts(
                result,
                scenario,
                scenario_dir=paths.scenario_dir(scenario.scenario_id),
                output_dir=paths.output_dir,
            )
        )

    manifest = {
        "bundle_id": run_result.bundle.bundle_id,
        "workbook_version": run_result.bundle.workbook_version,
        "scenario_count": len(run_result.bundle.scenarios),
        "render": _render_options_to_mapping(run_result.render),
        "normalized_bundle": _relative_to(paths.normalized_bundle_path, paths.output_dir),
        "scenarios": scenarios,
    }
    _write_json(paths.manifest_path, manifest)
    return manifest


def write_scenario_artifacts(
    result: NotebookLoopResult,
    scenario: ScenarioCase,
    *,
    scenario_dir: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Write rendered artifacts for one scenario and return a manifest entry."""

    scenario_root = Path(scenario_dir)
    output_root = Path(output_dir)
    inputs_path = scenario_root / "scenario_inputs.csv"
    inputs_path.parent.mkdir(parents=True, exist_ok=True)
    scenario_frame(result.run).to_csv(inputs_path, index=False)
    output_table_paths = _write_frames(
        result.output_tables,
        scenario_root / "output_tables",
    )
    headline_frame_paths = _write_frames(
        result.headline_frames,
        scenario_root / "headline_frames",
    )
    figure_paths = _write_figures(
        result.headline_figures,
        scenario_root / "headline_figures",
    )
    return {
        "scenario_id": scenario.scenario_id,
        "label": scenario.label,
        "description": scenario.description,
        "scenario_inputs": _relative_to(inputs_path, output_root),
        "output_tables": {
            name: _relative_to(path, output_root)
            for name, path in sorted(output_table_paths.items())
        },
        "headline_frames": {
            name: _relative_to(path, output_root)
            for name, path in sorted(headline_frame_paths.items())
        },
        "headline_figures": {
            name: _relative_to(path, output_root)
            for name, path in sorted(figure_paths.items())
        },
    }


def _scenario_bundle_from_mapping(data: Mapping[str, Any]) -> ScenarioBundle:
    render = _render_options_from_mapping(_optional_mapping(data.get("render"), "render"))
    scenarios_data = data.get("scenarios")
    if not isinstance(scenarios_data, list):
        raise ValueError("scenario bundle must contain a scenarios list")
    scenarios = tuple(_scenario_case_from_mapping(_require_mapping(item, "scenario")) for item in scenarios_data)
    return ScenarioBundle(
        version=int(data.get("version", 1)),
        bundle_id=str(data["bundle_id"]),
        workbook_version=str(data["workbook_version"]),
        description=_optional_text(data.get("description")),
        render=render,
        scenarios=scenarios,
    )


def _scenario_case_from_mapping(data: Mapping[str, Any]) -> ScenarioCase:
    return ScenarioCase(
        scenario_id=str(data["scenario_id"]),
        label=_optional_text(data.get("label")),
        description=_optional_text(data.get("description")),
        selections=dict(_require_mapping(data.get("selections"), "scenario selections")),
    )


def _render_options_from_mapping(data: Mapping[str, Any]) -> ScenarioBundleRenderOptions:
    return ScenarioBundleRenderOptions(
        output_table_names=_optional_text_tuple(data.get("output_table_names")),
        output_table_column_flavour_tags=_optional_text_or_tuple(data.get("output_table_column_flavour_tags")),
        include_context_columns=bool(data.get("include_context_columns", True)),
        headline_series_names=_optional_text_tuple(data.get("headline_series_names")),
        include_figures=bool(data.get("include_figures", False)),
    )


def _effective_render_options(
    render: ScenarioBundleRenderOptions,
    *,
    output_table_names: Sequence[str] | None,
    output_table_column_flavour_tags: str | Sequence[str] | None,
    include_context_columns: bool | None,
    headline_series_names: Sequence[str] | None,
    include_figures: bool | None,
) -> ScenarioBundleRenderOptions:
    return ScenarioBundleRenderOptions(
        output_table_names=tuple(output_table_names) if output_table_names is not None else render.output_table_names,
        output_table_column_flavour_tags=(
            _optional_text_or_tuple(output_table_column_flavour_tags)
            if output_table_column_flavour_tags is not None
            else render.output_table_column_flavour_tags
        ),
        include_context_columns=(
            include_context_columns if include_context_columns is not None else render.include_context_columns
        ),
        headline_series_names=(
            tuple(headline_series_names) if headline_series_names is not None else render.headline_series_names
        ),
        include_figures=include_figures if include_figures is not None else render.include_figures,
    )


def _bundle_to_mapping(bundle: ScenarioBundle, *, render: ScenarioBundleRenderOptions) -> dict[str, Any]:
    return {
        "version": bundle.version,
        "bundle_id": bundle.bundle_id,
        "workbook_version": bundle.workbook_version,
        "description": bundle.description,
        "render": _render_options_to_mapping(render),
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


def _render_options_to_mapping(render: ScenarioBundleRenderOptions) -> dict[str, Any]:
    return {
        "output_table_names": list(render.output_table_names) if render.output_table_names is not None else None,
        "output_table_column_flavour_tags": render.output_table_column_flavour_tags,
        "include_context_columns": render.include_context_columns,
        "headline_series_names": list(render.headline_series_names) if render.headline_series_names is not None else None,
        "include_figures": render.include_figures,
    }


def _write_frames(frames: Mapping[str, Any], root: Path) -> dict[str, Path]:
    root.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, frame in sorted(frames.items()):
        path = root / f"{_safe_filename(name)}.csv"
        frame.to_csv(path)
        paths[name] = path
    return paths


def _write_figures(figures: Mapping[str, Any], root: Path) -> dict[str, Path]:
    if not figures:
        return {}
    root.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, figure in sorted(figures.items()):
        path = root / f"{_safe_filename(name)}.png"
        figure.savefig(path)
        paths[name] = path
    return paths


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a mapping")
    return value


def _optional_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    return _require_mapping(value, label)


def _optional_text(value: Any) -> str | None:
    return None if value is None else str(value)


def _optional_text_tuple(value: Any) -> tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, str):
        raise ValueError("expected a list of strings, not a single string")
    return tuple(str(item) for item in value)


def _optional_text_or_tuple(value: Any) -> str | tuple[str, ...] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return tuple(str(item) for item in value)


def _require_slug(value: str, field_name: str) -> None:
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$", value):
        raise ValueError(f"{field_name} must be a path-safe slug, got {value!r}")


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._") or "artifact"


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
