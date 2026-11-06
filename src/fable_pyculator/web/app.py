"""FastAPI application factory for the optional FABLE Pyculator portal.

Import this module only when the optional ``fable-pyculator[web]`` extra is installed. The core
notebook package does not depend on FastAPI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from fable_pyculator import __version__
from fable_pyculator.web.artifacts import materialize_generated_model
from fable_pyculator.web.assistant import AgentError, AgentRequest, run_agent
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


class CompareRequest(BaseModel):
    """A run-comparison request."""

    run_ids: list[str] = Field(min_length=2, max_length=12)


class AssistantPayload(BaseModel):
    """Browser assistant payload."""

    message: str = Field(min_length=1, max_length=8000)
    run_id: str | None = None
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

    @app.post("/api/assistant")
    def assistant(payload: AssistantPayload) -> dict[str, Any]:
        if not config.allow_agent:
            raise PortalError(
                "the assistant is disabled; restart the portal with --allow-agent",
                status_code=403,
            )
        try:
            return run_agent(
                AgentRequest(
                    message=payload.message,
                    run_id=payload.run_id,
                    model=payload.model,
                    context=state.assistant_context(payload.run_id),
                ),
                workspace=config.repo_root,
                command=config.agent_command,
                timeout=config.agent_timeout,
            )
        except AgentError as error:
            raise PortalError(str(error), status_code=502) from error

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
