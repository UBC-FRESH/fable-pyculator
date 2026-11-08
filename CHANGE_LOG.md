# CHANGE_LOG.md

This file records completed project work in chronological order.

## 2026-11-07

- Closed Phase 29 after PR #221 squash-merged to `main` as `a6534d9`, post-merge Test workflow
  `42347244877` and Docs Pages workflow `42347245017` passed, and parent #215 plus P29.5 #220 were
  closed. The phase proved that a fresh Modelwright `0.1.0a9` regeneration from the repaired 2024
  workbook reproduces the tracked archive byte-for-byte (`cc8ac21…`), with 410,299 translated
  formulas, 10,274 declared outputs, zero output-closure failures, and zero generation diagnostics.
- Phase 30 added approved-artifact checksum sidecars and verification: the portal now reports
  `verified`/`mismatch`/`unknown`, re-materializes a stale working model from the tracked archive
  before preparation, and offers a re-materialize action on the Artifacts page.
- Prepared the `0.1.0a5` release candidate with the web portal, checksum verification, authenticated
  staging, and issue-filing assistant surface; the release artifact check installed
  `fable-pyculator-0.1.0a5`.
- Verified authenticated staging with `FABLE_PORTAL_ROOT_PATH=/fable`: health remained public, API
  and static routes required Basic auth, the SPA loaded through the proxied prefix, and a 2024 run
  completed with the expected headline values.
- Closed Phase 30 after PR #227 squash-merged as `ee344dd`; post-merge Test workflow
  `42348441589` and Docs Pages workflow `42348441626` passed, and parent #222 plus P30.4 #226 were
  closed. The phase is the `0.1.0a5` release candidate: checksum-verified artifacts, authenticated
  staging, and a documented public-host handoff.
- Published `fable-pyculator 0.1.0a5` with OIDC trusted publishing: TestPyPI rehearsal workflow
  `42348922051` passed, tag `v0.1.0a5` triggered PyPI workflow `42349225029`, and both the TestPyPI
  and PyPI publication jobs succeeded. A clean PyPI install with
  `python -m pip install --pre 'fable-pyculator[web]==0.1.0a5'` imported version `0.1.0a5` and the
  web app entry point.
- Created the GitHub prerelease `v0.1.0a5` with release notes and the workflow-built wheel/sdist:
  https://github.com/UBC-FRESH/fable-pyculator/releases/tag/v0.1.0a5
- Added a FABLE surrogate-assisted GPU optimization pilot: exact one-scenario oracle, parallel
  sample collection, Torch surrogate, CUDA population search, weighted-goal scalarization, and
  exact top-K replay. The 33-sample pilot worked end to end, but exact replay showed 15.5% mean food
  error and 35.0% mean GHG error, with top-five rank correlations of 0.10 and -0.10. Recorded the
  negative result and the requirement for a reduced decision space and larger sample design.
- Closed Phase 32 after PR #237 squash-merged as `cefc895`; post-merge Test and Docs Pages passed.
- Scaled the FABLE optimization pilot in Phase 33: exact one-at-a-time screen, 10-control reduced
  space, 201 exact samples, 5-member ensemble, CUDA GA, and exact top-five replay. Food mean error
  improved to 0.8%, but GHG mean error remained 23.6% with top-five rank correlations of −0.60
  (food) and −0.50 (GHG); the exact best GHG candidate was ranked last by the surrogate. Added a
  draft scenario-consistency rule surface and extensible coefficient/switch architecture under
  `planning/`. Closed Phase 33 after PR #243 merged as `9af5880`; post-merge Test and Docs Pages
  passed. Do not scale this surrogate without a structural change.
- Added and validated a reduced exact evaluator that rewrites only the generated model's
  `_output_refs` tuple to the 176 headline objective cells. It was exact on baseline and three
  samples, but only 1.35× faster (167 s → 123 s); food-only/GHG-only/land-only slices were 127/89/72 s.
  Concluded that output-ref slicing does not materially reduce the shared FABLE dependency cost.
  Closed Phase 34 after PR #248 merged as `d30488a`; post-merge Test and Docs Pages passed.
- Prepared the FABLE scenario-consistency expert review package: 18 proposed rules, a fillable
  decision CSV, priority questions, and concrete example scenarios, plus the extensible
  coefficient/switch architecture. No rule is active until expert review marks it approved.
- Added a status-aware scenario rule engine (`scenario_rules.py` and
  `scripts/evaluate_scenario_rules.py`). Exploratory mode treats proposed rules as warnings: all 201
  samples valid and 725,760 reduced-domain combinations valid, with 535,680 warning-only. Draft
  enforcement leaves 466,560 valid (64.3%) and 259,200 invalid. Counts and rule/spec hashes are in
  `tmp/fable-rules-audit/`.
- Integrated provisional rule filtering into exact sampling and dataset filtering. The existing 201
  samples filtered to 134 valid / 67 rejected / 112 warned. Retraining the ensemble on the filtered
  set improved GHG rank correlation from −0.50 to +0.50 but worsened absolute GHG error to 46.5%;
  the surrogate remains unusable.
- Added `scripts/fable_exact_optimization.py` and ran the exact narrow-domain fallback over
  `land_scen`, `diet_scen`, `fixtrade_scen`, and `livedens_scen`: 126 combinations, 18 rule-rejected,
  108 exact valid scenarios, zero errors, 926.5 s. The exact weighted-goal point is NoDefor2030 /
  FatDiet / fixtrade Yes / NoGrowth at 3,288.73 kcal and 121.23 MtCO2e; enabling trade-fix cuts GHG
  by 50.0% for a 0.36% food loss in the narrow domain. PR #261 merged as `bc3f0f7`; parent #258 and
  children #259-#260 are closed.
- Added `scripts/fable_exact_sensitivity.py` and ran exact one-at-a-time variants around the Phase 37
  point: 20 exact evaluations, 1 rule-rejected, 0 errors, 168.9 s. `live_scen=HighGrowth` is the
  strongest local GHG lever (−9.45% with +0.05% food). The exact three-way candidate
  (`live_scen=HighGrowth`, `crop_scen=HighGrowth`, `affor_scen=BonnChallenge+`) reaches 3,301.11 kcal
  and 108.95 MtCO2e, dominating the Phase 37 point. PR #265 merged as `9acc215`; parent #262 and
  children #263-#264 are closed.
- Ran the exact one-coordinate neighborhood around the Phase 38 candidate: 30 exact evaluations,
  2 rule-rejected, 0 errors, 321.6 s. No strict single-coordinate dominator was found; the candidate
  is a local Pareto point with 11 exact ties. PR #268 merged as `44b9ab5`; parent #266 and child #267
  are closed. Docs build passed; the GitHub Pages deploy job timed out in `finished_file_sync`.
- Added `scripts/fable_exact_decision.py` and eight targeted exact land/diet/trade interaction runs.
  The combined exact frontier has 169 points (160 unique selections) and 15 unique Pareto objective
  triples. Balanced and food-first (GHG ≤ 110) pick the Phase 38 candidate at 3,301.11 kcal /
  108.95 MtCO2e; GHG-first at food ≥ 3,000 picks 3,290.23 kcal / 108.84 MtCO2e.
  PR #272 merged as `5b88e8d`; post-merge Test and Docs Pages passed.
- Added the portal Optimization page and read API. The tracked artifact contains 160 exact points
  and 15 unique Pareto objectives; the Three.js view supports X/Y/Z/colour/size mapping,
  quality-floor and exact-front filters, point inspection, pinning/comparison, and Workbench prefill.
  Browser smoke and release artifact checks passed.
  PR #276 merged as `1beceee`; post-merge Test and Docs Pages passed.
