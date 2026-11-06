from __future__ import annotations

import importlib.util
from pathlib import Path

from fable_pyculator.web.assistant import AGENT_GUIDE

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_issue_body.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_issue_body", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _task_body(**overrides: str) -> str:
    headers = {
        "Task identifier:": "P28.10",
        "Parent phase issue:": "#50",
        "Status:": "planned",
        "Branch:": "`feature/p28-web-portal`",
        "Related planning:": "`ROADMAP.md` (Phase 28)",
    }
    sections = {
        "Goal:": "Make the example work.",
        "Scope:": "One small change.",
        "Out of scope:": "Unrelated changes.",
        "Subtasks:": "- [ ] Add the example.",
        "Acceptance criteria:": "The example exists.",
        "Verification:": "Run the focused test.",
        "Artifacts:": "`docs/guides/example.rst`",
        "Risks:": "Low.",
        "Completion metadata:": "Added at closeout.",
    }
    sections.update(overrides)
    lines = [f"{label} {value}" for label, value in headers.items()]
    lines.append("")
    for label, value in sections.items():
        lines.extend([label, value, ""])
    return "\n".join(lines)


def test_check_issue_body_accepts_canonical_task_body() -> None:
    module = _load_module()

    errors = module.validate_issue_body(
        _task_body(),
        kind="task",
        title="P28.10: Add an example task",
    )

    assert errors == []


def test_check_issue_body_rejects_placeholders_and_control_characters() -> None:
    module = _load_module()
    body = _task_body().replace("Make the example work.", "Make <task name> work.\r")

    errors = module.validate_issue_body(body, kind="task", title="P28.10: Bad")

    assert any("placeholder" in error for error in errors)
    assert any("carriage return" in error for error in errors)


def test_check_issue_body_rejects_missing_subtask_and_title_mismatch() -> None:
    module = _load_module()
    body = _task_body(**{"Subtasks:": "No list here."})

    errors = module.validate_issue_body(body, kind="task", title="P28.11: Wrong number")

    assert any("Subtasks:" in error for error in errors)
    assert any("disagree" in error for error in errors)


def test_check_issue_body_accepts_phase_and_requires_checklist() -> None:
    module = _load_module()
    phase = "\n".join(
        [
            "Phase identifier: P29",
            "",
            "Status: planned",
            "",
            "Branch: `feature/p29-issue-workflow`",
            "",
            'Roadmap: `ROADMAP.md`, section "Phase 29"',
            "",
            "Pull request: not opened yet",
            "",
            "Goal:",
            "Test the phase template.",
            "",
            "Scope:",
            "One phase.",
            "",
            "Out of scope:",
            "Other phases.",
            "",
            "Architecture notes:",
            "None.",
            "",
            "Child task checklist:",
            "- [ ] #51 P29.1: First task",
            "",
            "Acceptance criteria:",
            "The task is tracked.",
            "",
            "Verification:",
            "Read back the issue.",
            "",
            "Closeout requirements:",
            "Closeout comment.",
            "",
        ]
    )

    assert module.validate_issue_body(phase, kind="phase", title="P29: Issue workflow") == []
    missing = phase.replace("- [ ] #51 P29.1: First task", "No checklist.")
    assert any("Child task checklist" in error for error in module.validate_issue_body(missing, kind="phase"))


def test_agent_guide_explains_issue_filing_and_confirmation() -> None:
    guide = AGENT_GUIDE.casefold()

    for term in (
        "github issue filing",
        "gh issue create",
        "--body-file",
        "check_issue_body.py",
        "bug",
        "feature request",
        "documentation",
        "scope and scale",
        "confirmation",
    ):
        assert term in guide
