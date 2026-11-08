"""FastAPI application factory for the optional FABLE Pyculator portal.

Import this module only when the optional ``fable-pyculator[web]`` extra is installed. The core
notebook package does not depend on FastAPI.
"""

from __future__ import annotations

import base64
import secrets
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from fable_pyculator import __version__
from fable_pyculator.web.artifacts import materialize_generated_model
from fable_pyculator.web.assistant import AgentError, AgentRequest, agent_info, run_agent
from fable_pyculator.web.chats import auto_title
from fable_pyculator.web.service import PortalConfig, PortalError, PortalState

__all__ = ["create_app", "is_loopback", "run_server", "validate_bind"]

_STATIC_DIR = Path(__file__).resolve().parent / "static"


class ScenarioRequest(BaseModel):
    """One browser scenario-run request."""

    version: str
    name: str = Field(default="scenario", min_length=1, max_length=120)
    selections: dict[str, Any] = Field(default_factory=dict)
    output_table_names: list[str] | None = None
    headline_series_names: list[str] | None = None
    column_flavour_tags: str | list[str] | None = None
    include_context_columns: bool = True
    horizon: int = 2050


class CompareRequest(BaseModel):
    """A run-comparison request."""

    run_ids: list[str] = Field(min_length=2, max_length=12)


class OptimizationPresetRequest(BaseModel):
    """One shared Optimization preset request."""

    name: str = Field(min_length=1, max_length=40)
    state: dict[str, Any] = Field(default_factory=dict)
    saved_at: str | None = Field(default=None, max_length=40)
    author: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=200)
    review_status: str | None = Field(default=None, max_length=20)


class OptimizationLibraryRestoreRequest(BaseModel):
    """A shared Optimization library restore request."""

    presets: list[dict[str, Any]] = Field(default_factory=list)
    timeline_views: list[dict[str, Any]] = Field(default_factory=list)
    mode: str = Field(default="merge", max_length=20)
    dry_run: bool = True


class PruneHistoryRequest(BaseModel):
    """A shared-history retention request."""

    days: int = Field(default=90, ge=1, le=3650)
    dry_run: bool = False


class TimelineViewRequest(BaseModel):
    """One shared timeline filter view request."""

    name: str = Field(min_length=1, max_length=40)
    filter: dict[str, Any] = Field(default_factory=dict)
    saved_at: str | None = Field(default=None, max_length=40)
    author: str | None = Field(default=None, max_length=40)
    note: str | None = Field(default=None, max_length=200)
    review_status: str | None = Field(default=None, max_length=20)


class ChatCreateRequest(BaseModel):
    """Create a persistent assistant chat."""

    run_id: str | None = None


class ChatUpdateRequest(BaseModel):
    """Update chat metadata."""

    title: str | None = Field(default=None, min_length=1, max_length=120)
    pinned: bool | None = None
    archived: bool | None = None


class AssistantPayload(BaseModel):
    """Browser assistant payload."""

    message: str = Field(min_length=1, max_length=8000)
    chat_id: str | None = Field(default=None, max_length=80)
    run_id: str | None = None
    session: str | None = Field(default=None, max_length=200)
    model: str | None = None


def is_loopback(host: str) -> bool:
    """Return whether a host string is a loopback address."""

    return host.strip().lower() in {"127.0.0.1", "localhost", "::1", "0:0:0:0:0:0:0:1"}


def validate_bind(host: str, *, allow_remote: bool) -> None:
    """Refuse a non-loopback bind unless the user explicitly opted in."""

    if not is_loopback(host) and not allow_remote:
        raise ValueError(
            f"Refusing non-loopback bind {host!r} without --allow-remote. The portal has no authentication."
        )


