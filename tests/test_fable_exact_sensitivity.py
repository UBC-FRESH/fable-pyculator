from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fable_exact_sensitivity.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("fable_exact_sensitivity", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_variant_delta_reports_absolute_and_relative_changes() -> None:
    module = _load_module()
    baseline = {
        "objectives": {
            "food_total_kcal_feas": 100.0,
            "ghg_total_co2e": 50.0,
            "land_total_area": 10.0,
        }
    }
    variant = {
        "sample_id": "v",
        "objectives": {
            "food_total_kcal_feas": 90.0,
            "ghg_total_co2e": 25.0,
            "land_total_area": 10.0,
        },
    }

    annotated = module.variant_delta(baseline, variant)

    assert annotated["delta_food"] == -10.0
    assert annotated["delta_food_pct"] == -10.0
    assert annotated["delta_ghg"] == -25.0
    assert annotated["delta_ghg_pct"] == -50.0


def test_help() -> None:
    import subprocess

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "--baseline-file" in result.stdout
    assert "--controls" in result.stdout
