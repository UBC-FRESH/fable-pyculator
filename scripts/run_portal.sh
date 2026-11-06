#!/usr/bin/env bash
# Start the FABLE Pyculator portal from environment variables.
#
# Common local use:
#   scripts/run_portal.sh
#
# Public/reverse-proxy use:
#   FABLE_PORTAL_HOST=0.0.0.0 \
#   FABLE_PORTAL_ALLOW_REMOTE=1 \
#   FABLE_PORTAL_AUTH_USER=operator \
#   FABLE_PORTAL_AUTH_PASSWORD='...' \
#   scripts/run_portal.sh
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Start the FABLE Pyculator portal.

Environment:
  FABLE_PORTAL_ROOT           Repository root (default: parent of this script)
  FABLE_PORTAL_PYTHON         Python interpreter (default: $ROOT/.venv/bin/python)
  FABLE_PORTAL_RUNTIME        Ignored runtime directory (default: $ROOT/runtime/portal)
  FABLE_PORTAL_HOST           Bind host (default: 127.0.0.1)
  FABLE_PORTAL_PORT           Bind port (default: 8768)
  FABLE_PORTAL_ROOT_PATH      Proxy prefix (e.g. /user/me/proxy/8768)
  FABLE_PORTAL_ALLOW_REMOTE   Set to 1 to permit a non-loopback bind
  FABLE_PORTAL_ALLOW_AGENT    Set to 1 to enable the local assistant
  FABLE_PORTAL_AUTH_USER      Optional HTTP Basic auth user
  FABLE_PORTAL_AUTH_PASSWORD  Optional HTTP Basic auth password
EOF
  exit 0
fi

ROOT="${FABLE_PORTAL_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON="${FABLE_PORTAL_PYTHON:-$ROOT/.venv/bin/python}"
RUNTIME="${FABLE_PORTAL_RUNTIME:-$ROOT/runtime/portal}"
HOST="${FABLE_PORTAL_HOST:-127.0.0.1}"
PORT="${FABLE_PORTAL_PORT:-8768}"
ROOT_PATH="${FABLE_PORTAL_ROOT_PATH:-}"

ARGS=(web --root "$ROOT" --runtime "$RUNTIME" --host "$HOST" --port "$PORT")
if [[ -n "$ROOT_PATH" ]]; then
  ARGS+=(--root-path "$ROOT_PATH")
fi
if [[ "${FABLE_PORTAL_ALLOW_REMOTE:-0}" == "1" ]]; then
  ARGS+=(--allow-remote)
fi
if [[ "${FABLE_PORTAL_ALLOW_AGENT:-0}" == "1" ]]; then
  ARGS+=(--allow-agent)
fi
if [[ -n "${FABLE_PORTAL_AUTH_USER:-}" ]]; then
  ARGS+=(--auth-user "$FABLE_PORTAL_AUTH_USER")
fi
if [[ -n "${FABLE_PORTAL_AUTH_PASSWORD:-}" ]]; then
  ARGS+=(--auth-password "$FABLE_PORTAL_AUTH_PASSWORD")
fi

exec "$PYTHON" -m fable_pyculator.cli "${ARGS[@]}"
