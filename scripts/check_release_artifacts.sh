#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-"$ROOT_DIR/.venv/bin/python"}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RELEASE_CHECK_DIR:-"$ROOT_DIR/tmp/release-checks/$RUN_ID"}"
DIST_DIR="$RUN_DIR/dist"
INSTALL_DIR="$RUN_DIR/install-$RUN_ID"

if [[ ! -x "$PYTHON_BIN" ]]; then
  if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "$PYTHON_BIN")"
  else
    echo "Python executable not found: $PYTHON_BIN" >&2
    echo "Run scripts/bootstrap_dev_env.sh first or set PYTHON=/path/to/python." >&2
    exit 2
  fi
fi

mkdir -p "$RUN_DIR"

echo "[release-check] run directory: $RUN_DIR"
echo "[release-check] removing stale build outputs"
rm -rf "$ROOT_DIR/build"
rm -rf "$ROOT_DIR/src/fable_pyculator.egg-info"
rm -rf "$DIST_DIR"
rm -rf "$INSTALL_DIR"
mkdir -p "$DIST_DIR" "$INSTALL_DIR"

echo "[release-check] building sdist and wheel"
"$PYTHON_BIN" -m build --sdist --wheel --outdir "$DIST_DIR" "$ROOT_DIR"

echo "[release-check] running twine metadata check"
"$PYTHON_BIN" -m twine check "$DIST_DIR"/*

echo "[release-check] inspecting artifact contents"
"$PYTHON_BIN" - "$DIST_DIR" "$ROOT_DIR" <<'PY'
from __future__ import annotations

import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

dist_dir = Path(sys.argv[1])
root_dir = Path(sys.argv[2])
approved_generated_archives = {
    Path("examples/fable_2021/generated_fable_2021_model.py.xz"),
}
forbidden_parts = {
    ".venv",
    "_build",
    "tmp",
    "private-workbooks",
    "generated-models",
    "release-checks",
}
forbidden_suffixes = {
    ".xls",
    ".xlsb",
    ".xlsm",
    ".xlsx",
}


def names_for(path: Path) -> list[str]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path) as archive:
            return archive.getnames()
    raise RuntimeError(f"unsupported artifact type: {path}")


errors: list[str] = []


def inspect_name(name: str, *, source: str) -> None:
    path = Path(name)
    parts = set(path.parts)
    suffix = path.suffix.lower()
    if parts & forbidden_parts:
        errors.append(f"{source}: forbidden path: {name}")
    if suffix in forbidden_suffixes:
        errors.append(f"{source}: workbook file: {name}")
    if path.name.startswith("generated_fable_") and path.suffix == ".py":
        errors.append(f"{source}: decompressed generated model: {name}")
    if path.name.startswith("generated_fable_") and path.suffix == ".xz":
        normalized_parts = path.parts[1:] if path.parts and path.parts[0].startswith("fable_pyculator-") else path.parts
        normalized = Path(*normalized_parts)
        if normalized not in approved_generated_archives:
            errors.append(f"{source}: unapproved generated model archive: {name}")


tracked_names = subprocess.check_output(
    ["git", "-C", str(root_dir), "ls-files"],
    text=True,
).splitlines()
for name in tracked_names:
    inspect_name(name, source="git")

for artifact in sorted(dist_dir.iterdir()):
    names = names_for(artifact)
    for name in names:
        inspect_name(name, source=artifact.name)
    print(f"[release-check] inspected {artifact.name}: {len(names)} entries")

if errors:
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)
PY

echo "[release-check] creating clean install environment"
"$PYTHON_BIN" -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/python" -m pip install --upgrade pip
"$INSTALL_DIR/.venv/bin/python" -m pip install "$DIST_DIR"/*.whl

echo "[release-check] running installed package smoke tests"
"$INSTALL_DIR/.venv/bin/python" - <<'PY'
from __future__ import annotations

import fable_pyculator

assert fable_pyculator.__version__ == "0.1.0a2", fable_pyculator.__version__
assert "build_notebook_spec" in fable_pyculator.__all__
assert "build_2021_notebook_spec" in fable_pyculator.__all__
assert "run_2020_notebook_loop" in fable_pyculator.__all__
assert "run_2021_notebook_loop" in fable_pyculator.__all__
assert "scenario_definition_tables_for_location" in fable_pyculator.__all__
print(f"[release-check] imported fable_pyculator {fable_pyculator.__version__}")
PY

echo "[release-check] release artifact checks passed"
