"""Grounding evaluations for the FABLE portal assistant.

The structural checks always run and verify that the generated cheat sheet points at real,
existing docs/source files and contains the expected API facts. The live checks are opt-in: they run
the installed OpenCode CLI with the same new-session grounding prompt and check that each answer
cites an expected source and contains the expected facts.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fable_pyculator.web.artifacts import DEFAULT_VERSIONS, artifact_summary
from fable_pyculator.web.assistant import DEFAULT_AGENT_MODEL, AgentError, AgentRequest, run_agent
from fable_pyculator.web.cheatsheet import CheatSheet, ensure_cheat_sheet

__all__ = [
    "DEFAULT_CASES",
    "GroundingCase",
    "GroundingCaseResult",
    "GroundingEvalSummary",
    "run_grounding_evals",
]

AGENT_COMMAND: tuple[str, ...] = ("opencode", "run", "--format", "json", "--auto")


@dataclass(frozen=True)
class GroundingCase:
    """One assistant grounding question and its required evidence."""

    case_id: str
    question: str
    expected_paths: tuple[str, ...]
    required_terms: tuple[str, ...]
    forbidden_terms: tuple[str, ...] = ()


DEFAULT_CASES: tuple[GroundingCase, ...] = (
    GroundingCase(
        case_id="notebook_signature",
        question=(
            "What is the exact signature of build_notebook_spec in the current fable-pyculator "
            "source, including the optional headline-curation flag? Cite the exact file path."
        ),
        expected_paths=("src/fable_pyculator/notebook.py",),
        required_terms=("build_notebook_spec", "strict_headlines"),
        forbidden_terms=("no optional", "does not exist"),
    ),
    GroundingCase(
        case_id="modelwright_facade",
        question=("Which Modelwright module defines ModelFacade, and what does it wrap? Cite the exact file path."),
        expected_paths=("src/modelwright/wrappers.py",),
        required_terms=("ModelFacade", "generated"),
    ),
    GroundingCase(
        case_id="fable_2024_water",
        question=(
            "Which default FABLE headline series is unavailable in the 2024 Canada workbook, and "
            "why? Cite the workbook table name and a file path you used."
        ),
        expected_paths=("docs/guides/workbook-structure.rst", "src/fable_pyculator/discovery.py"),
        required_terms=("TotalResultsWF", "2024"),
    ),
    GroundingCase(
        case_id="portal_read_only",
        question=("Does the portal recompute FABLE results in the browser? Answer directly and cite a file path."),
        expected_paths=("docs/guides/web-portal.rst",),
        required_terms=("does not", "recompute"),
    ),
)


@dataclass
class GroundingCaseResult:
    """Outcome of one structural or live grounding case."""

    case_id: str
    status: str
    seconds: float = 0.0
    failures: list[str] = field(default_factory=list)
    response: str = ""
    actions: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready result."""

        return {
            "case_id": self.case_id,
            "status": self.status,
            "seconds": round(self.seconds, 2),
            "failures": list(self.failures),
            "response": self.response,
            "actions": list(self.actions),
        }


