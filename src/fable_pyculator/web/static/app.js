import { escapeHtml, renderMarkdown } from "./markdown.js?v=p28i";

const API = new URL("api/", document.baseURI);
const PAGES = ["overview", "workbench", "results", "compare", "validation", "artifacts"];

const state = {
  options: null,
  artifacts: [],
  runs: [],
  activeVersion: null,
  spec: null,
  prepared: false,
  activeRun: null,
  activeTable: null,
  pollToken: 0,
  agent: { enabled: false, available: false, model: null },
  chats: [],
  ask: { session: null, busy: false, runId: null, chatId: null, title: "New chat", showArchived: false, search: "" },
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

async function request(path, options = {}) {
  const response = await fetch(new URL(path, API), {
    headers: { "content-type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      detail = payload.detail || detail;
    } catch {
      /* keep the status text */
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function formatNumber(value, digits = 3) {
  if (value === null || value === undefined || value === "") return "—";
  if (typeof value !== "number" || !Number.isFinite(value)) return escapeHtml(value);
  const magnitude = Math.abs(value);
  if (magnitude !== 0 && (magnitude >= 1e6 || magnitude < 1e-3)) {
    return value.toExponential(2);
  }
  return new Intl.NumberFormat(undefined, { maximumSignificantDigits: digits }).format(value);
}

function formatSigned(value, digits = 3) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  const formatted = formatNumber(Math.abs(value), digits);
  return `${value > 0 ? "+" : value < 0 ? "−" : ""}${formatted}`;
}

function formatBytes(value) {
  if (!value && value !== 0) return "—";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = Number(value);
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return escapeHtml(value);
  return date.toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

function pill(text, tone = "muted") {
  return `<span class="pill ${tone}">${escapeHtml(text)}</span>`;
}

function setStatus(text, tone = "muted") {
  const element = $("#status-pill");
  element.textContent = text;
  element.className = `pill ${tone}`;
}

let toastTimer = null;
function toast(message, tone = "info") {
  const element = $("#toast");
  element.textContent = message;
  element.className = `toast ${tone}`;
  element.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    element.hidden = true;
  }, 5200);
}

function showPage(page) {
  if (!PAGES.includes(page)) page = "overview";
  $$(".page").forEach((section) => {
    section.hidden = section.id !== `page-${page}`;
    section.classList.toggle("active", section.id === `page-${page}`);
  });
  $$(".nav-tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.page === page);
    button.setAttribute("aria-current", button.dataset.page === page ? "page" : "false");
  });
  history.replaceState(null, "", `#${page}`);
  if (page === "workbench") loadWorkbench();
  if (page === "results") loadRuns();
  if (page === "compare") renderComparePicker();
  if (page === "validation") loadValidation();
  if (page === "artifacts") loadArtifacts();
}

async function bootstrap() {
  try {
    const [options, artifacts, runs, agent, chats] = await Promise.all([
      request("options"),
      request("artifacts"),
      request("runs"),
      request("agent").catch(() => null),
      request("chats?include_archived=true").catch(() => []),
    ]);
    state.options = options;
    state.artifacts = artifacts;
    state.runs = runs;
    state.chats = chats;
    state.agent = agent || { enabled: Boolean(options.assistant_enabled), available: false, model: options.assistant_model };
    $("#docs-link").href = options.docs_url || "#";
    const docsBase = (options.docs_url || "").replace(/\/$/, "");
    if (docsBase) {
      $("#docs-portal").href = `${docsBase}/guides/web-portal.html`;
      $("#docs-artifacts").href = `${docsBase}/guides/generated-model-artifacts.html`;
      $("#docs-validation").href = `${docsBase}/guides/validation-scope.html`;
    }
    document.title = `${options.title || "FABLE Pyculator"} · Scenario portal`;
    setupAsk();
    await restoreChat();
    setStatus("ready", "good");
    renderVersionSelect();
    renderOverview();
    const initial = location.hash.replace("#", "");
    showPage(PAGES.includes(initial) ? initial : "overview");
  } catch (error) {
    setStatus("service unavailable", "bad");
    toast(error.message, "bad");
  } finally {
    $("#app-loading").hidden = true;
  }
}

async function refreshArtifacts() {
  const [artifacts, runs] = await Promise.all([request("artifacts"), request("runs")]);
  state.artifacts = artifacts;
  state.runs = runs;
  renderOverview();
  renderVersionSelect();
  renderAskContext();
}

function renderOverview() {
  const container = $("#overview-cards");
  if (!state.artifacts.length) {
    container.innerHTML = `<p class="hint">No artifact versions are configured.</p>`;
    return;
  }
  container.innerHTML = state.artifacts
    .map((artifact) => {
      const ready = artifact.can_prepare;
      const prepared = artifact.prepared;
      const counts = artifact.summary?.counts;
      const tone = prepared ? "good" : ready ? "warn" : "bad";
      const label = prepared ? "prepared" : ready ? "ready to prepare" : "files missing";
      return `
        <article class="version-card">
          <div class="card-top">
            <div>
              <h3>FABLE ${escapeHtml(artifact.version)}</h3>
              <p class="hint">${artifact.model_source ? `${escapeHtml(artifact.model_source)} model` : "no model artifact"}</p>
            </div>
            ${pill(label, tone)}
          </div>
          <dl class="metric-row">
            <div><dt>Controls</dt><dd>${counts ? counts.selection_controls : "—"}</dd></div>
            <div><dt>Tables</dt><dd>${counts ? counts.output_tables : "—"}</dd></div>
            <div><dt>Headlines</dt><dd>${counts ? counts.headline_series : "—"}</dd></div>
          </dl>
          <div class="tiny-meta">
            <span>Workbook ${artifact.files.workbook.exists ? "present" : "missing"}</span>
            <span>Model ${artifact.files.generated_model.exists ? "working" : artifact.files.compressed_model.exists ? "compressed" : "missing"}</span>
            <span>Validation ${artifact.has_validation_evidence ? "yes" : "no"}</span>
          </div>
          <div class="button-row">
            <button class="button primary small" type="button" data-open-workbench="${escapeHtml(artifact.version)}">Open workbench</button>
            <button class="button ghost small" type="button" data-artifact="${escapeHtml(artifact.version)}">Artifact detail</button>
          </div>
        </article>`;
    })
    .join("");
  container.querySelectorAll("[data-open-workbench]").forEach((button) => {
    button.addEventListener("click", () => {
      state.activeVersion = button.dataset.openWorkbench;
      showPage("workbench");
    });
  });
  container.querySelectorAll("[data-artifact]").forEach((button) => {
    button.addEventListener("click", () => showPage("artifacts"));
  });

  const runs = $("#overview-runs");
  if (!state.runs.length) {
    runs.innerHTML = `<p class="hint">No saved runs yet. Prepare a model in the workbench and run a scenario.</p>`;
    return;
  }
  runs.innerHTML = state.runs
    .slice(0, 6)
    .map(
      (run) => `
      <button class="compact-run" type="button" data-run="${escapeHtml(run.run_id)}">
        <span><strong>${escapeHtml(run.name)}</strong><small>FABLE ${escapeHtml(run.version)} · ${formatDate(run.created_at)}</small></span>
        <span class="compact-run-metric">${run.headline_summary?.length || 0} headlines</span>
      </button>`,
    )
    .join("");
  runs.querySelectorAll("[data-run]").forEach((button) => {
    button.addEventListener("click", () => openRun(button.dataset.run));
  });
}

function renderVersionSelect() {
  const select = $("#workbench-version");
  const previous = state.activeVersion || select.value;
  select.innerHTML = state.artifacts
    .map((artifact) => `<option value="${escapeHtml(artifact.version)}">FABLE ${escapeHtml(artifact.version)}</option>`)
    .join("");
  if (previous && state.artifacts.some((artifact) => artifact.version === previous)) {
    select.value = previous;
  } else if (state.artifacts.length) {
    select.value = state.artifacts[0].version;
  }
  state.activeVersion = select.value;
}

async function loadWorkbench() {
  renderVersionSelect();
  const version = state.activeVersion;
  if (!version) return;
  const artifact = state.artifacts.find((item) => item.version === version);
  renderWorkbenchArtifact(artifact);
  if (artifact?.prepared) {
    await loadSpec(version);
    return;
  }
  state.prepared = false;
  state.spec = null;
  $("#workbench-empty").hidden = false;
  $("#workbench-controls").hidden = true;
  $("#run-scenario").disabled = true;
  $("#reset-controls").disabled = true;
  $("#workbench-status").textContent = artifact?.can_prepare ? "ready to prepare" : "files missing";
  $("#workbench-status").className = `pill ${artifact?.can_prepare ? "warn" : "bad"}`;
}

function renderWorkbenchArtifact(artifact) {
  const container = $("#workbench-artifact");
  if (!artifact) {
    container.innerHTML = "";
    return;
  }
  container.innerHTML = `
    <dt>Workbook</dt><dd>${artifact.files.workbook.exists ? "present" : "missing"}</dd>
    <dt>Model</dt><dd>${artifact.files.generated_model.exists ? "working copy" : artifact.files.compressed_model.exists ? "compressed archive" : "missing"}</dd>
    <dt>Validation</dt><dd>${artifact.has_validation_evidence ? "compact evidence" : "not packaged"}</dd>
    <dt>Runtime</dt><dd>${escapeHtml(state.options?.runtime_dir || "")}</dd>`;
  $("#prepare-model").disabled = artifact.prepared || !artifact.can_prepare;
  $("#prepare-model").textContent = artifact.prepared ? "Prepared" : "Prepare model";
}

async function prepareModel() {
  const version = state.activeVersion;
  if (!version) return;
  const button = $("#prepare-model");
  button.disabled = true;
  try {
    const job = await request(`models/${version}/prepare`, { method: "POST" });
    const finished = await waitForJob(job.job_id, (current) => {
      renderJob($("#run-progress"), current, "Preparing model");
    });
    if (finished.status !== "ok") {
      renderJob($("#run-progress"), finished, "Preparation failed");
      button.disabled = false;
      return;
    }
    $("#run-progress").hidden = true;
    toast(`FABLE ${version} prepared`, "good");
    await refreshArtifacts();
    await loadWorkbench();
  } catch (error) {
    toast(error.message, "bad");
    button.disabled = false;
  }
}

async function loadSpec(version) {
  try {
    const payload = await request(`models/${version}/spec`);
    state.spec = payload.summary;
    state.prepared = true;
    renderControls();
    $("#workbench-empty").hidden = true;
    $("#workbench-controls").hidden = false;
    $("#workbench-status").textContent = "prepared";
    $("#workbench-status").className = "pill good";
    $("#prepare-model").disabled = true;
    $("#prepare-model").textContent = "Prepared";
    $("#run-scenario").disabled = false;
    $("#reset-controls").disabled = false;
  } catch (error) {
    state.prepared = false;
    state.spec = null;
    $("#workbench-status").textContent = "needs preparation";
    $("#workbench-status").className = "pill warn";
    $("#workbench-empty").hidden = false;
    $("#workbench-controls").hidden = true;
    if (error.message) toast(error.message, "warn");
  }
}

function renderControls() {
  const spec = state.spec;
  if (!spec) return;
  $("#spec-provenance").textContent = spec.provenance ? `Workbook provenance: ${spec.provenance}` : "";
  const total = spec.selection_controls.length + spec.parameters.length;
  $("#control-count").textContent = `${total} controls`;
  const parameterControls = spec.parameters.map((parameter, index) => controlField(parameter, `parameter-${index}`)).join("");
  const selectionControls = spec.selection_controls.map((control) => selectionField(control)).join("");
  $("#control-grid").innerHTML = parameterControls + selectionControls;
  const tableSelect = $("#table-select");
  tableSelect.innerHTML = spec.output_tables
    .map((table) => `<option value="${escapeHtml(table.name)}">${escapeHtml(table.label || table.name)} · ${escapeHtml(table.sheet || "")}</option>`)
    .join("");
  updateTableMode();
}

function controlField(parameter, id) {
  const label = escapeHtml(parameter.label || parameter.name);
  if (parameter.choices?.length) {
    const options = parameter.choices
      .map((choice) => `<option value="${escapeHtml(choice)}" ${choice === parameter.default ? "selected" : ""}>${escapeHtml(choice)}</option>`)
      .join("");
    return `<label class="control-field"><span>${label}<small>${escapeHtml(parameter.unit || "")}</small></span><select data-control="${escapeHtml(parameter.name)}" data-default="${escapeHtml(parameter.default ?? "")}">${options}</select></label>`;
  }
  if (parameter.kind === "boolean") {
    return `<label class="control-field check-field"><input type="checkbox" data-control="${escapeHtml(parameter.name)}" data-default="${parameter.default ? "1" : "0"}" ${parameter.default ? "checked" : ""}><span>${label}</span></label>`;
  }
  const type = parameter.kind === "number" ? "number" : "text";
  return `<label class="control-field"><span>${label}<small>${escapeHtml(parameter.unit || "")}</small></span><input id="${id}" type="${type}" data-control="${escapeHtml(parameter.name)}" data-default="${escapeHtml(parameter.default ?? "")}" value="${escapeHtml(parameter.default ?? "")}"></label>`;
}

function selectionField(control) {
  const options = control.options
    .map((option) => {
      const selected = option.value === control.default ? "selected" : "";
      return `<option value="${escapeHtml(option.value)}" ${selected}>${escapeHtml(option.label || option.value)}</option>`;
    })
    .join("");
  const location = control.location ? `<small>${escapeHtml(control.location)}</small>` : "";
  return `<label class="control-field"><span>${escapeHtml(control.label || control.name)}${location}</span><select data-control="${escapeHtml(control.name)}" data-default="${escapeHtml(control.default ?? "")}">${options}</select></label>`;
}

function updateTableMode() {
  const mode = $("#table-mode").value;
  $("#table-select-wrap").hidden = mode !== "selected";
}

function collectSelections() {
  const selections = {};
  $$("[data-control]").forEach((element) => {
    const name = element.dataset.control;
    if (element.type === "checkbox") {
      selections[name] = element.checked ? 1 : 0;
    } else if (element.type === "number") {
      selections[name] = element.value === "" ? null : Number(element.value);
    } else {
      selections[name] = element.value;
    }
  });
  return selections;
}

function resetControls() {
  $$("[data-control]").forEach((element) => {
    if (element.type === "checkbox") {
      element.checked = element.dataset.default === "1";
    } else {
      element.value = element.dataset.default ?? "";
    }
  });
  $("#scenario-name").value = "Scenario 1";
  $("#run-horizon").value = "2050";
  $("#table-mode").value = "all";
  $("#flavour-tags").value = "";
  $("#include-context").checked = true;
  updateTableMode();
}

async function runScenario() {
  if (!state.prepared) return;
  const version = state.activeVersion;
  const mode = $("#table-mode").value;
  let outputTables = null;
  if (mode === "headline") outputTables = [];
  if (mode === "selected") {
    outputTables = Array.from($("#table-select").selectedOptions).map((option) => option.value);
    if (!outputTables.length) {
      toast("Select at least one output table, or choose another table mode.", "warn");
      return;
    }
  }
  const rawFlavour = $("#flavour-tags").value.trim();
  const flavour = rawFlavour
    ? rawFlavour.includes(",")
      ? rawFlavour.split(",").map((item) => item.trim()).filter(Boolean)
      : rawFlavour
    : null;
  const payload = {
    version,
    name: $("#scenario-name").value.trim() || "scenario",
    selections: collectSelections(),
    output_table_names: outputTables,
    column_flavour_tags: flavour,
    include_context_columns: $("#include-context").checked,
    horizon: Number($("#run-horizon").value || 2050),
  };
  const button = $("#run-scenario");
  button.disabled = true;
  $("#run-progress").hidden = false;
  try {
    const job = await request("runs", { method: "POST", body: JSON.stringify(payload) });
    const finished = await waitForJob(job.job_id, (current) => {
      renderJob($("#run-progress"), current, "Running scenario");
    });
    if (finished.status !== "ok") {
      renderJob($("#run-progress"), finished, "Scenario failed");
      return;
    }
    toast(`Scenario saved as ${finished.result.run_id}`, "good");
    state.runs = await request("runs");
    state.activeRun = finished.result;
    renderOverview();
    renderAskContext();
    showPage("results");
    renderRunDetail(finished.result);
  } catch (error) {
    toast(error.message, "bad");
  } finally {
    button.disabled = false;
  }
}

function renderJob(container, job, title) {
  container.hidden = false;
  const tone = job.status === "error" ? "bad" : job.status === "ok" ? "good" : "warn";
  container.innerHTML = `
    <div class="job-head"><strong>${escapeHtml(title)}</strong>${pill(job.status, tone)}</div>
    <div class="progress-track"><span style="width:${Number(job.progress) || 0}%"></span></div>
    <p>${escapeHtml(job.message || "")}</p>
    ${job.error ? `<p class="error-text">${escapeHtml(job.error)}</p>` : ""}`;
}

async function waitForJob(jobId, onProgress) {
  const token = ++state.pollToken;
  while (true) {
    const job = await request(`jobs/${jobId}`);
    onProgress?.(job);
    if (job.status === "ok" || job.status === "error") return job;
    if (token !== state.pollToken) return job;
    await new Promise((resolve) => setTimeout(resolve, 700));
  }
}

async function loadRuns() {
  try {
    state.runs = await request("runs");
    renderRunList();
    renderComparePicker();
    renderAskContext();
    if (state.activeRun?.run_id) {
      const record = await request(`runs/${state.activeRun.run_id}`);
      renderRunDetail(record);
    } else if (state.runs.length) {
      await openRun(state.runs[0].run_id);
    }
  } catch (error) {
    toast(error.message, "bad");
  }
}

function renderRunList() {
  const container = $("#runs-list");
  if (!state.runs.length) {
    container.innerHTML = `<p class="hint">No saved runs yet.</p>`;
    return;
  }
  container.innerHTML = state.runs
    .map(
      (run) => `
      <button class="run-list-item ${state.activeRun?.run_id === run.run_id ? "active" : ""}" type="button" data-run="${escapeHtml(run.run_id)}">
        <strong>${escapeHtml(run.name)}</strong>
        <span>FABLE ${escapeHtml(run.version)} · ${formatDate(run.created_at)}</span>
        <span class="tiny-meta">${run.headline_summary?.length || 0} headline indicators · ${run.table_summaries?.length || 0} tables</span>
      </button>`,
    )
    .join("");
  container.querySelectorAll("[data-run]").forEach((button) => {
    button.addEventListener("click", () => openRun(button.dataset.run));
  });
}

async function openRun(runId) {
  try {
    const record = await request(`runs/${runId}`);
    state.activeRun = record;
    state.activeTable = null;
    showPage("results");
    renderRunList();
    renderRunDetail(record);
  } catch (error) {
    toast(error.message, "bad");
  }
}

function renderRunDetail(record) {
  const detail = $("#run-detail");
  if (!record) {
    detail.innerHTML = `<div class="empty-state"><h2>Select a run</h2><p>Saved runs appear here after a scenario completes.</p></div>`;
    return;
  }
  const selectionChips = Object.entries(record.selections || {})
    .map(([name, value]) => `<span class="chip"><b>${escapeHtml(name)}</b>${escapeHtml(value)}</span>`)
    .join("");
  const extensionNote = record.extension
    ? `<p class="table-note">${escapeHtml(record.extension.note || "2070 trend extension is active.")}</p>`
    : "";
  const qualityWarnings = record.quality_warnings || [];
  const qualityPanel = qualityWarnings.length
    ? `<section class="quality-panel" aria-label="Data quality warnings">
        <div class="quality-head"><h3>Data quality</h3>${pill(`${qualityWarnings.length} note${qualityWarnings.length === 1 ? "" : "s"}`, "warn")}</div>
        <ul class="quality-list">
          ${qualityWarnings
            .map(
              (warning) => `<li class="quality-item ${escapeHtml(warning.severity || "info")}">
                <strong>${escapeHtml(warning.title || warning.code || "Note")}</strong>
                <p>${escapeHtml(warning.message || "")}</p>
                ${warning.scope ? `<small>${escapeHtml(warning.scope)}</small>` : ""}
              </li>`,
            )
            .join("")}
        </ul>
      </section>`
    : "";
  const kpis = (record.headline_summary || [])
    .map((item) => {
      const delta = item.delta === null || item.delta === undefined ? "—" : formatSigned(item.delta);
      const percent = item.percent_change === null || item.percent_change === undefined ? "" : `${formatSigned(item.percent_change, 2)}%`;
      return `
        <article class="kpi-card">
          <span class="kpi-label">${escapeHtml(item.label || item.name)}</span>
          <strong class="kpi-value">${formatNumber(item.last_value)}</strong>
          <span class="kpi-unit">${escapeHtml(item.unit || item.group || "")}</span>
          <span class="kpi-delta">${escapeHtml(String(item.first_year))} → ${escapeHtml(String(item.last_year))} · ${delta} <small>${percent}</small></span>
        </article>`;
    })
    .join("");
  const charts = Object.entries(record.headline_series || {})
    .map(
      ([name, payload]) => `
      <article class="chart-card">
        <div class="chart-head">
          <div>
            <h3>${escapeHtml(payload.label || name)}</h3>
            <p class="hint">${escapeHtml(payload.sheet || "")}${payload.range_ref ? ` · ${escapeHtml(payload.range_ref)}` : ""}${payload.description ? ` · ${escapeHtml(payload.description)}` : ""}</p>
          </div>
          <span class="pill muted">${escapeHtml(payload.unit || "value")}</span>
        </div>
        ${lineChart(payload, `${escapeHtml(payload.label || name)} by year`)}
      </article>`,
    )
    .join("");
  const tableOptions = (record.table_summaries || [])
    .map((table) => `<option value="${escapeHtml(table.name)}">${escapeHtml(table.label || table.name)} · ${escapeHtml(table.sheet || "")} (${table.row_count}×${table.column_count})</option>`)
    .join("");
  const skipped = Object.keys(record.skipped_output_tables || {});
  const skippedNote = skipped.length
    ? `<p class="hint">${skipped.length} table(s) skipped because no columns matched the flavour filter: ${skipped.map(escapeHtml).join(", ")}</p>`
    : "";
  const provenance = record.provenance
    ? `<details class="provenance">
        <summary>Run provenance</summary>
        <dl class="kv small-kv">
          <dt>Portal</dt><dd>${escapeHtml(record.provenance.portal_version || "")}</dd>
          <dt>Workbook</dt><dd>${escapeHtml(record.provenance.workbook?.path || "")} (${formatBytes(record.provenance.workbook?.size_bytes)})</dd>
          <dt>Model</dt><dd>${escapeHtml(record.provenance.generated_model?.path || "")} (${formatBytes(record.provenance.generated_model?.size_bytes)})</dd>
          <dt>Prepared</dt><dd>${formatDate(record.provenance.prepared_at)}</dd>
          <dt>Workbook id</dt><dd>${escapeHtml(record.provenance.workbook_id || "")}</dd>
        </dl>
      </details>`
    : "";
  detail.innerHTML = `
    <div class="run-head">
      <div>
        <p class="eyebrow">FABLE ${escapeHtml(record.version)} · ${escapeHtml(record.status || "ok")}</p>
        <h2>${escapeHtml(record.name)}</h2>
        <p class="hint">${formatDate(record.created_at)} · ${escapeHtml(String(record.duration_seconds ?? "—"))} s runtime · ${escapeHtml(record.input_count ?? 0)} input cells</p>
      </div>
      <div class="button-row">
        <button class="button ghost small" type="button" data-ask-run="${escapeHtml(record.run_id)}">+ Ask about this run</button>
        <button class="button ghost small" type="button" data-compare-one="${escapeHtml(record.run_id)}">Compare this run</button>
      </div>
    </div>
    <div class="chip-row">${selectionChips || `<span class="hint">No explicit selection overrides.</span>`}</div>
    ${extensionNote}
    ${qualityPanel}
    ${provenance}
    <div class="kpi-grid">${kpis || `<p class="hint">No headline series were declared for this version.</p>`}</div>
    <section class="section">
      <div class="section-head"><h3>Headline series</h3><span class="hint">Values returned by the generated model</span></div>
      <div class="chart-grid">${charts || `<p class="hint">No headline frames were rendered.</p>`}</div>
    </section>
    <section class="section">
      <div class="section-head">
        <div><h3>Output tables</h3><p class="hint">Rendered from the same run. Context columns are preserved when selected.</p></div>
        <div class="table-actions">
          <select id="table-picker" aria-label="Output table">${tableOptions}</select>
          <button id="download-table" class="button ghost small" type="button">Export CSV</button>
        </div>
      </div>
      ${skippedNote}
      <div id="table-panel" class="table-panel"><p class="hint">Choose a table.</p></div>
    </section>`;
  detail.querySelector("[data-ask-run]")?.addEventListener("click", () => {
    openAsk(record.run_id);
  });
  detail.querySelector("[data-compare-one]")?.addEventListener("click", () => {
    state.compareSeed = record.run_id;
    showPage("compare");
  });
  const picker = $("#table-picker");
  if (picker && record.table_summaries?.length) {
    picker.addEventListener("change", () => loadTable(record.run_id, picker.value));
    loadTable(record.run_id, picker.value);
  }
}

async function loadTable(runId, tableName) {
  const panel = $("#table-panel");
  if (!panel) return;
  panel.innerHTML = `<p class="hint">Loading ${escapeHtml(tableName)}…</p>`;
  try {
    const payload = await request(`runs/${runId}/tables/${encodeURIComponent(tableName)}`);
    state.activeTable = payload;
    panel.innerHTML = renderTable(payload);
    $("#download-table").onclick = () => downloadCsv(`${runId}-${tableName}.csv`, payload);
  } catch (error) {
    panel.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
  }
}

function renderTable(payload) {
  const columns = payload.columns || [];
  const rows = payload.rows || [];
  const limit = 2000;
  const shown = rows.slice(0, limit);
  const body = shown
    .map(
      (row) =>
        `<tr>${columns
          .map((column) => {
            const value = row[column];
            const numeric = typeof value === "number";
            return `<td class="${numeric ? "numeric" : ""}" title="${escapeHtml(value ?? "")}">${formatNumber(value)}</td>`;
          })
          .join("")}</tr>`,
    )
    .join("");
  const note = rows.length > limit ? `<p class="hint">Showing the first ${limit} of ${rows.length} rows; CSV export contains all rows.</p>` : "";
  return `
    <div class="table-meta">${pill(`${rows.length} rows`)} ${pill(`${columns.length} columns`)} ${payload.sheet ? pill(payload.sheet) : ""} ${payload.selected_column_flavour_tags ? pill(`flavour ${payload.selected_column_flavour_tags}`) : ""}</div>
    ${payload.display_repair ? `<p class="table-note">${escapeHtml(payload.display_repair)}</p>` : ""}
    ${payload.extension_note ? `<p class="table-note">${escapeHtml(payload.extension_note)}</p>` : ""}
    <div class="table-wrap"><table><thead><tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead><tbody>${body}</tbody></table></div>
    ${note}`;
}

function downloadCsv(filename, payload) {
  const columns = payload.columns || [];
  const rows = payload.rows || [];
  const quote = (value) => {
    const text = value === null || value === undefined ? "" : String(value);
    return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
  };
  const lines = [columns.map(quote).join(","), ...rows.map((row) => columns.map((column) => quote(row[column])).join(","))];
  const blob = new Blob([`${lines.join("\n")}\n`], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function lineChart(payload, label) {
  const points = (payload.rows || [])
    .filter((row) => typeof row.value === "number" && Number.isFinite(row.value))
    .map((row) => ({ year: row.year, value: row.value }));
  if (points.length < 2) {
    return `<p class="hint">No numeric series is available for this run.</p>`;
  }
  return chartSvg([{ label: payload.label || "value", color: "#2f7d4f", points }], { label });
}

function multiLineChart(entry) {
  const colors = ["#2f7d4f", "#1f6feb", "#b45309", "#7c3aed", "#0f766e", "#be123c", "#4b5563", "#a16207"];
  const series = entry.years.map((year, index) => ({
    label: entry.runLabels[index],
    color: colors[index % colors.length],
    points: entry.series.map((item) => ({ year, value: item.values[index] })),
  }));
  return chartSvg(series, { label: `${entry.label} comparison` });
}

function chartSvg(series, { label = "" } = {}) {
  const width = 680;
  const height = 230;
  const padding = { left: 58, right: 22, top: 14, bottom: 34 };
  const all = series.flatMap((item) => item.points.filter((point) => typeof point.value === "number" && Number.isFinite(point.value)));
  if (!all.length) return `<p class="hint">No numeric values to chart.</p>`;
  const years = [...new Set(all.map((point) => String(point.year)))];
  const values = all.map((point) => point.value);
  let min = Math.min(...values);
  let max = Math.max(...values);
  if (min === max) {
    const pad = Math.abs(min || 1) * 0.1;
    min -= pad;
    max += pad;
  } else {
    const pad = (max - min) * 0.08;
    min -= pad;
    max += pad;
  }
  const x = (year) => {
    const index = years.indexOf(String(year));
    return padding.left + (years.length <= 1 ? 0 : (index / (years.length - 1)) * (width - padding.left - padding.right));
  };
  const y = (value) => padding.top + ((max - value) / (max - min)) * (height - padding.top - padding.bottom);
  const grid = [0, 0.25, 0.5, 0.75, 1]
    .map((fraction) => {
      const value = max - fraction * (max - min);
      const yPos = padding.top + fraction * (height - padding.top - padding.bottom);
      return `<line x1="${padding.left}" y1="${yPos}" x2="${width - padding.right}" y2="${yPos}" class="chart-grid-line"/><text x="${padding.left - 8}" y="${yPos + 4}" text-anchor="end" class="chart-axis">${escapeHtml(formatNumber(value, 2))}</text>`;
    })
    .join("");
  const xLabels = years
    .map((year, index) => {
      if (years.length > 6 && index !== 0 && index !== years.length - 1 && index % Math.ceil(years.length / 4) !== 0) return "";
      const xPos = x(year);
      return `<text x="${xPos}" y="${height - 10}" text-anchor="middle" class="chart-axis">${escapeHtml(year)}</text>`;
    })
    .join("");
  const paths = series
    .map((item) => {
      const valid = item.points.filter((point) => typeof point.value === "number" && Number.isFinite(point.value));
      if (!valid.length) return "";
      const path = valid.map((point, index) => `${index === 0 ? "M" : "L"}${x(point.year).toFixed(1)},${y(point.value).toFixed(1)}`).join(" ");
      const dots = valid
        .map((point) => `<circle cx="${x(point.year).toFixed(1)}" cy="${y(point.value).toFixed(1)}" r="2.6" fill="${item.color}"/>`)
        .join("");
      return `<path d="${path}" fill="none" stroke="${item.color}" stroke-width="2.2" stroke-linejoin="round"/>${dots}`;
    })
    .join("");
  const legend =
    series.length > 1
      ? `<div class="chart-legend">${series.map((item) => `<span><i style="background:${item.color}"></i>${escapeHtml(item.label)}</span>`).join("")}</div>`
      : "";
  const latest = series
    .map((item) => {
      const valid = item.points.filter((point) => typeof point.value === "number" && Number.isFinite(point.value));
      return valid.length ? `${item.label}: ${formatNumber(valid.at(-1).value)}` : "";
    })
    .filter(Boolean)
    .join(" · ");
  return `
    ${legend}
    <svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(label)}">
      ${grid}${xLabels}${paths}
    </svg>
    <p class="chart-foot">${escapeHtml(latest)}</p>`;
}

function renderComparePicker() {
  const container = $("#compare-picker");
  if (!state.runs.length) {
    container.innerHTML = `<p class="hint">No saved runs yet. Run at least two scenarios first.</p>`;
    return;
  }
  container.innerHTML = `
    <div class="check-grid">
      ${state.runs
        .map(
          (run) => `
        <label class="check-card">
          <input type="checkbox" value="${escapeHtml(run.run_id)}" ${state.compareSeed === run.run_id ? "checked" : ""}>
          <span><strong>${escapeHtml(run.name)}</strong><small>FABLE ${escapeHtml(run.version)} · ${formatDate(run.created_at)}</small></span>
        </label>`,
        )
        .join("")}
    </div>`;
}

async function compareRuns() {
  const selected = $$("#compare-picker input:checked").map((input) => input.value);
  if (selected.length < 2) {
    toast("Select at least two runs to compare.", "warn");
    return;
  }
  const output = $("#compare-output");
  output.innerHTML = `<p class="hint">Comparing ${selected.length} runs…</p>`;
  try {
    const payload = await request("compare", { method: "POST", body: JSON.stringify({ run_ids: selected }) });
    const runLabels = payload.runs.map((run) => run.name);
    const charts = payload.series
      .map((entry) => {
        const enriched = {
          ...entry,
          runLabels,
          series: payload.runs.map((run) => ({ run, values: entry.values[run.run_id] })),
        };
        return `
          <article class="chart-card">
            <div class="chart-head">
              <div><h3>${escapeHtml(entry.label || entry.name)}</h3><p class="hint">${escapeHtml(entry.unit || "")}</p></div>
            </div>
            ${multiLineChart(enriched)}
          </article>`;
      })
      .join("");
    const inputNames = [...new Set(payload.runs.flatMap((run) => Object.keys(run.selections || {})))].sort();
    const inputRows = inputNames
      .map(
        (name) =>
          `<tr><td>${escapeHtml(name)}</td>${payload.runs.map((run) => `<td>${escapeHtml(run.selections?.[name] ?? "—")}</td>`).join("")}</tr>`,
      )
      .join("");
    const kpiNames = [...new Set(payload.runs.flatMap((run) => (run.headline_summary || []).map((item) => item.name)))];
    const kpiRows = kpiNames
      .map((name) => {
        const values = payload.runs.map((run) => (run.headline_summary || []).find((item) => item.name === name)?.last_value);
        return `<tr><td>${escapeHtml(name)}</td>${values.map((value) => `<td class="numeric">${formatNumber(value)}</td>`).join("")}</tr>`;
      })
      .join("");
    output.innerHTML = `
      <section class="section">
        <div class="section-head"><h2>Headline comparison</h2><span class="hint">${payload.runs.length} runs</span></div>
        <div class="chart-grid">${charts || `<p class="hint">No shared headline series.</p>`}</div>
      </section>
      <section class="section two-column">
        <div class="panel">
          <div class="panel-head"><h2>Selection differences</h2></div>
          <div class="table-wrap"><table><thead><tr><th>Control</th>${payload.runs.map((run) => `<th>${escapeHtml(run.name)}</th>`).join("")}</tr></thead><tbody>${inputRows || `<tr><td colspan="${payload.runs.length + 1}">No explicit selections.</td></tr>`}</tbody></table></div>
        </div>
        <div class="panel">
          <div class="panel-head"><h2>Latest headline values</h2></div>
          <div class="table-wrap"><table><thead><tr><th>Series</th>${payload.runs.map((run) => `<th>${escapeHtml(run.name)}</th>`).join("")}</tr></thead><tbody>${kpiRows || `<tr><td colspan="${payload.runs.length + 1}">No headline values.</td></tr>`}</tbody></table></div>
        </div>
      </section>`;
  } catch (error) {
    output.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
  }
}

async function loadValidation() {
  const container = $("#validation-output");
  container.innerHTML = `<p class="hint">Loading validation evidence…</p>`;
  try {
    const payloads = await Promise.all(state.artifacts.map((artifact) => request(`validation/${artifact.version}`)));
    container.innerHTML = payloads
      .map((payload) => {
        const summary = payload.summary;
        const comparison = summary?.comparison || {};
        const tone = summary?.equivalence_status === "pass" ? "good" : payload.available ? "warn" : "bad";
        const counts = ["comparable_output_count", "match_count", "mismatch_count", "non_comparable_count"]
          .filter((key) => comparison[key] !== null && comparison[key] !== undefined)
          .map((key) => `<div><dt>${escapeHtml(key.replaceAll("_", " "))}</dt><dd>${formatNumber(comparison[key])}</dd></div>`)
          .join("");
        const stages = summary?.stages
          ? `<details><summary>Stage summaries</summary><pre>${escapeHtml(JSON.stringify(summary.stages, null, 2))}</pre></details>`
          : "";
        const notes = summary?.notes?.length
          ? `<ul class="note-list">${summary.notes.map((note) => `<li>${escapeHtml(note)}</li>`).join("")}</ul>`
          : "";
        return `
          <article class="panel validation-card">
            <div class="panel-head">
              <div><h2>FABLE ${escapeHtml(payload.version)}</h2><p class="hint">${escapeHtml(summary?.evidence_status || payload.message || "")}</p></div>
              ${pill(summary?.equivalence_status || (payload.available ? "available" : "unavailable"), tone)}
            </div>
            ${counts ? `<dl class="metric-row validation-counts">${counts}</dl>` : ""}
            ${notes}${stages}
            <div class="table-wrap compact-table"><table><thead><tr><th>File</th><th>State</th><th>Size</th></tr></thead><tbody>
              ${Object.entries(payload.files || {})
                .map(([name, info]) => `<tr><td>${escapeHtml(name)}</td><td>${info.exists ? "present" : "missing"}</td><td class="numeric">${formatBytes(info.size_bytes)}</td></tr>`)
                .join("")}
            </tbody></table></div>
          </article>`;
      })
      .join("");
  } catch (error) {
    container.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
  }
}

async function loadArtifacts() {
  const container = $("#artifacts-output");
  const bundles = $("#bundles-output");
  container.innerHTML = `<p class="hint">Loading artifacts…</p>`;
  try {
    const [artifacts, bundlePayloads] = await Promise.all([request("artifacts"), request("scenario-bundles")]);
    state.artifacts = artifacts;
    container.innerHTML = artifacts
      .map((artifact) => {
        const counts = artifact.summary?.counts;
        const fileRows = Object.entries(artifact.files)
          .map(
            ([name, info]) => `
            <tr>
              <td>${escapeHtml(name)}</td>
              <td>${info.exists ? "present" : "missing"}</td>
              <td class="numeric">${formatBytes(info.size_bytes)}</td>
              <td class="path-cell" title="${escapeHtml(info.path)}">${escapeHtml(info.path)}</td>
            </tr>`,
          )
          .join("");
        const canMaterialize = !artifact.files.generated_model.exists && artifact.files.compressed_model.exists;
        return `
          <article class="panel artifact-card">
            <div class="panel-head">
              <div><h2>FABLE ${escapeHtml(artifact.version)}</h2><p class="hint">${escapeHtml(artifact.model_source || "no model")} model · ${artifact.can_prepare ? "preparable" : "missing files"}</p></div>
              <div class="button-row">
                ${canMaterialize ? `<button class="button ghost small" type="button" data-materialize="${escapeHtml(artifact.version)}">Materialize model</button>` : ""}
                ${counts ? pill(`${counts.output_tables} tables`, "muted") : ""}
              </div>
            </div>
            <div class="table-wrap compact-table"><table><thead><tr><th>Artifact</th><th>State</th><th>Size</th><th>Path</th></tr></thead><tbody>${fileRows}</tbody></table></div>
          </article>`;
      })
      .join("");
    container.querySelectorAll("[data-materialize]").forEach((button) => {
      button.addEventListener("click", async () => {
        button.disabled = true;
        try {
          await request(`models/${button.dataset.materialize}/materialize`, { method: "POST" });
          toast("Generated model materialized", "good");
          await refreshArtifacts();
          await loadArtifacts();
        } catch (error) {
          toast(error.message, "bad");
          button.disabled = false;
        }
      });
    });

    bundles.innerHTML = `
      <div class="section-head"><h2>Scenario bundles</h2><span class="hint">Tracked examples under <code>examples/scenario-bundles/</code></span></div>
      ${
        bundlePayloads.length
          ? `<div class="card-grid">${bundlePayloads
              .map(
                (bundle) => `
              <article class="version-card">
                <div class="card-top"><div><h3>${escapeHtml(bundle.bundle_id || bundle.name)}</h3><p class="hint">${escapeHtml(bundle.name)}</p></div>${pill(`FABLE ${bundle.workbook_version || "?"}`, "muted")}</div>
                ${bundle.error ? `<p class="error-text">${escapeHtml(bundle.error)}</p>` : `<p>${escapeHtml(bundle.description || "")}</p><div class="chip-row">${(bundle.scenarios || []).map((scenario) => `<span class="chip"><b>${escapeHtml(scenario.scenario_id)}</b>${escapeHtml(scenario.label || "")}</span>`).join("")}</div>`}
              </article>`,
              )
              .join("")}</div>`
          : `<p class="hint">No scenario bundles found.</p>`
      }`;
  } catch (error) {
    container.innerHTML = `<p class="error-text">${escapeHtml(error.message)}</p>`;
  }
}

function setupAsk() {
  const enabled = Boolean(state.agent?.enabled);
  const button = $("#assistant-open");
  button.hidden = !enabled;
  if (!enabled) {
    $("#ask-panel").hidden = true;
    return;
  }
  const model = state.agent.model ? String(state.agent.model).split("/").pop() : "default model";
  $("#ask-model").textContent = state.agent.available ? model : "opencode unavailable";
  if (!state.agent.available) {
    $("#ask-input").disabled = true;
    $("#ask-send").disabled = true;
    $("#ask-status").textContent = "opencode is not on the service PATH";
  }
  renderAskContext();
  renderAskSessions();
}

function renderAskContext() {
  const select = $("#ask-run");
  if (!select) return;
  const current = state.ask.runId || select.value;
  select.innerHTML =
    `<option value="">No run context</option>` +
    state.runs
      .map(
        (run) =>
          `<option value="${escapeHtml(run.run_id)}">${escapeHtml(run.name)} · FABLE ${escapeHtml(run.version)}</option>`,
      )
      .join("");
  if (current && state.runs.some((run) => run.run_id === current)) {
    select.value = current;
  }
}

function renderAskSessions() {
  const list = $("#ask-session-list");
  if (!list) return;
  const query = String($("#ask-search")?.value || "").trim().toLowerCase();
  const chats = state.chats.filter(
    (chat) =>
      (state.ask.showArchived || !chat.archived) &&
      (!query ||
        String(chat.title || "").toLowerCase().includes(query) ||
        String(chat.preview || "").toLowerCase().includes(query)),
  );
  if (!chats.length) {
    list.innerHTML = `<p class="ask-sessions-empty">${state.chats.length ? "No chats match this filter." : "No saved chats yet. Send a message to create one."}</p>`;
    return;
  }
  list.innerHTML = chats
    .map(
      (chat) => `
      <div class="ask-session ${chat.chat_id === state.ask.chatId ? "active" : ""} ${chat.archived ? "archived" : ""}">
        <button class="ask-session-main" type="button" data-chat-id="${escapeHtml(chat.chat_id)}">
          <strong>${chat.pinned ? "★ " : ""}${escapeHtml(chat.title || "Chat")}</strong>
          <small>${escapeHtml(chat.preview || "")} · ${formatDate(chat.updated_at)}</small>
        </button>
        <div class="ask-session-actions">
          <button class="ask-session-icon ${chat.pinned ? "pinned" : ""}" type="button" data-pin-chat="${escapeHtml(chat.chat_id)}" title="${chat.pinned ? "Unpin" : "Pin"} chat" aria-label="${chat.pinned ? "Unpin" : "Pin"} chat">★</button>
          <button class="ask-session-icon" type="button" data-rename-chat="${escapeHtml(chat.chat_id)}" title="Rename chat" aria-label="Rename chat">✎</button>
          <button class="ask-session-icon" type="button" data-archive-chat="${escapeHtml(chat.chat_id)}" title="${chat.archived ? "Unarchive" : "Archive"} chat" aria-label="${chat.archived ? "Unarchive" : "Archive"} chat">▣</button>
          <button class="ask-session-icon" type="button" data-delete-chat="${escapeHtml(chat.chat_id)}" title="Delete chat" aria-label="Delete chat">×</button>
        </div>
      </div>`,
    )
    .join("");
  list.querySelectorAll("[data-chat-id]").forEach((button) => {
    button.addEventListener("click", () => loadChat(button.dataset.chatId));
  });
  list.querySelectorAll("[data-pin-chat]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      togglePinChat(button.dataset.pinChat);
    });
  });
  list.querySelectorAll("[data-rename-chat]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      renameAskChat(button.dataset.renameChat);
    });
  });
  list.querySelectorAll("[data-archive-chat]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleArchiveChat(button.dataset.archiveChat);
    });
  });
  list.querySelectorAll("[data-delete-chat]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      deleteAskChat(button.dataset.deleteChat);
    });
  });
}

