from __future__ import annotations

import csv
import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path

import yaml

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


def _review_generator():
    path = Path("scripts/build_rule_review_package.py").resolve()
    spec = importlib.util.spec_from_file_location("build_rule_review_package", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_import(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/import_rule_review_decisions.py", *args],
        capture_output=True,
        text=True,
    )


def test_rule_review_import_dry_run_write_and_round_trip(tmp_path: Path) -> None:
    rules_path = tmp_path / "rules.yaml"
    rules_path.write_text(
        Path("planning/fable-scenario-consistency-rules.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    worksheet = tmp_path / "review.csv"
    worksheet.write_text(
        "rule_id,decision,reviewer,comments\n"
        "CUSTOM-DIET-001,approve_error,Reviewer A,Keep as hard error\n"
        "LAND-AFFOR-001,approve_warning,Reviewer B,Warning only\n"
        "LIVE-DENS-001,reject,Reviewer C,Not a real conflict\n"
        "NARRATIVE-SSP-001,defer,Reviewer D,Needs climate expert\n"
        "AGPRAC-CROP-001,replace,Reviewer E,Rewrite for organic systems\n",
        encoding="utf-8",
    )
    original = rules_path.read_text(encoding="utf-8")

    dry = _run_import("--rules", str(rules_path), "--worksheet", str(worksheet), "--json")
    assert dry.returncode == 0, dry.stderr
    dry_payload = json.loads(dry.stdout)
    assert dry_payload["written"] is False
    assert len(dry_payload["changes"]) == 5
    assert rules_path.read_text(encoding="utf-8") == original

    written = _run_import(
        "--rules",
        str(rules_path),
        "--worksheet",
        str(worksheet),
        "--write",
        "--no-refresh",
        "--json",
    )
    assert written.returncode == 0, written.stderr
    assert json.loads(written.stdout)["written"] is True
    updated = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
    by_id = {rule["id"]: rule for rule in updated["rules"]}
    assert by_id["CUSTOM-DIET-001"]["status"] == "approved"
    assert by_id["CUSTOM-DIET-001"]["severity"] == "error"
    assert by_id["CUSTOM-DIET-001"]["review"]["reviewer"] == "Reviewer A"
    assert by_id["LAND-AFFOR-001"]["status"] == "approved"
    assert by_id["LAND-AFFOR-001"]["severity"] == "warning"
    assert by_id["LIVE-DENS-001"]["status"] == "rejected"
    assert by_id["NARRATIVE-SSP-001"]["status"] == "proposed"
    assert by_id["NARRATIVE-SSP-001"]["review"]["decision"] == "defer"
    assert by_id["AGPRAC-CROP-001"]["status"] == "proposed"
    assert by_id["AGPRAC-CROP-001"]["review"]["decision"] == "replace"
    assert rules_path.read_text(encoding="utf-8").startswith("# DRAFT rule registry")
    decided_at = by_id["CUSTOM-DIET-001"]["review"]["decided_at"]

    repeated = _run_import(
        "--rules",
        str(rules_path),
        "--worksheet",
        str(worksheet),
        "--write",
        "--no-refresh",
        "--json",
    )
    assert repeated.returncode == 0, repeated.stderr
    repeated_payload = json.loads(repeated.stdout)
    assert repeated_payload["changes"] == []
    assert repeated_payload["written"] is False
    assert yaml.safe_load(rules_path.read_text(encoding="utf-8"))["rules"][0]["review"]["decided_at"] == decided_at

    generator = _review_generator()
    imported_rules = load_rule_registry(rules_path)
    rendered = generator.render_csv(imported_rules, tmp_path / "new-worksheet.csv")
    rows = {row["rule_id"]: row for row in csv.DictReader(io.StringIO(rendered))}
    assert rows["CUSTOM-DIET-001"]["status"] == "approved"
    assert rows["CUSTOM-DIET-001"]["decision"] == "approve_error"
    assert rows["CUSTOM-DIET-001"]["reviewer"] == "Reviewer A"
    assert rows["AGPRAC-CROP-001"]["decision"] == "replace"


def test_rule_review_import_fails_closed(tmp_path: Path) -> None:
    rules_path = tmp_path / "rules.yaml"
    rules_path.write_text(
        Path("planning/fable-scenario-consistency-rules.yaml").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    original = rules_path.read_text(encoding="utf-8")
    cases = {
        "unknown.csv": "rule_id,decision,reviewer,comments\nUNKNOWN,approve_error,Reviewer,\n",
        "missing-reviewer.csv": "rule_id,decision,reviewer,comments\nCUSTOM-DIET-001,approve_error,,\n",
        "invalid.csv": "rule_id,decision,reviewer,comments\nCUSTOM-DIET-001,approve,Reviewer,\n",
    }
    for filename, contents in cases.items():
        worksheet = tmp_path / filename
        worksheet.write_text(contents, encoding="utf-8")
        result = _run_import(
            "--rules",
            str(rules_path),
            "--worksheet",
            str(worksheet),
            "--write",
            "--no-refresh",
            "--json",
        )
        assert result.returncode == 2
        assert json.loads(result.stdout)["errors"]
        assert rules_path.read_text(encoding="utf-8") == original


def test_review_package_matches_rule_registry() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_rule_review_package.py", "--check"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_review_check_detects_drift(tmp_path: Path) -> None:
    markdown = tmp_path / "review.md"
    markdown.write_text(
        "## Rule table\n\nstale\n\n## Current status\n\nstale\n",
        encoding="utf-8",
    )
    worksheet = tmp_path / "review.csv"
    worksheet.write_text("stale\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_rule_review_package.py",
            "--check",
            "--markdown",
            str(markdown),
            "--csv",
            str(worksheet),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "out of date" in result.stdout


def test_review_worksheet_preserves_decisions(tmp_path: Path) -> None:
    generator = _review_generator()
    rules = load_rule_registry(Path("planning/fable-scenario-consistency-rules.yaml"))
    worksheet = tmp_path / "review.csv"
    worksheet.write_text(
        "rule_id,decision,reviewer,comments\nCUSTOM-DIET-001,approve_error,Reviewer,Keep this rule\n",
        encoding="utf-8",
    )

    rendered = generator.render_csv(rules, worksheet)
    rows = list(csv.DictReader(io.StringIO(rendered)))
    row = next(item for item in rows if item["rule_id"] == "CUSTOM-DIET-001")

    assert row["decision"] == "approve_error"
    assert row["reviewer"] == "Reviewer"
    assert row["comments"] == "Keep this rule"
    assert generator.format_condition({"switch": "x", "in": ["a", "b"]}) == "x in {a, b}"


def test_real_rule_registry_loads() -> None:
    path = Path("planning/fable-scenario-consistency-rules.yaml")
    rules = load_rule_registry(path)

    assert len(rules) == 18
    assert all(rule.status == "proposed" for rule in rules)
    assert rule_registry_sha256(path)
    assert any(rule.require and rule.require.get("key_value") for rule in rules)
    assert any(rule.require and rule.require.get("key_switch") for rule in rules)
