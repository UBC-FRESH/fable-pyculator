from __future__ import annotations

import json
from pathlib import Path


def test_fable_pyculator_2020_notebook_is_tracked_without_outputs() -> None:
    notebook_path = Path("examples/notebooks/fable-pyculator-2020-loop.ipynb")

    payload = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_source = "\n".join(
        "".join(cell["source"])
        for cell in payload["cells"]
        if cell["cell_type"] == "code"
    )

    assert payload["nbformat"] == 4
    assert payload["cells"]
    assert all(not cell.get("outputs") for cell in payload["cells"] if cell["cell_type"] == "code")
    assert all(cell.get("execution_count") is None for cell in payload["cells"] if cell["cell_type"] == "code")
    assert "raise FileNotFoundError" not in code_source
    assert "find_repo_root" in code_source
    assert "ARTIFACTS_READY" in code_source
    assert "modelwright_archive" in code_source
    assert "notebook_working_dir" in code_source
    assert "expected_kernel_prefix" in code_source
    assert "active_prefix" in code_source
    assert "using_repo_venv" in code_source
    assert "include_figures=False" in code_source
    assert "display(result.output_tables" in code_source
    assert "display(result.headline_frames" in code_source
    assert "display(plot_headline" in code_source
    assert any(
        "run_notebook_loop" in "".join(cell["source"])
        for cell in payload["cells"]
        if cell["cell_type"] == "code"
    )