function toggleAskSessions() {
  const panel = $("#ask-sessions");
  panel.hidden = !panel.hidden;
  $("#ask-history").setAttribute("aria-expanded", panel.hidden ? "false" : "true");
}

function renderChatMessages(messages) {
  const log = $("#ask-log");
  log.replaceChildren();
  if (!messages?.length) {
    const hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent =
      "New conversation. Ask about a saved run, a headline series, validation evidence, or where an artifact lives. Press Enter to send, Shift+Enter for a newline.";
    log.append(hint);
    return;
  }
  for (const message of messages) {
    const role = message.role === "user" ? "user" : message.role === "error" ? "error" : "agent";
    const content = role === "error" ? `Assistant unavailable: ${message.content}` : message.content;
    const node = appendAskMessage(role, content, { markdown: true });
    if (Array.isArray(message.actions) && message.actions.length) {
      const row = document.createElement("div");
      row.className = "ask-actions";
      for (const action of message.actions) {
        const chip = document.createElement("span");
        chip.className = "ask-action";
        chip.textContent = `${action.tool}${action.summary ? `: ${action.summary}` : ""}`;
        row.append(chip);
      }
      node.append(row);
    }
  }
}

async function loadChat(chatId, { silent = false } = {}) {
  if (!chatId) return;
  try {
    const chat = await request(`chats/${encodeURIComponent(chatId)}`);
    state.ask.chatId = chat.chat_id;
    state.ask.session = chat.agent_session || null;
    state.ask.runId = chat.run_id || null;
    state.ask.title = chat.title;
    try {
      localStorage.setItem("fable-portal-chat", chat.chat_id);
    } catch {
      /* localStorage can be unavailable in private contexts */
    }
    renderChatMessages(chat.messages || []);
    renderAskContext();
    renderAskSessions();
    if (chat.run_id) $("#ask-run").value = chat.run_id;
    if (!silent) {
      $("#ask-sessions").hidden = true;
      $("#ask-history").setAttribute("aria-expanded", "false");
      $("#ask-input").focus();
    }
  } catch (error) {
    if (!silent) toast(error.message, "bad");
  }
}

