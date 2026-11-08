"""Status-aware scenario-consistency rules for FABLE scenario selections."""

from __future__ import annotations

import hashlib
import itertools
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

__all__ = [
    "RuleEvaluation",
    "RuleHit",
    "ScenarioRule",
    "enumerate_domain",
    "evaluate_scenario",
    "load_rule_registry",
    "rule_registry_sha256",
    "table_population_from_spec",
]

_APPROVED = "approved"
_PROPOSED = "proposed"
_REJECTED = {"rejected", "superseded"}


@dataclass(frozen=True)
class ScenarioRule:
    """One reviewable scenario-consistency rule."""

    id: str
    family: str
    severity: str
    confidence: str
    status: str
    message: str
    review_question: str
    condition: Mapping[str, Any] | None = None
    require: Mapping[str, Any] | None = None
    coherence: Mapping[str, Any] | None = None
    review: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class RuleHit:
    """One rule consequence for a scenario."""

    rule_id: str
    family: str
    severity: str
    status: str
    message: str
    review_question: str


@dataclass(frozen=True)
class RuleEvaluation:
    """Rule consequences for one scenario."""

    errors: tuple[RuleHit, ...] = ()
    warnings: tuple[RuleHit, ...] = ()
    exploratory: tuple[RuleHit, ...] = ()

    @property
    def valid(self) -> bool:
        """Return whether no hard error was raised."""

        return not self.errors

    @property
    def triggered(self) -> tuple[RuleHit, ...]:
        """Return every triggered rule."""

        return self.errors + self.warnings + self.exploratory

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready result."""

        return {
            "valid": self.valid,
            "errors": [_hit_dict(hit) for hit in self.errors],
            "warnings": [_hit_dict(hit) for hit in self.warnings],
            "exploratory": [_hit_dict(hit) for hit in self.exploratory],
        }


def _hit_dict(hit: RuleHit) -> dict[str, str]:
    return {
        "rule_id": hit.rule_id,
        "family": hit.family,
        "severity": hit.severity,
        "status": hit.status,
        "message": hit.message,
        "review_question": hit.review_question,
    }


def load_rule_registry(path: str | Path) -> tuple[ScenarioRule, ...]:
    """Load the YAML rule registry into typed rules."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("rule registry must be a mapping")
    rules = payload.get("rules")
    if not isinstance(rules, list):
        raise ValueError("rule registry must contain a rules list")
    loaded: list[ScenarioRule] = []
    for item in rules:
        if not isinstance(item, Mapping):
            raise ValueError("each rule must be a mapping")
        status = str(item.get("status", "proposed"))
        severity = str(item.get("severity", "warning"))
        if severity not in {"error", "warning", "info"}:
            raise ValueError(f"invalid severity for {item.get('id')}: {severity}")
        loaded.append(
            ScenarioRule(
                id=str(item["id"]),
                family=str(item.get("family", "uncategorized")),
                severity=severity,
                confidence=str(item.get("confidence", "low")),
                status=status,
                message=str(item.get("message", "")),
                review_question=str(item.get("review_question", "")),
                condition=item.get("when"),
                require=item.get("require"),
                coherence=item.get("coherence"),
                review=item.get("review"),
            )
        )
    return tuple(loaded)


