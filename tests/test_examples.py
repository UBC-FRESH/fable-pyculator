from __future__ import annotations

import json
from pathlib import Path


def test_fable_pyculator_2020_notebook_is_tracked_without_outputs() -> None:
    notebook_path = Path("examples/notebooks/fable-pyculator-2020-loop.ipynb")

    payload = json.loads(notebook_path.read_text(encoding="utf-8"))

    assert payload["nbformat"] == 4
    assert payload["cells"]
    assert all(not cell.get("outputs") for cell in payload["cells"] if cell["cell_type"] == "code")
    assert any(
        "run_notebook_loop" in "".join(cell["source"])
        for cell in payload["cells"]
        if cell["cell_type"] == "code"
    )