async function restoreChat() {
  if (!state.agent?.enabled || !state.chats.length) return;
  let remembered = null;
  try {
    remembered = localStorage.getItem("fable-portal-chat");
  } catch {
    /* localStorage can be unavailable in private contexts */
  }
  const visible = state.chats.filter((chat) => !chat.archived);
  const target =
    visible.find((chat) => chat.chat_id === remembered) ||
    visible[0] ||
    state.chats.find((chat) => chat.chat_id === remembered);
  if (target) await loadChat(target.chat_id, { silent: true });
}

async function refreshChats() {
  try {
    state.chats = await request("chats?include_archived=true");
    renderAskSessions();
  } catch {
    /* keep the current list */
  }
}

async function renameAskChat(chatId) {
  const chat = state.chats.find((item) => item.chat_id === chatId);
  if (!chat) return;
  const title = window.prompt("Rename chat", chat.title || "Chat");
  if (!title || !title.trim()) return;
  try {
    const updated = await request(`chats/${encodeURIComponent(chatId)}`, {
      method: "PATCH",
      body: JSON.stringify({ title: title.trim() }),
    });
    if (state.ask.chatId === chatId) state.ask.title = updated.title;
    await refreshChats();
  } catch (error) {
    toast(error.message, "bad");
  }
}

