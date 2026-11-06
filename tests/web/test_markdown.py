from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

STATIC_DIR = Path(__file__).resolve().parents[2] / "src" / "fable_pyculator" / "web" / "static"


def test_markdown_renderer_handles_assistant_and_user_formatting() -> None:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not available for the static markdown check")

    script = """
import { renderMarkdown } from "./markdown.js";
const cases = {
  inline: renderMarkdown("**bold** and *italic*\\nnext line"),
  list: renderMarkdown("- One\\n- Two"),
  code: renderMarkdown("```\\nconst x = 1;\\n```"),
  link: renderMarkdown("[Example](https://example.com/path)"),
  table: renderMarkdown("| A | B |\\n|---|---|\\n| 1 | 2 |"),
  escape: renderMarkdown("<script>alert(1)</script>"),
  unsafe: renderMarkdown("[bad](javascript:alert(1))"),
};
console.log(JSON.stringify(cases));
"""
    completed = subprocess.run(
        [node, "--input-type=module", "--eval", script],
        cwd=STATIC_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    cases = json.loads(completed.stdout)

    assert "<strong>bold</strong>" in cases["inline"]
    assert "<em>italic</em>" in cases["inline"]
    assert "<br>next line" in cases["inline"]
    assert cases["list"] == "<ul><li>One</li><li>Two</li></ul>"
    assert "<pre><code>const x = 1;" in cases["code"]
    assert '<a href="https://example.com/path" target="_blank" rel="noreferrer">Example</a>' in cases["link"]
    assert '<table class="md-table">' in cases["table"]
    assert "&lt;script&gt;" in cases["escape"]
    assert "<script>" not in cases["escape"]
    assert 'href="javascript:' not in cases["unsafe"]
