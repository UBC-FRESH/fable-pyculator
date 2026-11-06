"""Optional local assistant bridge for the FABLE portal.

The assistant is disabled unless the service is started with ``--allow-agent``. When enabled it
invokes the installed ``opencode`` CLI in the configured repository root. The service never reads
provider keys and never gives the browser a shell.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "AGENT_GUIDE",
    "DEFAULT_AGENT_MODEL",
    "AgentError",
    "AgentRequest",
    "agent_info",
    "run_agent",
]

DEFAULT_AGENT_MODEL = "opencode-go/deepseek-v4.1-flash"

AGENT_GUIDE = """\
You are the FABLE Pyculator portal assistant. Help the user understand FABLE Calculator scenario
controls, generated-model outputs, headline series, validation evidence, and the local artifact
layout. The portal is a local reader over generated-model artifacts.

Useful context:
- Workbook versions offered by the portal are 2021, 2024, and 2020.
- Source workbooks live under `tmp/private-workbooks/`.
- Generated models live under `tmp/generated-models/fable-<version>/`.
- Approved compressed models live under `examples/fable_<version>/`.
- Compact validation evidence lives under `tmp/validation-evidence/fable-<version>/summary.json`.
- The 2024 Canada workbook exposes FOOD, LAND, and GHG headline series; it has no
  `TotalResultsWF` water-footprint table.

Rules:
- Use only values in the current portal context or values you obtain by reading the repository.
- Do not invent output values, scenario results, validation counts, or file paths.
- Do not claim you changed a scenario, prepared a model, or saved a run. Explain the UI steps.
- Keep answers short and concrete. Prefer short bullets, and use markdown for code and links.
- Do not print credentials, environment secrets, or full raw data tables.
"""

NEW_SESSION_GROUNDING = """\
MANDATORY NEW-SESSION GROUNDING:

This is the first turn of a new chat. Read the compiled grounding sheet at:

{cheat_sheet_path}

That sheet is generated from every FABLE Pyculator and Modelwright documentation file listed under
"Required reading" and includes a documentation digest plus an AST-generated source API index. Read
the sheet in full before answering.

Then open the full documentation or source file listed in "Required reading" whenever the question
needs exact signatures, behaviour, examples, paths, counts, or caveats. Use the available
file-reading tools. Do not answer from memory or from generic "vibes".

If a fact is not in the cheat sheet, the current portal context, or a file you actually read, say
that it is not available and explain where it would come from. Never invent API names, model
behaviour, paths, counts, output values, or validation claims. Do not claim to have changed a
scenario, prepared a model, or saved a run.

The cheat sheet content is included below so the key facts and compiled doc/API digest are
available even before you open the full files. Treat the actual files as authoritative when they
differ.

--- BEGIN CHEAT SHEET ---
{cheat_sheet}
--- END CHEAT SHEET ---

