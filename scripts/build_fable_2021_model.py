#!/usr/bin/env python
"""Compatibility shortcut for the default 2021 FABLE FreshForge rebuild workflow."""

from __future__ import annotations

from pathlib import Path
import sys

for _candidate in Path(__file__).resolve().parents:
    if (_candidate / "src" / "fable_pyculator").exists():
        sys.path.insert(0, str(_candidate / "src"))
        break

if __name__ == "__main__":
    from build_fable_model import main

    raise SystemExit(main())