async function togglePinChat(chatId) {
  const chat = state.chats.find((item) => item.chat_id === chatId);
  if (!chat) return;
  try {
    await request(`chats/${encodeURIComponent(chatId)}`, {
      method: "PATCH",
      body: JSON.stringify({ pinned: !chat.pinned }),
    });
    await refreshChats();
  } catch (error) {
    toast(error.message, "bad");
  }
}

async function toggleArchiveChat(chatId) {
  const chat = state.chats.find((item) => item.chat_id === chatId);
  if (!chat) return;
  try {
    await request(`chats/${encodeURIComponent(chatId)}`, {
      method: "PATCH",
      body: JSON.stringify({ archived: !chat.archived }),
    });
    await refreshChats();
  } catch (error) {
    toast(error.message, "bad");
  }
}

function exportAskChat() {
  if (!state.ask.chatId) {
    $("#ask-status").textContent = "Open or create a chat before exporting.";
    return;
  }
  window.open(`api/chats/${encodeURIComponent(state.ask.chatId)}/export.md`, "_blank", "noopener");
}

async function deleteAskChat(chatId) {
  try {
    await request(`chats/${encodeURIComponent(chatId)}`, { method: "DELETE" });
    if (state.ask.chatId === chatId) {
      state.ask.chatId = null;
      state.ask.session = null;
      state.ask.title = "New chat";
      try {
        localStorage.removeItem("fable-portal-chat");
      } catch {
        /* localStorage can be unavailable in private contexts */
      }
      renderChatMessages([]);
    }
    await refreshChats();
  } catch (error) {
    toast(error.message, "bad");
  }
}