@dataclass
class GroundingEvalSummary:
    """Combined structural and optional live evaluation summary."""

    repo_root: str
    cheat_sheet_path: str
    structural: list[str]
    cases: list[GroundingCaseResult]
    live: bool

    @property
    def passed(self) -> bool:
        """Return whether every check passed."""

        return not self.structural and all(case.status in {"pass", "skipped"} for case in self.cases)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready summary."""

        return {
            "repo_root": self.repo_root,
            "cheat_sheet_path": self.cheat_sheet_path,
            "structural": list(self.structural),
            "cases": [case.to_dict() for case in self.cases],
            "live": self.live,
            "passed": self.passed,
        }


def run_grounding_evals(
    repo_root: str | Path,
    *,
    runtime_dir: str | Path | None = None,
    cases: tuple[GroundingCase, ...] = DEFAULT_CASES,
    include_live: bool = False,
    timeout: float = 600.0,
) -> GroundingEvalSummary:
    """Run structural checks and, when requested, live assistant evaluations."""

    root = Path(repo_root).expanduser().resolve()
    runtime = (
        Path(runtime_dir).expanduser().resolve() if runtime_dir is not None else root / "runtime" / "assistant-evals"
    )
    artifacts = [artifact_summary(root, version) for version in DEFAULT_VERSIONS]
    cheat_sheet = ensure_cheat_sheet(
        repo_root=root,
        runtime_dir=runtime,
        artifacts=artifacts,
        prepared_summaries={},
        runs=[],
    )
    structural = structural_failures(root, cheat_sheet, cases)
    results: list[GroundingCaseResult] = []
    for case in cases:
        if not include_live:
            results.append(
                GroundingCaseResult(case_id=case.case_id, status="skipped", failures=["live checks not requested"])
            )
            continue
        results.append(_evaluate_live_case(root, cheat_sheet, case, timeout=timeout))
    return GroundingEvalSummary(
        repo_root=str(root),
        cheat_sheet_path=str(cheat_sheet.path),
        structural=structural,
        cases=results,
        live=include_live,
    )


def structural_failures(
    repo_root: Path,
    cheat_sheet: CheatSheet,
    cases: tuple[GroundingCase, ...] = DEFAULT_CASES,
) -> list[str]:
    """Check that the sheet and required-reading list point at real files and facts."""

    failures: list[str] = []
    required_paths = [Path(path) for path in cheat_sheet.required_reading]
    for case in cases:
        for relative in case.expected_paths:
            matches = [path for path in required_paths if _path_matches(path, relative)]
            if not matches:
                failures.append(f"{case.case_id}: expected path is not in required reading: {relative}")
            if not any(path.is_file() for path in matches):
                failures.append(f"{case.case_id}: expected path is missing: {relative}")
    for relative in (
        "docs/guides/web-portal.rst",
        "docs/guides/workbook-structure.rst",
        "src/fable_pyculator/notebook.py",
        "src/fable_pyculator/discovery.py",
    ):
        if not (repo_root / relative).is_file():
            failures.append(f"required FABLE source/doc is missing: {repo_root / relative}")
    for term in (
        "Documentation digest",
        "Source API index",
        "build_notebook_spec",
        "class ModelFacade",
        "TotalResultsWF",
        "2024",
    ):
        if term not in cheat_sheet.markdown:
            failures.append(f"cheat sheet is missing expected term: {term!r}")
    for path in cheat_sheet.required_reading:
        if not Path(path).is_file():
            failures.append(f"required reading path does not exist: {path}")
    return failures


def _evaluate_live_case(
    repo_root: Path,
    cheat_sheet: CheatSheet,
    case: GroundingCase,
    *,
    timeout: float,
) -> GroundingCaseResult:
    started = time.perf_counter()
    try:
        result = run_agent(
            AgentRequest(
                message=case.question,
                model=DEFAULT_AGENT_MODEL,
                new_session=True,
                cheat_sheet_path=str(cheat_sheet.path),
                required_reading=cheat_sheet.required_reading,
                context={
                    "repo_root": str(repo_root),
                    "cheat_sheet_path": str(cheat_sheet.path),
                },
            ),
            workspace=repo_root,
            command=AGENT_COMMAND,
            timeout=timeout,
        )
    except AgentError as error:
        return GroundingCaseResult(
            case_id=case.case_id,
            status="fail",
            seconds=time.perf_counter() - started,
            failures=[str(error)],
        )
    response = str(result.get("response", ""))
    actions = [action for action in result.get("actions", []) if isinstance(action, dict)]
    haystack = response + "\n" + json.dumps(actions)
    lowered = haystack.casefold()
    failures: list[str] = []
    if not any(path in haystack for path in case.expected_paths):
        failures.append("answer/actions do not cite any expected path: " + ", ".join(case.expected_paths))
    for term in case.required_terms:
        if term.casefold() not in lowered:
            failures.append(f"answer/actions do not contain expected term: {term!r}")
    for term in case.forbidden_terms:
        if term.casefold() in lowered:
            failures.append(f"answer/actions contain forbidden term: {term!r}")
    return GroundingCaseResult(
        case_id=case.case_id,
        status="pass" if not failures else "fail",
        seconds=time.perf_counter() - started,
        failures=failures,
        response=response,
        actions=actions,
    )


def _path_matches(path: Path, relative: str) -> bool:
    """Match repo-relative paths and installed-package paths with the same package/name."""

    if path.as_posix() == relative or path.as_posix().endswith("/" + relative):
        return True
    expected = Path(relative)
    return path.name == expected.name and path.parent.name == expected.parent.name
