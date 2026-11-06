"""Persistent chat sessions for the FABLE portal assistant.

Chats are small JSON records under the ignored runtime directory. The browser can list, reopen, and
delete them across page reloads and service restarts. Each record keeps the OpenCode session id so a
resumed chat continues the same local agent conversation.
"""

from __future__ import annotations

import json
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

__all__ = ["ChatRecord", "ChatStore", "auto_title"]

_CHAT_ID_PATTERN = re.compile(r"^chat_[A-Za-z0-9]+$")
_TITLE_LIMIT = 72
_PREVIEW_LIMIT = 140


@dataclass
class ChatRecord:
    """One persisted assistant conversation."""

    chat_id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    agent_session: str | None = None
    run_id: str | None = None
    pinned: bool = False
    archived: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return the full JSON-ready chat record."""

        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": list(self.messages),
            "agent_session": self.agent_session,
            "run_id": self.run_id,
            "pinned": self.pinned,
            "archived": self.archived,
        }

    def summary(self) -> dict[str, Any]:
        """Return the compact list entry used by the browser."""

        preview = ""
        if self.messages:
            preview = _preview(self.messages[-1].get("content"))
        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "message_count": len(self.messages),
            "preview": preview,
            "agent_session": self.agent_session,
            "run_id": self.run_id,
            "pinned": self.pinned,
            "archived": self.archived,
        }

    def to_markdown(self) -> str:
        """Render the conversation as exportable Markdown."""

        lines = [
            f"# {self.title}",
            "",
            f"- Chat: `{self.chat_id}`",
            f"- Created: {self.created_at}",
            f"- Updated: {self.updated_at}",
            f"- Agent session: `{self.agent_session or 'none'}`",
        ]
        if self.run_id:
            lines.append(f"- Run context: `{self.run_id}`")
        lines.append("")
        for message in self.messages:
            role = str(message.get("role", "message")).title()
            lines.extend(
                [
                    f"## {role} — {message.get('created_at', '')}",
                    "",
                    str(message.get("content", "")),
                    "",
                ]
            )
            actions = message.get("actions") or []
            if actions:
                lines.append("Actions:")
                for action in actions:
                    if isinstance(action, dict):
                        summary = action.get("summary") or ""
                        lines.append(f"- `{action.get('tool', 'tool')}` {summary}".rstrip())
                lines.append("")
        return "\n".join(lines).rstrip() + "\n"


class ChatStore:
    """Thread-safe JSON chat store under one directory."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def create(self, *, run_id: str | None = None, title: str = "New chat") -> ChatRecord:
        """Create and persist an empty chat."""

        now = _now()
        record = ChatRecord(
            chat_id=f"chat_{uuid.uuid4().hex[:12]}",
            title=title,
            created_at=now,
            updated_at=now,
            run_id=run_id,
        )
        with self._lock:
            self._write(record)
        return record

    def list(
        self,
        *,
        limit: int = 100,
        include_archived: bool = False,
        query: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return chat summaries, pinned first and newest first within each group."""

        records: list[ChatRecord] = []
        with self._lock:
            for path in self.directory.glob("chat_*.json"):
                record = self._read_path(path)
                if record is not None:
                    records.append(record)
        if not include_archived:
            records = [record for record in records if not record.archived]
        if query:
            needle = query.casefold()
            records = [
                record
                for record in records
                if needle in record.title.casefold()
                or any(needle in _preview(message.get("content")).casefold() for message in record.messages)
            ]
        records.sort(key=lambda record: record.updated_at, reverse=True)
        records.sort(key=lambda record: not record.pinned)
        return [record.summary() for record in records[:limit]]

    def get(self, chat_id: str) -> ChatRecord:
        """Return one chat or raise ``KeyError``."""

        path = self._path(chat_id)
        with self._lock:
            record = self._read_path(path)
        if record is None:
            raise KeyError(f"unknown chat id {chat_id!r}")
        return record

    def append_message(
        self,
        chat_id: str,
        *,
        role: str,
        content: str,
        actions: list[dict[str, str]] | None = None,
        run_id: str | None = None,
    ) -> ChatRecord:
        """Append one message and persist the chat."""

        with self._lock:
            record = self.get(chat_id)
            now = _now()
            record.messages.append(
                {
                    "role": role,
                    "content": str(content),
                    "actions": list(actions or []),
                    "created_at": now,
                }
            )
            if role == "user" and record.title == "New chat":
                record.title = _title(content)
            if run_id:
                record.run_id = run_id
            record.updated_at = now
            self._write(record)
            return record

    def set_session(self, chat_id: str, session_id: str | None) -> ChatRecord:
        """Persist the OpenCode session id for a chat."""

        with self._lock:
            record = self.get(chat_id)
            record.agent_session = session_id
            record.updated_at = _now()
            self._write(record)
            return record

    def set_metadata(
        self,
        chat_id: str,
        *,
        title: str | None = None,
        pinned: bool | None = None,
        archived: bool | None = None,
    ) -> ChatRecord:
        """Update chat title, pin, and archive state."""

        with self._lock:
            record = self.get(chat_id)
            if title is not None:
                record.title = _title(title)
            if pinned is not None:
                record.pinned = bool(pinned)
            if archived is not None:
                record.archived = bool(archived)
            record.updated_at = _now()
            self._write(record)
            return record

    def delete(self, chat_id: str) -> bool:
        """Delete one chat; return whether it existed."""

        path = self._path(chat_id)
        with self._lock:
            if not path.exists():
                return False
            path.unlink()
            return True

    def _path(self, chat_id: str) -> Path:
        if not _CHAT_ID_PATTERN.fullmatch(chat_id):
            raise KeyError("invalid chat id")
        return self.directory / f"{chat_id}.json"

    def _read_path(self, path: Path) -> ChatRecord | None:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None
        chat_id = str(payload.get("chat_id", ""))
        if not _CHAT_ID_PATTERN.fullmatch(chat_id):
            return None
        messages = payload.get("messages", [])
        return ChatRecord(
            chat_id=chat_id,
            title=str(payload.get("title", "Chat")),
            created_at=str(payload.get("created_at", "")),
            updated_at=str(payload.get("updated_at", "")),
            messages=[message for message in messages if isinstance(message, dict)],
            agent_session=payload.get("agent_session"),
            run_id=payload.get("run_id"),
            pinned=bool(payload.get("pinned", False)),
            archived=bool(payload.get("archived", False)),
        )

    def _write(self, record: ChatRecord) -> None:
        path = self._path(record.chat_id)
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_text(
            json.dumps(record.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)


def auto_title(user_message: str, assistant_message: str | None = None) -> str:
    """Choose a concise title from the first exchange.

    Short or generic user prompts fall back to the first meaningful assistant line.
    """

    user = " ".join(str(user_message or "").split())
    if len(user.split()) >= 2 and len(user) >= 12:
        return user[:_TITLE_LIMIT]
    for line in str(assistant_message or "").splitlines():
        cleaned = " ".join(line.replace("#", "").replace("*", "").replace("`", "").split())
        if cleaned and not cleaned.startswith(("-", "•")):
            return cleaned[:_TITLE_LIMIT]
    return user[:_TITLE_LIMIT] or "New chat"


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _title(text: str) -> str:
    collapsed = " ".join(str(text).split())
    return collapsed[:_TITLE_LIMIT] or "New chat"


def _preview(value: object) -> str:
    collapsed = " ".join(str(value or "").split())
    return collapsed[:_PREVIEW_LIMIT]
