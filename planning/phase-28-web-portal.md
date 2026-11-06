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
or service restart. Chats support rename, search, pin, archive, delete, Markdown export, and automatic
titles from the first exchange.

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

## 2070 trend extension

Native FABLE workbooks and generated models end at 2050. The Workbench optionally extends a run to
2070 with a linear trend fitted over 2035-2050 numeric values. Headline series and one-row-per-year
tables are extended. Multi-row-per-year tables are extended group-by-group on text identity columns
(such as `PROD_GROUP`, `Product`, `PRODUCT`, or `CROP`); tables without a usable trend stay native
and receive a "not extended" note.
Every extended run records `horizon: 2070`, `extension.method: linear_trend_2035_2050`, and an
explicit note that 2055-2070 are not native FABLE results. The generated model and source workbook
are never modified by this projection.

## Data quality panel

Results pages include a run-scoped data-quality panel. Warnings are persisted in `run.json` as
`quality_warnings` and cover the 2070 trend extension, the 2024 land component fallback, missing 2024
water data, derived GHG versus cached `TotalCO2e` divergence, and tables that were not extended.

## Deployment

`scripts/run_portal.sh` reads `FABLE_PORTAL_*` environment variables, supports a proxy
`FABLE_PORTAL_ROOT_PATH`, and can require optional HTTP Basic auth. Example systemd and nginx files
live under `deploy/`, with the full recipe in `docs/guides/web-deployment.rst`. The portal remains
loopback-only unless `FABLE_PORTAL_ALLOW_REMOTE=1` is set. Basic auth protects every path except the
health check.

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
