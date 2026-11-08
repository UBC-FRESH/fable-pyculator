from __future__ import annotations

from pathlib import Path

from fable_pyculator.scenario_rules import (
    ScenarioRule,
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
  - id: EXPORT-001
    family: custom
    severity: error
    confidence: high
    status: proposed
    when:
      switch: export
      in: [MyExportScen, MyExportScen2]
    require:
      table: export_table
      key_switch: export
      non_null_columns: [shift]
    message: "selected export row requires values"
    review_question: "Is the selected row populated?"
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


def test_key_switch_checks_the_selected_row(tmp_path: Path) -> None:
    rules = _rules(tmp_path / "rules.yaml")
    status = table_population_from_spec(
        {
            "scenario_definition_tables": [
                {
                    "name": "export_table",
                    "column_labels": ["key", "shift"],
                    "values": [["MyExportScen", 1], ["MyExportScen2", None]],
                }
            ]
        }
    )

    missing = evaluate_scenario({"export": "MyExportScen2"}, rules, table_status=status, mode="draft_enforced")
    populated = evaluate_scenario({"export": "MyExportScen"}, rules, table_status=status, mode="draft_enforced")

    assert [hit.rule_id for hit in missing.errors] == ["EXPORT-001"]
    assert "EXPORT-001" not in [hit.rule_id for hit in populated.errors]


def test_key_switch_fails_closed_without_a_selection() -> None:
    rule = ScenarioRule(
        id="EXPORT-MISSING-001",
        family="custom",
        severity="error",
        confidence="high",
        status="proposed",
        message="selected row requires values",
        review_question="Is the selected row populated?",
        require={
            "table": "export_table",
            "key_switch": "export",
            "non_null_columns": ["shift"],
        },
    )
    status = table_population_from_spec(
        {
            "scenario_definition_tables": [
                {"name": "export_table", "column_labels": ["key", "shift"], "values": [["x", 1]]}
            ]
        }
    )

    result = evaluate_scenario({}, (rule,), table_status=status, mode="draft_enforced")

    assert [hit.rule_id for hit in result.errors] == ["EXPORT-MISSING-001"]


def test_real_custom_export_rule_uses_selected_key() -> None:
    rules = load_rule_registry(Path("planning/fable-scenario-consistency-rules.yaml"))
    status = table_population_from_spec(
        {
            "scenario_definition_tables": [
                {
                    "name": "scenarios_definition_expscentarget",
                    "column_labels": ["key", "shift_2050"],
                    "values": [
                        ["MyExportScen", 1],
                        ["MyExportScen2", None],
                        ["MyExportScen3", 1],
                    ],
                }
            ]
        }
    )

    missing = evaluate_scenario({"scen_exports": "MyExportScen2"}, rules, table_status=status, mode="draft_enforced")
    populated = evaluate_scenario({"scen_exports": "MyExportScen3"}, rules, table_status=status, mode="draft_enforced")

    assert "CUSTOM-EXPORT-001" in [hit.rule_id for hit in missing.errors]
    assert "CUSTOM-EXPORT-001" not in [hit.rule_id for hit in populated.errors]


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
    assert any(rule.require and rule.require.get("key_switch") for rule in rules)
