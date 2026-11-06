"""Command-line entry point for FABLE Pyculator.

The notebook package is still the primary surface. This CLI exists so the optional web portal can
be started without a notebook::

    fable-pyculator web --root /path/to/fable-pyculator
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from fable_pyculator import __version__
from fable_pyculator.web.artifacts import DEFAULT_VERSIONS
from fable_pyculator.web.assistant import DEFAULT_AGENT_MODEL

__all__ = ["main"]


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI."""

    parser = _parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.command == "web":
        return _web(args)
    parser.print_help()
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fable-pyculator", description="FABLE Pyculator tools.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")
    web = subparsers.add_parser("web", help="Serve the optional local web portal.")
    web.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root containing examples/ and tmp/ (default: current directory).",
    )
    web.add_argument(
        "--runtime",
        type=Path,
        default=None,
        help="Ignored runtime directory for prepared specs and saved runs.",
    )
    web.add_argument(
        "--version-choice",
        dest="versions",
        action="append",
        choices=DEFAULT_VERSIONS,
        help="Workbook version to offer (repeatable). Defaults to 2021, 2024, and 2020.",
    )
    web.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1).")
    web.add_argument("--port", default=8766, type=int, help="Bind port (default: 8766).")
    web.add_argument(
        "--root-path",
        default="",
        help="Proxy prefix, for example /user/me/proxy/8766.",
    )
    web.add_argument(
        "--allow-remote",
        action="store_true",
        help="Allow a non-loopback bind. The portal has no authentication.",
    )
    web.add_argument(
        "--allow-agent",
        action="store_true",
        help="Enable the optional local assistant (installed opencode CLI).",
    )
    web.add_argument(
        "--agent-model",
        default=DEFAULT_AGENT_MODEL,
        help="Model identifier passed to the local assistant (blank to use opencode's default).",
    )
    web.add_argument(
        "--agent-timeout",
        default=180.0,
        type=float,
        help="Assistant subprocess timeout in seconds.",
    )
    return parser


def _web(args: argparse.Namespace) -> int:
    try:
        from fable_pyculator.web.app import run_server, validate_bind
        from fable_pyculator.web.service import PortalConfig
    except ModuleNotFoundError:
        print(
            "The web portal needs optional dependencies. Install with: pip install 'fable-pyculator[web]'",
        )
        return 1
    try:
        validate_bind(args.host, allow_remote=args.allow_remote)
    except ValueError as error:
        print(str(error))
        return 2
    config = PortalConfig(
        repo_root=args.root,
        runtime_dir=args.runtime,
        versions=tuple(args.versions) if args.versions else DEFAULT_VERSIONS,
        allow_agent=args.allow_agent,
        agent_model=args.agent_model or None,
        agent_timeout=args.agent_timeout,
    )
    try:
        run_server(
            config,
            host=args.host,
            port=args.port,
            root_path=args.root_path,
            allow_remote=args.allow_remote,
        )
    except (RuntimeError, ValueError) as error:
        print(str(error))
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
