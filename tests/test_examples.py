from __future__ import annotations

import json
import lzma
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


def test_fable_pyculator_2021_notebook_uses_2021_artifact_paths_only() -> None:
    notebook_path = Path("examples/notebooks/fable-pyculator-2021-loop.ipynb")

    payload = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in payload["cells"] if cell["cell_type"] == "code"]
    code_source = "\n".join(
        "".join(cell["source"])
        for cell in code_cells
    )

    assert payload["nbformat"] == 4
    assert payload["cells"]
    assert "DEFAULT_2021_WORKBOOK_PATH" in code_source
    assert "DEFAULT_2021_GENERATED_MODEL_PATH" in code_source
    assert "build_2021_notebook_spec" in code_source
    assert "run_2021_notebook_loop" in code_source
    assert "examples\" / \"fable_2021\" / \"generated_fable_2021_model.py.xz" in code_source
    assert "lzma.open" in code_source
    assert "tmp/generated-models/fable-2021/generated_fable_2021_model.py" in "".join(
        "".join(cell["source"])
        for cell in payload["cells"]
    )
    assert "modelwright_archive" not in code_source
    assert "generated_fable_2020_model" not in code_source
    assert "run_2020_notebook_loop" not in code_source


def test_fable_pyculator_2021_generated_model_archive_is_readable() -> None:
    archive_path = Path("examples/fable_2021/generated_fable_2021_model.py.xz")

    assert archive_path.exists()
    with lzma.open(archive_path, "rt", encoding="utf-8") as archive:
        source_prefix = archive.read(10000)

    assert "Source workbook: 2021_Open_FABLECalculator.xlsx" in source_prefix
    assert "def _sf_iferror" in source_prefix


def test_fable_pyculator_2021_freshforge_build_plan_notebook_is_static_template() -> None:
    notebook_path = Path("examples/notebooks/fable-pyculator-2021-freshforge-build-plan.ipynb")

    payload = json.loads(notebook_path.read_text(encoding="utf-8"))
    code_cells = [cell for cell in payload["cells"] if cell["cell_type"] == "code"]
    code_source = "\n".join("".join(cell["source"]) for cell in code_cells)
    markdown_source = "\n".join(
        "".join(cell["source"])
        for cell in payload["cells"]
        if cell["cell_type"] == "markdown"
    )

    assert payload["nbformat"] == 4
    assert payload["cells"]
    assert all(cell.get("execution_count") is None for cell in code_cells)
    assert not any(cell.get("outputs") for cell in code_cells)
    assert "build_2021_notebook_spec" in code_source
    assert "modelwright.model_infer_contract" in code_source
    assert "modelwright.validation_evaluate" in code_source
    assert "freshforge" in code_source.casefold()
    assert "RUN_BUILD = False" in code_source
    assert "output_refs.json" in code_source
    assert "validation-scenario.json" in code_source
    assert "evaluation-report.json" in code_source
    assert "generated_fable_2021_model.py" in code_source
    assert "tmp/generated-models/fable-2021" in markdown_source
    assert "FreshForge planning is not execution" in markdown_source
    assert "generated_fable_2020_model" not in code_source
    assert "run_2020_notebook_loop" not in code_source
