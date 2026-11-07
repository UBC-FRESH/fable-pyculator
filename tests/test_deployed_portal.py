from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_deployed_portal.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_deployed_portal", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_deployment_check_help() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "CF_ACCESS_CLIENT_ID" in result.stdout
    assert "--expect-version" in result.stdout
    assert "Cloudflare" in result.stdout


def test_headers_include_access_and_basic_auth() -> None:
    module = _load_module()

    headers = module._headers(
        access_client_id="client-id",
        access_client_secret="client-secret",
        basic_user="operator",
        basic_password="password",
    )

    assert headers["CF-Access-Client-Id"] == "client-id"
    assert headers["CF-Access-Client-Secret"] == "client-secret"
    assert headers["authorization"].startswith("Basic ")


def test_artifact_states_summarize_checksum_states() -> None:
    module = _load_module()

    states = module._artifact_states(
        [
            {"version": "2021", "model_checksum": {"state": "verified"}, "model_verified": True},
            {"version": "2020", "model_checksum": {"state": "unknown"}, "model_verified": False},
        ]
    )

    assert states == [
        {"version": "2021", "model_checksum": "verified", "model_verified": True},
        {"version": "2020", "model_checksum": "unknown", "model_verified": False},
    ]


def test_access_redirect_detection() -> None:
    module = _load_module()
    check = module.DeploymentCheck(
        path="/api/health",
        status=302,
        headers={"location": "https://ubc-fresh.cloudflareaccess.com/cdn-cgi/access/login/x"},
        body="",
    )

    assert module._is_access_redirect(check) is True
