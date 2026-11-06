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
    title: str = "FABLE Pyculator"

    def __post_init__(self) -> None:
        self.repo_root = Path(self.repo_root).expanduser().resolve()
        self.runtime_dir = (
            Path(self.runtime_dir).expanduser().resolve()
            if self.runtime_dir is not None
            else self.repo_root / "runtime" / "portal"
        )
        self.versions = tuple(dict.fromkeys(str(version) for version in self.versions))


class PortalState:
    """Shared state for artifact summaries, prepared models, saved runs, and jobs."""

    def __init__(self, config: PortalConfig) -> None:
        self.config = config
        self.config.runtime_dir.mkdir(parents=True, exist_ok=True)  # type: ignore[union-attr]
        self.jobs = JobManager()
        self.chats = ChatStore(self.runtime_dir / "chats")
        self._prepared: dict[str, PreparedModel] = {}
        self._compute_lock = threading.RLock()
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
        report: Report | None = None,
    ) -> dict[str, Any]:
        """Run one scenario and persist its summary and table payloads."""

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
            for table_name, frame in result.output_tables.items():
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
                    }
                )

            headline_payloads = {
                series_name: _frame_payload(frame, name=series_name)
                for series_name, frame in result.headline_frames.items()
            }
            headline_summary = _headline_summary(prepared.spec, result.headline_frames)
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

    def list_chats(self) -> list[dict[str, Any]]:
        """Return persistent chat summaries, newest first."""

        return self.chats.list()

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
    }


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
