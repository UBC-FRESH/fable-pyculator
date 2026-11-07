#!/usr/bin/env python
"""Build a reduced exact generated-model copy for selected FABLE headline objectives."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

__all__ = ["build_reduced_model", "main"]

_OUTPUT_START = "    _output_refs = (\n"
_OUTPUT_END = "    )\n    return {cell_ref: _get(cell_ref) for cell_ref in _output_refs}"


def main(argv: list[str] | None = None) -> int:
    """Build a reduced exact model copy."""

    args = _parser().parse_args(argv)
    result = build_reduced_model(
        version=args.version,
        workbook=args.workbook,
        source_model=args.model,
        output=args.output,
        objective_names=tuple(args.objective) if args.objective else None,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="2024", help="Workbook version.")
    parser.add_argument("--workbook", type=Path, default=None, help="Workbook path override.")
    parser.add_argument("--model", type=Path, default=None, help="Full generated-model path override.")
    parser.add_argument("--output", type=Path, required=True, help="Reduced model output path.")
    parser.add_argument(
        "--objective",
        action="append",
        default=None,
        help="Headline series name to retain; repeatable. Defaults to every headline series.",
    )
    return parser


def build_reduced_model(
    *,
    version: str,
    workbook: Path | None,
    source_model: Path | None,
    output: Path,
    objective_names: tuple[str, ...] | None,
) -> dict[str, object]:
    """Rewrite the generated model's output-ref tuple and return provenance."""

    from fable_pyculator.notebook import build_notebook_spec
    from fable_pyculator.web.artifacts import artifact_paths

    root = _repo_root()
    paths = artifact_paths(root, version)
    workbook_path = (workbook or paths.workbook).resolve()
    source_path = (source_model or paths.generated_model).resolve()
    output_path = (output if output.is_absolute() else root / output).resolve()
    if not workbook_path.is_file():
        raise FileNotFoundError(f"workbook not found: {workbook_path}")
    if not source_path.is_file():
        raise FileNotFoundError(f"generated model not found: {source_path}")

    spec = build_notebook_spec(workbook_path, workbook_id=f"fable-c-{version}")
    selected = [series for series in spec.headline_series if objective_names is None or series.name in objective_names]
    if not selected:
        raise ValueError("no matching headline series")
    refs = sorted({cell_ref for series in selected for point in series.points for cell_ref in point.cell_refs})
    if not refs:
        raise ValueError("selected headline series have no cell refs")

    source = source_path.read_text(encoding="utf-8")
    start = source.find(_OUTPUT_START)
    if start < 0:
        raise ValueError("could not find _output_refs start")
    end = source.find(_OUTPUT_END, start)
    if end < 0:
        raise ValueError("could not find _output_refs end")
    block = "".join(f"        {ref!r},\n" for ref in refs)
    replacement = f"{_OUTPUT_START}{block}{_OUTPUT_END}"
    patched = source[:start] + replacement + source[end + len(_OUTPUT_END) :]
    compile(patched, str(output_path), "exec")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(patched, encoding="utf-8")
    return {
        "version": version,
        "objectives": [series.name for series in selected],
        "objective_cell_refs": refs,
        "objective_cell_count": len(refs),
        "source_model": str(source_path),
        "source_sha256": _sha256(source_path),
        "reduced_model": str(output_path),
        "reduced_sha256": _sha256(output_path),
        "source_bytes": source_path.stat().st_size,
        "reduced_bytes": output_path.stat().st_size,
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