Required reading:
{required_reading}
"""


class AgentRequest(BaseModel):
    """One assistant prompt, optionally scoped to a saved run and a persistent chat."""

    message: str = Field(min_length=1, max_length=8000)
    run_id: str | None = Field(default=None, max_length=200)
    session: str | None = Field(default=None, max_length=200)
    context: dict[str, Any] | None = None
    model: str | None = Field(default=None, max_length=200)
    new_session: bool = False
    cheat_sheet_path: str | None = None
    required_reading: tuple[str, ...] = ()


class AgentError(RuntimeError):
    """The assistant subprocess failed."""


def agent_info(*, enabled: bool, model: str | None, workspace: Path, timeout: float) -> dict[str, Any]:
    """Return service-side assistant availability metadata."""

    executable = shutil.which("opencode")
    return {
        "enabled": enabled,
        "available": executable is not None,
        "executable": executable,
        "model": model,
        "cwd": str(workspace),
        "timeout": timeout,
    }


def run_agent(
    request: AgentRequest,
    *,
    workspace: Path,
    command: tuple[str, ...],
    timeout: float,
) -> dict[str, Any]:
    """Run one assistant turn and return markdown text, session id, and tool actions."""

    context = json.dumps(request.context or {}, indent=2, sort_keys=True, ensure_ascii=False)[-12000:]
    grounding = ""
    if request.new_session:
        cheat_sheet = ""
        if request.cheat_sheet_path:
            try:
                cheat_sheet = Path(request.cheat_sheet_path).read_text(encoding="utf-8")[:180000]
            except OSError:
                cheat_sheet = "(cheat sheet could not be read)"
        reading = "\n".join(f"- `{path}`" for path in request.required_reading) or "- (none)"
        grounding = NEW_SESSION_GROUNDING.format(
            cheat_sheet_path=request.cheat_sheet_path or "(not available)",
            cheat_sheet=cheat_sheet,
            required_reading=reading,
        )
    prompt = f"{AGENT_GUIDE}\n\n{grounding}\n\nCurrent portal context (JSON):\n{context}\n\nUser: {request.message}"
    argv = list(command)
    if request.model:
        argv.extend(["--model", request.model])
    if request.session and request.session.startswith("ses"):
        argv.extend(["--session", request.session])
    argv.append(prompt)
    try:
        completed = subprocess.run(
            argv,
            cwd=workspace,
            env=_agent_environment(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as error:
        raise AgentError(f"assistant command not found: {argv[0]}") from error
    except subprocess.TimeoutExpired as error:
        raise AgentError(f"assistant timed out after {timeout:g} s") from error
    except OSError as error:
        raise AgentError(f"could not start assistant: {error}") from error

    response, session_id, actions, errors = _parse_agent_events(completed.stdout)
    if not response:
        detail = errors[-1] if errors else (completed.stderr.strip() or "the assistant returned no text")
        raise AgentError(detail[-2000:])
    return {
        "response": response,
        "session": session_id or request.session,
        "actions": actions,
        "returncode": completed.returncode,
        "command": argv[0],
    }


def _agent_environment() -> dict[str, str]:
    """Return a copy of the environment without obvious session/cloud credentials."""

    environment = os.environ.copy()
    for name in list(environment):
        lowered = name.casefold()
        if any(token in lowered for token in ("token", "secret", "password", "credential")):
            environment.pop(name, None)
    for name in (
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "GLOBUS_ACCESS_TOKEN",
        "GLOBUS_REFRESH_TOKEN",
    ):
        environment.pop(name, None)
    return environment


def _parse_agent_events(stdout: str) -> tuple[str, str | None, list[dict[str, str]], list[str]]:
    """Parse the JSON-lines output of ``opencode run --format json``."""

    texts: list[str] = []
    actions: list[dict[str, str]] = []
    errors: list[str] = []
    session_id: str | None = None
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, Mapping):
            continue
        candidate = event.get("sessionID")
        if isinstance(candidate, str) and candidate.startswith("ses"):
            session_id = candidate
        event_type = event.get("type")
        if event_type == "error":
            failure = event.get("error")
            if isinstance(failure, Mapping) and isinstance(failure.get("message"), str):
                errors.append(str(failure["message"]))
            continue
        part = event.get("part")
        if not isinstance(part, Mapping):
            continue
        if event_type == "text":
            text = part.get("text")
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
        elif event_type == "tool_use":
            tool = part.get("tool")
            state = part.get("state")
            summary = ""
            if isinstance(state, Mapping):
                title = state.get("title")
                if isinstance(title, str):
                    summary = title
                inputs = state.get("input")
                if isinstance(inputs, Mapping):
                    for key in ("command", "filePath", "path", "pattern", "url", "description"):
                        value = inputs.get(key)
                        if isinstance(value, str) and value.strip():
                            summary = value.strip()
                            break
            if isinstance(tool, str):
                action = {"tool": tool, "summary": summary[:160]}
                if action not in actions:
                    actions.append(action)
    return "\n\n".join(texts).strip(), session_id, actions[-12:], errors