def rule_registry_sha256(path: str | Path) -> str:
    """Return the SHA-256 of the rule registry source."""

    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table_population_from_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Return populated column and row status for each scenario-definition table."""

    status: dict[str, Any] = {}
    for table in spec.get("scenario_definition_tables", []):
        if not isinstance(table, Mapping):
            continue
        name = table.get("name")
        columns = table.get("column_labels") or []
        values = table.get("values") or []
        if not isinstance(name, str):
            continue
        column_status: dict[str, bool] = {}
        row_status: dict[str, dict[str, bool]] = {}
        key_column: str | None = None
        for index, column in enumerate(columns):
            if not isinstance(column, str):
                continue
            column_status[column] = any(
                isinstance(row, Sequence)
                and not isinstance(row, (str, bytes))
                and index < len(row)
                and row[index] not in (None, "")
                for row in values
            )
        if columns and isinstance(columns[0], str):
            key_column = columns[0]
            for row in values:
                if not isinstance(row, Sequence) or isinstance(row, (str, bytes)) or not row:
                    continue
                key = str(row[0])
                row_columns = row_status.setdefault(key, {})
                for index, column in enumerate(columns):
                    if not isinstance(column, str):
                        continue
                    populated = index < len(row) and row[index] not in (None, "")
                    row_columns[column] = row_columns.get(column, False) or populated
        status[name] = {"columns": column_status, "rows": row_status, "key_column": key_column}
    return status


def evaluate_scenario(
    selections: Mapping[str, Any],
    rules: Iterable[ScenarioRule],
    *,
    table_status: Mapping[str, Any] | None = None,
    mode: str = "exploratory",
) -> RuleEvaluation:
    """Evaluate one scenario under approved, exploratory, or draft-enforced semantics."""

    if mode not in {"approved", "exploratory", "draft_enforced"}:
        raise ValueError("mode must be approved, exploratory, or draft_enforced")
    errors: list[RuleHit] = []
    warnings: list[RuleHit] = []
    exploratory: list[RuleHit] = []
    for rule in rules:
        if rule.status in _REJECTED:
            continue
        triggered = _rule_triggers(rule, selections, table_status)
        if not triggered:
            continue
        hit = RuleHit(
            rule_id=rule.id,
            family=rule.family,
            severity=rule.severity,
            status=rule.status,
            message=rule.message,
            review_question=rule.review_question,
        )
        if rule.status == _APPROVED:
            (errors if rule.severity == "error" else warnings).append(hit)
        elif mode == "draft_enforced":
            (errors if rule.severity == "error" else warnings).append(hit)
        else:
            exploratory.append(hit)
    return RuleEvaluation(tuple(errors), tuple(warnings), tuple(exploratory))


def _rule_triggers(
    rule: ScenarioRule,
    selections: Mapping[str, Any],
    table_status: Mapping[str, Any] | None,
) -> bool:
    if rule.coherence is not None:
        return _coherence_triggers(rule.coherence, selections)
    if rule.require is not None:
        condition = rule.condition
        if condition is not None and not _matches_condition(condition, selections):
            return False
        return _requirement_fails(rule.require, table_status, selections)
    if rule.condition is not None:
        return _matches_condition(rule.condition, selections)
    return False


def _matches_condition(condition: Mapping[str, Any], selections: Mapping[str, Any]) -> bool:
    if "all" in condition:
        return all(_matches_condition(item, selections) for item in condition["all"])
    if "any" in condition:
        return any(_matches_condition(item, selections) for item in condition["any"])
    switch = condition.get("switch")
    if not isinstance(switch, str):
        return False
    value = selections.get(switch)
    if "in" in condition:
        return any(_matches_value(value, expected) for expected in condition["in"])
    if "not_in" in condition:
        return not any(_matches_value(value, expected) for expected in condition["not_in"])
    if "equals" in condition:
        return _matches_value(value, condition["equals"])
    return False


def _matches_value(value: Any, expected: Any) -> bool:
    if expected is True:
        return value in {True, 1, "1", "yes", "Yes", "true", "True"}
    if expected is False:
        return value in {False, 0, "0", "no", "No", "false", "False"}
    return str(value) == str(expected)


def _requirement_fails(
    require: Mapping[str, Any],
    table_status: Mapping[str, Any] | None,
    selections: Mapping[str, Any] | None = None,
) -> bool:
    if table_status is None:
        return True
    table = require.get("table")
    if not isinstance(table, str) or table not in table_status:
        return True
    entry = table_status[table]
    if not isinstance(entry, Mapping):
        return True
    key_value = require.get("key_value")
    key_switch = require.get("key_switch")
    if key_switch is not None:
        if not isinstance(key_switch, str) or not isinstance(selections, Mapping):
            return True
        key_value = selections.get(key_switch)
        if key_value is None or str(key_value) == "":
            return True
    if key_value is not None:
        rows = entry.get("rows") or {}
        columns = rows.get(str(key_value)) if isinstance(rows, Mapping) else None
        if not isinstance(columns, Mapping):
            return True
    else:
        columns = entry.get("columns") or {}
    required = require.get("non_null_columns") or []
    if not isinstance(required, list):
        return True
    return not all(columns.get(str(column), False) for column in required)


def _coherence_triggers(coherence: Mapping[str, Any], selections: Mapping[str, Any]) -> bool:
    if coherence.get("rule") != "equal_when_all_in_ssp_1_3":
        return False
    switches = coherence.get("switches") or []
    if not isinstance(switches, list):
        return False
    values = [str(selections.get(name)) for name in switches if selections.get(name) is not None]
    if len(values) != len(switches):
        return False
    if not all(value in {"SSP1", "SSP2", "SSP3"} for value in values):
        return False
    return len(set(values)) > 1


def enumerate_domain(
    controls: Sequence[Mapping[str, Any]],
    baseline: Mapping[str, Any],
    rules: Iterable[ScenarioRule],
    *,
    table_status: Mapping[str, Any] | None = None,
    mode: str = "exploratory",
) -> dict[str, Any]:
    """Enumerate a small control domain and count rule outcomes."""

    names = [str(control["name"]) for control in controls]
    options = [[str(option) for option in control.get("options", [])] for control in controls]
    total = 0
    valid = 0
    warning_only = 0
    invalid = 0
    rule_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    for values in itertools.product(*options):
        selections = dict(baseline)
        selections.update(dict(zip(names, values)))
        result = evaluate_scenario(selections, rules, table_status=table_status, mode=mode)
        total += 1
        if result.valid:
            valid += 1
            if result.warnings or result.exploratory:
                warning_only += 1
        else:
            invalid += 1
        for hit in result.triggered:
            rule_counts[hit.rule_id] += 1
            family_counts[hit.family] += 1
    return {
        "controls": names,
        "total": total,
        "valid": valid,
        "warning_only": warning_only,
        "invalid": invalid,
        "valid_fraction": (valid / total) if total else 0.0,
        "mode": mode,
        "rule_hits": dict(rule_counts.most_common()),
        "family_hits": dict(family_counts.most_common()),
    }