def create_app(config: PortalConfig) -> FastAPI:
    """Create the portal application."""

    state = PortalState(config)
    app = FastAPI(title=config.title, version=__version__)

    if config.auth_user and config.auth_password:
        expected_auth = base64.b64encode(f"{config.auth_user}:{config.auth_password}".encode("utf-8")).decode("ascii")

        @app.middleware("http")
        async def _basic_auth(request: Request, call_next):
            root_path = str(request.scope.get("root_path", ""))
            path = request.url.path
            if root_path and path.startswith(root_path):
                path = path[len(root_path) :] or "/"
            if path == "/api/health":
                return await call_next(request)
            header = request.headers.get("authorization", "")
            supplied = header[6:].strip() if header.lower().startswith("basic ") else ""
            if not supplied or not secrets.compare_digest(supplied, expected_auth):
                return Response(
                    status_code=401,
                    content="Authentication required\n",
                    headers={"WWW-Authenticate": 'Basic realm="FABLE Pyculator"'},
                    media_type="text/plain",
                )
            return await call_next(request)

    @app.exception_handler(PortalError)
    async def _portal_error(_: Request, error: PortalError) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"detail": str(error)})

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "status": "ok",
            "version": __version__,
            "title": config.title,
            "repo_root": str(config.repo_root),
            "versions": list(config.versions),
            "prepared": [version for version in config.versions if state.status(version)["prepared"]],
            "assistant_enabled": config.allow_agent,
        }

    @app.get("/api/options")
    def options() -> dict[str, Any]:
        return state.options()

    @app.get("/api/agent")
    def agent() -> dict[str, Any]:
        return agent_info(
            enabled=config.allow_agent,
            model=config.agent_model,
            workspace=config.repo_root,
            timeout=config.agent_timeout,
        )

    @app.get("/api/artifacts")
    def artifacts() -> list[dict[str, Any]]:
        return state.artifacts()

    @app.get("/api/artifacts/{version}")
    def artifact(version: str) -> dict[str, Any]:
        return state.artifact(version)

    @app.get("/api/validation/{version}")
    def validation(version: str) -> dict[str, Any]:
        return state.validation(version)

    @app.get("/api/models/{version}/status")
    def model_status(version: str) -> dict[str, Any]:
        return state.status(version)

    @app.post("/api/models/{version}/prepare")
    def prepare_model(version: str) -> dict[str, Any]:
        job = state.prepare_job(version)
        return job.to_dict()

    @app.post("/api/models/{version}/materialize")
    def materialize(version: str, force: bool = Query(default=False)) -> dict[str, Any]:
        if version not in config.versions:
            raise PortalError(f"unknown workbook version {version!r}", status_code=404)
        try:
            return materialize_generated_model(config.repo_root, version, force=force)
        except FileNotFoundError as error:
            raise PortalError(str(error), status_code=404) from error
        except ValueError as error:
            raise PortalError(str(error), status_code=409) from error

    @app.get("/api/models/{version}/spec")
    def spec(version: str) -> dict[str, Any]:
        return state.spec(version)

    @app.get("/api/jobs/{job_id}")
    def job(job_id: str) -> dict[str, Any]:
        return state.jobs.get(job_id).to_dict()

    @app.get("/api/runs")
    def runs() -> list[dict[str, Any]]:
        return state.runs()

    @app.post("/api/runs")
    def start_run(request: ScenarioRequest) -> dict[str, Any]:
        job = state.run_job(
            version=request.version,
            name=request.name,
            selections=request.selections,
            output_table_names=request.output_table_names,
            headline_series_names=request.headline_series_names,
            column_flavour_tags=request.column_flavour_tags,
            include_context_columns=request.include_context_columns,
            horizon=request.horizon,
        )
        return job.to_dict()

    @app.get("/api/runs/{run_id}")
    def run_detail(run_id: str) -> dict[str, Any]:
        return state.run(run_id)

    @app.get("/api/runs/{run_id}/tables/{table_name}")
    def table(run_id: str, table_name: str) -> dict[str, Any]:
        return state.table(run_id, table_name)

    @app.post("/api/compare")
    def compare(request: CompareRequest) -> dict[str, Any]:
        return state.compare(request.run_ids)

    @app.get("/api/scenario-bundles")
    def scenario_bundles() -> list[dict[str, Any]]:
        return state.bundles()

    @app.get("/api/optimization/frontiers")
    def optimization_frontiers() -> list[dict[str, Any]]:
        return state.optimization_frontiers()

    @app.get("/api/optimization/frontiers/{version}")
    def optimization_frontier(version: str) -> dict[str, Any]:
        return state.optimization_frontier(version)

    @app.get("/api/optimization/presets")
    def optimization_presets() -> list[dict[str, Any]]:
        return state.optimization_presets()

    @app.get("/api/optimization/library")
    def optimization_library() -> dict[str, Any]:
        return state.optimization_library()

    @app.post("/api/optimization/library/restore")
    def restore_optimization_library(request: OptimizationLibraryRestoreRequest) -> dict[str, Any]:
        try:
            return state.restore_optimization_library(
                request.presets,
                request.timeline_views,
                mode=request.mode,
                dry_run=request.dry_run,
            )
        except ValueError as error:
            raise PortalError(str(error), status_code=400) from error

    @app.get("/api/optimization/retention")
    def optimization_retention() -> dict[str, Any]:
        return state.retention_status()

    @app.get("/api/optimization/retention/runs")
    def optimization_retention_runs(limit: int = Query(default=20, ge=1, le=100)) -> list[dict[str, Any]]:
        return state.retention_runs(limit)

    @app.post("/api/optimization/presets")
    def save_optimization_preset(request: OptimizationPresetRequest) -> dict[str, Any]:
        try:
            return state.save_optimization_preset(
                request.name,
                request.state,
                request.saved_at,
                author=request.author,
                note=request.note,
                review_status=request.review_status,
            )
        except ValueError as error:
            raise PortalError(str(error), status_code=400) from error

    @app.post("/api/optimization/presets/prune")
    def prune_optimization_history(request: PruneHistoryRequest) -> dict[str, Any]:
        try:
            return state.prune_optimization_history(request.days, request.dry_run)
        except ValueError as error:
            raise PortalError(str(error), status_code=400) from error

    @app.delete("/api/optimization/presets/{name}")
    def delete_optimization_preset(name: str) -> dict[str, Any]:
        return state.delete_optimization_preset(name)

    @app.get("/api/optimization/timeline-views")
    def timeline_views() -> list[dict[str, Any]]:
        return state.timeline_views()

    @app.post("/api/optimization/timeline-views")
    def save_timeline_view(request: TimelineViewRequest) -> dict[str, Any]:
        try:
            return state.save_timeline_view(
                request.name,
                request.filter,
                request.saved_at,
                author=request.author,
                note=request.note,
                review_status=request.review_status,
            )
        except ValueError as error:
            raise PortalError(str(error), status_code=400) from error

    @app.delete("/api/optimization/timeline-views/{name}")
    def delete_timeline_view(name: str) -> dict[str, Any]:
        return state.delete_timeline_view(name)

    @app.get("/api/chats")
    def chats(
        include_archived: bool = Query(default=False),
        q: str | None = Query(default=None, max_length=200),
    ) -> list[dict[str, Any]]:
        return state.list_chats(include_archived=include_archived, query=q)

    @app.post("/api/chats")
    def create_chat(request: ChatCreateRequest) -> dict[str, Any]:
        return state.create_chat(run_id=request.run_id)

    @app.get("/api/chats/{chat_id}")
    def chat_detail(chat_id: str) -> dict[str, Any]:
        return state.get_chat(chat_id)

    @app.patch("/api/chats/{chat_id}")
    def update_chat(chat_id: str, request: ChatUpdateRequest) -> dict[str, Any]:
        return state.update_chat(
            chat_id,
            title=request.title,
            pinned=request.pinned,
            archived=request.archived,
        )

    @app.get("/api/chats/{chat_id}/export.md", include_in_schema=False)
    def export_chat(chat_id: str) -> Response:
        return Response(
            content=state.export_chat(chat_id),
            media_type="text/markdown; charset=utf-8",
        )

    @app.delete("/api/chats/{chat_id}")
    def delete_chat(chat_id: str) -> dict[str, Any]:
        return state.delete_chat(chat_id)

    @app.get("/api/assistant/cheatsheet.md", include_in_schema=False)
    def assistant_cheatsheet() -> Response:
        cheat_sheet = state.ensure_cheat_sheet()
        return Response(content=cheat_sheet.markdown, media_type="text/markdown; charset=utf-8")

    @app.post("/api/assistant")
    def assistant(payload: AssistantPayload) -> dict[str, Any]:
        if not config.allow_agent:
            raise PortalError(
                "the assistant is disabled; restart the portal with --allow-agent",
                status_code=403,
            )
        chat = state.get_chat(payload.chat_id) if payload.chat_id else state.create_chat(run_id=payload.run_id)
        chat_id = str(chat["chat_id"])
        new_session = not bool(chat.get("agent_session"))
        cheat_sheet = state.ensure_cheat_sheet()
        state.chats.append_message(
            chat_id,
            role="user",
            content=payload.message,
            run_id=payload.run_id,
        )
        try:
            result = run_agent(
                AgentRequest(
                    message=payload.message,
                    run_id=payload.run_id,
                    session=chat.get("agent_session") or payload.session,
                    model=payload.model or config.agent_model,
                    context=state.assistant_context(payload.run_id),
                    new_session=new_session,
                    cheat_sheet_path=str(cheat_sheet.path),
                    required_reading=cheat_sheet.required_reading,
                ),
                workspace=config.repo_root,
                command=config.agent_command,
                timeout=config.agent_timeout,
            )
        except AgentError as error:
            state.chats.append_message(chat_id, role="error", content=str(error))
            raise PortalError(str(error), status_code=502) from error
        updated = state.chats.append_message(
            chat_id,
            role="assistant",
            content=result.get("response", ""),
            actions=result.get("actions"),
            run_id=payload.run_id,
        )
        if new_session:
            updated = state.chats.set_metadata(
                chat_id,
                title=auto_title(payload.message, result.get("response")),
            )
        updated = state.chats.set_session(chat_id, result.get("session"))
        return {
            **result,
            "chat_id": chat_id,
            "chat": updated.summary(),
            "messages": updated.to_dict()["messages"],
        }

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(_STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
    return app


def run_server(
    config: PortalConfig,
    *,
    host: str,
    port: int,
    root_path: str = "",
    allow_remote: bool = False,
) -> None:
    """Run the portal with uvicorn."""

    try:
        import uvicorn
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "The web portal needs optional dependencies. Install with: pip install 'fable-pyculator[web]'"
        ) from error

    validate_bind(host, allow_remote=allow_remote)
    app = create_app(config)
    uvicorn.run(app, host=host, port=port, root_path=root_path)


def main(argv: list[str] | None = None) -> int:
    """Compatibility alias for callers that import ``web.app.main``."""

    from fable_pyculator.cli import main as cli_main

    return cli_main(argv if argv is not None else sys.argv[1:])