- Polished the Optimization page with hover values, selected-point highlighting, actual axis ranges,
  categorical legends, and a hide-provisional-warning filter (91 of 160 points remain).
  PR #279 merged as `a661259`; post-merge Test and Docs Pages passed.
- Added shareable URL state and filtered CSV export to the Optimization page. X/Y/Z, colour, size,
  floor, filters, and selected point round-trip through the URL; copy-link and CSV export were
  browser-smoked.
  PR #282 merged as `49e3bed`; post-merge Test and Docs Pages passed.
- Added synchronized parallel coordinates to the Optimization page. The 9-axis SVG view uses the same
  filtered exact points, highlights the selected line, and selects the matching 3D point.
  PR #285 merged as `64e1a01`; post-merge Test and Docs Pages passed.
- Added selected-vs-reference comparison to the Optimization page: exact objective and selection
  deltas, a blue reference marker in 3D, a dashed reference line in parallel coordinates, and
  `opt_reference` URL state.
  PR #288 merged as `59866c5`; post-merge Test and Docs Pages passed.
- Added brush-to-filter on the parallel-coordinates axes. Dragging a range filters both the parallel
  and 3D views, displays a brush band, supports clearing, and persists as `opt_brush` URL state.
  PR #291 merged as `9e74875`; post-merge Test and Docs Pages passed.
- Added multi-axis brushing with Shift-drag, AND semantics, removable brush chips, clear-all, and
  `opt_brushes` URL state with legacy `opt_brush` compatibility.
  PR #294 merged as `bcf9f2a`; post-merge Test and Docs Pages passed.
- Added a local saved-view preset library for complete Optimization states: axes, colour, size,
  filters, brushes, reference, and selected point, with save/load/delete.
  PR #297 merged as `bd39a2d`; post-merge Test and Docs Pages passed.
- Added portable preset-library JSON export/import with schema validation, name-based merge, and a
  cap of 20 saved views.
  PR #300 merged as `b4d67d9`; post-merge Test and Docs Pages passed.
- Added Copy preset link with `opt_preset` plus full viewer state, portable to recipients without the
  local preset library; local `opt_preset` links restore by name when state params are absent.
  PR #303 merged as `034478b`; post-merge Test and Docs Pages passed.
- Added a server-backed shared Optimization preset library under `runtime/portal/`, with validated
  list/save/delete APIs and UI controls visible to everyone with portal access.
  PR #306 merged as `9bd4d1f`; post-merge Test and Docs Pages passed.
- Added self-declared author, note, and draft/reviewed metadata to shared Optimization presets, shown
  in the shared selector and persisted by the API.
  PR #309 merged as `17acb88`; post-merge Test and Docs Pages passed.
- Added a shared preset review queue: all/needs-review/reviewed filters, draft/reviewed counts, and a
  mark-reviewed action.
  PR #312 merged as `f516c2f`; post-merge Test and Docs Pages passed.
- Added per-preset shared review history with created/updated/reviewed events, self-declared author,
  timestamp, and a 10-event cap.
  PR #315 merged as `c9a7b16`; post-merge Test and Docs Pages passed.
- Added a read-only shared preset audit table and JSON audit export with metadata and full history.
  PR #318 merged as `94881a5`; post-merge Test and Docs Pages passed.
- Added a cross-preset shared review activity timeline and event-level audit CSV export.
  PR #321 merged as `0050ecb`; post-merge Test and Docs Pages passed.
- Added author/action/preset/date-window filters and Recently reviewed/Reset shortcuts to the shared
  review timeline.
  PR #324 merged as `2af07a9`; post-merge Test and Docs Pages passed.
- Added a per-author shared review workload table with created/updated/reviewed counts, latest
  activity, and click-through to the timeline author filter.
  PR #327 merged as `4975072`; post-merge Test and Docs Pages passed.
- Added local saved timeline filter views for author/action/preset/window combinations.
  PR #330 merged as `eda3171`; post-merge Test and Docs Pages passed.
- Added copyable timeline links plus JSON export/import for saved timeline filter views.
  PR #333 merged as `aebfc7e`; post-merge Test and Docs Pages passed.
- Added a server-backed shared timeline filter library with validated list/save/delete APIs and UI
  controls.
  PR #336 merged as `502a4f2`; post-merge Test and Docs Pages passed.
- Added self-declared author, note, and draft/reviewed metadata to shared timeline views.
  PR #339 merged as `04fd12b`; post-merge Test and Docs Pages passed.
- Added a previewable shared-history retention policy that prunes old events while preserving each
  preset's latest event.
  PR #342 merged as `89abc93`; post-merge Test and Docs Pages passed.
- Added opt-in startup retention via CLI/config, a JSONL retention audit log, and a policy/last-run
  read endpoint and UI hint.
  PR #345 merged as `b0d70ba`; post-merge Test and Docs Pages passed.
- Added opt-in interval-scheduled retention with a daemon loop and interval/next-run status.
  PR #348 merged as `b7ddf9b`; post-merge Test and Docs Pages passed.
- Added a retention maintenance dashboard with newest-first run history from the JSONL log.
  PR #351 merged as `edcd312`; post-merge Test and Docs Pages passed.
- Added CSV export for the recent retention maintenance runs.
  PR #354 merged as `9a20f5a`; post-merge Test and Docs Pages passed.
- Added bounded per-preset removed-event details to retention runs and a dashboard detail panel.
  PR #357 merged as `d5d26e3`; post-merge Test and Docs Pages passed.
- Added exact before/after history vectors to retention run details and rendered the diff in the
  dashboard.
  PR #360 merged as `d10b289`; post-merge Test and Docs Pages passed.
- Added a confirm-before-prune flow: first click previews and arms, second click commits.
  PR #363 merged as `32423b3`; post-merge Test and Docs Pages passed.
- Added CSV export of the selected retention run's per-preset before/after/removed vectors.
  PR #366 merged as `a31f5f3`; post-merge Test and Docs Pages passed.
- Added per-value custom-table row resolution (`key_switch`) and pointed `CUSTOM-EXPORT-001` at the
  selected `scen_exports` value, with fail-closed regression coverage.
  PR #369 merged as `15b8516`; post-merge Test and Docs Pages passed.
- Added a shared-library JSON backup and previewed merge/replace restore for preset histories and
  timeline views, with over-cap, duplicate, and invalid-entry rejection.
  PR #373 merged as `d67e064`; post-merge Test and Docs Pages passed.
- Added bounded manual/scheduled shared-library snapshots with inventory, download, and previewed
  restore.
- Added `scripts/check_deployed_portal.py` and Cloudflare Access deployment documentation, then
  merged them in PR #232 (`bd7cd0c`). The checker detects the live
  `fable-pyculator.01101.dev` Access redirect; the version check and `0.1.0a5` upgrade remain
  blocked on an Access service token or approved health bypass plus host update access.

## 2026-11-06

- Activated Phase 28 on `feature/p28-web-portal` and implemented the optional multi-page FABLE
  Pyculator portal: FastAPI service, dependency-free vanilla ES-module SPA, artifact readiness,
  compressed-model materialization, cached workbook-spec preparation, background scenario runs,
  headline KPI cards and charts, output-table rendering and CSV export, saved-run comparison,
  compact validation-evidence browsing, scenario-bundle browsing, provenance-bearing saved runs,
  and an opt-in local assistant.
- Added `fable-pyculator web` through `src/fable_pyculator/cli.py`, the `web` optional dependency
  extra, static package data, and ignored `runtime/portal/` spec/run caches.
