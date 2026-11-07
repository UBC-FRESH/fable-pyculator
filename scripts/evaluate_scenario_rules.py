#!/usr/bin/env python
"""Audit FABLE scenarios and enumerate a reduced domain under consistency rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

from fable_pyculator.scenario_rules import (  # noqa: E402
    enumerate_domain,
    evaluate_scenario,
    load_rule_registry,
    rule_registry_sha256,
    table_population_from_spec,
)

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """Run the rule audit."""

    args = _parser().parse_args(argv)
    spec_payload = json.loads(args.spec.read_text(encoding="utf-8"))
    spec = spec_payload.get("spec", spec_payload)
    rules = load_rule_registry(args.rules)
    table_status = table_population_from_spec(spec)
    controls = _controls(spec)
    selected_names = None
    baseline = {control["name"]: control["default"] for control in controls}
    samples: list[dict[str, object]] = []
    dataset_sha = None
    dataset_path = None
    if args.dataset is not None:
        dataset_path = str(args.dataset)
        dataset_sha = _sha256(args.dataset)
        dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
        samples = [sample for sample in dataset.get("samples", []) if "error" not in sample]
        baseline = dataset.get("baseline_selections") or baseline
        selected_names = dataset.get("variable_controls")
    if args.controls_file is not None:
        payload = json.loads(args.controls_file.read_text(encoding="utf-8"))
        selected_names = payload.get("controls", payload) if isinstance(payload, dict) else payload
    if selected_names is not None:
        selected = set(selected_names)
        controls = [control for control in controls if control["name"] in selected]
        # Keep the file order, not the spec order.
        order = {name: index for index, name in enumerate(selected_names)}
        controls.sort(key=lambda control: order.get(control["name"], len(order)))
    audit = _audit_samples(samples, rules, table_status, args.mode) if samples else None
    domain = None
    if not args.no_domain and controls:
        domain = enumerate_domain(controls, baseline, rules, table_status=table_status, mode=args.mode)
    payload = {
        "rules": str(args.rules),
        "rules_sha256": rule_registry_sha256(args.rules),
        "spec": str(args.spec),
        "spec_sha256": _sha256(args.spec),
        "dataset": dataset_path,
        "dataset_sha256": dataset_sha,
        "mode": args.mode,
        "rule_count": len(rules),
        "rule_status_counts": dict(Counter(rule.status for rule in rules)),
        "table_status": table_status,
        "audit": audit,
        "domain": domain,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"rules: {len(rules)} ({payload['rule_status_counts']})")
    if audit is not None:
        print(f"samples: {audit['total']} total, {audit['valid']} valid, {audit['invalid']} invalid")
        print(f"top rule hits: {list(audit['rule_hits'].items())[:8]}")
    if domain is not None:
        print(
            f"domain: {domain['total']} total, {domain['valid']} valid, "
            f"{domain['invalid']} invalid, {domain['valid_fraction']:.4f} valid fraction"
        )
    print(f"output: {args.output}")
    return 0


def _controls(spec: dict[str, object]) -> list[dict[str, object]]:
    controls = []
    for control in spec.get("selection_controls", []):
        if not isinstance(control, dict):
            continue
        controls.append(
            {
                "name": str(control["name"]),
                "options": [str(option["value"]) for option in control.get("options", [])],
                "default": str(control.get("default")),
            }
        )
    return controls


def _audit_samples(
    samples: list[dict[str, object]],
    rules: object,
    table_status: object,
    mode: str,
) -> dict[str, object]:
    errors = 0
    warnings = 0
    exploratory = 0
    invalid_ids = []
    rule_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    for sample in samples:
        selections = sample.get("selections") or {}
        if not isinstance(selections, dict):
            continue
        result = evaluate_scenario(selections, rules, table_status=table_status, mode=mode)
        if not result.valid:
            errors += 1
            invalid_ids.append(str(sample.get("sample_id")))
        if result.warnings:
            warnings += 1
        if result.exploratory:
            exploratory += 1
        for hit in result.triggered:
            rule_counts[hit.rule_id] += 1
            family_counts[hit.family] += 1
    return {
        "total": len(samples),
        "valid": len(samples) - errors,
        "invalid": errors,
        "with_warnings": warnings,
        "with_exploratory": exploratory,
        "invalid_sample_ids": invalid_ids,
        "rule_hits": dict(rule_counts.most_common()),
        "family_hits": dict(family_counts.most_common()),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rules",
        type=Path,
        default=Path("planning/fable-scenario-consistency-rules.yaml"),
    )
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("runtime/portal/specs/fable-2024.json"),
        help="Prepared 2024 spec JSON, or a raw spec mapping.",
    )
    parser.add_argument("--dataset", type=Path, default=None, help="Optional exact sample dataset.")
    parser.add_argument("--controls-file", type=Path, default=None, help="Optional reduced control list.")
    parser.add_argument(
        "--mode",
        choices=("approved", "exploratory", "draft_enforced"),
        default="exploratory",
    )
    parser.add_argument("--no-domain", action="store_true", help="Skip domain enumeration.")
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
