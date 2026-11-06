#!/usr/bin/env python
"""Run deterministic structural grounding checks and optional live assistant evals.

Examples::

    python scripts/evaluate_assistant_grounding.py
    python scripts/evaluate_assistant_grounding.py --live --json
    python scripts/evaluate_assistant_grounding.py --live --case notebook_signature
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fable_pyculator.web.grounding_evals import DEFAULT_CASES, GroundingEvalSummary, run_grounding_evals


def main(argv: list[str] | None = None) -> int:
    """Run the grounding evaluation suite."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="FABLE Pyculator repository root.")
    parser.add_argument(
        "--runtime",
        type=Path,
        default=None,
        help="Ignored runtime directory for the generated eval cheat sheet.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run the installed opencode CLI for each case instead of structural checks only.",
    )
    parser.add_argument(
        "--case",
        action="append",
        choices=[case.case_id for case in DEFAULT_CASES],
        help="Limit live checks to a case id (repeatable).",
    )
    parser.add_argument("--timeout", type=float, default=600.0, help="Timeout per live case in seconds.")
    parser.add_argument("--json", action="store_true", help="Print the full JSON summary.")
    args = parser.parse_args(argv)

    cases = tuple(case for case in DEFAULT_CASES if not args.case or case.case_id in set(args.case))
    summary = run_grounding_evals(
        args.root,
        runtime_dir=args.runtime,
        cases=cases,
        include_live=args.live,
        timeout=args.timeout,
    )
    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
    else:
        _print_summary(summary)
    return 0 if summary.passed else 1


def _print_summary(summary: GroundingEvalSummary) -> None:
    print(f"grounding sheet: {summary.cheat_sheet_path}")
    print(f"structural checks: {'PASS' if not summary.structural else 'FAIL'}")
    for failure in summary.structural:
        print(f"  - {failure}")
    for case in summary.cases:
        line = f"{case.case_id}: {case.status}"
        if case.seconds:
            line += f" ({case.seconds:.1f} s)"
        print(line)
        for failure in case.failures:
            print(f"  - {failure}")
    print(f"overall: {'PASS' if summary.passed else 'FAIL'}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
