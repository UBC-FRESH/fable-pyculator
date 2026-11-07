"""Compiled grounding sheet for the portal assistant.

The assistant is required to read this document and the files it lists before answering a new chat
session. It contains only facts the portal can verify from local configuration, artifacts, prepared
specs, and saved runs, plus explicit pointers to the FABLE Pyculator and Modelwright documentation
and source code.
"""

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fable_pyculator import __version__

__all__ = ["CheatSheet", "build_cheat_sheet", "ensure_cheat_sheet", "modelwright_root"]

_FABLE_DOCS = (
    "README.md",
    "docs/index.rst",
    "docs/guides/web-portal.rst",
    "docs/guides/notebook-control-surface.rst",
    "docs/guides/github-issue-workflow.rst",
    "docs/guides/optimization-pilot.rst",
    "docs/guides/workbook-structure.rst",
    "docs/guides/generated-model-artifacts.rst",
    "docs/guides/validation-scope.rst",
    "docs/guides/validation-evidence-packaging.rst",
    "docs/guides/scenario-bundles.rst",
    "docs/guides/scenario-definition-editing.rst",
    "docs/reference/api.rst",
    "AGENTS.md",
    "ROADMAP.md",
    "CHANGE_LOG.md",
)
_FABLE_ISSUE_TEMPLATES = (
    ".github/ISSUE_TEMPLATE/phase.md",
    ".github/ISSUE_TEMPLATE/task.md",
)
_FABLE_CODE = (
    "src/fable_pyculator/spec.py",
    "src/fable_pyculator/discovery.py",
    "src/fable_pyculator/notebook.py",
    "src/fable_pyculator/surface.py",
    "src/fable_pyculator/scenarios.py",
    "src/fable_pyculator/scenario_definitions.py",
    "src/fable_pyculator/scenario_rules.py",
    "src/fable_pyculator/validation.py",
    "src/fable_pyculator/web/app.py",
    "src/fable_pyculator/web/service.py",
    "src/fable_pyculator/web/assistant.py",
    "src/fable_pyculator/web/artifacts.py",
    "scripts/check_issue_body.py",
)
_MODELWRIGHT_DOCS = (
    "README.md",
    "AGENTS.md",
    "docs/index.rst",
    "docs/guides/quickstart.rst",
    "docs/guides/notebook-interface.rst",
    "docs/guides/wrapping-generated-models.rst",
    "docs/guides/generated-model-artifacts.rst",
    "docs/guides/validation.rst",
    "docs/guides/validation-evidence.rst",
    "docs/guides/limitations.rst",
    "docs/guides/workflow-boundaries.rst",
    "docs/reference/cli.rst",
)
_MODELWRIGHT_CODE = (
    "src/modelwright/wrappers.py",
    "src/modelwright/notebooks.py",
    "src/modelwright/generation.py",
    "src/modelwright/validation.py",
    "src/modelwright/contracts.py",
)
_MODELWRIGHT_PACKAGE_MODULES = (
    "wrappers.py",
    "notebooks.py",
    "generation.py",
    "validation.py",
    "__init__.py",
)


@dataclass(frozen=True)
class CheatSheet:
    """One compiled grounding document."""

    path: Path
    markdown: str
    generated_at: str
    required_reading: tuple[str, ...]


def modelwright_root(repo_root: Path) -> Path | None:
    """Resolve the local Modelwright checkout used for documentation and source pointers."""

    candidates: list[Path] = []
    configured = os.environ.get("FABLE_PYCULATOR_MODELWRIGHT_ROOT")
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend(
        [
            repo_root.parent / "modelwright",
            Path("/srv/shared-data/gep/jupyterhub14-projects/modelwright"),
        ]
    )
    for candidate in candidates:
        if (candidate / "src" / "modelwright").is_dir() or (candidate / "docs" / "index.rst").is_file():
            return candidate.resolve()
    return None