function openAsk(runId = null) {
  if (!state.agent?.enabled) return;
  const panel = $("#ask-panel");
  panel.hidden = false;
  $("#assistant-open").setAttribute("aria-expanded", "true");
  renderAskContext();
  renderAskSessions();
  if (runId) {
    state.ask.runId = runId;
    $("#ask-run").value = runId;
  } else if (state.activeRun?.run_id) {
    state.ask.runId = state.activeRun.run_id;
    $("#ask-run").value = state.activeRun.run_id;
  }
  $("#ask-input").focus();
}

function closeAsk() {
  $("#ask-panel").hidden = true;
  $("#assistant-open").setAttribute("aria-expanded", "false");
  $("#assistant-open").focus();
}

async function newAskChat() {
  if (state.ask.busy) return;
  if (!state.agent?.enabled) return;
  state.ask.chatId = null;
  state.ask.session = null;
  state.ask.runId = $("#ask-run")?.value || state.activeRun?.run_id || null;
  state.ask.title = "New chat";
  try {
    localStorage.removeItem("fable-portal-chat");
  } catch {
    /* localStorage can be unavailable in private contexts */
  }
  renderChatMessages([]);
  $("#ask-status").textContent = "";
  $("#ask-input").disabled = !state.agent.available;
  $("#ask-send").disabled = !state.agent.available;
  renderAskSessions();
  $("#ask-input").focus();
}

