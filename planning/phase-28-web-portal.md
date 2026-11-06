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

## Out of scope

- authentication or multi-user accounts;
- remote scheduling or multi-tenant storage;
- editing source workbooks from the browser;
- new generated-model equivalence claims;
- loading raw inference/expression/evaluation artifacts for validation display.
