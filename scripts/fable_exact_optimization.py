#!/usr/bin/env python
"""Exhaustively evaluate a narrow FABLE policy domain through the exact Pyculator.

This is the exact fallback for the surrogate pilot. It never predicts objectives: every reported
point is a real Pyculator run. The domain is explicit and narrow, so results must not be presented as
a full FABLE optimization.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

__all__ = ["main", "pareto_front", "unique_objective_points", "weighted_ranking"]

OBJECTIVES = ("food_total_kcal_feas", "ghg_total_co2e", "land_total_area")
# Food is maximized; GHG and land are minimized.
DIRECTIONS = {"food_total_kcal_feas": 1.0, "ghg_total_co2e": -1.0, "land_total_area": -1.0}
DEFAULT_ASPIRATIONS = {"food_total_kcal_feas": 1.0, "ghg_total_co2e": 0.0, "land_total_area": 0.25}
DEFAULT_WEIGHTS = {"food_total_kcal_feas": 1.0, "ghg_total_co2e": 1.0, "land_total_area": 1.0}
DEFAULT_CONTROLS = ("land_scen", "diet_scen", "fixtrade_scen", "livedens_scen")


def main(argv: list[str] | None = None) -> int:
    """Enumerate, evaluate, and rank one narrow exact policy domain."""

    args = _parser().parse_args(argv)
    root = _repo_root()
    output_dir = (args.output_dir if args.output_dir.is_absolute() else root / args.output_dir).resolve()
    selections_dir = output_dir / "selections"
    samples_dir = output_dir / "samples"
    logs_dir = output_dir / "logs"
    for directory in (output_dir, selections_dir, samples_dir, logs_dir):
        directory.mkdir(parents=True, exist_ok=True)

    from fable_pyculator.notebook import build_notebook_spec
    from fable_pyculator.scenario_rules import (
        evaluate_scenario,
        load_rule_registry,
        rule_registry_sha256,
        table_population_from_spec,
    )
    from fable_pyculator.web.artifacts import artifact_paths
    from fable_pyculator.web.spec_io import spec_to_payload

    paths = artifact_paths(root, args.version)
    if not paths.workbook.is_file() or not paths.generated_model.is_file():
        raise FileNotFoundError(
            f"need both workbook and generated model under {paths.workbook.parent} and {paths.generated_model.parent}"
        )
    spec = build_notebook_spec(paths.workbook, workbook_id=f"fable-c-{args.version}")
    controls = {control.name: control for control in spec.selection_controls}
    missing = [name for name in args.controls if name not in controls]
    if missing:
        raise ValueError(f"unknown controls: {', '.join(missing)}")
    baseline = {control.name: control.default for control in spec.selection_controls}
    rules = load_rule_registry(args.rules)
    table_status = table_population_from_spec(spec_to_payload(spec))
    rules_sha = rule_registry_sha256(args.rules)

    option_lists = [[option.value for option in controls[name].options] for name in args.controls]
    combinations = list(itertools.product(*option_lists))
    if args.limit is not None:
        combinations = combinations[: args.limit]

    scenarios: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for index, values in enumerate(combinations):
        selections = dict(baseline)
        for name, value in zip(args.controls, values, strict=True):
            selections[name] = value
        evaluation = evaluate_scenario(
            selections,
            rules,
            table_status=table_status,
            mode=args.rule_mode,
        )
        scenario = {
            "sample_id": f"domain_{index:03d}",
            "selections": selections,
            "rule_evaluation": evaluation.to_dict(),
        }
        if not evaluation.valid and args.rule_mode != "exploratory":
            rejected.append(scenario)
            continue
        scenarios.append(scenario)

    for scenario in scenarios:
        path = selections_dir / f"{scenario['sample_id']}.json"
        path.write_text(json.dumps(scenario["selections"], indent=2, sort_keys=True) + "\n", encoding="utf-8")

    started = time.perf_counter()

    def run_one(scenario: dict[str, Any]) -> dict[str, Any]:
        sample_id = str(scenario["sample_id"])
        command = [
            sys.executable,
            str(root / "scripts" / "fable_optimization_oracle.py"),
            "--version",
            args.version,
            "--selections-file",
            str(selections_dir / f"{sample_id}.json"),
            "--output",
            str(samples_dir / f"{sample_id}.json"),
        ]
        completed = subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=args.timeout,
            check=False,
        )
        (logs_dir / f"{sample_id}.log").write_text(
            f"$ {' '.join(command)}\n\nSTDOUT\n{completed.stdout}\nSTDERR\n{completed.stderr}\n",
            encoding="utf-8",
        )
        output_path = samples_dir / f"{sample_id}.json"
        if completed.returncode != 0 or not output_path.is_file():
            return {
                "sample_id": sample_id,
                "selections": scenario["selections"],
                "rule_evaluation": scenario["rule_evaluation"],
                "error": completed.stderr.strip()[-2000:] or f"exit {completed.returncode}",
            }
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        payload["sample_id"] = sample_id
        payload["rule_evaluation"] = scenario["rule_evaluation"]
        return payload

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_one, scenario): scenario for scenario in scenarios}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            status = "error" if "error" in result else "ok"
            print(f"{result['sample_id']}: {status}", flush=True)
    results.sort(key=lambda item: str(item["sample_id"]))
    elapsed = round(time.perf_counter() - started, 3)
    errors = [result for result in results if "error" in result]
    valid = [result for result in results if "error" not in result and _has_objectives(result)]

    domain = {
        "version": args.version,
        "workbook": str(paths.workbook),
        "generated_model": str(paths.generated_model),
        "controls": list(args.controls),
        "control_options": dict(zip(args.controls, option_lists, strict=True)),
        "baseline_selections": baseline,
        "rules": str(args.rules),
        "rules_sha256": rules_sha,
        "rule_mode": args.rule_mode,
        "combinations": len(combinations),
        "rejected_count": len(rejected),
        "rejected": rejected,
        "evaluated_count": len(results),
        "error_count": len(errors),
        "errors": errors,
        "runtime_seconds": elapsed,
        "samples": results,
    }
    domain_path = output_dir / "domain.json"
    domain_path.write_text(json.dumps(domain, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if valid:
        front = pareto_front(valid)
        unique_front = unique_objective_points(front)
        ranked = weighted_ranking(valid)
        report = {
            "version": args.version,
            "domain": str(domain_path),
            "domain_sha256": _sha256(domain_path),
            "rules_sha256": rules_sha,
            "rule_mode": args.rule_mode,
            "controls": list(args.controls),
            "objectives": list(OBJECTIVES),
            "directions": DIRECTIONS,
            "aspirations": DEFAULT_ASPIRATIONS,
            "weights": DEFAULT_WEIGHTS,
            "valid_count": len(valid),
            "pareto_count": len(front),
            "pareto_unique_count": len(unique_front),
            "pareto": unique_front,
            "weighted_top": ranked[:20],
            "best": {
                "food": max(valid, key=lambda row: _value(row, "food_total_kcal_feas")),
                "ghg": min(valid, key=lambda row: _value(row, "ghg_total_co2e")),
                "goal": ranked[0],
            },
        }
        front_path = output_dir / "front.json"
        front_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"front: {front_path}")
    else:
        front_path = None
    print(f"domain: {domain_path}")
    print(
        f"combinations: {len(combinations)}, rule-rejected: {len(rejected)}, "
        f"evaluated: {len(results)}, errors: {len(errors)}, valid: {len(valid)}, "
        f"runtime: {elapsed}s"
    )
    return 0 if valid else 1


def _has_objectives(sample: dict[str, Any]) -> bool:
    objectives = sample.get("objectives")
    return isinstance(objectives, dict) and all(
        isinstance(objectives.get(name), (int, float)) and not isinstance(objectives.get(name), bool)
        for name in OBJECTIVES
    )


def _value(sample: dict[str, Any], name: str) -> float:
    return float(sample["objectives"][name])


def pareto_front(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return non-dominated exact samples for food(max), GHG(min), land(min)."""

    active = [name for name in OBJECTIVES if not _is_constant([_value(sample, name) for sample in samples])]
    front: list[dict[str, Any]] = []
    for candidate in samples:
        if not any(_dominates(other, candidate, active) for other in samples if other is not candidate):
            front.append(candidate)
    return sorted(
        front,
        key=lambda row: (-_value(row, "food_total_kcal_feas"), _value(row, "ghg_total_co2e")),
    )