- Added `tests/web/test_portal.py`, `tests/web/test_assistant.py`, and `tests/web/test_markdown.py` for
  spec round-tripping, artifacts and materialization, preparation jobs, scenario execution, saved
  tables, comparison, validation lookup, assistant enablement and session passthrough, opencode event
  parsing, markdown rendering safety, and the loopback bind guard.
- Added the global **+ Ask** pill and fixed overlay assistant: markdown rendering for both user and
  assistant messages, safe links/code/tables, session continuation, tool-action chips, run context,
  Enter-to-send, Shift+Enter newline, and `a`/Escape shortcuts.
- Added persistent assistant chats under `runtime/portal/chats/`: the overlay lists saved chats,
  remembers the last selected chat in browser storage, restores messages after reload, and continues
  the same OpenCode session across service restarts.
- Added a generated grounding sheet at `runtime/portal/assistant/cheat-sheet.md`: served model
  instances, artifact readiness/paths, prepared spec counts, headline series, saved runs, API
  surface, known version differences, a digest compiled from every listed FABLE/Modelwright doc, and
  an AST-generated source API index. New chats must read it and open full cited files for exact
  details. It is served at `GET /api/assistant/cheatsheet.md`.
- Documented the portal in `docs/guides/web-portal.rst`, README, API reference, and
  `planning/phase-28-web-portal.md`.
- Fixed a real portal preparation failure on FABLE 2024: the Canada workbook has no
  `TotalResultsWF` water-footprint table, so `curate_default_headline_series` now skips unsupported
  default series and returns FOOD, LAND, and GHG for 2024. `strict=True` preserves the older
  fail-fast behavior, and `build_notebook_spec` exposes `strict_headlines`.
- Added synthetic and workbook-gated tests for version-tolerant headline curation, and verified real
  preparation plus scenario execution for both FABLE 2024 and FABLE 2020 through the portal:
  2024 prepared in 47.7 s and ran in 108.5 s with 24 controls, 17 output tables, and 3 headlines;
  2020 prepared in 137.0 s and ran in 167.2 s with 16 controls, 14 output tables, and 4 headlines.
- Verified the assistant end to end against the live local service: the first grounded turn read
  `notebook.py` and answered the exact `build_notebook_spec` signature in 25.5 s; after a service
  restart the saved chat listed, reloaded, and continued the same OpenCode session in 10.4 s.
- Added a grounding evaluation suite: deterministic structural checks plus opt-in live assistant
  questions that require citations to expected source paths and expected terms. The live suite
  covers `notebook_signature`, `modelwright_facade`, `fable_2024_water`, `portal_read_only`, and
  `github_issue_filing`; the new issue-filing case passed in 28.0 s against the real OpenCode CLI.
- Added the UBC-FRESH phase/task issue templates, a GitHub issue workflow guide, and
  `scripts/check_issue_body.py`. The portal assistant now classifies issue requests by type and
  scale, asks for missing reproduction/scope/acceptance details, drafts the canonical body, validates
  it, confirms with the user, posts with `gh issue create --body-file`, links child tasks to the
  parent, and reads the issue back; the grounding checks include a dedicated issue-filing case.
- Added a Playwright browser smoke (`scripts/browser_smoke.py` and a gated pytest wrapper) covering
  the + Ask overlay, Enter/Shift+Enter behavior, markdown rendering, and live assistant chat
  persistence across a full page reload; it passed locally.
- Added the `browser` optional extra, the grounding-eval guide, and README verification commands.
- Fixed the visible FABLE 2024 `land_total_area = #REF!` KPI. The 2024 workbook itself contains
  `SUMIFS(#REF!, …)` in `ResultsLand[TOTAL]`, and Excel caches that column as `#REF!`. The intended
  correction term is recoverable from the workbook's valid `calc_land_cor[TotallandFin]`:
  `CalcLoggedForest` is the missing subtraction. Curation now detects the broken total and uses a
  clearly labelled *Total land area (component sum)* fallback over `Cropland`, `Pasture`, `Urban`,
  `ForPlantations`, `OtherForest`, and `OtherLand`, reproducing `TotallandFin` exactly and recording
  the broken source formula in the series description. The portal spec-cache version was bumped so
  stale specs rebuild automatically. A real 2024 run now reports `896,559.0` instead of `#REF!`.
- Added `scripts/repair_fable_2024_land_total.py` and repaired the local 2024 workbook itself:
  the script replaces `SUMIFS(#REF!, …)` with `SUMIFS(calc_land_cor[CalcLoggedForest], …)` in
  `LAND!AA17:AA27` and restores the cached totals from `calc_land_cor[TotallandFin]` by editing the
  xlsx XML directly, with a `.xlsx.bak` backup. Both the working and pristine 2024 reference copies
  contained the same broken formula.
- Added `scripts/repair_fable_2024_generated_model.py` and repaired the tracked 2024 generated-model
  expressions for `LAND!AA17:AA27`. A full old-vs-repaired execution comparison across all 10,274
  declared outputs showed only those 11 cells changed (`#REF!` to `896,559.0`), with no other
  generated value affected. The repaired tracked archive checksum is
  `f62c74b246fa29068b54b2c8ad82ed34b35026e490f2e2d205148c18277ae469`, and a fresh portal run showed
  the LAND table TOTAL values coming directly from the model with no display repair note.
- Curated the GHG headline from declared `OUTPUT-8` components instead of the `TotalCO2e` `CALC`
  cell, so 2020/2021/2024 results pages now have a numeric GHG series. The 2024 series explicitly
  notes that `LandSeqAffor` is excluded because it is not a declared `OUTPUT-8` cell in that
  artifact.
- Validated the derived GHG series against cached workbook `TotalCO2e`: 2020 matched to ~1e-12 at
  every year; 2024 late-year differences remain because individual generated-model components and
  GWP assumptions differ from the cached workbook. The headline intentionally reports
  generated-model outputs, not cached workbook values, and says so in its description.
- Investigated a live 2021 `LandSeq`/GHG discrepancy at 2050. The apparent generated-model defect was
  a stale 85 MB local working model that omitted six `SCENARIOS definition` row-50 formulas
  (`EQ50`-`EV50`). The tracked 122 MB 2021 archive already contains those formulas and, when
  re-materialized, matches the cached 2050 outputs (`GHG!AI28 -302.1950203334845`,
  `LAND!V27 25000.0`, `LAND!X27 81407.07618113697`). The local working model was replaced from the
  archive; no tracked-artifact repair was needed. The live 2021 smoke is now
  `430.13 → 107.63 MtCO2e` with no GHG data-quality warning.
- Live 2024 horizon-2070 smoke: headline series extended to 2070 (`food 1,611.3`, `GHG 110.14`,
  `land 896,559.0`); `land_resultsland` had 15 rows; grouped `food_results_diets` extended from
  187 to 255 rows; grouped `trade_resultstrade` extended from 990 to 1,350 rows.
- Kept a transparent display repair for older/stale 2024 working models: if a `land_resultsland`
  TOTAL column still contains `#REF!`, the portal replaces only that displayed column with the same
  `TotallandFin` component sum and shows a warning note; generated-model semantics are unchanged.
- Wired the deterministic assistant grounding check into the Test workflow so cheat-sheet/source
  drift fails CI, while live agent and Chromium checks remain opt-in.
- Added an optional **2070 trend extension** to the Workbench. Native FABLE results remain
  2000-2050; when selected, headline series and one-row-per-year tables are extended to 2055-2070
  with a linear trend fitted over 2035-2050. Multi-row-per-year tables are extended group-by-group
  on text identity columns when possible; tables without a usable trend stay native with an explicit
  note. Every extended run records the method and a warning that 2055-2070 are not native FABLE
  results.
