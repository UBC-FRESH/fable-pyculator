#!/usr/bin/env python
"""Filter an exact FABLE optimization dataset under provisional consistency rules."""

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
    evaluate_scenario,
    load_rule_registry,
    rule_registry_sha256,
    table_population_from_spec,
)

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """Filter and annotate one exact sample dataset."""

    args = _parser().parse_args(argv)
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    spec_payload = json.loads(args.spec.read_text(encoding="utf-8"))
    spec = spec_payload.get("spec", spec_payload)
    rules = load_rule_registry(args.rules)
    table_status = table_population_from_spec(spec)
    kept: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    warnings = 0
    rule_counts: Counter[str] = Counter()
    for sample in dataset.get("samples", []):
        if not isinstance(sample, dict) or "error" in sample:
            continue
        selections = sample.get("selections")
        if not isinstance(selections, dict):
            continue
        result = evaluate_scenario(selections, rules, table_status=table_status, mode=args.mode)
        annotated = dict(sample)
        annotated["rule_evaluation"] = result.to_dict()
        for hit in result.triggered:
            rule_counts[hit.rule_id] += 1
        if result.warnings or result.exploratory:
            warnings += 1
        if result.valid:
            kept.append(annotated)
        else:
            rejected.append(annotated)
    filtered = {
        **{key: value for key, value in dataset.items() if key != "samples"},
        "source_dataset": str(args.dataset),
        "source_dataset_sha256": _sha256(args.dataset),
        "rules": str(args.rules),
        "rules_sha256": rule_registry_sha256(args.rules),
        "rule_mode": args.mode,
        "provisional": True,
        "rejected_count": len(rejected),
        "warning_count": warnings,
        "rule_hits": dict(rule_counts.most_common()),
        "samples": kept,
        "rejected_samples": [
            {
                "sample_id": sample.get("sample_id"),
                "rule_evaluation": sample.get("rule_evaluation"),
            }
            for sample in rejected
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(filtered, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.rejected_output is not None:
        args.rejected_output.parent.mkdir(parents=True, exist_ok=True)
        args.rejected_output.write_text(
            json.dumps({"samples": rejected, "count": len(rejected)}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(
        f"samples: {len(dataset.get('samples', []))} input, {len(kept)} kept, "
        f"{len(rejected)} rejected, {warnings} with warnings"
    )
    print(f"output: {args.output}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--rules", type=Path, default=Path("planning/fable-scenario-consistency-rules.yaml"))
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("runtime/portal/specs/fable-2024.json"),
    )
    parser.add_argument(
        "--mode",
        choices=("approved", "exploratory", "draft_enforced"),
        default="draft_enforced",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rejected-output", type=Path, default=None)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
