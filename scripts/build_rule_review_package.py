#!/usr/bin/env python
"""Generate the FABLE scenario-rule review worksheet and Markdown rule block.

The YAML registry is the single source for rule ids, statuses, severities, conditions, and
requirements. Reviewer decision/reviewer/comments cells are preserved by rule id, so regenerating
the worksheet never discards an expert decision.

Run with ``--check`` to fail when tracked artifacts drift from the registry.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from fable_pyculator.scenario_rules import (
    ScenarioRule,
    load_rule_registry,
    rule_registry_sha256,
)

__all__ = [
    "BEGIN_MARKER",
    "END_MARKER",
    "format_condition",
    "format_requirement",
    "main",
    "render_csv",
    "render_markdown_block",
]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "planning" / "fable-scenario-consistency-rules.yaml"
DEFAULT_MARKDOWN = ROOT / "planning" / "fable-scenario-consistency-review-package.md"
DEFAULT_CSV = ROOT / "planning" / "fable-scenario-consistency-review-package.csv"

BEGIN_MARKER = "<!-- BEGIN GENERATED RULE TABLE -->"
END_MARKER = "<!-- END GENERATED RULE TABLE -->"

CSV_COLUMNS = (
    "rule_id",
    "family",
    "status",
    "proposed_severity",
    "confidence",
    "condition",
    "require",
    "message",
    "review_question",
    "decision",
    "reviewer",
    "comments",
)
DECISION_COLUMNS = ("decision", "reviewer", "comments")

_FAMILY_LABELS = {
    "custom_tables": "Custom tables",
    "land": "Land and spatial",
    "narrative": "Narrative",
    "trade": "Trade",
    "agriculture": "Agriculture",
    "livestock": "Livestock",
}


def _scalar(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def _values(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ", ".join(_scalar(item) for item in value)
    return _scalar(value)


def format_condition(condition: Mapping[str, Any] | None) -> str:
    """Render a rule condition as a compact, exact human-readable expression."""

    if not isinstance(condition, Mapping):
        return ""
    if "all" in condition:
        parts = [format_condition(item) for item in condition.get("all") or []]
        return f"all({'; '.join(part for part in parts if part)})"
    if "any" in condition:
        parts = [format_condition(item) for item in condition.get("any") or []]
        return f"any({'; '.join(part for part in parts if part)})"
    switch = condition.get("switch")
    if isinstance(switch, str):
        if "in" in condition:
            return f"{switch} in {{{_values(condition['in'])}}}"
        if "not_in" in condition:
            return f"{switch} not in {{{_values(condition['not_in'])}}}"
        if "equals" in condition:
            return f"{switch} = {_scalar(condition['equals'])}"
        return switch
    if condition.get("rule") == "equal_when_all_in_ssp_1_3":
        switches = condition.get("switches") or []
        return f"equal_when_all_in_ssp_1_3({', '.join(_scalar(item) for item in switches)})"
    return json.dumps(dict(condition), sort_keys=True, separators=(",", ":"))


def format_requirement(require: Mapping[str, Any] | None) -> str:
    """Render a table requirement as a compact, exact expression."""

    if not isinstance(require, Mapping):
        return ""
    table = require.get("table")
    if not isinstance(table, str):
        return json.dumps(dict(require), sort_keys=True, separators=(",", ":"))
    key_switch = require.get("key_switch")
    key_value = require.get("key_value")
    if isinstance(key_switch, str):
        key = f"key_switch: {key_switch}"
    elif key_value is not None:
        key = f"key_value: {_scalar(key_value)}"
    else:
        key = "all rows"
    columns = require.get("non_null_columns") or []
    required = _values(columns) if isinstance(columns, (list, tuple)) else _scalar(columns)
    return f"{table}[{key}] non-null: {required}"


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _code_cell(value: str) -> str:
    return f"`{_cell(value)}`" if value else "—"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _load_decisions(path: Path) -> dict[str, dict[str, str]]:
    decisions: dict[str, dict[str, str]] = {}
    if not path.is_file():
        return decisions
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rule_id = (row.get("rule_id") or "").strip()
                if not rule_id:
                    continue
                decisions[rule_id] = {column: row.get(column, "") or "" for column in DECISION_COLUMNS}
    except (OSError, csv.Error):
        return {}
    return decisions


def render_csv(rules: tuple[ScenarioRule, ...], csv_path: Path) -> str:
    """Render the fillable review worksheet, preserving existing decisions."""

    decisions = _load_decisions(csv_path)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for rule in rules:
        condition_value = rule.condition or rule.coherence
        condition = (
            json.dumps(dict(condition_value), sort_keys=True, separators=(",", ":"))
            if isinstance(condition_value, Mapping)
            else ""
        )
        require = (
            json.dumps(dict(rule.require), sort_keys=True, separators=(",", ":"))
            if isinstance(rule.require, Mapping)
            else ""
        )
        existing = decisions.get(rule.id, {column: "" for column in DECISION_COLUMNS})
        review = rule.review if isinstance(rule.review, Mapping) else {}
        row = {
            "rule_id": rule.id,
            "family": rule.family,
            "status": rule.status,
            "proposed_severity": rule.severity,
            "confidence": rule.confidence,
            "condition": condition,
            "require": require,
            "message": rule.message,
            "review_question": rule.review_question,
        }
        for column in DECISION_COLUMNS:
            row[column] = (existing.get(column) or "").strip() or str(review.get(column, "")).strip()
        writer.writerow(row)
    return buffer.getvalue()


def render_markdown_block(rules: tuple[ScenarioRule, ...], rules_path: Path) -> str:
    """Render the generated Markdown rule block."""

    severity = Counter(rule.severity for rule in rules)
    status = Counter(rule.status for rule in rules)
    families = list(dict.fromkeys(rule.family for rule in rules))
    lines = [
        BEGIN_MARKER,
        f"_Generated from `{_display_path(rules_path)}` "
        f"(SHA-256 `{rule_registry_sha256(rules_path)}`). Do not edit this block by hand; run "
        "`python scripts/build_rule_review_package.py`._",
        "",
        f"- Rules: {len(rules)}",
        "- Severity: " + ", ".join(f"{count} {name}" for name, count in sorted(severity.items())),
        "- Status: " + ", ".join(f"{count} {name}" for name, count in sorted(status.items())),
        "",
    ]
    for family in families:
        label = _FAMILY_LABELS.get(family, family.replace("_", " ").title())
        lines.extend(
            [
                f"### {label}",
                "",
                "| Rule | Status | Severity | Confidence | Condition | Requirement | Review question |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for rule in rules:
            if rule.family != family:
                continue
            condition = format_condition(rule.condition or rule.coherence)
            requirement = format_requirement(rule.require)
            lines.append(
                "| "
                + " | ".join(
                    (
                        _cell(rule.id),
                        _cell(rule.status),
                        _cell(rule.severity),
                        _cell(rule.confidence),
                        _code_cell(condition),
                        _code_cell(requirement),
                        _cell(rule.review_question),
                    )
                )
                + " |"
            )
        lines.append("")
    lines.append(END_MARKER)
    return "\n".join(lines).rstrip() + "\n"


def _extract_block(text: str) -> str:
    start = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if start < 0 or end < 0 or end < start:
        return ""
    return text[start : end + len(END_MARKER)]


def _replace_block(text: str, block: str) -> str:
    start = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)
    if start >= 0 and end >= start:
        return text[:start] + block + text[end + len(END_MARKER) :]
    rule_start = text.find("## Rule table")
    status_start = text.find("## Current status")
    if rule_start < 0 or status_start < 0 or status_start < rule_start:
        raise ValueError("review package needs a Rule table section and a Current status section")
    return text[:rule_start] + "## Rule table\n\n" + block + "\n" + text[status_start:]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if the tracked worksheet or Markdown block is out of date instead of writing.",
    )
    args = parser.parse_args(argv)

    rules = load_rule_registry(args.rules)
    expected_csv = render_csv(rules, args.csv)
    expected_block = render_markdown_block(rules, args.rules)
    markdown = args.markdown.read_text(encoding="utf-8")
    existing_block = _extract_block(markdown)

    if args.check:
        stale: list[str] = []
        if not args.csv.is_file() or args.csv.read_text(encoding="utf-8") != expected_csv:
            stale.append(str(args.csv))
        if existing_block != expected_block.strip():
            stale.append(str(args.markdown))
        if stale:
            print("Review package is out of date:")
            for path in stale:
                print(f"- {path}")
            print("Run: python scripts/build_rule_review_package.py")
            return 1
        print("Review package matches the rule registry.")
        return 0

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.csv.write_text(expected_csv, encoding="utf-8")
    updated = _replace_block(markdown, expected_block)
    args.markdown.write_text(updated, encoding="utf-8")
    print(f"Wrote {_display_path(args.csv)} and {_display_path(args.markdown)}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
