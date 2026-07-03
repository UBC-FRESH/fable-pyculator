from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(
    os.environ.get("FABLE_PYCULATOR_RUN_2021_NOTEBOOK_SMOKE") != "1",
    reason="set FABLE_PYCULATOR_RUN_2021_NOTEBOOK_SMOKE=1 to run restored-artifact 2021 notebook smoke",
)
def test_restored_2021_notebook_loop_smoke() -> None:
    workbook_path = Path("tmp/private-workbooks/2021_Open_FABLECalculator.xlsx")
    generated_model_path = Path("tmp/generated-models/fable-2021/generated_fable_2021_model.py")
    if not workbook_path.exists() or not generated_model_path.exists():
        pytest.skip("restored 2021 workbook/generated-model artifacts are not available")

    result = subprocess.run(
        [sys.executable, "scripts/smoke_2021_notebook_loop.py", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert "trade_resultstrade" in payload["rendered_tables"]
    assert payload["proof"]["ok"] is True
    assert payload["proof"]["missing_columns"] == []
    assert payload["proof"]["missing_values"] == {"PRODUCT": False, "YEAR": False}
