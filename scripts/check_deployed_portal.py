#!/usr/bin/env python
"""Check a deployed FABLE Pyculator portal without storing credentials.

Cloudflare Access service tokens are read from ``CF_ACCESS_CLIENT_ID`` and
``CF_ACCESS_CLIENT_SECRET``. Optional portal Basic auth is read from
``FABLE_PORTAL_AUTH_USER`` and ``FABLE_PORTAL_AUTH_PASSWORD``.

Examples::

    python scripts/check_deployed_portal.py --url https://fable-pyculator.01101.dev
    python scripts/check_deployed_portal.py --url https://fable-pyculator.01101.dev \
        --expect-version 0.1.0a5 --json
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

__all__ = ["DeploymentCheck", "check_deployment", "main"]


@dataclass(frozen=True)
class DeploymentCheck:
    """One HTTP result from the deployed portal."""

    path: str
    status: int | None
    headers: dict[str, str]
    body: str
    error: str | None = None


def main(argv: list[str] | None = None) -> int:
    """Run the deployment check."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=os.environ.get("FABLE_DEPLOY_URL", "https://fable-pyculator.01101.dev"),
        help="Deployed portal base URL.",
    )
    parser.add_argument("--expect-version", help="Fail unless /api/health reports this version.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout in seconds.")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Print JSON.")
    parser.add_argument(
        "--allow-access-redirect",
        action="store_true",
        help="Treat a Cloudflare Access redirect as an incomplete but successful check.",
    )
    args = parser.parse_args(argv)

    result = check_deployment(
        args.url,
        expect_version=args.expect_version,
        timeout=args.timeout,
    )
    if args.json_output:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        _print_text(result)
    if result["access_required"]:
        return 0 if args.allow_access_redirect else 2
    if result["expected_version"] and result.get("version") != result["expected_version"]:
        return 1
    return 0


def check_deployment(
    base_url: str,
    *,
    expect_version: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Check health, agent, root, and artifact state on a deployed portal."""

    base = base_url.rstrip("/")
    headers = _headers(
        access_client_id=os.environ.get("CF_ACCESS_CLIENT_ID"),
        access_client_secret=os.environ.get("CF_ACCESS_CLIENT_SECRET"),
        basic_user=os.environ.get("FABLE_PORTAL_AUTH_USER"),
        basic_password=os.environ.get("FABLE_PORTAL_AUTH_PASSWORD"),
    )
    health = _request(base + "/api/health", headers, timeout)
    access_required = _is_access_redirect(health)
    health_payload = _json_body(health)
    version = health_payload.get("version") if isinstance(health_payload, dict) else None

    checks: dict[str, DeploymentCheck] = {"health": health}
    if not access_required and health.status == 200:
        checks["root"] = _request(base + "/", headers, timeout)
        checks["agent"] = _request(base + "/api/agent", headers, timeout)
        checks["artifacts"] = _request(base + "/api/artifacts", headers, timeout)

    artifacts_payload = _json_body(checks.get("artifacts")) if "artifacts" in checks else None
    agent_payload = _json_body(checks.get("agent")) if "agent" in checks else None
    return {
        "url": base,
        "access_required": access_required,
        "access_service_token_configured": bool(
            os.environ.get("CF_ACCESS_CLIENT_ID") and os.environ.get("CF_ACCESS_CLIENT_SECRET")
        ),
        "basic_auth_configured": bool(
            os.environ.get("FABLE_PORTAL_AUTH_USER") and os.environ.get("FABLE_PORTAL_AUTH_PASSWORD")
        ),
        "version": version,
        "expected_version": expect_version,
        "prepared": health_payload.get("prepared") if isinstance(health_payload, dict) else None,
        "assistant_enabled": health_payload.get("assistant_enabled") if isinstance(health_payload, dict) else None,
        "agent": agent_payload,
        "artifacts": _artifact_states(artifacts_payload),
        "checks": {
            name: {
                "status": check.status,
                "error": check.error,
                "location": check.headers.get("location"),
            }
            for name, check in checks.items()
        },
    }


def _headers(
    *,
    access_client_id: str | None,
    access_client_secret: str | None,
    basic_user: str | None,
    basic_password: str | None,
) -> dict[str, str]:
    """Build request headers from optional Access and Basic-auth credentials."""

    headers = {"accept": "application/json", "user-agent": "fable-pyculator-deployment-check/1"}
    if access_client_id and access_client_secret:
        headers["CF-Access-Client-Id"] = access_client_id
        headers["CF-Access-Client-Secret"] = access_client_secret
    if basic_user and basic_password:
        token = base64.b64encode(f"{basic_user}:{basic_password}".encode("utf-8")).decode("ascii")
        headers["authorization"] = f"Basic {token}"
    return headers


def _request(url: str, headers: dict[str, str], timeout: float) -> DeploymentCheck:
    """Make one request without following redirects."""

    request = urllib.request.Request(url, headers=headers, method="GET")
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(request, timeout=timeout) as response:
            return DeploymentCheck(
                path=urllib.parse.urlsplit(url).path or "/",
                status=response.status,
                headers={key.lower(): value for key, value in response.headers.items()},
                body=response.read(2_000_000).decode("utf-8", errors="replace"),
            )
    except urllib.error.HTTPError as error:
        return DeploymentCheck(
            path=urllib.parse.urlsplit(url).path or "/",
            status=error.code,
            headers={key.lower(): value for key, value in error.headers.items()},
            body=error.read(2_000_000).decode("utf-8", errors="replace"),
        )
    except OSError as error:
        return DeploymentCheck(
            path=urllib.parse.urlsplit(url).path or "/",
            status=None,
            headers={},
            body="",
            error=f"{type(error).__name__}: {error}",
        )


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _is_access_redirect(check: DeploymentCheck) -> bool:
    location = check.headers.get("location", "").casefold()
    return check.status in {301, 302, 303, 307, 308} and "cloudflareaccess.com" in location


def _json_body(check: DeploymentCheck | None) -> Any:
    if check is None or check.status != 200 or not check.body:
        return None
    try:
        return json.loads(check.body)
    except json.JSONDecodeError:
        return None


def _artifact_states(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    states = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        checksum = item.get("model_checksum")
        states.append(
            {
                "version": item.get("version"),
                "model_checksum": checksum.get("state") if isinstance(checksum, dict) else None,
                "model_verified": item.get("model_verified"),
            }
        )
    return states


def _print_text(result: dict[str, Any]) -> None:
    print(f"Deployed portal: {result['url']}")
    if result["access_required"]:
        print("Cloudflare Access: required (no service token configured)")
        print("Set CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET to inspect the deployment.")
        return
    print(f"Version: {result.get('version') or 'unknown'}")
    if result.get("expected_version"):
        print(f"Expected: {result['expected_version']}")
    print(f"Prepared models: {', '.join(result.get('prepared') or []) or 'none'}")
    print(f"Assistant enabled: {result.get('assistant_enabled')}")
    print("Artifacts:")
    for item in result.get("artifacts") or []:
        print(f"- {item.get('version')}: checksum={item.get('model_checksum')} verified={item.get('model_verified')}")
    failures = [
        f"{name}: {check['error'] or check['location'] or check['status']}"
        for name, check in result["checks"].items()
        if check["status"] not in {200, 401, 403}
    ]
    if failures:
        print("Warnings:")
        for failure in failures:
            print(f"- {failure}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
