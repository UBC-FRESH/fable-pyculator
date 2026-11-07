from __future__ import annotations

from pathlib import Path

from fable_pyculator.scenario_rules import (
    enumerate_domain,
    evaluate_scenario,
    load_rule_registry,
    rule_registry_sha256,
    table_population_from_spec,
)

RULES = """
rules:
  - id: HARD-001
    family: test
    severity: error
    confidence: high
    status: approved
    when:
      switch: a
      in: [bad]
    message: "a=bad is invalid"
    review_question: "Is this truly invalid?"
  - id: SOFT-001
    family: test
    severity: warning
    confidence: low
    status: proposed
    when:
      switch: b
      in: [warn]
    message: "b=warn is unusual"
    review_question: "Is this a warning?"
  - id: REJECTED-001
    family: test
    severity: error
    confidence: low
    status: rejected
    when:
      switch: a
      in: [bad]
    message: "rejected rule"
    review_question: "n/a"
  - id: CUSTOM-001
    family: custom
    severity: error
    confidence: high
    status: proposed
    when:
      switch: c
      in: [custom]
    require:
      table: custom_table
      key_value: custom
      non_null_columns: [value]
    message: "custom requires values"
    review_question: "Which columns are required?"
"""


def _rules(path: Path):
    path.write_text(RULES, encoding="utf-8")
    return load_rule_registry(path)


def test_approved_error_proposed_warning_and_rejected_rule(tmp_path: Path) -> None:
    rules = _rules(tmp_path / "rules.yaml")

    approved = evaluate_scenario({"a": "bad", "b": "ok"}, rules, mode="approved")
    exploratory = evaluate_scenario({"a": "ok", "b": "warn"}, rules, mode="exploratory")
    rejected = evaluate_scenario({"a": "bad", "b": "ok"}, rules, mode="draft_enforced")

    assert not approved.valid
    assert [hit.rule_id for hit in approved.errors] == ["HARD-001"]
    assert exploratory.valid
    assert [hit.rule_id for hit in exploratory.exploratory] == ["SOFT-001"]
    assert [hit.rule_id for hit in rejected.errors] == ["HARD-001"]


def test_table_population_is_checked_per_key(tmp_path: Path) -> None:
    rules = _rules(tmp_path / "rules.yaml")
    spec = {
        "scenario_definition_tables": [
            {
                "name": "custom_table",
                "column_labels": ["key", "value"],
                "values": [["custom", None], ["other", 1]],
            }
        ]
    }
    status = table_population_from_spec(spec)
    result = evaluate_scenario({"c": "custom"}, rules, table_status=status, mode="draft_enforced")

    assert status["custom_table"]["rows"]["custom"]["value"] is False
    assert status["custom_table"]["rows"]["other"]["value"] is True
    assert [hit.rule_id for hit in result.errors] == ["CUSTOM-001"]


def test_enumerate_domain_counts_valid_and_invalid(tmp_path: Path) -> None:
    rules = _rules(tmp_path / "rules.yaml")
    controls = [
        {"name": "a", "options": ["ok", "bad"]},
        {"name": "b", "options": ["ok", "warn"]},
    ]

    result = enumerate_domain(controls, {"a": "ok", "b": "ok", "c": ""}, rules, mode="approved")

    assert result["total"] == 4
    assert result["invalid"] == 2
    assert result["valid"] == 2


def test_real_rule_registry_loads() -> None:
    path = Path("planning/fable-scenario-consistency-rules.yaml")
    rules = load_rule_registry(path)

    assert len(rules) == 18
    assert all(rule.status == "proposed" for rule in rules)
    assert rule_registry_sha256(path)
    assert any(rule.require and rule.require.get("key_value") for rule in rules)
