from __future__ import annotations

import json
from pathlib import Path


def test_fable_pyculator_2020_notebook_is_tracked_with_rendered_outputs() -> None:
    notebook_path = Path("examples/notebooks/fable-pyculator-2020-loop.ipynb")

    payload = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in payload["cells"] if cell["cell_type"] == "code"]
    outputs = [output for cell in code_cells for output in cell.get("outputs", [])]
    code_source = "\n".join(
        "".join(cell["source"])
        for cell in code_cells
    )

    assert payload["nbformat"] == 4
    assert payload["cells"]
    assert all(cell.get("execution_count") is not None for cell in code_cells)
    assert not any(output.get("output_type") == "error" for output in outputs)
    assert not any(output.get("output_type") == "stream" for output in outputs)
    assert any("text/markdown" in output.get("data", {}) for output in outputs)
    assert any("text/html" in output.get("data", {}) for output in outputs)
    assert any("image/png" in output.get("data", {}) for output in outputs)
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
    assert "plot_headline" in code_source
    assert any(
        "run_notebook_loop" in "".join(cell["source"])
        for cell in code_cells
    )
