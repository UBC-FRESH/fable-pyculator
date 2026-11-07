#!/usr/bin/env python
"""Exact one-at-a-time sensitivity around a FABLE policy point.

Every objective is a real Pyculator run. This is a local exact sensitivity analysis, not a
surrogate and not a global optimization.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
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

__all__ = ["main", "variant_delta"]

DEFAULT_CONTROLS = ("affor_scen", "crop_scen", "scen_exports", "scen_imports", "gwp_scen", "live_scen")


def main(argv: list[str] | None = None) -> int:
    """Run exact one-at-a-time variants around a baseline selection."""

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

    baseline = json.loads(args.baseline_file.read_text(encoding="utf-8"))
    if not isinstance(baseline, dict):
        raise ValueError("baseline file must contain a JSON selection mapping")
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
    rules = load_rule_registry(args.rules)
    table_status = table_population_from_spec(spec_to_payload(spec))
    rules_sha = rule_registry_sha256(args.rules)

    scenarios: list[dict[str, Any]] = [
        {
            "sample_id": "baseline",
            "sample_kind": "baseline",
            "control": None,
            "value": None,
            "selections": dict(baseline),
            "rule_evaluation": evaluate_scenario(
                baseline,
                rules,
                table_status=table_status,
                mode=args.rule_mode,
            ).to_dict(),
        }
    ]
    rejected: list[dict[str, Any]] = []
    for control_name in args.controls:
        control = controls[control_name]
        baseline_value = baseline.get(control_name, control.default)
        for option in control.options:
            if str(option.value) == str(baseline_value):
                continue
            selections = dict(baseline)
            selections[control_name] = option.value
            evaluation = evaluate_scenario(
                selections,
                rules,
                table_status=table_status,
                mode=args.rule_mode,
            )
            scenario = {
                "sample_id": f"variant_{len(scenarios) + len(rejected):03d}",
                "sample_kind": "one-at-a-time",
                "control": control_name,
                "value": option.value,
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
                "error": completed.stderr.strip()[-2000:] or f"exit {completed.returncode}",
            }
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        for key, value in scenario.items():
            if key not in {"selections"}:
                payload[key] = value
        return payload

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_one, scenario): scenario for scenario in scenarios}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            status = "error" if "error" in result else "ok"
            print(f"{result['sample_id']}: {status}", flush=True)
    elapsed = round(time.perf_counter() - started, 3)
    results.sort(key=lambda item: str(item["sample_id"]))
    errors = [result for result in results if "error" in result]
    baseline_result = next((result for result in results if result.get("sample_kind") == "baseline"), None)
    variants = [result for result in results if result.get("sample_kind") == "one-at-a-time" and "error" not in result]
    if baseline_result is not None and "error" not in baseline_result:
        variants = [variant_delta(baseline_result, variant) for variant in variants]
    else:
        baseline_result = None

    payload = {
        "version": args.version,
        "workbook": str(paths.workbook),
        "generated_model": str(paths.generated_model),
        "baseline_file": str(args.baseline_file),
        "baseline_file_sha256": _sha256(args.baseline_file),
        "baseline_selections": baseline,
        "controls": list(args.controls),
        "control_options": {name: [option.value for option in controls[name].options] for name in args.controls},
        "rules": str(args.rules),
        "rules_sha256": rules_sha,
        "rule_mode": args.rule_mode,
        "rejected_count": len(rejected),
        "rejected": rejected,
        "evaluated_count": len(results),
        "error_count": len(errors),
        "errors": errors,
        "runtime_seconds": elapsed,
        "baseline": baseline_result,
        "variants": variants,
        "best_food": (
            max(
                (row for row in variants if isinstance(row.get("delta_food"), (int, float))),
                key=lambda row: row["delta_food"],
                default=None,
            )
        ),
        "best_ghg": (
            min(
                (row for row in variants if isinstance(row.get("delta_ghg"), (int, float))),
                key=lambda row: row["delta_ghg"],
                default=None,
            )
        ),
    }
    output_path = output_dir / "sensitivity.json"
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"sensitivity: {output_path}")
    print(
        f"evaluated: {len(results)}, errors: {len(errors)}, rule-rejected: {len(rejected)}, "
        f"baseline: {'ok' if baseline_result else 'missing/error'}, runtime: {elapsed}s"
    )
    return 0 if baseline_result is not None and not errors else 1


def variant_delta(baseline: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    """Return one variant annotated with exact deltas from the baseline."""

    annotated = dict(variant)
    base_objectives = baseline.get("objectives") or {}
    objectives = variant.get("objectives") or {}
    for name, key in (("food", "food_total_kcal_feas"), ("ghg", "ghg_total_co2e")):
        base_value = base_objectives.get(key)
        value = objectives.get(key)
        if isinstance(base_value, (int, float)) and isinstance(value, (int, float)):
            delta = float(value) - float(base_value)
            annotated[f"delta_{name}"] = delta
            annotated[f"delta_{name}_pct"] = None if float(base_value) == 0 else 100.0 * delta / float(base_value)
        else:
            annotated[f"delta_{name}"] = None
            annotated[f"delta_{name}_pct"] = None
    return annotated


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="2024")
    parser.add_argument("--baseline-file", type=Path, required=True)
    parser.add_argument("--controls", nargs="+", default=list(DEFAULT_CONTROLS))
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
    parser.add_argument("--output-dir", type=Path, default=Path("tmp/fable-exact-sensitivity"))
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
