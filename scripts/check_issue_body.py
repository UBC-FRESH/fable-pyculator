#!/usr/bin/env python
"""Validate a GitHub issue body against the UBC-FRESH issue standard.

The portal assistant writes a draft body to a file, runs this checker, shows the draft to
the user, and posts it with ``gh issue create --body-file`` only after confirmation. The
checker is intentionally local and deterministic: it does not call GitHub or a model.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

__all__ = ["main", "validate_issue_body"]

_TASK_SECTIONS = (
    "Goal:",
    "Scope:",
    "Out of scope:",
    "Subtasks:",
    "Acceptance criteria:",
    "Verification:",
    "Artifacts:",
    "Risks:",
    "Completion metadata:",
)
_PHASE_SECTIONS = (
    "Goal:",
    "Scope:",
    "Out of scope:",
    "Architecture notes:",
    "Child task checklist:",
    "Acceptance criteria:",
    "Verification:",
    "Closeout requirements:",
)
_PLACEHOLDERS = re.compile(r"<(?:n|m|parent|child|issue|phase name|task name|slug|parent issue)>")
_SECRETS = re.compile(r"(?:gho_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})")
_BRANCH = re.compile(r"^Branch: `feature/p\d+-[a-z0-9][a-z0-9-]*`$", re.MULTILINE)
_STATUS = re.compile(r"^Status: (?:planned|active|pr-open|complete|deferred)$", re.MULTILINE)


def main(argv: list[str] | None = None) -> int:
    """Run the issue-body checker."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("task", "phase"), required=True, help="Issue level.")
    parser.add_argument("--title", help="Proposed issue title, for format checking.")
    parser.add_argument("--file", type=Path, required=True, help="Markdown issue body to validate.")
    args = parser.parse_args(argv)

    try:
        text = args.file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        print(f"could not read {args.file}: {error}")
        return 2
    errors = validate_issue_body(text, kind=args.kind, title=args.title)
    if errors:
        print(f"{args.file}: {len(errors)} issue(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"{args.file}: ok ({args.kind})")
    return 0


def validate_issue_body(text: str, *, kind: str, title: str | None = None) -> list[str]:
    """Return format errors for one issue body."""

    if kind not in {"task", "phase"}:
        raise ValueError("kind must be 'task' or 'phase'")
    errors: list[str] = []
    errors.extend(_encoding_errors(text))
    required = _TASK_SECTIONS if kind == "task" else _PHASE_SECTIONS
    sections = _sections(text, required)
    for label in required:
        if label not in sections:
            errors.append(f"missing section label on its own line: {label}")
    positions = [sections[label] for label in required if label in sections]
    if positions != sorted(positions):
        errors.append("section labels are not in the required order")

    body_text = text.casefold()
    if _PLACEHOLDERS.search(body_text):
        errors.append("unreplaced placeholder remains in the issue body")
    if _SECRETS.search(text):
        errors.append("secret-shaped string is present in the issue body")
    for line in text.splitlines():
        if "[ ]" in line and not re.match(r"^\s*- \[[ xX]\]", line):
            errors.append(f"inline pseudo-checklist: {line.strip()[:80]}")

    if kind == "task":
        errors.extend(_task_header_errors(text, title))
        if not _task_list(section_text(text, sections, "Subtasks:")):
            errors.append("Subtasks: needs at least one '- [ ]' or '- [x]' item")
    else:
        errors.extend(_phase_header_errors(text, title))
        if not _task_list(section_text(text, sections, "Child task checklist:")):
            errors.append("Child task checklist: needs at least one '- [ ]' or '- [x]' item")
    return errors


def _encoding_errors(text: str) -> list[str]:
    """Reject byte-order marks, carriage returns, and control characters."""

    errors: list[str] = []
    if text.startswith("\ufeff"):
        errors.append("byte-order mark (U+FEFF) at start of file")
    if "\r" in text:
        errors.append("carriage return is present; use LF line endings")
    for character in text:
        if character == "\n":
            continue
        if unicodedata.category(character) in {"Cc", "Cf"}:
            errors.append(f"control character U+{ord(character):04X} is present")
            break
    return errors


def _sections(text: str, required: tuple[str, ...]) -> dict[str, int]:
    """Return line numbers for required labels that are on their own line."""

    lines = text.splitlines()
    return {line.strip(): index for index, line in enumerate(lines) if line.strip() in required}


def section_text(text: str, sections: dict[str, int], label: str) -> str:
    """Return the text after one labelled section, up to the next required label."""

    if label not in sections:
        return ""
    lines = text.splitlines()
    start = sections[label] + 1
    end = len(lines)
    for index in sorted(sections.values()):
        if index >= start:
            end = index
            break
    return "\n".join(lines[start:end])


def _task_list(section: str) -> bool:
    """Return whether a section contains a real task-list item."""

    return any(re.match(r"^\s*- \[[ xX]\] .+", line) for line in section.splitlines())


def _task_header_errors(text: str, title: str | None) -> list[str]:
    errors: list[str] = []
    match = re.search(r"^Task identifier:\s*(P\d+\.\d+)\s*$", text, re.MULTILINE)
    if not match:
        errors.append("Task identifier must be on its own line as P<n>.<m>")
    elif title:
        if not re.match(r"^P\d+\.\d+: \S", title):
            errors.append("task title must match 'P<n>.<m>: <task name>'")
        elif not title.startswith(match.group(1) + ":"):
            errors.append("task title and Task identifier disagree")
    if not re.search(r"^Parent phase issue:\s*#\d+\s*$", text, re.MULTILINE):
        errors.append("Parent phase issue must be on its own line as #<number>")
    errors.extend(_common_header_errors(text))
    return errors


def _phase_header_errors(text: str, title: str | None) -> list[str]:
    errors: list[str] = []
    match = re.search(r"^Phase identifier:\s*(P\d+)\s*$", text, re.MULTILINE)
    if not match:
        errors.append("Phase identifier must be on its own line as P<n>")
    elif title:
        if not re.match(r"^P\d+: \S", title):
            errors.append("phase title must match 'P<n>: <phase name>'")
        elif not title.startswith(match.group(1) + ":"):
            errors.append("phase title and Phase identifier disagree")
    errors.extend(_common_header_errors(text))
    return errors


def _common_header_errors(text: str) -> list[str]:
    errors: list[str] = []
    if not _STATUS.search(text, re.MULTILINE):
        errors.append("Status must be one of planned, active, pr-open, complete, or deferred")
    if not _BRANCH.search(text, re.MULTILINE):
        errors.append("Branch must be `feature/p<n>-<slug>`")
    return errors


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
