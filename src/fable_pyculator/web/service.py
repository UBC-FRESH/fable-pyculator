"""Runtime state, preparation, and scenario execution for the FABLE web portal.

The service is deliberately a thin presentation layer over the notebook APIs. Model execution and
workbook discovery happen in background jobs; every response is built from a real run or a real
artifact, never from browser-only state.
"""

from __future__ import annotations

import json
import re
import threading
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from fable_pyculator import __version__
from fable_pyculator.notebook import build_notebook_spec, load_generated_model, run_notebook_loop
from fable_pyculator.web.artifacts import (
    DEFAULT_VERSIONS,
    artifact_paths,
    artifact_summary,
    bundle_summaries,
    file_info,
    materialize_generated_model,
    model_checksum_status,
)
from fable_pyculator.web.assistant import DEFAULT_AGENT_MODEL
from fable_pyculator.web.chats import ChatStore
from fable_pyculator.web.cheatsheet import CheatSheet, ensure_cheat_sheet
from fable_pyculator.web.spec_io import jsonable, spec_from_payload, spec_summary, spec_to_payload

__all__ = [
    "Job",
    "JobManager",
    "PortalConfig",
    "PortalError",
    "PortalState",
    "PreparedModel",
]

JobStatus = Literal["queued", "running", "ok", "error"]
Report = Callable[[int, str], None]
SPEC_CACHE_VERSION = "2026-11-06-ghg-output-components"
NATIVE_LAST_YEAR = 2050
EXTENSION_YEARS = (2055, 2060, 2065, 2070)
EXTENSION_NOTE = (
    "2055-2070 are trend extensions extrapolated from the 2035-2050 linear trend, not native FABLE Calculator results."
)
_PRESET_STATE_KEYS = (
    "version",
    "x",
    "y",
    "z",
    "colour",
    "size",
    "floor_dimension",
    "floor",
    "front",
    "warning_free",
    "brushes",
    "reference",
    "point",
)


def _clean_optimization_preset(
    name: Any,
    state: Any,
    saved_at: Any = None,
    author: Any = None,
    note: Any = None,
    review_status: Any = None,
) -> dict[str, Any]:
    """Validate and normalize one shared Optimization preset."""

    if not isinstance(name, str) or not name.strip():
        raise ValueError("preset name must be a non-empty string")
    if not isinstance(state, Mapping):
        raise ValueError("preset state must be an object")
    clean_name = name.strip()[:40]
    if not clean_name:
        raise ValueError("preset name must be a non-empty string")
    clean_state: dict[str, Any] = {}
    for key in _PRESET_STATE_KEYS:
        if key not in state:
            continue
        value = state[key]
        if key in {"version", "x", "y", "z", "colour", "size", "floor_dimension"}:
            clean_state[key] = str(value)[:60]
        elif key == "floor":
            number = float(value)
            if not 0 <= number <= 100:
                raise ValueError("preset floor must be between 0 and 100")
            clean_state[key] = number
        elif key in {"front", "warning_free"}:
            clean_state[key] = bool(value)
        elif key == "brushes":
            if not isinstance(value, (list, tuple)) or len(value) > 20:
                raise ValueError("preset brushes must be a list of at most 20 entries")
            brushes: list[dict[str, Any]] = []
            for brush in value:
                if not isinstance(brush, Mapping):
                    raise ValueError("each preset brush must be an object")
                axis_key = brush.get("axisKey")
                if not isinstance(axis_key, str) or not axis_key:
                    raise ValueError("each preset brush needs an axisKey")
                start = float(brush.get("start"))
                end = float(brush.get("end"))
                if not 0 <= start <= 1 or not 0 <= end <= 1:
                    raise ValueError("preset brush ranges must be between 0 and 1")
                brushes.append({"axisKey": axis_key[:60], "start": start, "end": end})
            clean_state[key] = brushes
        elif key in {"reference", "point"}:
            clean_state[key] = None if value in (None, "") else str(value)[:20]
    if not clean_state.get("version"):
        raise ValueError("preset state needs a version")
    timestamp = saved_at if isinstance(saved_at, str) and len(saved_at) <= 40 else None
    if timestamp is None:
        timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    clean_author = author.strip()[:40] if isinstance(author, str) else ""
    clean_note = note.strip()[:200] if isinstance(note, str) else ""
    status = str(review_status or "draft").strip().lower()
    if status not in {"draft", "reviewed"}:
        raise ValueError("preset review_status must be draft or reviewed")
    return {
        "name": clean_name,
        "saved_at": timestamp,
        "author": clean_author,
        "note": clean_note,
        "review_status": status,
        "state": clean_state,
    }


