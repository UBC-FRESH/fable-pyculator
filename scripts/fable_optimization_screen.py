#!/usr/bin/env python
"""Summarize one-at-a-time FABLE control effects and freeze a reduced set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """Rank control effects and write the reduced control list."""

    args = _parser().parse_args(argv)
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    samples = [sample for sample in dataset["samples"] if "error" not in sample]
    baseline = next(sample for sample in samples if sample.get("sample_kind") == "baseline")
    base_objectives = baseline["objectives"]
    rows = []
    for sample in samples:
        if sample.get("sample_kind") != "one-at-a-time":
            continue
        objectives = sample["objectives"]
        changes = {}
        for name, value in objectives.items():
            base = base_objectives.get(name)
            if value is None or base in (None, 0):
                changes[name] = None
                continue
            changes[name] = (float(value) - float(base)) / abs(float(base))
        food = abs(changes.get("food_total_kcal_feas") or 0.0)
        ghg = abs(changes.get("ghg_total_co2e") or 0.0)
        land = abs(changes.get("land_total_area") or 0.0)
        score = max(food, ghg) + 0.1 * land
        rows.append(
            {
                "control": sample["control_name"],
                "baseline_value": sample.get("baseline_value"),
                "variant_value": sample.get("variant_value"),
                "baseline_objectives": base_objectives,
                "variant_objectives": objectives,
                "relative_change": changes,
                "score": score,
            }
        )
    rows.sort(key=lambda row: row["score"], reverse=True)
    selected = [row["control"] for row in rows[: args.top]]
    result = {
        "dataset": str(args.dataset),
        "baseline_objectives": base_objectives,
        "ranked_controls": rows,
        "selected_controls": selected,
        "top": args.top,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.controls_output is not None:
        args.controls_output.write_text(json.dumps(selected, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(
            f"{row['control']:24s} score={row['score']:.4f} "
            f"baseline={row['baseline_value']!r} variant={row['variant_value']!r} "
            f"food={row['relative_change'].get('food_total_kcal_feas')} "
            f"ghg={row['relative_change'].get('ghg_total_co2e')}"
        )
    print("selected:", ", ".join(selected))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True, help="One-at-a-time dataset JSON.")
    parser.add_argument("--output", type=Path, required=True, help="Screen summary JSON.")
    parser.add_argument("--controls-output", type=Path, default=None, help="Reduced control list JSON.")
    parser.add_argument("--top", type=int, default=10, help="Number of controls to keep.")
    return parser


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
