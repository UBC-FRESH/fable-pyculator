#!/usr/bin/env python
"""Import completed expert-review worksheet decisions into the YAML rule registry.

The worksheet is the input; the YAML registry is the machine-readable source. Decisions are
self-declared provenance, not authenticated approval.

Dry-run is the default. Use ``--write`` to apply status/severity/provenance changes and refresh the
generated review package.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

__all__ = ["main", "plan_import"]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "planning" / "fable-scenario-consistency-rules.yaml"
DEFAULT_WORKSHEET = ROOT / "planning" / "fable-scenario-consistency-review-package.csv"

_DECISIONS = {"approve_error", "approve_warning", "reject", "defer", "replace"}
_MANUAL_DECISIONS = {"defer", "replace"}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _worksheet_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = {"rule_id", "decision", "reviewer", "comments"} - fields
        if missing:
            raise ValueError("worksheet is missing columns: " + ", ".join(sorted(missing)))
        return [dict(row) for row in reader]


def _prefix_comment_block(text: str) -> list[str]:
    prefix: list[str] = []
    for line in text.splitlines():
        if line.startswith("#") or (not line.strip() and prefix):
            prefix.append(line)
            continue
        break
    return prefix


def _dump_yaml(payload: dict[str, Any], original: str) -> str:
    prefix = _prefix_comment_block(original)
    body = yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )
    return ("\n".join(prefix) + "\n" if prefix else "") + body


def _review_decision(rule: Any, row: dict[str, str], now: str) -> tuple[dict[str, Any], str | None, str | None]:
    decision = _clean(row.get("decision")).lower()
    reviewer = _clean(row.get("reviewer"))
    comments = _clean(row.get("comments"))
    if decision not in _DECISIONS:
        raise ValueError(f"invalid decision {decision!r}")
    if not reviewer:
        raise ValueError("reviewer is required for every non-blank decision")
    existing = rule.get("review") if isinstance(rule.get("review"), dict) else {}
    same = (
        _clean(existing.get("decision")).lower() == decision
        and _clean(existing.get("reviewer")) == reviewer
        and _clean(existing.get("comments")) == comments
    )
    decided_at = str(existing.get("decided_at") or now) if same else now
    review = {
        "decision": decision,
        "reviewer": reviewer,
        "comments": comments,
        "decided_at": decided_at,
    }
    if decision == "approve_error":
        return review, "approved", "error"
    if decision == "approve_warning":
        return review, "approved", "warning"
    if decision == "reject":
        return review, "rejected", None
    return review, None, None


def plan_import(
    *,
    rules_payload: dict[str, Any],
    rows: list[dict[str, str]],
    now: str | None = None,
) -> dict[str, Any]:
    """Build a validation and change plan without mutating the payload."""

    timestamp = now or datetime.now(UTC).isoformat(timespec="seconds")
    rules = rules_payload.get("rules")
    if not isinstance(rules, list):
        raise ValueError("registry needs a rules list")
    by_id: dict[str, dict[str, Any]] = {}
    for rule in rules:
        if isinstance(rule, dict) and isinstance(rule.get("id"), str):
            by_id[rule["id"]] = rule
    errors: list[str] = []
    changes: list[dict[str, Any]] = []
    manual: list[str] = []
    deferred: list[str] = []
    no_decision: list[str] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        rule_id = _clean(row.get("rule_id"))
        if not rule_id:
            if _clean(row.get("decision")) or _clean(row.get("reviewer")) or _clean(row.get("comments")):
                errors.append(f"row {index}: rule_id is required when a decision is present")
            continue
        if rule_id in seen:
            errors.append(f"row {index}: duplicate rule_id {rule_id!r}")
            continue
        seen.add(rule_id)
        rule = by_id.get(rule_id)
        if rule is None:
            errors.append(f"row {index}: unknown rule_id {rule_id!r}")
            continue
        decision = _clean(row.get("decision")).lower()
        if not decision:
            no_decision.append(rule_id)
            continue
        try:
            review, next_status, next_severity = _review_decision(rule, row, timestamp)
        except ValueError as error:
            errors.append(f"row {index} ({rule_id}): {error}")
            continue
        before_status = str(rule.get("status", "proposed"))
        before_severity = str(rule.get("severity", "warning"))
        after_status = next_status or before_status
        after_severity = next_severity or before_severity
        changed = before_status != after_status or before_severity != after_severity or rule.get("review") != review
        if changed:
            changes.append(
                {
                    "rule_id": rule_id,
                    "decision": decision,
                    "before_status": before_status,
                    "after_status": after_status,
                    "before_severity": before_severity,
                    "after_severity": after_severity,
                    "review": review,
                    "manual": decision in _MANUAL_DECISIONS,
                }
            )
            if decision in _MANUAL_DECISIONS:
                manual.append(rule_id)
        if decision == "defer":
            deferred.append(rule_id)
    return {
        "rules": len(rules),
        "errors": errors,
        "changes": changes,
        "manual": manual,
        "deferred": deferred,
        "no_decision": no_decision,
    }


def _apply_plan(rules_payload: dict[str, Any], changes: list[dict[str, Any]]) -> None:
    by_id = {
        str(rule["id"]): rule
        for rule in rules_payload.get("rules", [])
        if isinstance(rule, dict) and isinstance(rule.get("id"), str)
    }
    for change in changes:
        rule = by_id[change["rule_id"]]
        rule["status"] = change["after_status"]
        rule["severity"] = change["after_severity"]
        rule["review"] = change["review"]


def _print_human(result: dict[str, Any], *, write: bool) -> None:
    mode = "write" if write else "dry run (no files written; pass --write to apply)"
    print(f"Rule decision import: {mode}")
    for change in result["changes"]:
        suffix = " [manual follow-up]" if change["manual"] else ""
        print(
            f"- {change['rule_id']}: {change['before_status']}/{change['before_severity']} -> "
            f"{change['after_status']}/{change['after_severity']} "
            f"({change['decision']}, {change['review']['reviewer']}){suffix}"
        )
    if not result["changes"]:
        print("- No registry changes.")
    if result["no_decision"]:
        print(f"- No decision: {len(result['no_decision'])} rule(s)")
    if result["manual"]:
        print("- Manual follow-up required: " + ", ".join(result["manual"]))
    if result.get("package_refreshed"):
        print("- Review package refreshed.")
    elif result.get("refresh_skipped"):
        print("- Review package refresh skipped for a custom rules path.")
    if result["errors"]:
        print("- Errors:")
        for error in result["errors"]:
            print(f"  - {error}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--worksheet", type=Path, default=DEFAULT_WORKSHEET)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply the plan to the registry and refresh the generated package.",
    )
    parser.add_argument("--no-refresh", action="store_true", help="Skip regenerating the review package.")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable plan/result.")
    args = parser.parse_args(argv)

    try:
        original = args.rules.read_text(encoding="utf-8")
        payload = yaml.safe_load(original)
        if not isinstance(payload, dict):
            raise ValueError("registry must be a mapping")
        rows = _worksheet_rows(args.worksheet)
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"Could not read the rule registry or worksheet: {error}", file=sys.stderr)
        return 2

    result = plan_import(rules_payload=payload, rows=rows)
    result["written"] = False
    if result["errors"]:
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            _print_human(result, write=args.write)
        return 2
    if args.write and result["changes"]:
        _apply_plan(payload, result["changes"])
        updated = _dump_yaml(payload, original)
        temporary = args.rules.with_name(f".{args.rules.name}.{uuid.uuid4().hex}.tmp")
        temporary.write_text(updated, encoding="utf-8")
        temporary.replace(args.rules)
        result["written"] = bool(result["changes"])
        result["package_refreshed"] = False
        if result["changes"] and not args.no_refresh:
            if args.rules.resolve() != DEFAULT_RULES.resolve():
                result["refresh_skipped"] = "custom rules path"
            else:
                refreshed = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "build_rule_review_package.py")],
                    capture_output=True,
                    text=True,
                )
                if refreshed.returncode != 0:
                    print(refreshed.stdout + refreshed.stderr, file=sys.stderr)
                    return 2
                result["package_refreshed"] = True
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_human(result, write=args.write)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
