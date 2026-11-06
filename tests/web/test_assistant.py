from __future__ import annotations

from types import SimpleNamespace

import pytest

from fable_pyculator.web import assistant
from fable_pyculator.web.assistant import AgentRequest, _parse_agent_events, run_agent


def test_parse_agent_events_extracts_text_session_and_actions() -> None:
    stdout = "\n".join(
        [
            '{"type":"text","sessionID":"ses_abc123","part":{"text":"Here is the answer."}}',
            '{"type":"tool_use","sessionID":"ses_abc123","part":{"tool":"read","state":{"title":"Read docs"}}}',
            '{"type":"error","sessionID":"ses_abc123","error":{"message":"minor warning"}}',
        ]
    )

    reply, session_id, actions, errors = _parse_agent_events(stdout)

    assert reply == "Here is the answer."
    assert session_id == "ses_abc123"
    assert actions == [{"tool": "read", "summary": "Read docs"}]
    assert errors == ["minor warning"]


def test_run_agent_continues_session_and_returns_actions(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["cwd"] = kwargs["cwd"]
        return SimpleNamespace(
            returncode=0,
            stdout=(
                '{"type":"text","sessionID":"ses_abc123","part":{"text":"Markdown **reply**"}}\n'
                '{"type":"tool_use","sessionID":"ses_abc123","part":{"tool":"grep","state":{"title":"Search"}}}\n'
            ),
            stderr="",
        )

    monkeypatch.setattr(assistant.subprocess, "run", fake_run)
    result = run_agent(
        AgentRequest(message="hello", session="ses_abc123"),
        workspace=tmp_path,
        command=("opencode", "run", "--format", "json", "--auto"),
        timeout=30,
    )

    argv = captured["argv"]
    assert isinstance(argv, list)
    assert "--session" in argv
    assert "ses_abc123" in argv
    assert result["response"] == "Markdown **reply**"
    assert result["session"] == "ses_abc123"
    assert result["actions"] == [{"tool": "grep", "summary": "Search"}]


def test_run_agent_new_session_includes_cheat_sheet_grounding(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}
    cheat_sheet = tmp_path / "cheat-sheet.md"
    cheat_sheet.write_text("# Grounding\n\nKey fact.", encoding="utf-8")

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return SimpleNamespace(
            returncode=0,
            stdout='{"type":"text","sessionID":"ses_new","part":{"text":"Grounded reply"}}\n',
            stderr="",
        )

    monkeypatch.setattr(assistant.subprocess, "run", fake_run)
    run_agent(
        AgentRequest(
            message="hello",
            new_session=True,
            cheat_sheet_path=str(cheat_sheet),
            required_reading=("/tmp/docs/index.rst",),
        ),
        workspace=tmp_path,
        command=("opencode", "run", "--format", "json", "--auto"),
        timeout=30,
    )

    argv = captured["argv"]
    assert isinstance(argv, list)
    prompt = argv[-1]
    assert "MANDATORY NEW-SESSION GROUNDING" in prompt
    assert "Key fact." in prompt
    assert "/tmp/docs/index.rst" in prompt
    assert "Do not answer from memory" in prompt


def test_run_agent_reports_empty_reply(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(
        assistant.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr="no output"),
    )

    with pytest.raises(assistant.AgentError, match="no output"):
        run_agent(
            AgentRequest(message="hello"),
            workspace=tmp_path,
            command=("opencode", "run", "--format", "json", "--auto"),
            timeout=30,
        )