async function createAskChat() {
  const runId = $("#ask-run")?.value || state.activeRun?.run_id || null;
  const chat = await request("chats", {
    method: "POST",
    body: JSON.stringify({ run_id: runId }),
  });
  state.ask.chatId = chat.chat_id;
  state.ask.session = null;
  state.ask.runId = chat.run_id || null;
  state.ask.title = chat.title || "New chat";
  try {
    localStorage.setItem("fable-portal-chat", chat.chat_id);
  } catch {
    /* localStorage can be unavailable in private contexts */
  }
  if (chat.run_id) $("#ask-run").value = chat.run_id;
  const summary = {
    chat_id: chat.chat_id,
    title: chat.title || "New chat",
    created_at: chat.created_at,
    updated_at: chat.updated_at,
    message_count: 0,
    preview: "",
    agent_session: null,
    run_id: chat.run_id || null,
    pinned: false,
    archived: false,
  };
  state.chats = [summary, ...state.chats.filter((item) => item.chat_id !== chat.chat_id)];
  renderAskSessions();
  return chat;
}

function appendAskMessage(role, content, { markdown = false } = {}) {
  const log = $("#ask-log");
  log.querySelector(".hint")?.remove();
  const node = document.createElement("div");
  node.className = `ask-msg ${role}`;
  if (markdown) {
    node.innerHTML = renderMarkdown(content);
  } else {
    node.textContent = content;
  }
  log.append(node);
  log.scrollTop = log.scrollHeight;
  return node;
}

