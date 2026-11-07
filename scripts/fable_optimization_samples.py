#!/usr/bin/env python
"""Collect exact FABLE optimization samples for the surrogate pilot."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import random
import subprocess
import sys
from pathlib import Path

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

__all__ = ["main"]


def main(argv: list[str] | None = None) -> int:
    """Collect a bounded exact sample set."""

    args = _parser().parse_args(argv)
    root = _repo_root()
    output_dir = (args.output_dir if args.output_dir.is_absolute() else root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    selections_dir = output_dir / "selections"
    samples_dir = output_dir / "samples"
    logs_dir = output_dir / "logs"
    for directory in (selections_dir, samples_dir, logs_dir):
        directory.mkdir(parents=True, exist_ok=True)

    from fable_pyculator.notebook import build_notebook_spec
    from fable_pyculator.web.artifacts import artifact_paths

    paths = artifact_paths(root, args.version)
    if not paths.workbook.is_file() or not paths.generated_model.is_file():
        raise FileNotFoundError(
            f"need both workbook and generated model under {paths.workbook.parent} and {paths.generated_model.parent}"
        )
    spec = build_notebook_spec(paths.workbook, workbook_id=f"fable-c-{args.version}")
    controls = [
        {
            "name": control.name,
            "label": control.label,
            "options": [option.value for option in control.options],
            "default": control.default,
        }
        for control in spec.selection_controls
    ]
    baseline = {control["name"]: control["default"] for control in controls}
    selected_names = [control["name"] for control in controls]
    if args.controls_file is not None:
        payload = json.loads(args.controls_file.read_text(encoding="utf-8"))
        selected_names = payload.get("controls", payload) if isinstance(payload, dict) else payload
        if not isinstance(selected_names, list) or not all(isinstance(name, str) for name in selected_names):
            raise ValueError("controls file must contain a JSON array of control names")
        known = {control["name"] for control in controls}
        unknown = sorted(set(selected_names) - known)
        if unknown:
            raise ValueError(f"unknown controls: {', '.join(unknown)}")
    selected_controls = [control for control in controls if control["name"] in set(selected_names)]
    rng = random.Random(args.seed)
    scenarios: list[dict[str, object]] = [
        {
            "sample_id": "baseline",
            "sample_kind": "baseline",
            "selections": baseline,
        }
    ]
    seen = {json.dumps(baseline, sort_keys=True)}
    if args.design == "one-at-a-time":
        for control in selected_controls:
            alternatives = [option for option in control["options"] if option != control["default"]]
            if not alternatives:
                continue
            variant = rng.choice(alternatives)
            selections = dict(baseline)
            selections[control["name"]] = variant
            scenarios.append(
                {
                    "sample_id": f"screen_{control['name']}",
                    "sample_kind": "one-at-a-time",
                    "control_name": control["name"],
                    "baseline_value": control["default"],
                    "variant_value": variant,
                    "selections": selections,
                }
            )
    else:
        attempts = 0
        while len(scenarios) < args.count + 1 and attempts < args.count * 100:
            attempts += 1
            selections = dict(baseline)
            for control in selected_controls:
                selections[control["name"]] = rng.choice(control["options"])
            key = json.dumps(selections, sort_keys=True)
            if key in seen:
                continue
            seen.add(key)
            scenarios.append(
                {
                    "sample_id": f"sample_{len(scenarios):03d}",
                    "sample_kind": "random",
                    "selections": selections,
                }
            )

    for scenario in scenarios:
        path = selections_dir / f"{scenario['sample_id']}.json"
        path.write_text(json.dumps(scenario["selections"], indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def run_one(scenario: dict[str, object]) -> dict[str, object]:
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
        payload["sample_id"] = sample_id
        for key, value in scenario.items():
            if key not in {"sample_id", "selections"}:
                payload[key] = value
        return payload

    samples: list[dict[str, object]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_one, scenario): scenario for scenario in scenarios}
        for future in concurrent.futures.as_completed(futures):
            sample = future.result()
            samples.append(sample)
            status = "error" if "error" in sample else "ok"
            print(f"{sample['sample_id']}: {status}", flush=True)
    samples.sort(key=lambda item: str(item["sample_id"]))
    dataset = {
        "version": args.version,
        "workbook": str(paths.workbook),
        "generated_model": str(paths.generated_model),
        "design": args.design,
        "controls": controls,
        "variable_controls": selected_names,
        "baseline_selections": baseline,
        "samples": samples,
    }
    dataset_path = output_dir / "dataset.json"
    dataset_path.write_text(json.dumps(dataset, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    errors = sum(1 for sample in samples if "error" in sample)
    print(f"dataset: {dataset_path}")
    print(f"samples: {len(samples) - errors} ok, {errors} error")
    return 0 if errors == 0 else 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="2024", help="Workbook version.")
    parser.add_argument("--count", type=int, default=32, help="Random samples in addition to baseline.")
    parser.add_argument("--workers", type=int, default=16, help="Concurrent exact model workers.")
    parser.add_argument("--seed", type=int, default=7, help="Sampling seed.")
    parser.add_argument("--timeout", type=float, default=900.0, help="Per-sample timeout in seconds.")
    parser.add_argument(
        "--design",
        choices=("random", "one-at-a-time"),
        default="random",
        help="Random space-filling samples or one non-default variant per control.",
    )
    parser.add_argument(
        "--controls-file",
        type=Path,
        default=None,
        help="Optional JSON array of control names to vary; others stay at baseline.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tmp/fable-optimization"),
        help="Ignored output directory.",
    )
    return parser


def _repo_root() -> Path:
    start = Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "src" / "fable_pyculator").exists():
            return candidate
    raise RuntimeError("could not find the fable-pyculator repository root")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