- Added run-scoped **data-quality notes** to Results: 2070 extension, 2024 land component fallback,
  missing 2024 water series, derived GHG versus cached `TotalCO2e` divergence, and tables that were
  not extended. Notes are persisted in `run.json` as `quality_warnings`.
- Finished chat management: rename, search, pin, archive, delete, Markdown export, and automatic
  titles from the first exchange. Added `PATCH /api/chats/{chat_id}` and
  `GET /api/chats/{chat_id}/export.md`; live smoke verified auto-title, pin/archive filtering, and
  Markdown export.
- Re-ran `scripts/check_release_artifacts.sh`; it passed and the wheel contains chats, cheat-sheet,
  grounding evals, and all portal static assets.
- Added deployment support: optional built-in HTTP Basic auth, `scripts/run_portal.sh`, proxy
  `FABLE_PORTAL_ROOT_PATH`, example systemd unit, environment template, nginx config, and
  `docs/guides/web-deployment.rst`. Live test confirmed unauthenticated health checks remain public
  while the SPA/API require auth under a proxy prefix.
- Verified the implementation with Ruff, targeted Ruff format checks, JavaScript syntax checking, the
  full test suite (`193` passed and `15` skipped), the gated Chromium smoke (`1` passed), workbook
  headline tests (`2` passed), a warning-clean Sphinx build, Read the Docs theme verification, the
  release artifact check, and real restored-artifact 2021/2024/2020 preparation and runs.
- Closed Phase 28: mapped parent issue #203 and child issues #204-#213, squash-merged PR #214 as
  `a6758db`, confirmed post-merge Test workflow `42308703202` and Docs Pages workflow `42308703198`,
  and closed the completed child issues with closeout comments. Final CI on the PR head passed
  quality, pytest, release-artifacts, and the Docs Pages build with the web extra installed.