async function ensureAskChat() {
  if (state.ask.chatId) return state.ask.chatId;
  const chat = await createAskChat();
  return chat.chat_id;
}

async function sendAsk(message) {
  if (!state.agent?.enabled || state.ask.busy) return;
  if (!state.agent.available) {
    $("#ask-status").textContent = "The assistant process is not available.";
    return;
  }
  const prompt = String(message ?? "").trim();
  if (!prompt) return;
  let chatId = null;
  try {
    chatId = await ensureAskChat();
  } catch (error) {
    $("#ask-status").textContent = `Could not create a chat session: ${error.message}`;
    return;
  }
  if (!chatId) {
    $("#ask-status").textContent = "Could not create a chat session.";
    return;
  }
  appendAskMessage("user", prompt, { markdown: true });
  $("#ask-input").value = "";
  const thinking = appendAskMessage("agent", "thinking…");
  thinking.classList.add("thinking");
  state.ask.busy = true;
  $("#ask-send").disabled = true;
  $("#ask-new").disabled = true;
  $("#ask-status").textContent = "Grounding and running the local assistant…";
  try {
    const payload = await request("assistant", {
      method: "POST",
      body: JSON.stringify({
        message: prompt,
        chat_id: chatId,
        session: state.ask.session,
        run_id: $("#ask-run").value || null,
      }),
    });
    state.ask.session = payload.session || state.ask.session;
    if (payload.chat) {
      state.ask.title = payload.chat.title || state.ask.title;
      const index = state.chats.findIndex((item) => item.chat_id === payload.chat.chat_id);
      if (index >= 0) state.chats[index] = payload.chat;
      else state.chats.unshift(payload.chat);
      renderAskSessions();
    }
    thinking.remove();
    const reply = appendAskMessage("agent", payload.response || "(no reply)", { markdown: true });
    if (Array.isArray(payload.actions) && payload.actions.length) {
      const row = document.createElement("div");
      row.className = "ask-actions";
      for (const action of payload.actions) {
        const chip = document.createElement("span");
        chip.className = "ask-action";
        chip.textContent = `${action.tool}${action.summary ? `: ${action.summary}` : ""}`;
        chip.title = chip.textContent;
        row.append(chip);
      }
      reply.append(row);
    }
    $("#ask-status").textContent = "";
  } catch (error) {
    thinking.remove();
    appendAskMessage("error", `Assistant unavailable: ${error.message}`);
    $("#ask-status").textContent = "";
    await refreshChats();
  } finally {
    state.ask.busy = false;
    $("#ask-send").disabled = false;
    $("#ask-new").disabled = false;
    $("#ask-input").focus();
    $("#ask-log").scrollTop = $("#ask-log").scrollHeight;
  }
}