def _installed_modelwright_code() -> list[Path]:
    """Return installed Modelwright modules when a documentation checkout is unavailable."""

    try:
        import modelwright
    except ModuleNotFoundError:
        return []
    package = Path(modelwright.__file__).resolve().parent
    return [package / name for name in _MODELWRIGHT_PACKAGE_MODULES if (package / name).is_file()]


def ensure_cheat_sheet(
    *,
    repo_root: Path,
    runtime_dir: Path,
    artifacts: list[dict[str, Any]],
    prepared_summaries: dict[str, dict[str, Any]],
    runs: list[dict[str, Any]],
) -> CheatSheet:
    """Build, write, and return the current grounding sheet."""

    generated_at = datetime.now(UTC).isoformat(timespec="seconds")
    markdown, required = build_cheat_sheet(
        repo_root=repo_root,
        artifacts=artifacts,
        prepared_summaries=prepared_summaries,
        runs=runs,
        generated_at=generated_at,
    )
    path = runtime_dir / "assistant" / "cheat-sheet.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(markdown, encoding="utf-8")
    temporary.replace(path)
    return CheatSheet(
        path=path,
        markdown=markdown,
        generated_at=generated_at,
        required_reading=tuple(required),
    )


def build_cheat_sheet(
    *,
    repo_root: Path,
    artifacts: list[dict[str, Any]],
    prepared_summaries: dict[str, dict[str, Any]],
    runs: list[dict[str, Any]],
    generated_at: str,
) -> tuple[str, list[str]]:
    """Return the markdown grounding sheet and the absolute required-reading paths."""

    modelwright = modelwright_root(repo_root)
    fable_docs = _existing_paths(repo_root, _FABLE_DOCS)
    fable_code = _existing_paths(repo_root, _FABLE_CODE)
    fable_issue_templates = _existing_paths(repo_root, _FABLE_ISSUE_TEMPLATES)
    modelwright_docs = _existing_paths(modelwright, _MODELWRIGHT_DOCS) if modelwright else []
    modelwright_code = _existing_paths(modelwright, _MODELWRIGHT_CODE) if modelwright else _installed_modelwright_code()
    required = [
        str(path) for path in fable_docs + fable_code + fable_issue_templates + modelwright_docs + modelwright_code
    ]
    lines: list[str] = [
        "# FABLE Pyculator assistant grounding sheet",
        "",
        "This file is generated by the local FABLE Pyculator portal. Read it before answering the first",
        "question in a new chat session. It is the authoritative index for portal facts, served model",
        "instances, and the documentation/source files you must consult. If a fact is not here, in the",
        "current portal context, or in a file you actually read, say so instead of guessing.",
        "",
        "## Portal metadata",
        "",
        f"- Portal version: `{__version__}`",
        f"- Generated at: `{generated_at}`",
        f"- Repository root: `{repo_root}`",
        (
            f"- Modelwright checkout: `{modelwright}`"
            if modelwright
            else (
                f"- Modelwright package: `{modelwright_code[0].parent}`"
                if modelwright_code
                else "- Modelwright docs/source: not found locally"
            )
        ),
        "- Source workbooks, generated models, and runtime caches are ignored local artifacts.",
        "- The portal is a reader. It does not convert workbooks, generate model code, mutate source files,",
        "  or recompute FABLE results in the browser.",
        "- Scenario runs use the native FABLE horizon (2050) by default. The optional 2070 mode extends",
        "  2055-2070 with a 2035-2050 linear trend and labels those values as non-native projections.",
        "- Results pages show run-scoped data-quality warnings for trend extension, land component",
        "  fallback, missing water data, GHG-vs-cached divergence, and unextended tables.",
        "",
        "## Served model instances",
        "",
        "| Version | Preparable | Prepared in this process | Model source | Controls | Output tables | Headline series |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for artifact in artifacts:
        version = str(artifact.get("version", ""))
        summary = prepared_summaries.get(version, {})
        counts = summary.get("counts", {}) if summary else {}
        headlines = ", ".join(series.get("name", "") for series in summary.get("headline_series", [])) or "—"
        lines.append(
            f"| {version} | {artifact.get('can_prepare')} | {artifact.get('prepared')} | "
            f"{artifact.get('model_source') or 'missing'} | {counts.get('selection_controls', '—')} | "
            f"{counts.get('output_tables', '—')} | {headlines} |"
        )
    lines.extend(
        [
            "",
            "Known version differences:",
            "",
            "- FABLE 2020 and 2021 expose FOOD, LAND, GHG, and WATER default headline series.",
            "- FABLE 2024 (Canada) has no `TotalResultsWF` water-footprint table; default headline curation",
            "  returns FOOD, LAND, and GHG and skips the unsupported WATER series.",
            "- The FABLE 2024 `ResultsLand[TOTAL]` formula contains `#REF!`; the curated land series is",
            "  explicitly labelled as a component sum and reproduces the workbook's valid",
            "  `calc_land_cor[TotallandFin]` total. Its description records the broken source formula.",
            "- The GHG headline is derived from declared OUTPUT-8 components because `TotalCO2e` is a",
            "  CALC cell. Values are generated-model outputs, not workbook-cached totals. The 2024 series",
            "  excludes `LandSeqAffor`, which is not a declared OUTPUT-8 cell in the current artifact.",
            "- The tracked 2021 archive is authoritative. A stale 85 MB local working model previously",
            "  omitted `SCENARIOS definition` row-50 formulas and produced a false 2050 LandSeq/GHG",
            "  discrepancy. The tracked 122 MB archive contains those formulas and matches the cached",
            "  workbook at 2050; if a local working model differs, re-materialize it from the archive",
            "  before preparing.",
            "- 2024 was generated with the Modelwright 0.1.0a9 runtime-hardening line; 2021 is the",
            "  validated public 2021 FABLE-C generated model. Verify claims against the tracked example",
            "  READMEs and local artifacts rather than assuming they are interchangeable.",
            "",
            "## GitHub issue filing",
            "",
            "Use `docs/guides/github-issue-workflow.rst`, `.github/ISSUE_TEMPLATE/task.md`, and",
            "`.github/ISSUE_TEMPLATE/phase.md`. The default for a bug, feature request, documentation",
            "change, or maintenance item is a task issued under the active phase, with the `task` label",
            "plus a type label such as `bug`, `enhancement`, `documentation`, or `question`.",
            "",
            "Before drafting, ask for any missing details: issue type, scope and scale (task, new phase,",
            "or checklist subtask), affected versions/areas, impact and urgency, reproduction and",
            "expected/actual behaviour for bugs, desired outcome for features, in/out-of-scope items,",
            "acceptance criteria, verification evidence, and whether the content is safe to publish.",
            "Inspect `ROADMAP.md` and `gh issue list` for the active parent issue and next task ID. If no",
            "open parent exists, ask whether to create one from `phase.md` or attach to an existing phase.",
            "Never invent issue numbers, task IDs, labels, or repository state.",
            "",
            "Task body sections, in order:",
            "",
            "```text",
            "Task identifier: P<n>.<m>",
            "Parent phase issue: #<parent>",
            "Status: planned",
            "Branch: `feature/p<n>-<slug>`",
            "Related planning: `ROADMAP.md` (Phase <n>)",
            "Goal:",
            "Scope:",
            "Out of scope:",
            "Subtasks:",
            "- [ ] First subtask.",
            "Acceptance criteria:",
            "Verification:",
            "Artifacts:",
            "Risks:",
            "Completion metadata:",
            "```",
            "",
            "Write the body to an ignored file, validate it, show the draft, and get explicit",
            "confirmation before posting:",
            "",
            "```bash",
            "python scripts/check_issue_body.py --kind task \\",
            '  --title "P28.10: Add an example task" --file tmp/issue-example.md',
            "gh issue create --repo UBC-FRESH/fable-pyculator \\",
            '  --title "P28.10: Add an example task" --body-file tmp/issue-example.md \\',
            "  --label task --label enhancement",
            "gh issue view <child> --json number,title,state,body,labels,url",
            "```",
            "",
            "Use `--body-file`, never hand-built escaped strings. Link a task to its parent through the",
            "`sub_issues` API when needed. If `gh` is unavailable or unauthenticated, report the exact",
            "failure and keep a draft manifest under `tmp/`; do not claim the issue was filed. Never",
            "include secrets, private workbook contents, personal home paths, or raw transcripts.",
            "",
            "## Artifact path contract",
            "",
            "```text",
            "tmp/private-workbooks/<version>_Open_FABLECalculator.xlsx",
            "examples/fable_<version>/generated_fable_<version>_model.py.xz",
            "tmp/generated-models/fable-<version>/generated_fable_<version>_model.py",
            "tmp/generated-models/fable-<version>/contract.json",
            "tmp/generated-models/fable-<version>/validation-scenario.json",
            "tmp/validation-evidence/fable-<version>/summary.json",
            "runtime/portal/specs/fable-<version>.json",
            "runtime/portal/runs/<run_id>/run.json",
            "runtime/portal/runs/<run_id>/tables/<table>.json",
            "runtime/portal/chats/<chat_id>.json",
            "runtime/portal/assistant/cheat-sheet.md",
            "```",
            "",
            "## Portal API",
            "",
            "| Method | Path | Meaning |",
            "|---|---|---|",
            "| GET | `/api/health` | Service version and prepared state |",
            "| GET | `/api/agent` | Assistant enablement, availability, model, timeout |",
            "| GET | `/api/artifacts` | Artifact readiness for every configured version |",
            "| GET | `/api/models/{version}/spec` | Compact prepared control/table/headline metadata |",
            "| POST | `/api/models/{version}/prepare` | Prepare a workbook/model pair as a background job |",
            "| GET | `/api/runs` | Saved scenario runs |",
            "| POST | `/api/runs` | Start a scenario run as a background job |",
            "| GET | `/api/runs/{run_id}` | Saved run summary and headline frames |",
            "| GET | `/api/runs/{run_id}/tables/{table}` | One rendered output table |",
            "| POST | `/api/compare` | Compare saved runs by year and selections |",
            "| GET | `/api/validation/{version}` | Compact validation evidence or an unavailable message |",
            "| GET | `/api/chats` | Persistent assistant chat sessions |",
            "| POST | `/api/assistant` | One assistant turn, persisted to a chat |",
            "",
            "## FABLE Pyculator architecture",
            "",
            "- `spec.py` defines the typed `FableCalculatorSpec`, selection controls, output tables,",
            "  scenario-definition tables, and headline series.",
            "- `discovery.py` reads workbook structure and curates default headline series.",
            "- `notebook.py` builds specs, loads generated models, and renders notebook loops.",
            "- `surface.py` runs scenarios through `ModelFacade` and renders tables/headline frames.",
            "- `scenarios.py` and `scenario_workflows.py` handle scenario bundles and FreshForge planning.",
            "- `validation.py` extracts compact validation evidence from local stage artifacts.",
            "- `web/` contains the FastAPI portal, artifact discovery, spec cache, chat store, and assistant bridge.",
            "",
            "## Modelwright architecture",
            "",
            "- Modelwright is the generic workbook-to-Python conversion toolkit. FABLE Pyculator is a",
            "  FABLE-specific notebook and portal layer above it; do not describe FABLE behavior as generic",
            "  Modelwright behavior or vice versa.",
            "- `wrappers.py` exposes `ModelFacade` and generated-model cell/table declarations.",
            "- `notebooks.py` adapts generated models for notebook display.",
            "- `generation.py`, `extraction.py`, `formulas.py`, and `validation.py` own conversion and",
            "  validation mechanics.",
            "- Generated models are accompanied by `contract.json`, `expressions.json`, and `constants.json`.",
            "",
            "## Documentation digest",
            "",
            "This digest is compiled from every documentation file listed under Required reading. It is",
            "intentionally excerpted; open the full file when a question needs exact wording or examples.",
            "",
            _documentation_digest(fable_docs + modelwright_docs),
            "",
            "## Source API index",
            "",
            "This index is generated from the actual modules with Python's AST. Signatures come from the",
            "source, not from memory. Open the cited file for implementation details and docstrings.",
            "",
            _source_api_digest(fable_code + modelwright_code),
            "",
            "## Recent saved runs",
            "",
        ]
    )
    if runs:
        lines.extend(
            [
                "| Run id | Name | Version | Created | Headline values |",
                "|---|---|---|---|---|",
            ]
        )
        for run in runs[:10]:
            headline_values = ", ".join(
                f"{item.get('name')}={item.get('last_value')}" for item in run.get("headline_summary", [])
            )
            lines.append(
                f"| {run.get('run_id')} | {run.get('name')} | {run.get('version')} | "
                f"{run.get('created_at')} | {headline_values or '—'} |"
            )
    else:
        lines.append("No saved runs yet.")
    lines.extend(
        [
            "",
            "## Rules for answering",
            "",
            "- Ground every API name, file path, model behavior, count, output value, and validation claim",
            "  in this sheet, the current portal context, or a file you actually read.",
            "- Do not invent FABLE semantics, Modelwright APIs, headline values, validation counts, or paths.",
            "- Distinguish generated-model outputs from workbook display context and from validation evidence.",
            "- Do not claim you changed a scenario, prepared a model, saved a run, or edited a workbook.",
            "- If asked for a number that is not in the portal context or a saved run, say it is not available",
            "  and explain where it would come from.",
            "- Prefer short, concrete answers. Use markdown for code and links. Cite paths where useful.",
            "",
            "## Required reading",
            "",
            "Read these files before answering a new session's first question. Read the ones relevant to the",
            "question in full; at minimum read the two docs indexes, the web portal guide, the API reference,",
            "and the Modelwright wrapping/validation guides.",
            "",
        ]
    )
    if required:
        lines.extend(f"- `{path}`" for path in required)
    else:
        lines.append("- No local documentation/source files were found. Say so explicitly.")
    lines.append("")
    return "\n".join(lines), required


def _existing_paths(root: Path | None, relative: tuple[str, ...]) -> list[Path]:
    if root is None:
        return []
    return [root / item for item in relative if (root / item).is_file()]


def _documentation_digest(paths: list[Path], *, max_chars_per_file: int = 1400) -> str:
    """Extract a compact excerpt from every documentation file."""

    blocks: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        excerpt = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(excerpt) > max_chars_per_file:
            excerpt = excerpt[:max_chars_per_file].rstrip() + "\n…"
        blocks.append(f"### `{path}`\n\n```text\n{excerpt}\n```")
    return "\n\n".join(blocks) if blocks else "(no documentation files were readable)"


def _source_api_digest(paths: list[Path], *, max_entries_per_file: int = 60) -> str:
    """Extract public classes and functions with signatures from source files."""

    blocks: list[str] = []
    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        entries: list[str] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                entries.append(f"- `{path}:{node.lineno}` `def {node.name}{ast.unparse(node.args)}`")
            elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                bases = f"({', '.join(ast.unparse(base) for base in node.bases)})" if node.bases else ""
                entries.append(f"- `{path}:{node.lineno}` `class {node.name}{bases}`")
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and not child.name.startswith("_"):
                        entries.append(f"  - `{child.name}{ast.unparse(child.args)}` (line {child.lineno})")
            if len(entries) >= max_entries_per_file:
                break
        if entries:
            blocks.append(f"### `{path}`\n\n" + "\n".join(entries))
    return "\n\n".join(blocks) if blocks else "(no source API entries were readable)"
