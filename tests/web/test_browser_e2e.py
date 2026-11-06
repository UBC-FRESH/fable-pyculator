from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.skipif(
    os.environ.get("FABLE_PYCULATOR_RUN_BROWSER_TESTS") != "1",
    reason="set FABLE_PYCULATOR_RUN_BROWSER_TESTS=1 to run browser smoke tests",
)
def test_browser_smoke_with_live_chat_persistence() -> None:
    if importlib.util.find_spec("playwright") is None:
        pytest.skip("playwright is not installed")

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "browser_smoke.py"),
            "--root",
            str(REPO_ROOT),
            "--server-python",
            sys.executable,
            "--live-agent",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )

    assert completed.returncode == 0, f"browser smoke failed\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
    assert "PASS: overlay, markdown, Enter and Shift+Enter" in completed.stdout
    assert "PASS: live assistant chat persisted across reload" in completed.stdout
