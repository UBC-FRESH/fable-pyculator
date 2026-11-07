#!/usr/bin/env python
"""Evaluate one FABLE scenario selection through the exact Pyculator model."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

__all__ = ["main", "evaluate"]


def main(argv: list[str] | None = None) -> int:
    """Run one exact scenario evaluation."""

    args = _parser().parse_args(argv)
    selections = json.loads(Path(args.selections_file).read_text(encoding="utf-8"))
    result = evaluate(
        version=args.version,
        selections=selections,
        workbook=args.workbook,
        model=args.model,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"version": result["version"], "objectives": result["objectives"]}, sort_keys=True))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="2024", help="Workbook version, such as 2021 or 2024.")
    parser.add_argument("--selections-file", type=Path, required=True, help="JSON selection mapping.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path.")
    parser.add_argument("--workbook", type=Path, default=None, help="Source workbook path override.")
    parser.add_argument("--model", type=Path, default=None, help="Generated model path override.")
    return parser


def evaluate(
    *,
    version: str,
    selections: dict[str, object],
    workbook: Path | None = None,
    model: Path | None = None,
) -> dict[str, object]:
    """Run the exact model and return objective values and provenance."""

    from fable_pyculator.notebook import build_notebook_spec, load_generated_model, run_notebook_loop
    from fable_pyculator.web.artifacts import artifact_paths

    root = _repo_root()
    paths = artifact_paths(root, version)
    workbook_path = (workbook or paths.workbook).resolve()
    model_path = (model or paths.generated_model).resolve()
    if not workbook_path.is_file():
        raise FileNotFoundError(f"workbook not found: {workbook_path}")
    if not model_path.is_file():
        raise FileNotFoundError(f"generated model not found: {model_path}")

    started = time.perf_counter()
    spec = build_notebook_spec(workbook_path, workbook_id=f"fable-c-{version}")
    names = tuple(series.name for series in spec.headline_series)
    generated_model = load_generated_model(model_path, module_name=f"fable_optimization_oracle_{version}")
    result = run_notebook_loop(
        generated_model,
        spec,
        selections,
        scenario_name="optimization-sample",
        output_table_names=(),
        headline_series_names=names,
        include_figures=False,
    )
    objectives: dict[str, float | None] = {}
    for name, frame in result.headline_frames.items():
        if frame is None or frame.empty:
            objectives[name] = None
            continue
        value = frame.iloc[-1]["value"]
        objectives[name] = float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
    runtime = round(time.perf_counter() - started, 3)
    return {
        "version": version,
        "selections": selections,
        "objectives": objectives,
        "runtime_seconds": runtime,
        "workbook": str(workbook_path),
        "workbook_sha256": _sha256(workbook_path),
        "model": str(model_path),
        "model_sha256": _sha256(model_path),
        "headline_series": names,
    }


def _repo_root() -> Path:
    start = Path.cwd().resolve()
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
