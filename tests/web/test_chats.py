from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fable_pyculator.web import app as portal_app
from fable_pyculator.web.app import create_app
from fable_pyculator.web.chats import ChatStore
from fable_pyculator.web.service import PortalConfig


def test_chat_store_persists_messages_and_session(tmp_path: Path) -> None:
    store = ChatStore(tmp_path / "chats")
    chat = store.create()
    store.append_message(chat.chat_id, role="user", content="A long **question** about FABLE outputs")
    store.append_message(
        chat.chat_id,
        role="assistant",
        content="A grounded answer",
        actions=[{"tool": "read", "summary": "docs"}],
    )
    store.set_session(chat.chat_id, "ses_persisted")

    reloaded = ChatStore(tmp_path / "chats").get(chat.chat_id)
    summaries = store.list()

    assert reloaded.title.startswith("A long **question**")
    assert reloaded.agent_session == "ses_persisted"
    assert [message["role"] for message in reloaded.messages] == ["user", "assistant"]
    assert summaries[0]["message_count"] == 2
    assert summaries[0]["preview"] == "A grounded answer"
    assert store.delete(chat.chat_id) is True
    assert store.list() == []


def test_chat_api_creates_lists_loads_and_deletes(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2021",))
    with TestClient(create_app(config)) as client:
        created = client.post("/api/chats", json={}).json()
        chat_id = created["chat_id"]
        listed = client.get("/api/chats").json()
        loaded = client.get(f"/api/chats/{chat_id}").json()
        deleted = client.delete(f"/api/chats/{chat_id}").json()

        assert listed[0]["chat_id"] == chat_id
        assert loaded["messages"] == []
        assert deleted["deleted"] is True
        assert client.get(f"/api/chats/{chat_id}").status_code == 404


def test_assistant_persists_chat_and_grounds_new_sessions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = PortalConfig(
        repo_root=tmp_path,
        runtime_dir=tmp_path / "runtime",
        versions=("2021",),
        allow_agent=True,
    )
    source = tmp_path / "src" / "fable_pyculator" / "notebook.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        "def build_notebook_spec(workbook_path, *, workbook_id, strict_headlines=False):\n    return None\n",
        encoding="utf-8",
    )
    captured = []

    def fake_run_agent(request, **kwargs):
        captured.append(request)
        return {
            "response": f"Answer {len(captured)}",
            "session": "ses_chat",
            "actions": [{"tool": "read", "summary": "cheat sheet"}],
            "returncode": 0,
            "command": "opencode",
        }

    monkeypatch.setattr(portal_app, "run_agent", fake_run_agent)
    with TestClient(create_app(config)) as client:
        first = client.post("/api/assistant", json={"message": "First question"}).json()
        chat_id = first["chat_id"]
        second = client.post(
            "/api/assistant",
            json={"message": "Second question", "chat_id": chat_id},
        ).json()
        loaded = client.get(f"/api/chats/{chat_id}").json()
        listed = client.get("/api/chats").json()
        cheat_sheet = client.get("/api/assistant/cheatsheet.md")

    assert first["chat"]["title"] == "First question"
    assert second["chat_id"] == chat_id
    assert captured[0].new_session is True
    assert captured[1].new_session is False
    assert captured[0].session is None
    assert captured[1].session == "ses_chat"
    assert Path(captured[0].cheat_sheet_path).is_file()
    assert "Required reading" in Path(captured[0].cheat_sheet_path).read_text(encoding="utf-8")
    assert [message["role"] for message in loaded["messages"]] == [
        "user",
        "assistant",
        "user",
        "assistant",
    ]
    assert listed[0]["message_count"] == 4
    assert cheat_sheet.status_code == 200
    assert "FABLE 2024" in cheat_sheet.text
    assert "Modelwright" in cheat_sheet.text
    assert "Documentation digest" in cheat_sheet.text
    assert "Source API index" in cheat_sheet.text
    assert "build_notebook_spec" in cheat_sheet.text


def test_chat_store_metadata_pin_archive_search_and_markdown(tmp_path: Path) -> None:
    from fable_pyculator.web.chats import auto_title

    store = ChatStore(tmp_path / "chats")
    first = store.create()
    second = store.create()
    store.append_message(first.chat_id, role="user", content="Explain land totals")
    store.append_message(first.chat_id, role="assistant", content="Here is the answer")
    store.set_metadata(first.chat_id, title="Land totals", pinned=True)
    store.set_metadata(second.chat_id, archived=True)
    store.append_message(second.chat_id, role="user", content="Old archived chat")

    assert store.list()[0]["chat_id"] == first.chat_id
    assert store.list()[0]["pinned"] is True
    assert all(item["chat_id"] != second.chat_id for item in store.list())
    assert any(item["chat_id"] == second.chat_id for item in store.list(include_archived=True))
    assert [item["chat_id"] for item in store.list(query="land")] == [first.chat_id]
    markdown = store.get(first.chat_id).to_markdown()
    assert "# Land totals" in markdown
    assert "Here is the answer" in markdown
    assert auto_title("hi", "Here is a useful answer about FABLE") == "Here is a useful answer about FABLE"


def test_chat_api_update_and_export(tmp_path: Path) -> None:
    config = PortalConfig(repo_root=tmp_path, runtime_dir=tmp_path / "runtime", versions=("2021",))
    with TestClient(create_app(config)) as client:
        chat = client.post("/api/chats", json={}).json()
        chat_id = chat["chat_id"]
        updated = client.patch(
            f"/api/chats/{chat_id}",
            json={"title": "Renamed", "pinned": True, "archived": True},
        ).json()
        listed = client.get("/api/chats").json()
        archived = client.get("/api/chats?include_archived=true").json()
        exported = client.get(f"/api/chats/{chat_id}/export.md")

    assert updated["title"] == "Renamed"
    assert updated["pinned"] is True
    assert updated["archived"] is True
    assert listed == []
    assert archived[0]["chat_id"] == chat_id
    assert exported.status_code == 200
    assert "# Renamed" in exported.text
