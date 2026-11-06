from __future__ import annotations

import os
from pathlib import Path

import pytest

from fable_pyculator.web import grounding_evals
from fable_pyculator.web import cheatsheet
from fable_pyculator.web.grounding_evals import GroundingCase, run_grounding_evals

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_structural_grounding_checks_pass_against_real_docs_and_source() -> None:
    summary = run_grounding_evals(REPO_ROOT)

    assert summary.structural == []
    assert summary.passed
    assert Path(summary.cheat_sheet_path).is_file()
    markdown = Path(summary.cheat_sheet_path).read_text(encoding="utf-8")
    assert "Documentation digest" in markdown
    assert "Source API index" in markdown
    assert "build_notebook_spec" in markdown
    assert "class ModelFacade" in markdown
    assert "TotalResultsWF" in markdown


def test_structural_grounding_checks_use_installed_modelwright_when_checkout_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cheatsheet, "modelwright_root", lambda root: None)

    summary = run_grounding_evals(REPO_ROOT)

    assert summary.structural == []
    markdown = Path(summary.cheat_sheet_path).read_text(encoding="utf-8")
    assert "class ModelFacade" in markdown
    assert "wrappers.py" in markdown


def test_live_case_checks_paths_terms_and_forbidden_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = GroundingCase(
        case_id="fake",
        question="Where is build_notebook_spec defined? Cite the path.",
        expected_paths=("src/fable_pyculator/notebook.py",),
        required_terms=("build_notebook_spec", "strict_headlines"),
        forbidden_terms=("invented_api",),
    )

    def fake_run_agent(request, **kwargs):
        return {
            "response": ("`build_notebook_spec` is in `src/fable_pyculator/notebook.py` and has `strict_headlines`."),
            "session": "ses_test",
            "actions": [{"tool": "read", "summary": "src/fable_pyculator/notebook.py"}],
        }

    monkeypatch.setattr(grounding_evals, "run_agent", fake_run_agent)
    summary = run_grounding_evals(
        REPO_ROOT,
        cases=(case,),
        include_live=True,
    )

    assert summary.structural == []
    assert summary.cases[0].status == "pass"
    assert summary.cases[0].failures == []


def test_live_case_reports_missing_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    case = GroundingCase(
        case_id="fake",
        question="Where is build_notebook_spec defined? Cite the path.",
        expected_paths=("src/fable_pyculator/notebook.py",),
        required_terms=("strict_headlines",),
    )

    monkeypatch.setattr(
        grounding_evals,
        "run_agent",
        lambda request, **kwargs: {
            "response": "I think it is somewhere in the model layer.",
            "session": "ses_test",
            "actions": [],
        },
    )
    summary = run_grounding_evals(REPO_ROOT, cases=(case,), include_live=True)

    assert summary.cases[0].status == "fail"
    assert any("expected path" in failure for failure in summary.cases[0].failures)
    assert any("strict_headlines" in failure for failure in summary.cases[0].failures)


@pytest.mark.skipif(
    os.environ.get("FABLE_PYCULATOR_RUN_AGENT_EVALS") != "1",
    reason="set FABLE_PYCULATOR_RUN_AGENT_EVALS=1 to run live assistant grounding evals",
)
def test_live_grounding_evals_pass() -> None:
    summary = run_grounding_evals(REPO_ROOT, include_live=True)

    assert summary.structural == []
    assert all(case.status == "pass" for case in summary.cases), [
        case.to_dict() for case in summary.cases if case.status != "pass"
    ]