def unique_objective_points(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse samples that share the same rounded objective triple."""

    seen: set[tuple[float, ...]] = set()
    unique: list[dict[str, Any]] = []
    for sample in samples:
        key = tuple(round(_value(sample, name), 6) for name in OBJECTIVES)
        if key in seen:
            continue
        seen.add(key)
        unique.append(sample)
    return unique


def _dominates(left: dict[str, Any], right: dict[str, Any], objectives: list[str]) -> bool:
    left_values = [_value(left, name) * DIRECTIONS[name] for name in objectives]
    right_values = [_value(right, name) * DIRECTIONS[name] for name in objectives]
    return all(a >= b for a, b in zip(left_values, right_values, strict=True)) and any(
        a > b for a, b in zip(left_values, right_values, strict=True)
    )


def _is_constant(values: list[float]) -> bool:
    low, high = min(values), max(values)
    return high - low <= 1e-6 * max(1.0, abs(low), abs(high))


def weighted_ranking(
    samples: list[dict[str, Any]],
    *,
    aspirations: dict[str, float] | None = None,
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Rank samples by weighted squared distance to normalized aspirations."""

    aspirations = aspirations or DEFAULT_ASPIRATIONS
    weights = weights or DEFAULT_WEIGHTS
    ranges: dict[str, tuple[float, float]] = {}
    for name in OBJECTIVES:
        values = [_value(sample, name) for sample in samples]
        ranges[name] = (min(values), max(values))
    ranked: list[dict[str, Any]] = []
    for sample in samples:
        components: dict[str, float] = {}
        for name in OBJECTIVES:
            low, high = ranges[name]
            normalized = (
                0.5
                if _is_constant([_value(item, name) for item in samples])
                else (_value(sample, name) - low) / (high - low)
            )
            components[name] = weights[name] * (normalized - aspirations[name]) ** 2
        goal = sum(components.values()) / sum(weights.values())
        ranked.append(
            {
                "sample_id": sample.get("sample_id"),
                "selections": sample.get("selections"),
                "objectives": sample.get("objectives"),
                "goal": goal,
                "components": components,
                "rule_evaluation": sample.get("rule_evaluation"),
            }
        )
    return sorted(ranked, key=lambda row: (row["goal"], str(row["sample_id"])))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="2024")
    parser.add_argument(
        "--controls",
        nargs="+",
        default=list(DEFAULT_CONTROLS),
        help="Contrast controls to vary; all other controls remain at baseline.",
    )
    parser.add_argument("--workers", type=int, default=24)
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument(
        "--rules",
        type=Path,
        default=Path("planning/fable-scenario-consistency-rules.yaml"),
    )
    parser.add_argument(
        "--rule-mode",
        choices=("approved", "exploratory", "draft_enforced"),
        default="draft_enforced",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("tmp/fable-exact-optimization"))
    parser.add_argument("--limit", type=int, default=None, help="Smoke-test cap on combinations.")
    return parser


def _repo_root() -> Path:
    start = Path(__file__).resolve().parent
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "src" / "fable_pyculator").exists():
            return candidate
    raise RuntimeError("could not find the fable-pyculator repository root")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
