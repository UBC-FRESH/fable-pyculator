#!/usr/bin/env python
"""Browser smoke for the FABLE portal assistant overlay.

Checks the real SPA in Chromium:

- the + Ask overlay opens;
- Shift+Enter inserts a newline while Enter submits;
- markdown replies render as HTML;
- a real assistant chat persists across a full page reload.

The script starts its own isolated portal server and removes its runtime directory afterwards. It
skips cleanly when Playwright or a Chromium browser is unavailable.
"""

from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path
from typing import Any

__all__ = ["main"]

SKIP_EXIT = 0


def main(argv: list[str] | None = None) -> int:
    """Run the browser smoke."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument(
        "--server-python",
        type=Path,
        default=Path(sys.executable),
        help="Python interpreter that has fable-pyculator installed (default: current interpreter).",
    )
    parser.add_argument(
        "--live-agent",
        action="store_true",
        help="Also exercise a real assistant turn for reload persistence.",
    )
    parser.add_argument("--timeout", type=float, default=300.0, help="Timeout for the live assistant turn.")
    args = parser.parse_args(argv)

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        print("SKIP: playwright is not installed (pip install 'fable-pyculator[browser]')")
        return SKIP_EXIT

    root = args.root.expanduser().resolve()
    runtime = root / "runtime" / f"browser-smoke-{uuid.uuid4().hex[:8]}"
    port = _free_port()
    server = _start_server(root, port, runtime, args.server_python)
    log_path = runtime / "server.log"
    try:
        _wait_for_health(port, timeout=60)
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(headless=True)
            except Exception as error:  # noqa: BLE001 - environment-dependent skip
                print(f"SKIP: Chromium could not start: {error}")
                return SKIP_EXIT
            try:
                return _run_checks(browser, port, live_agent=args.live_agent, timeout=args.timeout)
            finally:
                browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
        if log_path.exists():
            print(f"server log: {log_path}")
        shutil.rmtree(runtime, ignore_errors=True)


def _run_checks(browser: Any, port: int, *, live_agent: bool, timeout: float) -> int:
    base = f"http://127.0.0.1:{port}"
    context = browser.new_context()
    page = context.new_page()
    try:
        page.goto(base, wait_until="networkidle")
        page.locator("#app-loading").wait_for(state="hidden", timeout=30000)
        page.locator("#assistant-open").click()
        page.locator("#ask-panel").wait_for(state="visible", timeout=10000)

        calls: list[dict[str, Any]] = []

        def fake_assistant(route: Any) -> None:
            payload = route.request.post_data_json or {}
            chat_id = payload.get("chat_id") or "chat_fake"
            calls.append(payload)
            now = "2026-11-06T00:00:00+00:00"
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps(
                    {
                        "response": "**Grounded** reply.\n\n- first item\n- second item",
                        "session": "ses_fake",
                        "actions": [{"tool": "read", "summary": "src/fable_pyculator/notebook.py"}],
                        "chat_id": chat_id,
                        "chat": {
                            "chat_id": chat_id,
                            "title": "line one",
                            "created_at": now,
                            "updated_at": now,
                            "message_count": 2,
                            "preview": "Grounded reply.",
                            "agent_session": "ses_fake",
                            "run_id": None,
                        },
                    }
                ),
            )

        page.route("**/api/assistant", fake_assistant)
        page.locator("#ask-new").click()
        input_box = page.locator("#ask-input")
        input_box.fill("line one")
        input_box.press("Shift+Enter")
        value = input_box.input_value()
        assert "\n" in value, f"Shift+Enter did not insert a newline: {value!r}"
        input_box.type("line two")
        input_box.press("Enter")
        page.locator(".ask-msg.agent:not(.thinking)").wait_for(state="visible", timeout=15000)
        log_text = page.locator("#ask-log").inner_text()
        assert "line one" in log_text and "line two" in log_text, log_text
        assert "Grounded" in log_text, log_text
        assert page.locator(".ask-msg.agent strong", has_text="Grounded").count() >= 1
        assert calls and calls[0]["message"].startswith("line one"), calls
        page.unroute("**/api/assistant", fake_assistant)
        print("PASS: overlay, markdown, Enter and Shift+Enter")

        if not live_agent:
            print("SKIP: live-agent persistence (pass --live-agent to enable)")
            return 0
        agent = json.loads(page.request.get(f"{base}/api/agent").text())
        if not agent.get("available"):
            print("SKIP: live-agent persistence (opencode is not available)")
            return 0

        page.locator("#ask-new").click()
        input_box.fill("Reply with exactly OK and nothing else.")
        input_box.press("Enter")
        page.wait_for_function(
            "() => document.querySelector('#ask-log').innerText.includes('Reply with exactly OK')",
            timeout=30000,
        )
        page.wait_for_function(
            "() => !document.querySelector('#ask-send').disabled && !document.querySelector('.ask-msg.thinking')",
            timeout=timeout * 1000,
        )
        log_text = page.locator("#ask-log").inner_text()
        assert "Assistant unavailable" not in log_text, log_text
        assert "Reply with exactly OK" in log_text, log_text
        chat_id = page.evaluate("localStorage.getItem('fable-portal-chat')")
        assert chat_id, "chat id was not remembered"
        page.locator("#ask-history").click()
        page.locator("#ask-sessions").wait_for(state="visible", timeout=5000)
        assert "Reply with exactly OK" in page.locator("#ask-sessions").inner_text()

        page.reload(wait_until="networkidle")
        page.locator("#app-loading").wait_for(state="hidden", timeout=30000)
        page.locator("#assistant-open").click()
        page.wait_for_function(
            "() => document.querySelector('#ask-log').innerText.includes('Reply with exactly OK')",
            timeout=15000,
        )
        assert page.evaluate("localStorage.getItem('fable-portal-chat')") == chat_id
        print("PASS: live assistant chat persisted across reload")
        return 0
    except Exception as error:  # noqa: BLE001 - report the assertion and page text
        print(f"FAIL: {error}")
        try:
            print("assistant log:", page.locator("#ask-log").inner_text()[:2000])
        except Exception:
            pass
        return 1
    finally:
        context.close()


def _start_server(root: Path, port: int, runtime: Path, python: Path) -> subprocess.Popen:
    runtime.mkdir(parents=True, exist_ok=True)
    log_path = runtime / "server.log"
    log = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            str(python),
            "-m",
            "fable_pyculator.cli",
            "web",
            "--root",
            str(root),
            "--runtime",
            str(runtime),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--allow-agent",
        ],
        cwd=root,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    return process


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_health(port: int, *, timeout: float) -> None:
    deadline = time.time() + timeout
    url = f"http://127.0.0.1:{port}/api/health"
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"portal did not become healthy on port {port}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
