#!/usr/bin/env python
"""Regenerate the 2024 FABLE generated model from the repaired workbook.

This is a reproducibility check, not an artifact publisher. It writes the regenerated model
to an ignored directory and compares it with the tracked archive when that archive exists.
Use Modelwright 0.1.0a9 or newer; earlier releases do not support the full 2024 formula set.
"""

from __future__ import annotations

import argparse
import hashlib
import lzma
import sys
from collections import Counter
from pathlib import Path

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

__all__ = ["main", "regenerate"]


def main(argv: list[str] | None = None) -> int:
    """Run the 2024 regeneration check."""

    args = _parser().parse_args(argv)
    try:
        result = regenerate(
            repo_root=args.repo_root,
            workbook=args.workbook,
            output=args.output,
            tracked_archive=args.tracked_archive,
        )
    except Exception as error:  # noqa: BLE001 - CLI boundary
        print(f"regeneration failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(f"generated model: {result['output']}")
    print(f"formula cells: {result['formula_cells']:,}")
    print(f"output refs: {result['output_refs']:,}")
    print(f"declared outputs: {result['declared_outputs']:,}")
    print(f"output-closure failures: {result['closure_failures']:,}")
    print(f"model sha256: {result['sha256']}")
    if result["tracked_archive"] is None:
        print("tracked archive: not compared")
    elif result["tracked_matches"]:
        print(f"tracked archive: exact match ({result['tracked_archive']})")
    else:
        print(f"tracked archive: DIFFERS ({result['tracked_archive']})")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to auto-detection.")
    parser.add_argument(
        "--workbook",
        type=Path,
        default=Path("tmp/private-workbooks/2024_Open_FABLECalculator.xlsx"),
        help="Repaired 2024 workbook path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tmp/fable2024-regeneration/generated_fable_2024_model.py"),
        help="Ignored output path for the regenerated model.",
    )
    parser.add_argument(
        "--tracked-archive",
        type=Path,
        default=Path("examples/fable_2024/generated_fable_2024_model.py.xz"),
        help="Tracked archive to compare against, or omit to skip the comparison.",
    )
    return parser


def regenerate(
    *,
    repo_root: Path | None = None,
    workbook: Path | None = None,
    output: Path | None = None,
    tracked_archive: Path | None = None,
) -> dict[str, object]:
    """Run a full Modelwright conversion and return reproduction metadata."""

    from modelwright.extraction import extract_workbook
    from modelwright.formulas import build_formula_reference_index, translate_formula_cell
    from modelwright.generation import generate_python_module, infer_generated_module_contract
    from modelwright.graph import build_dependency_graph

    from fable_pyculator.notebook import build_notebook_spec
    from fable_pyculator.workflows import derive_output_refs

    root = _repo_root(repo_root)
    workbook_path = _resolve(root, workbook or Path("tmp/private-workbooks/2024_Open_FABLECalculator.xlsx"))
    output_path = _resolve(root, output or Path("tmp/fable2024-regeneration/generated_fable_2024_model.py"))
    archive_path = _resolve(
        root,
        tracked_archive or Path("examples/fable_2024/generated_fable_2024_model.py.xz"),
    )
    if not workbook_path.is_file():
        raise FileNotFoundError(f"2024 workbook not found: {workbook_path}")

    _progress("building the 2024 workbook spec")
    spec = build_notebook_spec(workbook_path, workbook_id="fable-c-2024")
    output_refs = derive_output_refs(spec, column_flavour_tags="OUTPUT-*")
    _progress(f"output refs: {len(output_refs):,}")

    _progress("extracting workbook")
    workbook_record = extract_workbook(workbook_path, progress=None)
    _progress(f"cells: {len(workbook_record.cells):,}")

    _progress("building dependency graph")
    graph = build_dependency_graph(workbook_record, progress=None)
    _progress(f"edges: {len(graph.edges):,}")

    _progress("translating formulas")
    reference_index = build_formula_reference_index(graph)
    expressions = {
        cell.cell_ref: translate_formula_cell(cell, graph, reference_index)
        for cell in workbook_record.cells
        if cell.formula is not None
    }
    translated = sum(1 for expression in expressions.values() if expression.translated)
    _progress(f"translated: {translated:,} / {len(expressions):,}")

    _progress("inferring the output contract")
    inference = infer_generated_module_contract(
        workbook=workbook_record,
        graph=graph,
        expressions=expressions,
        output_refs=output_refs,
        module_name="generated_fable_2024_model",
        progress=None,
    )
    closure_failures = sum(
        1
        for symbol in inference.contract.symbols
        if symbol.kind != "input"
        and ((expression := inference.expressions.get(symbol.cell_ref)) is None or not expression.translated)
    )
    _progress(f"output-closure failures: {closure_failures:,}")

    _progress("generating the Python model")
    generation = generate_python_module(
        contract=inference.contract,
        expressions=inference.expressions,
        constants=inference.constants,
        output_path=output_path,
        progress=None,
    )
    diagnostics = Counter(diagnostic.code for diagnostic in generation.diagnostics)
    _progress(f"generation diagnostics: {dict(diagnostics)}")
    if not generation.generated:
        raise RuntimeError(f"generation did not complete: {dict(diagnostics)}")

    output_bytes = output_path.read_bytes()
    digest = hashlib.sha256(output_bytes).hexdigest()
    tracked_matches: bool | None = None
    tracked_path: str | None = None
    if archive_path.is_file():
        tracked_path = str(archive_path)
        tracked_bytes = lzma.decompress(archive_path.read_bytes())
        tracked_matches = tracked_bytes == output_bytes
    return {
        "output": str(output_path),
        "formula_cells": len(expressions),
        "output_refs": len(output_refs),
        "declared_outputs": len(output_refs),
        "closure_failures": closure_failures,
        "sha256": digest,
        "tracked_archive": tracked_path,
        "tracked_matches": tracked_matches,
    }


def _repo_root(value: Path | None) -> Path:
    if value is not None:
        return value.resolve()
    start = Path.cwd().resolve()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").exists() and (candidate / "src" / "fable_pyculator").exists():
            return candidate
    raise RuntimeError("could not find the fable-pyculator repository root")


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _progress(message: str) -> None:
    print(f"[regenerate-2024] {message}", flush=True)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
