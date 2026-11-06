# Phase 28 Web Portal Contract

Date: 2026-11-06
Branch: `feature/p28-web-portal`

## Purpose

Add a local, multi-page web portal over the artifacts and notebook APIs FABLE Pyculator already
uses. The portal is a presentation and comparison layer, not a second model.

## Reused patterns

- **FHOPS / WS4**: optional `web` extra, FastAPI service, vanilla ES-module SPA, loopback-only
  default, explicit `--allow-remote` guard, reader service over existing computation.
- **Fresh Urban Forest Lab**: multi-page decision-support shell, artifact readiness, KPI cards,
  scenario context, optional local assistant.
- **fresh-fvsbc**: provenance-oriented run records with portal version, source artifact paths, and
  preparation timestamps kept beside every saved output.
- **HectaresBC**: workspace tabs, accessible empty states, progressive detail panels, no build
  toolchain.
- **FABLE Pyculator**: typed spec, selection controls, output-table rendering, headline frames,
  scenario bundles, validation-evidence vocabulary.

## Service boundary

- The browser never computes a FABLE output.
- Preparation materializes the approved compressed model when needed, discovers the workbook spec,
  and loads the matching generated model in a background job.
- Scenario runs call `run_notebook_loop` with the prepared spec and model.
- Saved runs contain only real generated-model values plus declaration/provenance metadata.
- Source workbooks are never mutated.
- The validation page reads compact evidence summaries, not multi-gigabyte stage artifacts.

## Runtime layout

```text
runtime/portal/
  specs/fable-<version>.json        # cached spec + workbook/model fingerprint
  runs/<run_id>/run.json            # metadata, selections, headline frames, table summaries
  runs/<run_id>/tables/<name>.json  # rendered table payloads
  chats/<chat_id>.json              # persistent assistant conversations
  assistant/cheat-sheet.md          # generated grounding sheet
```

`runtime/` is ignored by Git.

## Job contract

Preparation and scenario execution return a job id immediately. `GET /api/jobs/{job_id}` reports
`queued`, `running`, `ok`, or `error` with progress and message. One compute lock serializes heavy
work so two tabs cannot build or run the same huge model concurrently.

## Assistant overlay

The assistant is a global green **+ Ask** pill with a fixed bottom-right overlay, reusing the
Fresh Urban Forest Lab / FHOPS interaction pattern. It is opt-in through `--allow-agent`, calls the
installed `opencode` CLI with `--format json --auto`, keeps an OpenCode session id across turns, and
renders markdown for both user and assistant messages. Untrusted text is escaped and only safe
link schemes are linked. The composer submits on Enter and inserts a newline on Shift+Enter.
Tool-use events become compact action chips.

Chats are persisted as JSON under `runtime/portal/chats/`. The overlay lists saved chats, remembers
the last selected chat in browser storage, and reloads messages from the server after a page reload
or service restart.

## Grounding contract

On the first turn of a new chat, the service regenerates
`runtime/portal/assistant/cheat-sheet.md` and passes its path and required-reading list to the
agent. The prompt requires the agent to read the cheat sheet and the FABLE Pyculator and Modelwright
documentation/source files it lists before answering. The cheat sheet is built from current portal
state: served versions, artifact readiness, prepared spec counts, headline series, saved runs, API
surfaces, key modules, and known version differences. It also includes a digest compiled from every
listed doc and an AST-generated source API index. The agent is told to open the full cited file when
a question needs exact signatures, behaviour, examples, or caveats. The sheet is available to users
at `GET /api/assistant/cheatsheet.md`.

## Out of scope

- authentication or multi-user accounts;
- remote scheduling or multi-tenant storage;
- editing source workbooks from the browser;
- new generated-model equivalence claims;
- loading raw inference/expression/evaluation artifacts for validation display;
- requiring a live model provider or Chromium for the default CI test gate.

## Verification layers

- `tests/web/` covers artifact/spec/service/chat/assistant/markdown contracts without a browser.
- `scripts/evaluate_assistant_grounding.py` runs deterministic structural grounding checks by
  default and real assistant questions only with `--live`.
- `scripts/browser_smoke.py` drives Chromium for the actual overlay, Enter/Shift+Enter, markdown,
  and reload-persistence behavior; the pytest wrapper is gated by
  `FABLE_PYCULATOR_RUN_BROWSER_TESTS=1`.