class PortalError(RuntimeError):
    """A user-facing portal error with an HTTP status hint."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(slots=True)
class Job:
    """One background preparation or scenario-run job."""

    job_id: str
    kind: str
    status: JobStatus = "queued"
    progress: int = 0
    message: str = "queued"
    result: Any = None
    error: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))
    started_at: str | None = None
    finished_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready snapshot."""

        return {
            "job_id": self.job_id,
            "kind": self.kind,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


class JobManager:
    """Run callables on daemon threads and expose pollable status snapshots."""

    def __init__(self, *, keep: int = 50) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._keep = keep

    def start(self, kind: str, target: Callable[[Report], Any]) -> Job:
        """Start a job and return its initial snapshot."""

        job = Job(job_id=uuid.uuid4().hex[:12], kind=kind)
        with self._lock:
            self._jobs[job.job_id] = job
            self._trim()
        thread = threading.Thread(target=self._run, args=(job, target), name=f"portal-{job.job_id}", daemon=True)
        thread.start()
        return job

    def get(self, job_id: str) -> Job:
        """Return one job or raise a 404 portal error."""

        with self._lock:
            job = self._jobs.get(job_id)
        if job is None:
            raise PortalError(f"unknown job id {job_id!r}", status_code=404)
        return job

    def _run(self, job: Job, target: Callable[[Report], Any]) -> None:
        with self._lock:
            job.status = "running"
            job.started_at = datetime.now(UTC).isoformat(timespec="seconds")

        def report(progress: int, message: str) -> None:
            with self._lock:
                job.progress = max(0, min(100, int(progress)))
                job.message = str(message)

        try:
            result = target(report)
        except Exception as error:  # noqa: BLE001 - represented in the job payload
            with self._lock:
                job.status = "error"
                job.progress = 100
                job.message = "failed"
                job.error = f"{type(error).__name__}: {error}"
                job.finished_at = datetime.now(UTC).isoformat(timespec="seconds")
            return
        with self._lock:
            job.status = "ok"
            job.progress = 100
            job.message = "complete"
            job.result = result
            job.finished_at = datetime.now(UTC).isoformat(timespec="seconds")

    def _trim(self) -> None:
        if len(self._jobs) <= self._keep:
            return
        ordered = sorted(self._jobs.values(), key=lambda item: item.created_at)
        for job in ordered[: len(self._jobs) - self._keep]:
            self._jobs.pop(job.job_id, None)


@dataclass(slots=True)
class PreparedModel:
    """A workbook-derived spec and its matching generated-model module."""

    version: str
    spec: Any
    model: Any
    summary: dict[str, Any]
    prepared_at: str
    report: dict[str, Any]


@dataclass(slots=True)
class PortalConfig:
    """Portal configuration.

    Attributes
    ----------
    repo_root:
        Repository root containing ``examples/`` and ``tmp/``.
    runtime_dir:
        Ignored directory for prepared specs and saved runs.
    versions:
        Workbook versions offered by the portal.
    allow_agent:
        Enable the optional local assistant.
    agent_command:
        Command prefix for the assistant CLI.
    agent_model:
        Optional model identifier passed to the assistant CLI.
    agent_timeout:
        Assistant timeout in seconds.
    title:
        Browser title and header label.
    """

    repo_root: Path = field(default_factory=Path.cwd)
    runtime_dir: Path | None = None
    versions: tuple[str, ...] = DEFAULT_VERSIONS
    allow_agent: bool = False
    agent_command: tuple[str, ...] = ("opencode", "run", "--format", "json", "--auto")
    agent_model: str | None = DEFAULT_AGENT_MODEL
    agent_timeout: float = 600.0
    auth_user: str | None = None
    auth_password: str | None = None
    title: str = "FABLE Pyculator"

    def __post_init__(self) -> None:
        self.repo_root = Path(self.repo_root).expanduser().resolve()
        self.runtime_dir = (
            Path(self.runtime_dir).expanduser().resolve()
            if self.runtime_dir is not None
            else self.repo_root / "runtime" / "portal"
        )
        self.versions = tuple(dict.fromkeys(str(version) for version in self.versions))
        if bool(self.auth_user) != bool(self.auth_password):
            raise ValueError("auth_user and auth_password must be configured together")


class PortalState:
    """Shared state for artifact summaries, prepared models, saved runs, and jobs."""

    def __init__(self, config: PortalConfig) -> None:
        self.config = config
        self.config.runtime_dir.mkdir(parents=True, exist_ok=True)  # type: ignore[union-attr]
        self.jobs = JobManager()
        self.chats = ChatStore(self.runtime_dir / "chats")
        self._prepared: dict[str, PreparedModel] = {}
        self._compute_lock = threading.RLock()
        self._preset_lock = threading.Lock()
        self._cheat_sheet: CheatSheet | None = None
        self.ensure_cheat_sheet()

    @property
    def runtime_dir(self) -> Path:
        """Return the resolved runtime directory."""

        assert self.config.runtime_dir is not None
        return self.config.runtime_dir

    def options(self) -> dict[str, Any]:
        """Return portal-wide options for the browser shell."""

        return {
            "title": self.config.title,
            "repo_root": str(self.config.repo_root),
            "runtime_dir": str(self.runtime_dir),
            "versions": list(self.config.versions),
            "assistant_enabled": self.config.allow_agent,
            "assistant_model": self.config.agent_model,
            "docs_url": "https://ubc-fresh.github.io/fable-pyculator/",
        }

    def artifacts(self) -> list[dict[str, Any]]:
        """Return one artifact summary per configured version."""

        return [
            {
                **artifact_summary(self.config.repo_root, version),
                "prepared": version in self._prepared,
                "summary": self._prepared[version].summary if version in self._prepared else None,
            }
            for version in self.config.versions
        ]

    def artifact(self, version: str) -> dict[str, Any]:
        """Return one artifact summary with its validation state."""

        self._require_version(version)
        summary = artifact_summary(self.config.repo_root, version)
        return {
            **summary,
            "prepared": version in self._prepared,
            "summary": self._prepared[version].summary if version in self._prepared else None,
            "validation": self.validation(version),
        }

    def validation(self, version: str) -> dict[str, Any]:
        """Return compact validation evidence without loading the large stage artifacts."""

        self._require_version(version)
        paths = artifact_paths(self.config.repo_root, version)
        files = {
            "validation_summary": file_info(paths.validation_summary),
            "validation_scenario": file_info(paths.validation_scenario),
            "evaluation_report": file_info(paths.evaluation_report),
            "contract": file_info(paths.contract),
        }
        if paths.validation_summary.exists():
            try:
                payload = json.loads(paths.validation_summary.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                return {
                    "version": version,
                    "available": False,
                    "files": files,
                    "message": f"validation summary could not be read: {error}",
                }
            return {
                "version": version,
                "available": True,
                "files": files,
                "summary": payload,
                "message": "compact validation evidence loaded",
            }
        if paths.validation_scenario.exists():
            try:
                scenario = json.loads(paths.validation_scenario.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                scenario = {}
            return {
                "version": version,
                "available": False,
                "files": files,
                "scenario": {
                    "scenario_id": scenario.get("scenario_id"),
                    "description": scenario.get("description"),
                    "source_workbook": scenario.get("source_workbook"),
                    "generated_model": scenario.get("generated_model"),
                    "output_count": len(scenario.get("outputs", [])),
                }
                if scenario
                else None,
                "message": (
                    "A validation scenario exists, but the compact validation-evidence summary is missing. "
                    "Run the validation-evidence packaging workflow to populate it."
                ),
            }
        return {
            "version": version,
            "available": False,
            "files": files,
            "message": "No validation evidence is available for this version.",
        }

    def status(self, version: str) -> dict[str, Any]:
        """Return in-memory preparation status for one version."""

        self._require_version(version)
        prepared = self._prepared.get(version)
        return {
            "version": version,
            "prepared": prepared is not None,
            "summary": prepared.summary if prepared is not None else None,
            "artifact": artifact_summary(self.config.repo_root, version),
        }

    def prepare_job(self, version: str) -> Job:
        """Start a background preparation job for one version."""

        self._require_version(version)
        return self.jobs.start("prepare", lambda report: self.prepare(version, report))

    def prepare(self, version: str, report: Report) -> dict[str, Any]:
        """Materialize, discover, load, and cache one version.

        The operation is guarded so two analyst tabs do not decompress or build the same model at the
        same time. A valid cache avoids rebuilding the expensive workbook spec after a restart.
        """

        with self._compute_lock:
            prepared = self._prepared.get(version)
            if prepared is not None:
                report(100, "model already prepared")
                return prepared.report

            paths = artifact_paths(self.config.repo_root, version)
            if not paths.workbook.exists():
                raise PortalError(
                    f"source workbook is missing: {paths.workbook}. "
                    "Restore it under the ignored tmp/private-workbooks/ path.",
                    status_code=409,
                )
            if not paths.generated_model.exists():
                if not paths.compressed_model.exists():
                    raise PortalError(
                        f"generated model is missing: {paths.generated_model}",
                        status_code=409,
                    )
                report(5, "decompressing approved generated-model artifact")
                materialize_generated_model(self.config.repo_root, version)

            checksum = model_checksum_status(self.config.repo_root, version)
            if checksum["state"] == "mismatch":
                if not paths.compressed_model.exists():
                    raise PortalError(
                        "working generated model does not match the approved checksum and no "
                        f"compressed archive is available: {paths.generated_model}",
                        status_code=409,
                    )
                report(6, "working model checksum mismatch; re-materializing approved archive")
                materialize_generated_model(self.config.repo_root, version, force=True)
                checksum = model_checksum_status(self.config.repo_root, version)
                if checksum["state"] not in {"verified", "unknown"}:
                    raise PortalError(
                        "approved generated model failed checksum verification after materialization",
                        status_code=409,
                    )

            fingerprint = _fingerprint(paths.workbook, paths.generated_model)
            cache = self._read_spec_cache(version, fingerprint)
            if cache is None:
                report(12, "discovering workbook controls and output tables")
                started = time.perf_counter()
                spec = build_notebook_spec(paths.workbook, workbook_id=version)
                summary = spec_summary(spec)
                duration = round(time.perf_counter() - started, 2)
                report(72, f"workbook spec ready in {duration:g} s")
                self._write_spec_cache(version, fingerprint, spec, summary)
            else:
                spec, summary = cache
                report(55, "loaded cached workbook spec")

            report(78, "loading generated model")
            started = time.perf_counter()
            model = load_generated_model(
                paths.generated_model,
                module_name=f"fable_pyculator_web_generated_fable_{version}",
            )
            load_seconds = round(time.perf_counter() - started, 2)
            report(96, f"generated model loaded in {load_seconds:g} s")

            prepared_at = datetime.now(UTC).isoformat(timespec="seconds")
            payload = {
                "version": version,
                "prepared": True,
                "prepared_at": prepared_at,
                "model_load_seconds": load_seconds,
                "artifact": artifact_summary(self.config.repo_root, version),
                "summary": summary,
            }
            self._prepared[version] = PreparedModel(
                version=version,
                spec=spec,
                model=model,
                summary=summary,
                prepared_at=prepared_at,
                report=payload,
            )
            self._refresh_cheat_sheet()
            report(100, "model prepared")
            return payload

    def spec(self, version: str) -> dict[str, Any]:
        """Return the compact prepared spec, or a 409 when preparation is not done."""

        self._require_version(version)
        prepared = self._prepared.get(version)
        if prepared is None:
            raise PortalError(
                f"model {version} is not prepared; start POST /api/models/{version}/prepare",
                status_code=409,
            )
        return {
            "version": version,
            "prepared_at": prepared.prepared_at,
            "summary": prepared.summary,
        }

    def run_job(
        self,
        *,
        version: str,
        name: str,
        selections: Mapping[str, object],
        output_table_names: Sequence[str] | None = None,
        headline_series_names: Sequence[str] | None = None,
        column_flavour_tags: str | Sequence[str] | None = None,
        include_context_columns: bool = True,
        horizon: int = NATIVE_LAST_YEAR,
    ) -> Job:
        """Start a background scenario run."""

        self._require_version(version)
        return self.jobs.start(
            "run",
            lambda report: self.run_scenario(
                version=version,
                name=name,
                selections=selections,
                output_table_names=output_table_names,
                headline_series_names=headline_series_names,
                column_flavour_tags=column_flavour_tags,
                include_context_columns=include_context_columns,
                horizon=horizon,
                report=report,
            ),
        )

    def run_scenario(
        self,
        *,
        version: str,
        name: str,
        selections: Mapping[str, object],
        output_table_names: Sequence[str] | None = None,
        headline_series_names: Sequence[str] | None = None,
        column_flavour_tags: str | Sequence[str] | None = None,
        include_context_columns: bool = True,
        horizon: int = NATIVE_LAST_YEAR,
        report: Report | None = None,
    ) -> dict[str, Any]:
        """Run one scenario and persist its summary and table payloads."""

        if horizon not in {NATIVE_LAST_YEAR, 2070}:
            raise PortalError("horizon must be 2050 or 2070")
        report = report or (lambda _progress, _message: None)
        with self._compute_lock:
            prepared = self._prepared.get(version)
            if prepared is None:
                report(5, "model is not prepared; preparing it first")
                self.prepare(version, lambda progress, message: report(5 + int(progress * 0.45), message))
                prepared = self._prepared[version]

            scenario_name = (name or "scenario").strip() or "scenario"
            report(55, "running generated model")
            started = time.perf_counter()
            result = run_notebook_loop(
                prepared.model,
                prepared.spec,
                dict(selections),
                scenario_name=scenario_name,
                output_table_names=output_table_names,
                output_table_column_flavour_tags=column_flavour_tags,
                include_context_columns=include_context_columns,
                headline_series_names=headline_series_names,
                include_figures=False,
            )
            duration = round(time.perf_counter() - started, 2)
            report(85, f"generated model run complete in {duration:g} s")

            run_id = _run_id(scenario_name)
            run_dir = self.runtime_dir / "runs" / run_id
            table_dir = run_dir / "tables"
            table_dir.mkdir(parents=True, exist_ok=True)

            table_summaries: list[dict[str, Any]] = []
            table_files: dict[str, str] = {}
            table_frames: dict[str, pd.DataFrame] = {}
            for table_name, frame in result.output_tables.items():
                frame = _repair_known_output_table(version, table_name, frame)
                if horizon == 2070:
                    frame = _extend_frame_to_2070(frame)
                table_frames[table_name] = frame
                payload = _frame_payload(frame, name=table_name)
                slug = _slug(table_name)
                relative = Path("tables") / f"{slug}.json"
                (run_dir / relative).write_text(
                    json.dumps(payload, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
                table_files[table_name] = str(relative)
                table_summaries.append(
                    {
                        "name": table_name,
                        "label": payload.get("label"),
                        "sheet": payload.get("sheet"),
                        "range_ref": payload.get("range_ref"),
                        "row_count": len(payload["rows"]),
                        "column_count": len(payload["columns"]),
                        "file": str(relative),
                        "display_repair": payload.get("display_repair"),
                        "extension_note": payload.get("extension_note"),
                    }
                )

            headline_frames = {
                series_name: (_extend_frame_to_2070(frame) if horizon == 2070 else frame)
                for series_name, frame in result.headline_frames.items()
            }
            headline_payloads = {
                series_name: _frame_payload(frame, name=series_name) for series_name, frame in headline_frames.items()
            }
            headline_summary = _headline_summary(prepared.spec, headline_frames)
            quality_warnings = _quality_warnings(
                version=version,
                spec=prepared.spec,
                horizon=horizon,
                headline_frames=headline_frames,
                table_frames=table_frames,
                table_summaries=table_summaries,
            )
            paths = artifact_paths(self.config.repo_root, version)
            provenance = {
                "portal_version": __version__,
                "repo_root": str(self.config.repo_root),
                "prepared_at": prepared.prepared_at,
                "workbook_id": prepared.spec.workbook_id,
                "workbook": file_info(paths.workbook),
                "generated_model": file_info(paths.generated_model),
                "spec_provenance": prepared.spec.provenance,
                "run_started_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            record = {
                "run_id": run_id,
                "version": version,
                "name": scenario_name,
                "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "status": "ok",
                "duration_seconds": duration,
                "horizon": horizon,
                "extension": (
                    {
                        "enabled": horizon == 2070,
                        "method": "linear_trend_2035_2050",
                        "native_last_year": NATIVE_LAST_YEAR,
                        "note": EXTENSION_NOTE,
                    }
                    if horizon == 2070
                    else None
                ),
                "quality_warnings": quality_warnings,
                "selections": jsonable(dict(selections)),
                "input_count": len(result.run.inputs),
                "inputs": jsonable(result.run.inputs),
                "headline_summary": headline_summary,
                "headline_series": headline_payloads,
                "table_summaries": sorted(table_summaries, key=lambda item: item["name"]),
                "table_files": table_files,
                "skipped_output_tables": jsonable(result.skipped_output_tables),
                "provenance": provenance,
                "spec": {
                    "workbook_id": prepared.spec.workbook_id,
                    "provenance": prepared.spec.provenance,
                },
            }
            (run_dir / "run.json").write_text(
                json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._refresh_cheat_sheet()
            report(100, "scenario saved")
            return record

    def bundles(self) -> list[dict[str, Any]]:
        """Return tracked scenario-bundle examples."""

        return bundle_summaries(self.config.repo_root)

    def optimization_frontiers(self) -> list[dict[str, Any]]:
        """Return summaries of tracked exact frontier artifacts."""

        directory = self.config.repo_root / "examples" / "optimization"
        if not directory.is_dir():
            return []
        records: list[dict[str, Any]] = []
        for path in sorted(directory.glob("*/frontier.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue
            points = payload.get("points") or []
            origins: dict[str, int] = {}
            for point in points if isinstance(points, list) else []:
                if isinstance(point, dict):
                    origin = str(point.get("origin") or "Other")
                    origins[origin] = origins.get(origin, 0) + 1
            records.append(
                {
                    "version": str(payload.get("version") or path.parent.name.removeprefix("fable_")),
                    "title": str(payload.get("title") or "Exact decision frontier"),
                    "point_count": len(points) if isinstance(points, list) else 0,
                    "pareto_count": len(payload.get("pareto_ids") or []),
                    "generated_at": payload.get("generated_at"),
                    "boundary": payload.get("boundary"),
                    "origins": origins,
                }
            )
        return sorted(records, key=lambda item: item["version"])

    def optimization_frontier(self, version: str) -> dict[str, Any]:
        """Return one tracked exact frontier artifact for the browser."""

        directory = self.config.repo_root / "examples" / "optimization"
        for path in sorted(directory.glob("*/frontier.json")) if directory.is_dir() else []:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(payload, dict):
                continue
            if str(payload.get("version")) == str(version):
                return payload
        raise PortalError(f"unknown optimization frontier {version!r}", status_code=404)

    def optimization_presets(self) -> list[dict[str, Any]]:
        """Return the shared Optimization preset library."""

        with self._preset_lock:
            return self._load_shared_presets()

    def save_optimization_preset(
        self,
        name: str,
        state: Mapping[str, Any],
        saved_at: str | None = None,
        *,
        author: str | None = None,
        note: str | None = None,
        review_status: str | None = None,
    ) -> dict[str, Any]:
        """Create or replace one shared Optimization preset."""

        preset = _clean_optimization_preset(
            name,
            state,
            saved_at,
            author=author,
            note=note,
            review_status=review_status,
        )
        with self._preset_lock:
            presets = [item for item in self._load_shared_presets() if item["name"] != preset["name"]]
            presets.insert(0, preset)
            self._write_shared_presets(presets[:20])
        return preset

    def delete_optimization_preset(self, name: str) -> dict[str, Any]:
        """Delete one shared Optimization preset by name."""

        with self._preset_lock:
            presets = self._load_shared_presets()
            remaining = [item for item in presets if item["name"] != name]
            if len(remaining) == len(presets):
                raise PortalError(f"unknown optimization preset {name!r}", status_code=404)
            self._write_shared_presets(remaining)
        return {"deleted": name, "count": len(remaining)}

    def _load_shared_presets(self) -> list[dict[str, Any]]:
        path = self.runtime_dir / "optimization-presets.json"
        if not path.is_file():
            return []
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(payload, list):
            return []
        presets: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, Mapping):
                continue
            try:
                presets.append(
                    _clean_optimization_preset(
                        item.get("name"),
                        item.get("state"),
                        item.get("saved_at"),
                        author=item.get("author"),
                        note=item.get("note"),
                        review_status=item.get("review_status"),
                    )
                )
            except ValueError:
                continue
        return presets[:20]

    def _write_shared_presets(self, presets: list[dict[str, Any]]) -> None:
        path = self.runtime_dir / "optimization-presets.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
        temporary.write_text(json.dumps(presets, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)

    def runs(self) -> list[dict[str, Any]]:
        """Return saved runs, newest first, without loading table files."""

        directory = self.runtime_dir / "runs"
        records: list[dict[str, Any]] = []
        if not directory.is_dir():
            return records
        for path in directory.glob("*/run.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            record = dict(payload)
            record.pop("inputs", None)
            record.pop("headline_series", None)
            records.append(record)
        return sorted(records, key=lambda item: str(item.get("created_at", "")), reverse=True)

    def run(self, run_id: str) -> dict[str, Any]:
        """Return one saved run."""

        path = self._run_path(run_id)
        if not path.exists():
            raise PortalError(f"unknown run id {run_id!r}", status_code=404)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PortalError(f"run {run_id!r} could not be read: {error}", status_code=500) from error

    def table(self, run_id: str, table_name: str) -> dict[str, Any]:
        """Return one saved table payload."""

        record = self.run(run_id)
        relative = record.get("table_files", {}).get(table_name)
        if not relative:
            raise PortalError(f"unknown table {table_name!r} for run {run_id!r}", status_code=404)
        path = (self._run_path(run_id).parent / str(relative)).resolve()
        if not path.is_relative_to(self._run_path(run_id).parent.resolve()):
            raise PortalError("table path escapes the run directory", status_code=400)
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise PortalError(f"table {table_name!r} could not be read: {error}", status_code=500) from error

    def compare(self, run_ids: Sequence[str]) -> dict[str, Any]:
        """Compare two or more saved runs by headline series and selected inputs."""

        unique = list(dict.fromkeys(str(run_id) for run_id in run_ids))
        if len(unique) < 2:
            raise PortalError("select at least two runs to compare")
        records = [self.run(run_id) for run_id in unique]
        series: dict[str, dict[str, Any]] = {}
        years: set[Any] = set()
        for record in records:
            for name, payload in record.get("headline_series", {}).items():
                entry = series.setdefault(
                    name,
                    {
                        "name": name,
                        "label": payload.get("label") or name,
                        "unit": payload.get("unit"),
                        "group": payload.get("group"),
                        "series": {},
                    },
                )
                mapping = {
                    row.get("year"): row.get("value") for row in payload.get("rows", []) if isinstance(row, dict)
                }
                entry["series"][record["run_id"]] = mapping
                years.update(mapping)
        for entry in series.values():
            entry["years"] = sorted(years, key=_year_key)
            entry["values"] = {
                record["run_id"]: [entry["series"][record["run_id"]].get(year) for year in entry["years"]]
                for record in records
            }
            entry.pop("series", None)
        return {
            "runs": [
                {
                    "run_id": record["run_id"],
                    "name": record.get("name"),
                    "version": record.get("version"),
                    "created_at": record.get("created_at"),
                    "selections": record.get("selections", {}),
                    "headline_summary": record.get("headline_summary", []),
                }
                for record in records
            ],
            "series": sorted(series.values(), key=lambda item: item["name"]),
        }

    def assistant_context(self, run_id: str | None) -> dict[str, Any]:
        """Build a compact context object for the optional local assistant."""

        cheat_sheet = self._cheat_sheet or self.ensure_cheat_sheet()
        context: dict[str, Any] = {
            "versions": [artifact["version"] for artifact in self.artifacts()],
            "cheat_sheet_path": str(cheat_sheet.path),
            "cheat_sheet_generated_at": cheat_sheet.generated_at,
        }
        if run_id:
            try:
                record = self.run(run_id)
            except PortalError:
                return context
            context["run"] = {
                key: record.get(key)
                for key in ("run_id", "name", "version", "created_at", "selections", "headline_summary")
            }
        return context

    def ensure_cheat_sheet(self) -> CheatSheet:
        """Regenerate the compiled assistant grounding sheet from current portal state."""

        cheat_sheet = ensure_cheat_sheet(
            repo_root=self.config.repo_root,
            runtime_dir=self.runtime_dir,
            artifacts=self.artifacts(),
            prepared_summaries={version: prepared.summary for version, prepared in self._prepared.items()},
            runs=self.runs(),
        )
        self._cheat_sheet = cheat_sheet
        return cheat_sheet

    def _refresh_cheat_sheet(self) -> None:
        """Best-effort refresh after preparation or a saved run."""

        try:
            self.ensure_cheat_sheet()
        except Exception:  # noqa: BLE001 - auxiliary cache must not fail model jobs
            # The grounding sheet is auxiliary; never fail a model job because its cache write failed.
            return

    def create_chat(self, *, run_id: str | None = None) -> dict[str, Any]:
        """Create a persistent assistant chat."""

        return self.chats.create(run_id=run_id).to_dict()

    def list_chats(
        self,
        *,
        include_archived: bool = False,
        query: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return persistent chat summaries, pinned first and newest first."""

        return self.chats.list(include_archived=include_archived, query=query)

    def update_chat(
        self,
        chat_id: str,
        *,
        title: str | None = None,
        pinned: bool | None = None,
        archived: bool | None = None,
    ) -> dict[str, Any]:
        """Update chat title, pin, or archive state."""

        try:
            return self.chats.set_metadata(
                chat_id,
                title=title,
                pinned=pinned,
                archived=archived,
            ).to_dict()
        except KeyError as error:
            raise PortalError(f"unknown chat id {chat_id!r}", status_code=404) from error

    def export_chat(self, chat_id: str) -> str:
        """Return a Markdown export of one chat."""

        try:
            return self.chats.get(chat_id).to_markdown()
        except KeyError as error:
            raise PortalError(f"unknown chat id {chat_id!r}", status_code=404) from error

    def get_chat(self, chat_id: str) -> dict[str, Any]:
        """Return one persistent chat."""

        try:
            return self.chats.get(chat_id).to_dict()
        except KeyError as error:
            raise PortalError(f"unknown chat id {chat_id!r}", status_code=404) from error

    def delete_chat(self, chat_id: str) -> dict[str, Any]:
        """Delete one persistent chat."""

        try:
            deleted = self.chats.delete(chat_id)
        except KeyError as error:
            raise PortalError(f"invalid chat id {chat_id!r}", status_code=400) from error
        if not deleted:
            raise PortalError(f"unknown chat id {chat_id!r}", status_code=404)
        return {"chat_id": chat_id, "deleted": True}

    def _require_version(self, version: str) -> None:
        if version not in self.config.versions:
            raise PortalError(f"unknown workbook version {version!r}", status_code=404)

    def _run_path(self, run_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9._-]+", run_id):
            raise PortalError("invalid run id", status_code=400)
        return self.runtime_dir / "runs" / run_id / "run.json"

    def _cache_path(self, version: str) -> Path:
        return self.runtime_dir / "specs" / f"fable-{version}.json"

    def _read_spec_cache(
        self,
        version: str,
        fingerprint: dict[str, Any],
    ) -> tuple[Any, dict[str, Any]] | None:
        path = self._cache_path(version)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload.get("cache_version") != SPEC_CACHE_VERSION:
                return None
            if payload.get("fingerprint") != fingerprint:
                return None
            spec = spec_from_payload(payload["spec"])
            summary = payload["summary"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return None
        return spec, summary

    def _write_spec_cache(
        self,
        version: str,
        fingerprint: dict[str, Any],
        spec: Any,
        summary: dict[str, Any],
    ) -> None:
        path = self._cache_path(version)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": version,
            "cache_version": SPEC_CACHE_VERSION,
            "fingerprint": fingerprint,
            "summary": summary,
            "spec": spec_to_payload(spec),
        }
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8")
        temporary.replace(path)


def _fingerprint(workbook: Path, model: Path) -> dict[str, Any]:
    def stat(path: Path) -> dict[str, Any]:
        info = path.stat()
        return {"size_bytes": info.st_size, "modified_ns": info.st_mtime_ns}

    return {"workbook": stat(workbook), "model": stat(model)}


def _frame_payload(frame: pd.DataFrame, *, name: str) -> dict[str, Any]:
    attrs = frame.attrs
    rows = [
        {str(column): jsonable(value) for column, value in zip(frame.columns, row, strict=False)}
        for row in frame.itertuples(index=False, name=None)
    ]
    return {
        "name": name,
        "label": attrs.get("label"),
        "description": attrs.get("description"),
        "sheet": attrs.get("sheet"),
        "range_ref": attrs.get("range_ref"),
        "columns": [str(column) for column in frame.columns],
        "index": [jsonable(value) for value in frame.index],
        "rows": rows,
        "selected_column_flavour_tags": jsonable(attrs.get("selected_column_flavour_tags")),
        "matched_column_flavour_tags": jsonable(attrs.get("matched_column_flavour_tags")),
        "column_flavour_tags": jsonable(attrs.get("column_flavour_tags")),
        "display_repair": attrs.get("display_repair"),
        "extension_note": attrs.get("extension_note"),
    }


def _repair_known_output_table(
    version: str,
    table_name: str,
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Repair known broken display values without changing generated-model semantics.

    The 2024 generated model still contains the pre-repair ``LAND!AA`` ``#REF!`` expressions. Until
    that artifact is regenerated, the portal replaces only the displayed LAND TOTAL column with the
    workbook's ``TotallandFin`` component sum and records the repair in ``DataFrame.attrs``.
    """

    if version != "2024" or table_name != "land_resultsland":
        return frame
    components = ("Cropland", "Pasture", "Urban", "ForPlantations", "OtherForest", "OtherLand")
    if "TOTAL" not in frame.columns or not all(component in frame.columns for component in components):
        return frame
    total = frame["TOTAL"]
    if not any(isinstance(value, str) and "#REF!" in value for value in total):
        return frame
    repaired = frame.copy()
    numeric = repaired.loc[:, list(components)].apply(pd.to_numeric, errors="coerce")
    repaired["TOTAL"] = numeric.sum(axis=1, min_count=len(components))
    repaired.attrs.update(frame.attrs)
    repaired.attrs["display_repair"] = (
        "The generated model's LAND TOTAL column is #REF!; this table displays the workbook's "
        "TotallandFin component sum instead (LoggedForest is represented inside OtherForest and is "
        "not added separately)."
    )
    return repaired


def _quality_warnings(
    *,
    version: str,
    spec: Any,
    horizon: int,
    headline_frames: Mapping[str, pd.DataFrame],
    table_frames: Mapping[str, pd.DataFrame],
    table_summaries: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return run-scoped data-quality notes for the Results panel."""

    warnings: list[dict[str, Any]] = []
    if horizon == 2070:
        warnings.append(
            {
                "code": "trend_extension_2070",
                "severity": "warn",
                "title": "2070 values are trend extensions",
                "message": EXTENSION_NOTE,
                "scope": "headline series and extended output tables",
            }
        )
    land = next((series for series in spec.headline_series if series.name == "land_total_area"), None)
    if land is not None and (
        "component sum" in (land.label or "").casefold() or "totallandfin" in (land.description or "").casefold()
    ):
        warnings.append(
            {
                "code": "land_component_sum",
                "severity": "info",
                "title": "Land total uses a component sum",
                "message": (
                    "The workbook's ResultsLand[TOTAL] total is not usable as-is. The land series "
                    "reproduces calc_land_cor[TotallandFin] from the component columns and records "
                    "the source caveat in its description."
                ),
                "scope": "land_total_area",
            }
        )
    if version == "2024" and not any(series.name == "water_total_footprint" for series in spec.headline_series):
        warnings.append(
            {
                "code": "water_unavailable_2024",
                "severity": "info",
                "title": "Water-footprint series is unavailable",
                "message": (
                    "The 2024 Canada workbook has no TotalResultsWF table, so no water-footprint "
                    "headline series is exposed."
                ),
                "scope": "WATER",
            }
        )
    mismatch = _ghg_cached_mismatch(headline_frames, table_frames, spec=spec)
    if mismatch is not None:
        years, maximum, max_year = mismatch
        warnings.append(
            {
                "code": "ghg_cached_mismatch",
                "severity": "warn",
                "title": "GHG components differ from cached workbook totals",
                "message": (
                    f"The derived GHG series differs from cached ResultsGHG[TotalCO2e] at "
                    f"{len(years)} native year(s); the largest difference is {maximum:.3g} MtCO2e "
                    f"in {max_year}. Cached values may reflect a different scenario/GWP, or an "
                    "individual generated-model component may differ."
                ),
                "scope": "ghg_total_co2e vs cached TotalCO2e",
            }
        )
    skipped = [
        str(summary.get("label") or summary.get("name"))
        for summary in table_summaries
        if "not applied" in str(summary.get("extension_note") or "").casefold()
    ]
    if skipped:
        warnings.append(
            {
                "code": "tables_not_extended",
                "severity": "info",
                "title": "Some tables were not extended to 2070",
                "message": (
                    "These tables have no usable identity/trend grouping and remain at native 2050: "
                    + ", ".join(skipped)
                ),
                "scope": "output tables",
            }
        )
    return warnings


def _cached_ghg_from_spec(spec: Any | None) -> dict[int, float]:
    if spec is None:
        return {}
    tables = getattr(spec, "output_tables", ())
    table = next((item for item in tables if item.name == "ghg_resultsghg"), None)
    if table is None or not table.values:
        return {}
    labels = [str(label).casefold() for label in table.column_labels]
    try:
        year_index = labels.index("year")
        total_index = labels.index("totalco2e")
    except ValueError:
        return {}
    cached: dict[int, float] = {}
    for row in table.values:
        if len(row) <= max(year_index, total_index):
            continue
        year = _coerce_year(row[year_index])
        value = row[total_index]
        if year is not None and isinstance(value, int | float) and not isinstance(value, bool):
            cached[year] = float(value)
    return cached


def _ghg_cached_mismatch(
    headline_frames: Mapping[str, pd.DataFrame],
    table_frames: Mapping[str, pd.DataFrame],
    *,
    spec: Any | None = None,
) -> tuple[list[int], float, int] | None:
    headline = headline_frames.get("ghg_total_co2e")
    if headline is None:
        return None
    cached = _cached_ghg_from_spec(spec)
    if not cached:
        table = table_frames.get("ghg_resultsghg")
        if table is None or table.empty:
            return None
        year_column = next((column for column in table.columns if str(column).casefold() == "year"), None)
        if year_column is None or "TotalCO2e" not in table.columns:
            return None
        for _, row in table.iterrows():
            year = _coerce_year(row.get(year_column))
            value = row.get("TotalCO2e")
            if year is not None and isinstance(value, int | float) and not isinstance(value, bool):
                cached[year] = float(value)
    mismatches: list[tuple[int, float]] = []
    for _, row in headline.iterrows():
        year = _coerce_year(row.get("year"))
        value = row.get("value")
        if (
            year is None
            or year > NATIVE_LAST_YEAR
            or year not in cached
            or not isinstance(value, int | float)
            or isinstance(value, bool)
        ):
            continue
        difference = abs(float(value) - cached[year])
        tolerance = max(1e-6, abs(cached[year]) * 1e-6)
        if difference > tolerance:
            mismatches.append((year, difference))
    if not mismatches:
        return None
    max_year, maximum = max(mismatches, key=lambda item: item[1])
    return [year for year, _ in mismatches], maximum, max_year


def _extend_frame_to_2070(frame: pd.DataFrame) -> pd.DataFrame:
    """Extend a year-indexed or year-column table using the 2035-2050 linear trend."""

    if frame.empty:
        return frame
    copied = frame.copy()
    copied.attrs.update(frame.attrs)
    year_column = next(
        (column for column in copied.columns if str(column).casefold() == "year"),
        None,
    )
    if year_column is not None:
        extended = _extend_year_rows(copied, year_column)
        if extended is not None:
            extended.attrs.update(copied.attrs)
            extended.attrs["extension_note"] = EXTENSION_NOTE
            return extended
        copied.attrs["extension_note"] = (
            "This table has multiple rows per year; 2055-2070 trend extension was not applied."
        )
        return copied
    if _extend_year_columns(copied):
        copied.attrs["extension_note"] = EXTENSION_NOTE
        return copied
    return frame


def _extend_year_rows(frame: pd.DataFrame, year_column: Any) -> pd.DataFrame | None:
    years = [_coerce_year(value) for value in frame[year_column]]
    numeric_years = [year for year in years if year is not None]
    if not numeric_years:
        return None
    native_max = max(numeric_years)
    targets = [year for year in EXTENSION_YEARS if year > native_max]
    if not targets:
        return None
    if len(set(numeric_years)) == len(numeric_years):
        return _extend_series_rows(frame, year_column, years, native_max, targets)
    return _extend_grouped_rows(frame, year_column, native_max, targets)


def _extend_series_rows(
    frame: pd.DataFrame,
    year_column: Any,
    years: list[int | None],
    native_max: int,
    targets: list[int],
) -> pd.DataFrame:
    """Extend a frame where each row is one year."""

    trend_floor = max(2035, native_max - 15)
    last_index = frame.index[max(range(len(years)), key=lambda index: years[index] or -1)]
    appended: list[dict[Any, Any]] = []
    for target in targets:
        row: dict[Any, Any] = {}
        for column in frame.columns:
            if column == year_column:
                row[column] = target
                continue
            if column == "cell_refs":
                row[column] = ()
                continue
            if column == "description":
                row[column] = "Trend extension (non-native)"
                continue
            values = [
                (year, value)
                for year, value in zip(years, frame[column], strict=False)
                if year is not None and trend_floor <= year <= native_max
            ]
            projected = _trend_value(values, target)
            row[column] = projected if projected is not None else frame.loc[last_index, column]
        appended.append(row)
    new = pd.DataFrame(appended, index=targets)
    extended = pd.concat([frame, new])
    extended.attrs.update(frame.attrs)
    return extended


def _extend_grouped_rows(
    frame: pd.DataFrame,
    year_column: Any,
    native_max: int,
    targets: list[int],
) -> pd.DataFrame | None:
    """Extend a multi-row-per-year frame by grouping on its text identity columns."""

    group_columns = [
        column
        for column in frame.columns
        if column != year_column
        and (pd.api.types.is_object_dtype(frame[column]) or pd.api.types.is_string_dtype(frame[column]))
    ]
    if not group_columns:
        return None
    trend_floor = max(2035, native_max - 15)
    appended: list[dict[Any, Any]] = []
    extended_groups = 0
    for _, group in frame.groupby(group_columns, dropna=False, sort=False):
        years = [_coerce_year(value) for value in group[year_column]]
        numeric_years = [year for year in years if year is not None]
        trend_years = [year for year in numeric_years if trend_floor <= year <= native_max]
        if len(trend_years) < 2 or len(set(numeric_years)) != len(numeric_years):
            continue
        last_index = group.index[max(range(len(years)), key=lambda index: years[index] or -1)]
        for target in targets:
            row: dict[Any, Any] = {}
            for column in frame.columns:
                if column == year_column:
                    row[column] = target
                elif column == "cell_refs":
                    row[column] = ()
                elif column == "description":
                    row[column] = "Trend extension (non-native)"
                else:
                    values = [
                        (year, value)
                        for year, value in zip(years, group[column], strict=False)
                        if year is not None and trend_floor <= year <= native_max
                    ]
                    projected = _trend_value(values, target)
                    row[column] = projected if projected is not None else group.loc[last_index, column]
            appended.append(row)
        extended_groups += 1
    if not appended:
        return None
    new = pd.DataFrame(appended, index=[target for _ in range(extended_groups) for target in targets])
    extended = pd.concat([frame, new])
    extended.attrs.update(frame.attrs)
    return extended


def _extend_year_columns(frame: pd.DataFrame) -> bool:
    year_columns: list[tuple[Any, int]] = []
    for column in frame.columns:
        text = str(column)
        if text.isdigit() and 2000 <= int(text) <= 2100:
            year_columns.append((column, int(text)))
    if len(year_columns) < 2:
        return False
    native_max = max(year for _, year in year_columns)
    targets = [year for year in EXTENSION_YEARS if year > native_max]
    if not targets:
        return False
    trend_floor = max(2035, native_max - 15)
    style = type(year_columns[0][0])
    for target in targets:
        frame[style(target)] = [
            _trend_value(
                [
                    (year, row[column])
                    for column, year in year_columns
                    if year is not None and trend_floor <= year <= native_max
                ],
                target,
            )
            for _, row in frame.iterrows()
        ]
    return True


def _trend_value(points: Sequence[tuple[int, Any]], target: int) -> float | None:
    usable = [
        (float(year), float(value))
        for year, value in points
        if isinstance(value, int | float) and not isinstance(value, bool)
    ]
    if not usable:
        return None
    if len(usable) == 1:
        return usable[0][1]
    count = len(usable)
    sum_x = sum(year for year, _ in usable)
    sum_y = sum(value for _, value in usable)
    sum_xy = sum(year * value for year, value in usable)
    sum_xx = sum(year * year for year, _ in usable)
    denominator = count * sum_xx - sum_x * sum_x
    if denominator == 0:
        return usable[-1][1]
    slope = (count * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / count
    return intercept + slope * target


def _coerce_year(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return int(value)
    text = str(value).strip()
    return int(text) if text.isdigit() else None


def _headline_summary(spec: Any, frames: Mapping[str, pd.DataFrame]) -> list[dict[str, Any]]:
    series_by_name = {series.name: series for series in spec.headline_series}
    summary: list[dict[str, Any]] = []
    for name, frame in frames.items():
        if "year" not in frame.columns or "value" not in frame.columns:
            continue
        points = [
            {"year": jsonable(row["year"]), "value": jsonable(row["value"])}
            for _, row in frame.iterrows()
            if row.get("value") is not None
        ]
        if not points:
            continue
        first = points[0]
        last = points[-1]
        first_value = first["value"]
        last_value = last["value"]
        delta = None
        percent_change = None
        if isinstance(first_value, int | float) and isinstance(last_value, int | float):
            delta = last_value - first_value
            if first_value not in (0, None):
                percent_change = (delta / abs(first_value)) * 100
        series = series_by_name.get(name)
        summary.append(
            {
                "name": name,
                "label": series.label if series else name,
                "group": series.group if series else None,
                "unit": series.unit if series else None,
                "first_year": first["year"],
                "first_value": first_value,
                "last_year": last["year"],
                "last_value": last_value,
                "delta": jsonable(delta),
                "percent_change": jsonable(percent_change),
                "point_count": len(points),
            }
        )
    return sorted(summary, key=lambda item: item["name"])


def _run_id(name: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{_slug(name)}-{uuid.uuid4().hex[:4]}"


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value)).strip("-").lower()
    return slug or "item"


def _year_key(value: Any) -> tuple[int, Any]:
    try:
        return (0, int(value))
    except (TypeError, ValueError):
        return (1, str(value))
