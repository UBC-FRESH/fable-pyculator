"""Artifact discovery for the FABLE Pyculator web portal.

The portal is a presentation layer over the same ignored local artifacts the notebook helpers use.
This module names each artifact path, reports whether it exists, and materializes the approved
compressed generated-model artifact when a local working copy is missing.
"""

from __future__ import annotations

import json
import lzma
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

__all__ = [
    "DEFAULT_VERSIONS",
    "ArtifactPaths",
    "artifact_paths",
    "artifact_summary",
    "bundle_summaries",
    "file_info",
    "materialize_generated_model",
]

DEFAULT_VERSIONS: tuple[str, ...] = ("2021", "2024", "2020")


@dataclass(frozen=True)
class ArtifactPaths:
    """Every local path the portal may read for one FABLE workbook version."""

    version: str
    workbook: Path
    generated_model: Path
    compressed_model: Path
    contract: Path
    inference_result: Path
    validation_scenario: Path
    evaluation_report: Path
    generated_values: Path
    validation_summary: Path
    output_dir: Path

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-ready path map."""

        return {
            "version": self.version,
            "workbook": str(self.workbook),
            "generated_model": str(self.generated_model),
            "compressed_model": str(self.compressed_model),
            "contract": str(self.contract),
            "inference_result": str(self.inference_result),
            "validation_scenario": str(self.validation_scenario),
            "evaluation_report": str(self.evaluation_report),
            "generated_values": str(self.generated_values),
            "validation_summary": str(self.validation_summary),
            "output_dir": str(self.output_dir),
        }


def artifact_paths(repo_root: str | Path, version: str) -> ArtifactPaths:
    """Return the conventional artifact paths for one workbook version.

    Paths follow the tracked artifact and ignored local-artifact conventions documented in
    ``examples/fable_<version>/README.md`` and ``docs/guides/generated-model-artifacts.rst``.
    """

    root = Path(repo_root).expanduser().resolve()
    version = str(version)
    artifact_dir = root / "tmp" / "generated-models" / f"fable-{version}"
    return ArtifactPaths(
        version=version,
        workbook=root / "tmp" / "private-workbooks" / f"{version}_Open_FABLECalculator.xlsx",
        generated_model=artifact_dir / f"generated_fable_{version}_model.py",
        compressed_model=root / "examples" / f"fable_{version}" / f"generated_fable_{version}_model.py.xz",
        contract=artifact_dir / "contract.json",
        inference_result=artifact_dir / "inference-result.json",
        validation_scenario=artifact_dir / "validation-scenario.json",
        evaluation_report=artifact_dir / "evaluation-report.json",
        generated_values=artifact_dir / "generated-values.json",
        validation_summary=root / "tmp" / "validation-evidence" / f"fable-{version}" / "summary.json",
        output_dir=artifact_dir,
    )


def file_info(path: Path) -> dict[str, Any]:
    """Return compact existence, size, and modification metadata for a path."""

    try:
        stat = path.stat()
    except OSError:
        return {"path": str(path), "exists": False, "size_bytes": None, "modified_at": None}
    modified = datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(timespec="seconds")
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_at": modified,
    }


def artifact_summary(repo_root: str | Path, version: str) -> dict[str, Any]:
    """Summarize whether a version can be prepared, validated, or run.

    A version is *preparable* when the source workbook and either a decompressed or approved
    compressed generated model are present. Nothing is guessed: every missing file is named.
    """

    paths = artifact_paths(repo_root, version)
    files = {
        "workbook": file_info(paths.workbook),
        "generated_model": file_info(paths.generated_model),
        "compressed_model": file_info(paths.compressed_model),
        "contract": file_info(paths.contract),
        "inference_result": file_info(paths.inference_result),
        "validation_scenario": file_info(paths.validation_scenario),
        "evaluation_report": file_info(paths.evaluation_report),
        "generated_values": file_info(paths.generated_values),
        "validation_summary": file_info(paths.validation_summary),
    }
    missing = [name for name, info in files.items() if not info["exists"]]
    has_model = files["generated_model"]["exists"] or files["compressed_model"]["exists"]
    can_prepare = files["workbook"]["exists"] and has_model
    can_run = can_prepare
    return {
        "version": version,
        "paths": paths.to_dict(),
        "files": files,
        "missing": missing,
        "can_prepare": can_prepare,
        "can_run": can_run,
        "model_source": (
            "decompressed"
            if files["generated_model"]["exists"]
            else "compressed"
            if files["compressed_model"]["exists"]
            else None
        ),
        "has_validation_evidence": files["validation_summary"]["exists"],
    }


def materialize_generated_model(
    repo_root: str | Path,
    version: str,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Decompress the approved generated-model archive into the ignored working path.

    The operation is atomic: the archive is streamed to a sibling temporary file and then replaced.
    It never overwrites an existing working model unless ``force`` is true.
    """

    paths = artifact_paths(repo_root, version)
    if paths.generated_model.exists() and not force:
        return {
            "version": version,
            "materialized": False,
            "reason": "generated model already exists",
            "path": str(paths.generated_model),
            "size_bytes": paths.generated_model.stat().st_size,
        }
    if not paths.compressed_model.exists():
        raise FileNotFoundError(f"compressed generated model not found: {paths.compressed_model}")

    paths.generated_model.parent.mkdir(parents=True, exist_ok=True)
    temporary = paths.generated_model.with_name(paths.generated_model.name + ".tmp")
    try:
        with lzma.open(paths.compressed_model, "rb") as source, temporary.open("wb") as target:
            while chunk := source.read(1024 * 1024):
                target.write(chunk)
        os.replace(temporary, paths.generated_model)
    finally:
        temporary.unlink(missing_ok=True)
    return {
        "version": version,
        "materialized": True,
        "path": str(paths.generated_model),
        "size_bytes": paths.generated_model.stat().st_size,
    }


def bundle_summaries(repo_root: str | Path) -> list[dict[str, Any]]:
    """Return the tracked scenario-bundle examples as compact summaries.

    Bad or partially written bundles are reported with an ``error`` field rather than being hidden.
    """

    root = Path(repo_root).expanduser().resolve()
    directory = root / "examples" / "scenario-bundles"
    if not directory.is_dir():
        return []
    summaries: list[dict[str, Any]] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.casefold() not in {".json", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
            payload = json.loads(text) if path.suffix.casefold() == ".json" else yaml.safe_load(text)
            if not isinstance(payload, dict):
                raise ValueError("bundle must be a mapping")
            scenarios = payload.get("scenarios", [])
            summaries.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "bundle_id": payload.get("bundle_id"),
                    "workbook_version": str(payload.get("workbook_version", "")),
                    "description": payload.get("description"),
                    "scenario_count": len(scenarios) if isinstance(scenarios, list) else 0,
                    "scenarios": [
                        {
                            "scenario_id": scenario.get("scenario_id"),
                            "label": scenario.get("label"),
                        }
                        for scenario in scenarios
                        if isinstance(scenario, dict)
                    ],
                }
            )
        except (OSError, ValueError, yaml.YAMLError) as error:  # type: ignore[attr-defined]
            summaries.append({"name": path.name, "path": str(path), "error": str(error)})
    return summaries