- Activated Phase 29 (parent #215, children #216-#220) to regenerate the 2024 model from the repaired
  workbook. Added `scripts/regenerate_fable_2024_model.py` and bumped the dependency floor to
  `modelwright[notebook]>=0.1.0a9`. A fresh conversion translated 410,299 of 410,299 formulas,
  closed all 10,274 declared outputs with 0 failures and 0 generation diagnostics, and produced
  SHA-256 `cc8ac21ab55293f648aa9f6b3b8782b1f2dbe1b7789fda43bb1d100c1d8221ee`, exactly matching
  the decompressed tracked archive. No artifact replacement was needed; `LAND!AA17:AA27` are native
  generated formulas. The earlier blocked repro used the stale `0.1.0a8` environment.

## 2026-08-15

- Added the tracked `examples/fable_2024/` generated-model artifact (compressed
  `generated_fable_2024_model.py.xz`, about 1.7 MiB) for the 2024 FABLE Calculator (Canada)
  workbook, generated with Modelwright `0.1.0a9`. The README records provenance and validation
  evidence: 536,593 extracted cells, 410,299 formula cells, 10,274 declared outputs with zero
  runtime errors, and a 94% exact-match rate on a 300-output cached-value sample with remaining
  mismatches at 0.05-0.3% relative.
- Restored the 2024 source workbook under `tmp/private-workbooks/` and added its checksum to
  `benchmarks/fable-calculator/checksums.sha256`; added a generated-model archive readability test
  in `tests/test_examples.py`.
- Fixed two repo-wide CI gates uncovered by the example PR: pinned `ruff>=0.8,<0.16` in the quality
  and dev extras (CI's newer ruff 0.16 rule set fails the repo's existing import sorting), and added
  the 2024 archive to the approved generated-model archive allowlist in
  `scripts/check_release_artifacts.sh`.

## 2026-07-03

- Activated Phase 27 on `feature/p27-alpha-tester-notebook-hardening`, created parent issue #194
  and child issues #195 through #199, and scoped the phase around alpha-tester notebook reliability,
  an opt-in 2021 notebook-loop smoke check, skipped output-table diagnostics, and notebook-failure
  issue hygiene.
- Added `scripts/smoke_2021_notebook_loop.py`, default skipped-output-table diagnostics on
  `NotebookLoopResult`, a notebook-run failure issue template, and docs guidance clarifying that
  workbook-cached context values and screenshots are display/debugging aids rather than generated
  equivalence evidence.
- Verified Phase 27 locally with Ruff, full pytest (`147` passed and `12` skipped), warning-clean
  Sphinx docs, Read the Docs theme verification, public workbook checksums, release artifact checks,
  `git diff --check`, and a restored-artifact 2021 smoke run that passed in about 213 seconds.
- Merged Phase 27 through PR #201 and confirmed post-merge Test workflow #28631757605 plus Docs
  Pages workflow #28631757588 passed.
- Fixed the 2021 loop notebook crash where rendering all default output tables with an `OUTPUT-*`
  flavour filter raised on tables without matching output columns; default all-table rendering now
  skips non-matching tables while explicit table requests still fail clearly.
- Added an explicit 2021 loop notebook context-column proof cell for Abdulateef's output-table
  rendering bug, showing `trade_resultstrade` and checking `PRODUCT`/`YEAR` values when restored
  local 2021 artifacts are available.
- Fixed Abdulateef's reported output-table rendering bug where context/support columns such as
  `Product` and `Year` could display as missing when a generated model was built from narrow
  `OUTPUT-*` refs; discovered output tables now retain cached workbook values for display-only
  non-output columns while generated `OUTPUT-*` values remain the validation boundary.
- Published a GitHub-only Phase 26 checkpoint release,
  `checkpoint-p26-scenario-definition-surface`, to mark the editable scenario-definition patch
  milestone without publishing a new PyPI package or changing the installed alpha version.
- Added the Abulateef-facing Phase 26 hands-on notebook
  `examples/notebooks/fable-pyculator-2021-scenario-definition-patch.ipynb`, linking the editable
  scenario-definition patch example into the docs and README as a concrete alpha-tester artifact.

## 2026-07-02

- Activated Phase 26 on `feature/p26-editable-scenario-definition-surface`, created child issues
  #180 through #184 under parent issue #172, and scoped the phase around a conservative
  scenario-definition editing surface that produces generated-model input overrides without mutating
  source workbooks.
- Added `fable_pyculator.scenario_definitions`, optional scenario-definition patch integration for
  `run_scenario` and notebook-loop helpers, `scripts/validate_fable_scenario_definition_patch.py`,
  a public-safe patch schema example, and Sphinx documentation for validating non-formula `DIRECT`
  scenario-definition cell edits as generated-model input overrides.
- Verified the Phase 26 implementation with Ruff, full pytest (`140` passed and `11` skipped
  workbook tests), warning-clean Sphinx docs, Read the Docs theme verification, public workbook
  checksums, release artifact checks, `git diff --check`, and workbook-backed scenario-definition
  tests (`5` passed), plus a real validation-script smoke test for the tracked 2021 example patch.
- Merged Phase 26 through PR #185 and confirmed post-merge Test workflow #28629339255 passed plus
  Docs Pages workflow #28629339241 passed after rerunning a transient GitHub Pages deploy failure.
- Activated Phase 25 on `feature/p25-fable-benchmark-matrix-evidence-cookbook`, created child
  issues #174 through #178 under parent issue #171, and scoped the phase around packaging FABLE
  2021 benchmark matrix evidence through Modelwright's generic matrix evidence aggregation while
  keeping matrix execution explicit and equivalence claims evidence-bound.
- Added FABLE-facing benchmark matrix evidence path, summary, packaging, and writer helpers plus
  `scripts/package_fable_matrix_evidence.py`, delegating generic matrix aggregation to Modelwright
  Phase 38 and failing clearly when that backend is unavailable.
- Added the FABLE 2021 benchmark matrix evidence cookbook and linked it from README, benchmark
  evidence, output-ref strategy comparison, generated-model artifact, and validation-scope docs.
- Verified the Phase 25 implementation with Ruff, full pytest (`130` passed and `9` skipped
  workbook tests), warning-clean Sphinx docs, Read the Docs theme verification, public workbook
  checksums, release artifact checks, and `git diff --check`.
- Merged Phase 25 through PR #179 and confirmed post-merge Test workflow #28627076860 passed plus
  Docs Pages workflow #28627076848 passed after rerunning a transient GitHub Pages deploy failure.
- Added planned Phase 25 and Phase 26 parent issues to extend the FreshForge workflow lane: Phase 25
  will consume Modelwright matrix evidence aggregation for a 2021 benchmark matrix cookbook, and
  Phase 26 will tackle editable scenario-definition parameter surfaces.
- Updated the optional FreshForge integration dependency now that FreshForge is published on PyPI:
  `fable-pyculator[freshforge]`, `dev`, and `test` install `freshforge>=0.1.0a5,<0.2` while the core
  FABLE Pyculator package remains FreshForge-free.
- Activated Phase 21 on `feature/p21-v0.1.0a3-release`, created parent issue #143 and child
  issues #144 through #147, and scoped the release around publishing the benchmark workflow
  automation alpha after FreshForge `v0.1.0a3` and Modelwright `v0.1.0a8`.
- Started the `v0.1.0a3` release candidate by bumping package/import/provider versions, raising the
  Modelwright dependency floor to `modelwright[notebook]>=0.1.0a8`, updating FreshForge guidance to
  `v0.1.0a3`, and refreshing README, release docs, tests, and release-artifact checks for the
  output-ref strategy comparison, FreshForge-backed scenario-bundle, and opt-in benchmark evidence
  automation milestone.
- Verified the `v0.1.0a3` release candidate with Ruff, full pytest (`108` passed and `9` skipped
  workbook tests), warning-clean Sphinx docs, Read the Docs theme verification, public workbook
  checksums, release artifact checks with a clean wheel install against published Modelwright
  `0.1.0a8`, `git diff --check`, and a benchmark evidence script smoke test selecting the
  Modelwright evidence backend.
- Released `fable-pyculator==0.1.0a3` after PR #148 merged to `main`, post-merge Test workflow
  #28559940344 passed, post-merge Docs Pages workflow #28559940366 passed, annotated tag
  `v0.1.0a3` triggered Release workflow #28559980122, and trusted publishing uploaded the wheel and
  sdist to PyPI.
- Created the GitHub prerelease for `v0.1.0a3` with the workflow-built artifacts, verified PyPI
  listed both package artifacts, and smoke-tested a clean PyPI install of
  `fable-pyculator[notebook]==0.1.0a3` importing `fable_pyculator 0.1.0a3` with
  `modelwright 0.1.0a8`.

## 2026-07-01

- Activated Phase 20 on `feature/p20-opt-in-benchmark-workflow-upgrade`, created child issues #137
  through #141 under parent issue #124, and scoped the phase around opt-in benchmark evidence
  orchestration without PR-triggered benchmark runs, workbook downloads, raw artifact uploads, or new
  unsupported equivalence claims.
- Added `fable_pyculator.benchmarks` and `scripts/run_fable_benchmark_evidence.py` so users can
  package compact evidence, prepare a FreshForge benchmark plan, or explicitly run a restored local
  benchmark workflow while recording whether the evidence backend was generic Modelwright or the
  FABLE-local fallback.
- Upgraded the manual `Benchmark Evidence` GitHub Actions workflow with safe `workflow_dispatch`
  inputs for benchmark mode, output-ref strategy, scenario-bundle summary ingestion, run namespace,
  and required artifacts while keeping uploads restricted to compact sanitized summaries.
- Added Sphinx documentation and tests for the opt-in benchmark evidence workflow, including
  conservative missing-artifact behavior, backend fallback, no raw-artifact uploads, and no
  equivalence claims without explicit comparison counts.
- Merged Phase 20 through PR #142 and confirmed post-merge Test workflow run #28558959744 plus Docs
  Pages workflow run #28558959735 passed, including GitHub Pages deployment.
- Activated Phase 19 on `feature/p19-freshforge-scenario-bundle-orchestration`, created child
  issues #131, #132, #133, #134, and #135 under parent issue #123, and scoped the phase around
  FreshForge-backed scenario-bundle orchestration while preserving the direct bundle runner.
- Added FreshForge-backed scenario-bundle workflow helpers, executable FABLE Pyculator provider
  nodes, explicit scenario-bundle script plan/run modes, a public-safe 2021 SSP demo workflow
  example, and Sphinx documentation for namespace-isolated scenario-bundle orchestration.
- Verified the Phase 19 implementation with Ruff, full pytest (`96` passed and `9` skipped workbook
  tests), Sphinx warning-as-error docs, Read the Docs theme verification, workbook checksums, release
  artifact checks against published `modelwright 0.1.0a7`, `git diff --check`, FreshForge
  validate/plan checks for the public-safe scenario-bundle workflow, and a real local 2021
  `--freshforge-plan` smoke run.
- Merged Phase 19 through PR #136 and confirmed post-merge Test workflow run #28558440319 plus Docs
  Pages workflow run #28558440328 passed, including GitHub Pages deployment.
- Activated Phase 18 on `feature/p18-output-ref-strategy-comparison-workflows`, created child
  issues #127, #126, #128, #125, and #129 under parent issue #122, and scoped the phase around
  comparing FABLE output-ref strategy boundaries without making new generated-model equivalence
  claims.
- Added `fable_pyculator.strategy_comparison`, public package exports, and
  `scripts/compare_fable_output_ref_strategies.py` so users can compare default FABLE output-ref
  boundaries, cached comparable-output counts, intended FreshForge namespaces, optional workflow
  artifacts, and optional existing validation evidence summaries before choosing a build target.
- Documented output-ref strategy comparison in Sphinx and linked it from README, generated-model
  artifacts, FreshForge provider, rebuild-command, validation-evidence packaging, and API reference
  pages.
- Verified the Phase 18 implementation with Ruff, full pytest (`90` passed and `9` skipped workbook
  tests), Sphinx warning-as-error docs, Read the Docs theme verification, workbook checksums, release
  artifact checks against published `modelwright 0.1.0a7`, `git diff --check`, and a real local 2021
  strategy-comparison smoke run for `output-columns` and `headline-only`.
- Merged Phase 18 through PR #130, confirmed post-merge Test workflow run #28557443902 and Docs
  Pages workflow run #28557443878 passed, smoke-checked the live output-ref strategy comparison docs,
  and closed the Phase 18 issue set.
- Activated Phase 17 on `feature/p17-v0.1.0a2-release`, created parent issue #116 and child issues
  #120, #118, #119, and #117, and scoped the phase around publishing the FABLE workflow automation
  alpha after the FreshForge `v0.1.0a2` and Modelwright `v0.1.0a7` dependency releases.
- Started the `v0.1.0a2` release candidate by bumping package/import/provider versions, raising the
  Modelwright dependency floor to `modelwright[notebook]>=0.1.0a7`, and updating release docs,
  README alpha language, FreshForge installation guidance, tests, and release-artifact checks.
- Verified the `v0.1.0a2` release candidate with Ruff, pytest, Sphinx warning-as-error docs, Read
  the Docs theme verification, public workbook checksums, release artifact checks with a clean wheel
  install, validation-evidence packaging smoke test, and import/API smoke tests confirming the
  FABLE Pyculator and Modelwright release-train versions.
- Published `fable-pyculator==0.1.0a2` to PyPI from tag `v0.1.0a2`, verified the PyPI wheel and
  sdist records, smoke-tested a clean PyPI install that imported `fable_pyculator 0.1.0a2` with
  `modelwright 0.1.0a7`, created the GitHub prerelease, and recorded post-merge Test plus Docs Pages
  workflow success for PR #121.
- Created planned backlog parent issues #122, #123, and #124 for post-alpha output-ref strategy
  comparison workflows, FreshForge-backed scenario-bundle orchestration, and opt-in benchmark
  workflow upgrades; updated the roadmap and deployment-target planning note to align these phases
  with FreshForge Phase 7/8 and Modelwright Phase 35/36 dependencies while deferring child issues
  until each phase is activated.
- Activated Phase 16 on `feature/p16-validation-evidence-packaging`, created child issues #112,
  #110, #111, #113, and #114 under parent issue #79, and scoped the phase around compact validation
  evidence summaries from restored local artifacts plus an extraction-only opt-in benchmark workflow.
- Added `fable_pyculator.validation` with compact validation-evidence path helpers, sanitized
  summary extraction, conservative pass/fail/incomplete equivalence classification, and stable JSON
  plus Markdown writers that avoid copying raw workbook, generated source, and generated-value
  payloads.
- Added `scripts/package_fable_validation_evidence.py` and a manual-only
  `.github/workflows/benchmark-evidence.yml` workflow so restored local generated-model artifacts can
  be summarized and uploaded as compact sanitized evidence without running full model generation by
  default.
- Added Sphinx documentation for validation-evidence packaging and linked it from README,
  validation-scope, generated-model artifact, docs index, and API reference pages.
- Verified the Phase 16 local implementation with Ruff, pytest, Sphinx warning-as-error docs, Read
  the Docs theme verification, workbook checksums, release artifact checks, whitespace checks, and a
  real local 2021 evidence-packaging smoke test that correctly reported incomplete equivalence when
  explicit comparison counts were unavailable.
- Merged Phase 16 through PR #115 and confirmed post-merge Test workflow run #28539084681 plus Docs
  Pages workflow run #28539084645 passed, including GitHub Pages deployment.
- Activated Phase 15 on `feature/p15-scenario-bundles-result-artifacts`, created child issues
  #104, #106, #105, #107, and #108 under parent issue #78, and scoped the phase around
  selection-control scenario bundles plus rendered result artifacts under ignored `tmp/`.
- Added `fable_pyculator.scenarios` with JSON/YAML scenario-bundle loading, selection-control
  validation, bundle execution through the existing notebook loop, and deterministic rendered
  artifact writers for normalized bundle metadata, manifests, CSV frames, and optional headline
  figures.
- Added `scripts/run_fable_scenario_bundle.py`, public-safe JSON/YAML example bundles, and Sphinx
  documentation for running named scenario bundles against existing generated models without
  expanding generated-model equivalence claims.
- Verified the Phase 15 slice with Ruff, pytest, Sphinx warning-as-error docs, Read the Docs theme
  verification, workbook checksums, release artifact checks, whitespace checks, and a real 2021
  scenario-bundle dry-run smoke test against the restored local workbook.
- Merged Phase 15 through PR #109 and confirmed post-merge Test workflow run #28537043841 plus Docs
  Pages workflow run #28537043793 passed, including GitHub Pages deployment.
- Activated Phase 14 on `feature/p14-version-general-fable-build-workflows`, created child issues
  #99, #101, #100, #102, and #98 under parent issue #77, and scoped the phase around
  version-general FABLE build workflows plus output-ref strategy comparison.
- Added version-general FreshForge build helpers, including `fable_freshforge_build_paths`,
  `prepare_freshforge_rebuild`, and named output-ref strategies for output columns, headline-only
  slices, named tables, explicit flavour tags, and all columns, while preserving the 2021
  compatibility wrappers.
- Added `scripts/build_fable_model.py` as the version-general plan-first rebuild command and kept
  `scripts/build_fable_2021_model.py` as a 2021 shortcut.
- Updated README and Sphinx docs to describe version conventions, strategy choices, and 2021
  examples without expanding generated-model equivalence claims.
- Verified Phase 14 locally with Ruff, pytest, Sphinx warning-as-error docs, Read the Docs theme
  verification, workbook checksums, release artifact checks, whitespace checks, and real 2021
  plan-mode smoke tests for default output columns, headline-only refs, and the `ghg_resultsghg`
  table strategy.
- Merged Phase 14 through PR #103 and confirmed post-merge Test workflow run #28535828270 plus Docs
  Pages workflow run #28535828354 passed, including GitHub Pages deployment.
- Activated Phase 13 on `feature/p13-one-command-2021-freshforge-rebuild`, created child issues #91
  through #94 under parent issue #76, and scoped the tranche around a plan-first one-command 2021
  FreshForge/Modelwright rebuild path.
- Added `prepare_2021_freshforge_rebuild` and `FableFreshForgeRebuildPlan` to consolidate the
  notebook-local 2021 output-ref derivation, cached-workbook validation scenario writing, and
  Modelwright FreshForge workflow construction into tested package APIs.
- Added executable script `scripts/build_fable_2021_model.py`, which defaults to plan-only artifact
  preparation under `tmp/generated-models/fable-2021/`, prints a concise summary, supports
  output-table/tag filtering options, and requires `--run` before invoking FreshForge execution.
- Switched cached-workbook validation-scenario preparation to indexed workbook access after the real
  2021 smoke test exposed pathological random access through `openpyxl` read-only worksheets.
- Added focused tests for the package rebuild preparation helper and script help, missing-workbook,
  and plan-mode behavior.
- Added Sphinx documentation for the 2021 FreshForge rebuild command and linked it from the generated
  model artifact guide and README.
- Verified the Phase 13 slice with the real 2021 plan-only command, which wrote 16,478 `OUTPUT-*`
  refs and 16,478 comparable cached outputs under ignored `tmp/generated-models/fable-2021/`, plus
  Ruff, pytest, Sphinx warning-as-error docs, Read the Docs theme verification, workbook checksum
  verification, release-artifact checks, and `git diff --check`.
- Addressed issue #96 by adding narrow suppression for known-benign `openpyxl` warnings about
  unsupported WMF images and data-validation extension metadata during FABLE workbook loads. These
  workbook features are not part of FABLE Pyculator's scenario, output, notebook, or rebuild
  surfaces.

## 2026-06-25

- Added FreshForge orchestration roadmap placeholders: Phase 9 for a future plan-only FABLE Pyculator
  provider and Phase 10 for a future cross-package FABLE Pyculator plus Modelwright workflow example,
  with GitHub parent issues #61 and #62 and planning notes under `planning/`.
- Activated Phase 10 on `feature/p10-2021-freshforge-build-notebook`, created child issues #64
  through #66, and added an Abdulateef-facing
  `examples/notebooks/fable-pyculator-2021-freshforge-build-plan.ipynb` template that uses FABLE
  Pyculator to derive 2021 output refs, FreshForge to plan the Modelwright workflow graph, and gated
  Modelwright commands to infer, generate, and execute the 2021 model from ignored local artifacts.
- Verified the Phase 10 notebook slice with targeted example tests, Ruff, full pytest, Sphinx
  warning-as-error docs, Read the Docs theme verification, workbook checksum verification, release
  artifact checks, and `git diff --check`.
- Merged Phase 10 PR #67, verified post-merge Test and Docs Pages workflows, confirmed GitHub Pages
  deployment, and closed the Phase 10 issue set.
- Activated Phase 11 on `feature/p11-freshforge-2021-run-notebook`, created parent issue #69 and
  child issues #70 through #73, and scoped the phase around an Abdulateef-facing companion notebook
  that runs the 2021 Modelwright build through FreshForge's serial local runner.
- Added `examples/notebooks/fable-pyculator-2021-freshforge-run.ipynb`, which derives 2021
  `OUTPUT-*` output refs, prepares cached-workbook validation, writes a Modelwright FreshForge
  workflow, validates/plans it, gates `run_workflow(...)` behind `RUN_FRESHFORGE = False`, and loads
  the newly generated 2021 model for FABLE Pyculator output inspection when present.
- Verified Phase 11 locally with targeted example tests, Ruff, full pytest, Sphinx warning-as-error
  docs, Read the Docs theme verification, workbook checksum verification, release-artifact checks,
  and `git diff --check`.
- Merged Phase 11 PR #74, verified PR checks and post-merge Docs Pages deployment, and closed the
  Phase 11 issue set.
- Added `planning/freshforge_modelwright_fable_deployment_targets.md` to collect next-step
  FreshForge workflow automation targets for the narrower Modelwright + FABLE Pyculator lane within
  the CLEWs-C2020 project context, including upstream functional caveats.
- Bootstrapped the `fable-pyculator` package scaffold as a FABLE Calculator-specific notebook layer on
  top of Modelwright-generated Python models.
- Added typed scenario parameter, selection control, output indicator, and output table declarations
  under `src/fable_pyculator/`.
- Added discovery helpers for FABLE-C `SCENARIOS selection` tables and canonical output-sheet Excel
  tables.
- Added an `ipywidgets` scenario control surface and pandas/matplotlib notebook rendering helpers.
- Added tests for constants, control surfaces, workbook discovery, spec mapping, and output rendering.
- Added a Sphinx Read the Docs themed documentation scaffold with artifact, workbook-structure, and
  notebook-control-surface guides.
- Downloaded and tracked the public 2020 FABLE Calculator documentation PDF under
  `reference/fable-calculator/`.
- Downloaded the public 2019, 2020, and 2021 FABLE-C workbooks into ignored
  `tmp/private-workbooks/` and tracked checksums plus benchmark metadata under
  `benchmarks/fable-calculator/`.
- Inspected the public workbook structure and recorded that the 2020 and 2021 workbooks expose 16
  high-level `SCENARIOS selection` controls, while the 2019 workbook exposes an older 12-control
  structure.
- Established the FABLE-C output data surface order as `FOOD`, `PRODUCTION`, `TRADE`,
  `BIODIVERSITY`, `LAND`, `GHG`, and `WATER`.
- Adopted the Modelwright-style agent-assisted development workflow by adding `AGENTS.md`,
  `ROADMAP.md`, `CHANGE_LOG.md`, and `planning/README.md`.
- Configured the local Git remote `origin` as `https://github.com/UBC-FRESH/fable-pyculator.git`,
  created the public `UBC-FRESH/fable-pyculator` GitHub repository, installed and authenticated
  GitHub CLI locally, pushed the bootstrap commit to `main`, created Phase 0 parent issue #1 and
  child issues #2 through #5, and recorded the issue mapping in `ROADMAP.md`.
- Closed Phase 0 after posting verification evidence to child issues #2 through #5 and parent issue
  #1.
- Activated Phase 1 on `feature/p1-fable-c-notebook-wrapper-maturation`, created GitHub parent issue
  #6 and child issues #7 through #10, and scoped the phase around hardening FABLE-C selection-control
  discovery, curating headline outputs and figures, building the first 2020 generated-model notebook
  loop, and adding user-guide/validation evidence.
- Completed P1.1 by adding opt-in workbook-backed tests that validate the 2020 S.1 through S.16
  selection-control contract, confirm 2021 shares the same control structure with the known
  `Affor_scen` default difference, and preserve 2019 as an older 12-control fragility check; recorded
  findings in `planning/phase-1-selection-control-validation.md`.
- Completed P1.2 by adding curated headline output series for FOOD, LAND, GHG, and WATER, plus
  notebook rendering helpers for tidy pandas headline frames and matplotlib line figures; recorded
  source table mappings in `planning/phase-1-headline-output-curation.md`.
- Added a `Docs Pages` GitHub Actions workflow and phase close-out guidance so Sphinx docs build on
  pull requests to `main` and deploy to GitHub Pages after merges to `main`.
- Completed P1.3 by adding the first 2020 notebook-loop helpers that build a workbook-derived spec,
  load an ignored generated Modelwright model from `tmp/generated-models/fable-2020/`, apply
  selection-control overrides, and return rendered output tables plus curated headline frames and
  figures; added `examples/notebooks/fable-pyculator-2020-loop.ipynb` and recorded the contract in
  `planning/phase-1-2020-notebook-loop.md`.
- Completed P1.4 by adding Sphinx guide pages for the 2020 notebook workflow and validation scope,
  linking the tracked example notebook into the docs, and recording 2020 benchmark evidence plus 2021
  follow-up scope in `planning/phase-1-user-guide-validation-closeout.md`.
- Aligned FABLE Pyculator's Sphinx configuration and Pages workflow with Modelwright's Read the Docs
  themed documentation setup, including matching RTD theme options, `docs/requirements.txt`, and a
  generated-artifact theme verifier.
- Added a repo-local VSCode/Jupyter bootstrap script, documented the expected `.venv` notebook
  kernel, and made the 2020 example notebook resolve the repository root from its working directory
  instead of assuming the kernel starts at the repo root.
- Committed the 2020 example notebook after a successful benchmark run so GitHub can render the
  example output tables and headline figure directly in the browser.
- Activated Phase 2 on `feature/p2-output-table-column-flavour-filtering`, promoted issue #15 to the
  phase parent, and created child issues #16, #18, #19, and #17 for output table column-flavour
  metadata, filtering API, documentation, and workbook-backed validation.
- Completed Phase 2 implementation by adding workbook-derived output table column flavour metadata,
  render-time flavour filtering for output DataFrames and notebook loops, Sphinx guide examples, and
  opt-in workbook-backed validation for the 2020 and 2021 public FABLE-C tag inventories.
- Reopened Phase 2 for follow-up issue #21 to add wildcard and prefix-family output flavour filters
  such as `DATA`, `DATA*`, and `OUTPUT-*`.
- Completed Phase 2 follow-up issue #21 by adding prefix-family and trailing-star wildcard output
  flavour filters plus README and Sphinx examples.
- Activated Phase 3 on `feature/p3-default-all-rendered-outputs`, created parent issue #23 and child
  issues #25 and #24, and scoped the phase around rendering all output tables and headline frames by
  default from a single generated-model run.
- Completed Phase 3 implementation by making notebook loops render all declared output tables and
  headline frames by default, preserving explicit subset rendering, and re-executing the 2020 example
  notebook with working wildcard flavour-filter examples.
- Started post-Phase-3 polish issue #27 to make the 2020 example notebook's rendered output
  inspection cells clearer in GitHub preview.
- Activated Phase 4 on `feature/p4-scenario-definition-table-discovery`, created parent issue #29
  and child issues #30 through #33, and scoped the phase around discovering
  `SCENARIOS definition` native tables as notebook-inspectable metadata before richer editing widgets.
- Completed the Phase 4 implementation by adding typed scenario-definition table declarations,
  workbook discovery, pandas inspection helpers, documentation, and synthetic plus opt-in
  workbook-backed validation for the 2020/2021 definition-table inventory.
- Closed Phase 4 after PR #34 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed.
- Activated Phase 5 on `feature/p5-scenario-definition-input-semantics`, created parent issue #35
  and child issues #36 through #39, and scoped the phase around separating output-table flavour
  metadata from scenario-definition role/source metadata while adding selection-location links.
- Completed the Phase 5 implementation by renaming scenario-definition table metadata to
  `column_role_*`, removing `SCEN` from output flavour-tag normalization, adding
  scenario-definition location markers and `scenario_definition_tables_for_location`, and updating
  docs/tests/planning evidence.
- Closed Phase 5 after PR #40 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed.
- Activated Phase 6 on `feature/p6-alpha-release-readiness`, created parent issue #41 and child
  issues #42 through #45, and scoped the phase around `v0.1.0a1` alpha release readiness, release
  workflow symmetry with Modelwright, and expanded API/docs coverage.
- Completed the Phase 6 implementation by aligning package metadata and release extras with
  Modelwright, adding release artifact checks and a trusted-publishing workflow, expanding Sphinx API
  documentation and public docstrings, and documenting the `v0.1.0a1` alpha release runbook and
  caveats.
- Closed Phase 6 after PR #46 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed, including the release-artifact job and GitHub Pages deployment.

## 2026-06-29

- Activated Phase 7 on `feature/p7-2021-artifact-wiring`, created parent issue #48 and child issues
  #50, #52, #51, and #49, and scoped the phase around first-user feedback that 2021 workbook testing
  could accidentally reuse the 2020 generated model and that generated-model artifact creation was
  under-documented.
- Completed the Phase 7 implementation by adding explicit 2021 workbook/generated-model defaults,
  `build_2021_notebook_spec`, `run_2021_notebook_loop`, a shared `build_notebook_spec`, a 2021
  notebook wiring template with no 2020 fallback, generated-model artifact documentation, and tests
  guarding the 2020/2021 artifact boundary.
- Created Modelwright follow-up issue UBC-FRESH/modelwright#201 to clarify how Modelwright
  `contract.json`, `expressions.json`, and `constants.json` generation inputs are produced for new
  production-sized workbook models.
- Closed Phase 7 after PR #53 merged to `main` and the post-merge Tests and Docs Pages workflows
  passed, including release-artifact checks and GitHub Pages deployment.
- Activated Phase 8 on `feature/p8-validated-2021-generated-model`, created parent issue #54 and
  child issues #59, #58, #55, #57, and #56, and scoped the phase around publishing a compressed 2021
  generated-model artifact only if Modelwright validation reaches the same zero-mismatch
  comparable-output standard used for the 2020 benchmark.
- Completed the core Phase 8 validation path: Modelwright extraction, graph construction, formula
  translation, contract inference, Python generation, generated-model execution, and cached-output
  comparison passed for the public 2021 FABLE-C workbook with 281,922 comparable outputs, 281,922
  matches, 0 mismatches, and 15,080 non-comparable cached blank formula outputs recorded as boundary
  evidence.
- Published the approved compressed 2021 generated model under
  `examples/fable_2021/generated_fable_2021_model.py.xz`, added sanitized validation evidence in
  `examples/fable_2021/README.md` and `planning/phase-8-2021-validation-summary.md`, and updated the
  2021 notebook to materialize that archive into ignored `tmp/generated-models/fable-2021/` working
  space.
- Merged upstream Modelwright PR #204 at `c3734d3` to fix generated `VLOOKUP` `#N/A` propagation,
  then reran the 2021 generation/validation path and recorded the clean Phase 8 verification suite.
- Closed Phase 8 after PR #60 merged to `main` at `c073f4e` and the post-merge Test and Docs Pages
  workflows passed, including GitHub Pages deployment.
- Created FreshForge deployment parent issues #75 through #79 for FABLE Pyculator Phases 12 through
  16, created active Phase 12 child issues #80 through #83, and opened
  `feature/p12-output-ref-workflow-builder-apis` to extract notebook-local output-ref/workflow logic
  into tested package helpers before adding a one-command 2021 rebuild workflow.
- Implemented the Phase 12 helper extraction by adding `fable_pyculator.workflows`, public output-ref
  derivation, version-specific FreshForge build paths, stable output-ref/workflow/validation JSON
  writers, cached-workbook validation-scenario generation, and Modelwright FreshForge workflow
  construction; updated the 2021 FreshForge notebooks and Sphinx API docs to use the new package
  helpers.
- Closed Phase 12 after PR #84 merged to `main`, post-merge Test and Docs Pages workflows passed,
  and live docs verification confirmed the new workflow-helper API and notebook-control guide content
  were deployed.
- Reactivated skipped Phase 9 on `feature/p9-fable-freshforge-provider`, created child issues #85
  through #89, and implemented a plan-only FABLE Pyculator FreshForge provider with a public-safe
  2021 notebook workflow example, Sphinx docs, entry-point metadata, and provider discovery/planning
  tests.
- Closed Phase 9 after PR #90 merged to `main`, post-merge Test and Docs Pages workflows passed, and
  live docs verification confirmed the new provider guide and API reference content were deployed.

## 2026-07-02

- Activated Phase 22 on `feature/p22-freshforge-strategy-matrices`, created parent issue #149 and child issues #150 through #154, and scoped the phase around connecting output-ref strategy comparison to FreshForge Phase 8 matrices while preserving compare-only defaults and optional FreshForge integration.
- Implemented the Phase 22 matrix layer by adding FreshForge-free matrix records and writers, lazy matrix plan/run helpers, strategy-comparison CLI flags for `--include-matrix`, `--matrix-plan`, and explicit `--matrix-run`, and documentation/tests for the matrix workflow boundary.
- Closed Phase 22 after PR #155 merged to `main` and the post-merge Test and Docs Pages workflows passed, including GitHub Pages deployment.

## 2026-07-02

- Activated Phase 23 on `feature/p23-freshforge-scenario-bundle-matrices`, created parent issue #156 and child issues #157 through #161, and scoped the phase around treating each scenario-bundle scenario as an explicit FreshForge matrix case while preserving direct and single-workflow FreshForge modes.
- Implemented the Phase 23 matrix layer by adding scenario-bundle matrix path/plan records, YAML matrix/template writers, lazy FreshForge matrix plan/run helpers, scenario-bundle CLI flags for `--freshforge-matrix-plan` and explicit `--freshforge-matrix-run`, public-safe examples, and documentation/tests for the matrix boundary.
- Closed Phase 23 after PR #162 merged to `main` and the post-merge Test and Docs Pages workflows passed, including GitHub Pages deployment.
- Activated Phase 24 on `feature/p24-v0.1.0a4-release`, created parent issue #163 and child issues
  #164 through #167, and scoped the phase around publishing the matrix workflow automation alpha after
  FreshForge `v0.1.0a4`.
- Prepared the `v0.1.0a4` release candidate by bumping package/import/provider versions, updating
  FreshForge guidance to `v0.1.0a4`, and refreshing README, release docs, tests, and release-artifact
  checks for output-ref strategy matrices and scenario-bundle matrices.
- Verified the `v0.1.0a4` release candidate with Ruff, full pytest (`121` passed and `9` skipped
  workbook tests), Sphinx warning-as-error docs, Read the Docs theme verification, public workbook
  checksums, release-artifact checks against published `modelwright 0.1.0a8`, and `git diff --check`.
- Released `fable-pyculator==0.1.0a4` after PR #168 merged to `main`, post-merge Test workflow
  #28562906226 and Docs Pages workflow #28562906254 passed, tag `v0.1.0a4` triggered Release
  workflow #28562950207, and trusted publishing uploaded the wheel and sdist to PyPI.
- Created the GitHub prerelease for `v0.1.0a4` with the workflow-built artifacts, verified PyPI
  propagation, and smoke-tested a clean PyPI install of `fable-pyculator[notebook]==0.1.0a4`
  importing `fable_pyculator 0.1.0a4` with `modelwright 0.1.0a8`.