function bindEvents() {
  $$(".nav-tab").forEach((button) => {
    button.addEventListener("click", () => showPage(button.dataset.page));
  });
  $$("[data-go]").forEach((button) => {
    button.addEventListener("click", () => showPage(button.dataset.go));
  });
  window.addEventListener("hashchange", () => showPage(location.hash.replace("#", "") || "overview"));
  $("#overview-refresh").addEventListener("click", () => refreshArtifacts().catch((error) => toast(error.message, "bad")));
  $("#results-refresh").addEventListener("click", () => loadRuns());
  $("#artifacts-refresh").addEventListener("click", () => loadArtifacts());
  $("#prepare-model").addEventListener("click", () => prepareModel());
  $("#run-scenario").addEventListener("click", () => runScenario());
  $("#reset-controls").addEventListener("click", () => resetControls());
  $("#workbench-version").addEventListener("change", () => {
    state.activeVersion = $("#workbench-version").value;
    loadWorkbench();
  });
  $("#table-mode").addEventListener("change", updateTableMode);
  $("#tables-all").addEventListener("click", () => {
    $$("#table-select option").forEach((option) => {
      option.selected = true;
    });
  });
  $("#tables-none").addEventListener("click", () => {
    $$("#table-select option").forEach((option) => {
      option.selected = false;
    });
  });
  $("#compare-button").addEventListener("click", () => compareRuns());
  $("#help-button").addEventListener("click", () => $("#help-dialog").showModal());
  $("#help-close").addEventListener("click", () => $("#help-dialog").close());
  $("#help-dialog").addEventListener("click", (event) => {
    if (event.target === $("#help-dialog")) $("#help-dialog").close();
  });
  $("#assistant-open").addEventListener("click", () => {
    if ($("#ask-panel").hidden) openAsk();
    else closeAsk();
  });
  $("#ask-close").addEventListener("click", closeAsk);
  $("#ask-history").addEventListener("click", toggleAskSessions);
  $("#ask-new").addEventListener("click", newAskChat);
  $("#ask-export").addEventListener("click", exportAskChat);
  $("#ask-search").addEventListener("input", () => renderAskSessions());
  $("#ask-show-archived").addEventListener("change", (event) => {
    state.ask.showArchived = event.target.checked;
    renderAskSessions();
  });
  $("#ask-run").addEventListener("change", () => {
    state.ask.runId = $("#ask-run").value || null;
  });
  $("#ask-form").addEventListener("submit", (event) => {
    event.preventDefault();
    sendAsk($("#ask-input").value);
  });
  $("#ask-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      $("#ask-form").requestSubmit();
    }
  });
  $$("[data-ask-prompt]").forEach((button) => {
    button.addEventListener("click", () => sendAsk(button.dataset.askPrompt));
  });
  document.addEventListener("click", (event) => {
    const panel = $("#ask-panel");
    if (panel.hidden) return;
    if (!panel.contains(event.target) && !$("#assistant-open").contains(event.target)) {
      closeAsk();
    }
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !$("#ask-panel").hidden) {
      closeAsk();
      return;
    }
    if (event.target.matches("input, textarea, select")) return;
    if (event.key === "/") {
      event.preventDefault();
      const target = $(".page.active input:not([type=checkbox]):not([type=hidden]), .page.active textarea");
      target?.focus();
    }
    if (event.key === "r") showPage("results");
    if (event.key === "a") openAsk();
    const index = Number(event.key);
    if (index >= 1 && index <= PAGES.length) showPage(PAGES[index - 1]);
  });
}

bindEvents();
bootstrap();
