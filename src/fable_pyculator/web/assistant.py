"""Optional local assistant bridge for the FABLE portal.

The assistant is disabled unless the service is started with ``--allow-agent``. When enabled it
invokes the installed ``opencode`` CLI in the configured repository root. The service never reads
provider keys and never gives the browser a shell.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

__all__ = ["AgentError", "AgentRequest", "run_agent"]


class AgentRequest(BaseModel):
    """One assistant prompt, optionally scoped to a saved run."""

    message: str = Field(min_length=1, max_length=8000)
    run_id: str | None = Field(default=None, max_length=200)
    context: dict[str, Any] | None = None
    model: str | None = Field(default=None, max_length=200)


class AgentError(RuntimeError):
    """The assistant subprocess failed."""


def run_agent(
    request: AgentRequest,
    *,
    workspace: Path,
    command: tuple[str, ...],
    timeout: float,
) -> dict[str, Any]:
    """Run the assistant CLI and return its textual response."""

    context = json.dumps(request.context or {}, indent=2, sort_keys=True)[-12000:]
    prompt = (
        "You are the FABLE Pyculator portal assistant. Help the user understand FABLE Calculator "
        "scenario controls, generated-model outputs, headline series, validation evidence, and the "
        "local artifact layout. Use only values in the context below or values you obtain by reading "
        "the repository. Do not invent output values or claim you changed a scenario. Keep answers "
        "short and concrete.\n\n"
        f"Current portal context:\n{context}\n\n"
        f"User question: {request.message}"
    )
    argv = list(command)
    if request.model:
        argv.extend(["--model", request.model])
    argv.append(prompt)
    try:
        completed = subprocess.run(
            argv,
            cwd=workspace,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as error:
        raise AgentError(f"assistant command not found: {argv[0]}") from error
    except subprocess.TimeoutExpired as error:
        raise AgentError(f"assistant timed out after {timeout:g} s") from error
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()[-2000:]
        raise AgentError(detail or f"assistant exited with code {completed.returncode}")
    return {
        "response": _extract_response(completed.stdout),
        "returncode": completed.returncode,
        "command": argv[0],
    }


def _extract_response(stdout: str) -> str:
    text = stdout.strip()
    if not text:
        return ""
    # ``opencode run --format json`` emits one JSON object per line; keep the last assistant text.
    for line in reversed(text.splitlines()):
        try:
            payload = json.loads(line)
        except ValueError:
            continue
        if isinstance(payload, dict):
            for key in ("text", "content", "message"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            part = payload.get("part")
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                return part["text"].strip()
    return text[-12000:]
