import * as THREE from "three";
import { OrbitControls } from "three/addons/OrbitControls.js";
import { escapeHtml, renderMarkdown } from "./markdown.js?v=p41a";

const API = new URL("api/", document.baseURI);
const PAGES = ["overview", "workbench", "results", "compare", "optimization", "validation", "artifacts"];

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
  optimization: {
    list: null,
    data: null,
    chart: null,
    mesh: null,
    selected: null,
    reference: null,
    brushes: [],
    sharedPresets: [],
    sharedFilter: "all",
    timelineFilter: { author: "", action: "", preset: "", window: "all" },
    filtered: [],
    pinned: [],
    pending: null,
  },
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
  history.replaceState(null, "", `${location.search || ""}#${page}`);
  if (page === "workbench") loadWorkbench();
  if (page === "results") loadRuns();
  if (page === "compare") renderComparePicker();
  if (page === "optimization") loadOptimization();
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


const OPTIMIZATION_CONTROL_LABELS = {
  land_scen: "Land",
  diet_scen: "Diet",
  fixtrade_scen: "Fix trade",
  livedens_scen: "Ruminant density",
  live_scen: "Livestock productivity",
  crop_scen: "Crop productivity",
  affor_scen: "Afforestation",
  scen_exports: "Exports",
  scen_imports: "Imports",
  gwp_scen: "GWP metric",
};

async function loadOptimization() {
  const status = $("#optimization-status");
  if (!status) return;
  try {
    renderOptimizationPresets();
    renderTimelinePresets();
    if (!state.optimization.list) {
      state.optimization.list = await request("optimization/frontiers");
    }
    await loadSharedOptimizationPresets();
    const select = $("#optimization-version");
    if (!state.optimization.list.length) {
      status.textContent = "no frontier";
      status.className = "pill warn";
      $("#pareto-meta").textContent = "No tracked exact frontier artifact was found under examples/optimization/.";
      $("#optimization-views").innerHTML = '<p class="hint">No decision views are available.</p>';
      return;
    }
    const params = new URLSearchParams(location.search);
    const previous = params.get("opt_version") || select.value || state.optimization.data?.version || "";
    select.innerHTML = state.optimization.list
      .map((item) => `<option value="${escapeHtml(item.version)}">FABLE ${escapeHtml(item.version)} · ${escapeHtml(item.title || "exact frontier")}</option>`)
      .join("");
    const chosen = state.optimization.list.some((item) => item.version === previous)
      ? previous
      : state.optimization.list[0].version;
    select.value = chosen;
    if (!state.optimization.data || state.optimization.data.version !== chosen) {
      await loadOptimizationFrontier(chosen);
    } else {
      drawOptimization();
    }
  } catch (error) {
    status.textContent = "unavailable";
    status.className = "pill bad";
    $("#pareto-meta").textContent = error.message;
  }
}

async function loadOptimizationFrontier(version) {
  const status = $("#optimization-status");
  status.textContent = "loading";
  status.className = "pill muted";
  const data = await request(`optimization/frontiers/${encodeURIComponent(version)}`);
  if (!data.points || !data.points.length) throw new Error("the frontier artifact has no points");
  state.optimization.data = data;
  state.optimization.selected = null;
  state.optimization.reference = null;
  state.optimization.brushes = [];
  state.optimization.pinned = [];
  state.optimization.filtered = [];
  $("#pareto-info").innerHTML = '<p class="hint">Select a point to inspect its exact objectives and selections.</p>';
  $("#pareto-load").disabled = true;
  $("#pareto-pin").disabled = true;
  $("#pareto-reference").disabled = true;
  $("#pareto-clear-reference").disabled = true;
  $("#pareto-clear-pins").disabled = true;
  $("#pareto-delta").innerHTML = "";
  $("#pareto-compare").innerHTML = "";
  initOptimizationControls(data);
  restoreOptimizationState();
  $("#pareto-meta").textContent =
    `${data.points.length} exact points · ${data.pareto_ids.length} unique Pareto objectives · ${formatDate(data.generated_at)}`;
  $("#pareto-count").textContent = `${data.points.length} pts`;
  renderOptimizationViews(data);
  ensureOptimizationChart();
  drawOptimization();
  status.textContent = "exact";
  status.className = "pill good";
}

function initOptimizationControls(data) {
  const dimensions = data.dimensions || [];
  const dimensionOptions = dimensions
    .map((dimension) => `<option value="${escapeHtml(dimension.key)}">${escapeHtml(dimension.label)}${dimension.unit ? ` (${escapeHtml(dimension.unit)})` : ""}</option>`)
    .join("");
  const fill = (id, options, preferred) => {
    const select = $(`#${id}`);
    if (!select) return;
    const previous = select.value;
    select.innerHTML = options;
    if (preferred && Array.from(select.options).some((option) => option.value === preferred)) {
      select.value = preferred;
    } else if (previous && Array.from(select.options).some((option) => option.value === previous)) {
      select.value = previous;
    }
  };
  fill("pareto-x", dimensionOptions, "food_total_kcal_feas");
  fill("pareto-y", dimensionOptions, "ghg_total_co2e");
  fill("pareto-z", dimensionOptions, "goal");
  fill("pareto-floor-dimension", dimensionOptions, "goal");
  const colours = [
    '<option value="front">Exact front</option>',
    '<option value="origin">Phase origin</option>',
    ...(data.controls || []).map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(OPTIMIZATION_CONTROL_LABELS[name] || name)}</option>`),
  ].join("");
  fill("pareto-colour", colours, "front");
  fill(
    "pareto-size",
    '<option value="uniform">Uniform</option>' + dimensionOptions,
    "uniform",
  );
}

function optimizationDimension(data, key) {
  return (data.dimensions || []).find((dimension) => dimension.key === key) || { key, label: key, direction: "max" };
}

function optimizationQuality(data, key, value) {
  const bounds = data.ranges?.[key];
  if (!Array.isArray(bounds) || bounds.length < 2) return 0.5;
  const low = Number(bounds[0]);
  const high = Number(bounds[1]);
  const number = Number(value);
  const normalized = Math.abs(high - low) <= 1e-12 ? 0.5 : Math.max(0, Math.min(1, (number - low) / (high - low)));
  return optimizationDimension(data, key).direction === "max" ? normalized : 1 - normalized;
}

function optimizationPointQuality(data, point, key) {
  if (key === "goal") return optimizationQuality(data, "goal", point.goal);
  return optimizationQuality(data, key, point.objectives?.[key]);
}

function optimizationControlValue(point, name) {
  return point.selections?.[name] ?? "—";
}

function optimizationHue(value) {
  const text = String(value);
  let hash = 0;
  for (let index = 0; index < text.length; index += 1) hash = (hash * 31 + text.charCodeAt(index)) % 360;
  return hash;
}

function optimizationSelectionSummary(point, limit = 6) {
  const names = ["land_scen", "diet_scen", "fixtrade_scen", "livedens_scen", "live_scen", "crop_scen", "affor_scen"];
  return names
    .map((name) => `${OPTIMIZATION_CONTROL_LABELS[name] || name}: ${optimizationControlValue(point, name)}`)
    .slice(0, limit)
    .join(" · ");
}

function renderOptimizationViews(data) {
  const container = $("#optimization-views");
  const views = data.views || {};
  const entries = [
    views.balanced,
    views.food_first,
    views.ghg_first,
    ...(views.food_first_views || []),
    ...(views.ghg_first_views || []),
  ].filter((view) => view && view.point_id);
  if (!entries.length) {
    container.innerHTML = '<p class="hint">No decision views are available in this artifact.</p>';
    $("#optimization-views-count").textContent = "0";
    return;
  }
  container.innerHTML = entries
    .map((view) => {
      const objectives = view.objectives || {};
      return `
        <article class="optimization-view-card" data-optimization-view="${escapeHtml(view.point_id)}" tabindex="0" role="button">
          <h3>${escapeHtml(view.label || "Decision view")}</h3>
          <p class="constraint">${escapeHtml(view.constraint || "")}</p>
          <div class="view-metrics">
            <div><span>Food</span><strong>${formatNumber(objectives.food_total_kcal_feas, 2)}</strong></div>
            <div><span>GHG</span><strong>${formatNumber(objectives.ghg_total_co2e, 2)}</strong></div>
          </div>
          <p class="view-selection">${escapeHtml(optimizationSelectionSummary({ selections: view.selections || {} }, 5))}</p>
          <button class="link-button" type="button" data-optimization-view="${escapeHtml(view.point_id)}">Inspect on the frontier</button>
        </article>`;
    })
    .join("");
  $("#optimization-views-count").textContent = `${entries.length} views`;
  container.querySelectorAll("[data-optimization-view]").forEach((element) => {
    element.addEventListener("click", () => selectOptimizationPoint(element.dataset.optimizationView));
    element.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        selectOptimizationPoint(element.dataset.optimizationView);
      }
    });
  });
}

function selectOptimizationPoint(pointId) {
  const point = state.optimization.data?.points?.find((item) => item.id === pointId);
  if (!point) return;
  renderOptimizationInfo(point);
  persistOptimizationState();
  const stage = $("#page-optimization");
  const grid = document.querySelector(".optimization-grid");
  if (stage && !stage.hidden && grid) {
    grid.scrollIntoView({ block: "start", behavior: "smooth" });
  }
}

function ensureOptimizationChart() {
  if (state.optimization.chart) return state.optimization.chart;
  const canvas = $("#pareto-canvas");
  if (!canvas) return null;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(canvas.clientWidth, Math.max(canvas.clientHeight, 1), false);
  renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, canvas.clientWidth / Math.max(canvas.clientHeight, 1), 0.1, 100);
  camera.position.set(2.8, 2.2, 2.9);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.target.set(0, 0, 0);
  controls.minDistance = 1.2;
  controls.maxDistance = 8;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x63705d, 1.5));
  const light = new THREE.DirectionalLight(0xffffff, 1.4);
  light.position.set(3, 5, 4);
  scene.add(light);
  const box = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(3.2, 3.2, 3.2)),
    new THREE.LineBasicMaterial({ color: 0x8fa68a, transparent: true, opacity: 0.55 }),
  );
  scene.add(box);
  const axes = buildOptimizationAxes();
  scene.add(axes);
  const marker = new THREE.Mesh(
    new THREE.SphereGeometry(0.075, 16, 12),
    new THREE.MeshBasicMaterial({ color: 0xf6d47a, wireframe: true, transparent: true, opacity: 0.95 }),
  );
  marker.visible = false;
  scene.add(marker);
  const referenceMarker = new THREE.Mesh(
    new THREE.SphereGeometry(0.08, 16, 12),
    new THREE.MeshBasicMaterial({ color: 0x1f6feb, wireframe: true, transparent: true, opacity: 0.95 }),
  );
  referenceMarker.visible = false;
  scene.add(referenceMarker);
  const raycaster = new THREE.Raycaster();
  const pointer = new THREE.Vector2();
  const tooltip = $("#pareto-tooltip");
  const hoverPoint = (event) => {
    const mesh = state.optimization.mesh;
    if (!mesh) return null;
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObject(mesh, false);
    if (!hits.length) return null;
    return { point: mesh.userData.points?.[hits[0].instanceId], event };
  };
  canvas.addEventListener("mousemove", (event) => {
    const hit = hoverPoint(event);
    if (!hit?.point || !tooltip) {
      if (tooltip) tooltip.hidden = true;
      canvas.style.cursor = "default";
      return;
    }
    const point = hit.point;
    const objectives = point.objectives || {};
    tooltip.innerHTML = `
      <strong>${escapeHtml(point.id)}</strong> · ${escapeHtml(point.origin || "exact")}<br>
      Food ${formatNumber(objectives.food_total_kcal_feas, 4)} kcal<br>
      GHG ${formatNumber(objectives.ghg_total_co2e, 4)} MtCO2e<br>
      Goal ${formatNumber(point.goal, 4)}`;
    tooltip.hidden = false;
    const rect = canvas.getBoundingClientRect();
    tooltip.style.left = `${Math.max(8, Math.min(rect.width - 180, event.clientX - rect.left + 14))}px`;
    tooltip.style.top = `${Math.max(8, Math.min(rect.height - 82, event.clientY - rect.top + 14))}px`;
    canvas.style.cursor = "pointer";
  });
  canvas.addEventListener("mouseleave", () => {
    if (tooltip) tooltip.hidden = true;
    canvas.style.cursor = "default";
  });
  canvas.addEventListener("click", (event) => {
    const mesh = state.optimization.mesh;
    if (!mesh) return;
    const rect = canvas.getBoundingClientRect();
    pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hits = raycaster.intersectObject(mesh, false);
    if (!hits.length) return;
    const point = mesh.userData.points?.[hits[0].instanceId];
    if (point) renderOptimizationInfo(point);
  });
  const chart = { renderer, scene, camera, controls, canvas, mesh: null, axes, marker, referenceMarker };
  window.addEventListener("resize", () => {
    if (!chart.canvas.clientWidth) return;
    renderer.setSize(chart.canvas.clientWidth, Math.max(chart.canvas.clientHeight, 1), false);
    camera.aspect = chart.canvas.clientWidth / Math.max(chart.canvas.clientHeight, 1);
    camera.updateProjectionMatrix();
  });
  state.optimization.chart = chart;
  updateOptimizationAxes(chart, { x: "X", y: "Y", z: "Z" });
  animateOptimization();
  return chart;
}

function buildOptimizationAxes() {
  const group = new THREE.Group();
  const origin = new THREE.Vector3(0, 0, 0);
  const end = 1.8;
  const axes = [
    [new THREE.Vector3(end, 0, 0), 0xc85555],
    [new THREE.Vector3(0, end, 0), 0x5f9f54],
    [new THREE.Vector3(0, 0, end), 0x4d7fc4],
  ];
  for (const [target, colour] of axes) {
    const geometry = new THREE.BufferGeometry().setFromPoints([origin, target]);
    const material = new THREE.LineBasicMaterial({ color: colour, transparent: true, opacity: 0.9 });
    group.add(new THREE.Line(geometry, material));
    const cone = new THREE.Mesh(
      new THREE.ConeGeometry(0.07, 0.2, 10),
      new THREE.MeshBasicMaterial({ color: colour }),
    );
    cone.position.copy(target);
    cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), target.clone().sub(origin).normalize());
    group.add(cone);
  }
  return group;
}

function updateOptimizationAxes(chart, labels) {
  chart.axisLabelText = labels;
  $("#pareto-axis-x").textContent = `X: ${labels.x || "X"}`;
  $("#pareto-axis-y").textContent = `Y: ${labels.y || "Y"}`;
  $("#pareto-axis-z").textContent = `Z: ${labels.z || "Z"}`;
}

function positionOptimizationAxisLabels() {
  // Axis labels use fixed stage anchors; the 3D orientation is controlled by OrbitControls.
}

function animateOptimization() {
  const chart = state.optimization.chart;
  if (!chart) return;
  chart.controls.update();
  chart.renderer.render(chart.scene, chart.camera);
  requestAnimationFrame(animateOptimization);
}


function updateOptimizationRangeNote(data, xKey, yKey, zKey) {
  const note = $("#pareto-ranges");
  if (!note) return;
  const parts = [["X", xKey], ["Y", yKey], ["Z", zKey]].map(([axis, key]) => {
    const dimension = optimizationDimension(data, key);
    const bounds = data.ranges?.[key] || [];
    const low = Number(bounds[0]);
    const high = Number(bounds[1]);
    const constant = Math.abs(high - low) <= 1e-6 * Math.max(1, Math.abs(low), Math.abs(high));
    const unit = dimension.unit ? ` ${dimension.unit}` : "";
    const direction = dimension.direction === "min" ? " · lower is better" : "";
    return `${axis} ${dimension.label}: ${formatNumber(low, 4)}–${formatNumber(high, 4)}${unit}${constant ? " · constant" : direction}`;
  });
  note.textContent = `${parts.join("  ·  ")}  ·  axes are normalized so higher is better`;
}

function optimizationLegendHtml(data, colourMode, filtered) {
  const swatch = (colour, label) => `<span><i style="background:${colour}"></i>${escapeHtml(label)}</span>`;
  let entries = [];
  if (colourMode === "front") {
    entries = [swatch("#2f7d4f", "exact front"), swatch("#9fb3c8", "dominated")];
  } else if (colourMode === "origin") {
    entries = [...new Set(filtered.map((entry) => entry.point.origin || "Other"))].map((origin) =>
      swatch(`hsl(${optimizationHue(origin)} 58% 48%)`, origin),
    );
  } else if ((data.controls || []).includes(colourMode)) {
    const values = [...new Set(filtered.map((entry) => optimizationControlValue(entry.point, colourMode)))].sort();
    entries = values.slice(0, 8).map((value) =>
      swatch(`hsl(${optimizationHue(value)} 55% 50%)`, value),
    );
    if (values.length > 8) entries.push(`<span>+${values.length - 8} more</span>`);
  } else {
    const label = optimizationDimension(data, colourMode).label || colourMode;
    entries = [swatch("hsl(209 68% 48%)", `${label}: better`), swatch("hsl(73 68% 48%)", "worse")];
  }
  return entries.join("");
}

function updateOptimizationSelectionMarker() {
  const chart = state.optimization.chart;
  const data = state.optimization.data;
  if (!chart?.marker || !data) return;
  const place = (marker, point) => {
    if (!marker) return;
    const visible = point && state.optimization.filtered.some((item) => item.id === point.id);
    if (!visible) {
      marker.visible = false;
      return;
    }
    const x = optimizationPointQuality(data, point, $("#pareto-x").value);
    const y = optimizationPointQuality(data, point, $("#pareto-y").value);
    const z = optimizationPointQuality(data, point, $("#pareto-z").value);
    marker.position.set((x - 0.5) * 3.2, (y - 0.5) * 3.2, (z - 0.5) * 3.2);
    marker.visible = true;
  };
  place(chart.marker, state.optimization.selected);
  place(chart.referenceMarker, state.optimization.reference);
}


const PARALLEL_AXES = [
  { key: "land_scen", label: "Land", kind: "control" },
  { key: "diet_scen", label: "Diet", kind: "control" },
  { key: "fixtrade_scen", label: "Fix trade", kind: "control" },
  { key: "live_scen", label: "Livestock", kind: "control" },
  { key: "crop_scen", label: "Crop", kind: "control" },
  { key: "affor_scen", label: "Afforestation", kind: "control" },
  { key: "food_total_kcal_feas", label: "Food", kind: "outcome" },
  { key: "ghg_total_co2e", label: "GHG", kind: "outcome" },
  { key: "goal", label: "Goal", kind: "outcome" },
];

function parallelValue(point, key) {
  return key === "goal" ? point.goal : point.objectives?.[key] ?? point.selections?.[key];
}

function shortenParallelLabel(value, limit = 13) {
  const text = String(value ?? "—");
  return text.length > limit ? `${text.slice(0, limit - 1)}…` : text;
}


const PARALLEL_TOP = 54;
const PARALLEL_PLOT_HEIGHT = 364;

function parallelAxisNormalized(data, key, value) {
  const axis = PARALLEL_AXES.find((item) => item.key === key);
  if (!axis) return 0.5;
  if (axis.kind === "control") {
    const values = [...new Set((data.points || []).map((point) => optimizationControlValue(point, key)))].sort();
    const index = values.indexOf(String(value));
    return values.length <= 1 || index < 0 ? 0.5 : index / (values.length - 1);
  }
  const bounds = data.ranges?.[key] || [0, 1];
  const low = Number(bounds[0]);
  const high = Number(bounds[1]);
  const number = Number(value);
  return Math.abs(high - low) <= 1e-12 ? 0.5 : 1 - (number - low) / (high - low);
}

function parallelBrushMatches(data, point) {
  const brushes = state.optimization.brushes || [];
  return brushes.every((brush) => {
    const normalized = parallelAxisNormalized(data, brush.axisKey, parallelValue(point, brush.axisKey));
    const low = Math.min(brush.start, brush.end);
    const high = Math.max(brush.start, brush.end);
    return normalized >= low - 1e-9 && normalized <= high + 1e-9;
  });
}

function updateParallelBrushLabel() {
  const label = $("#parallel-brush-label");
  const clear = $("#parallel-clear-brush");
  const brushes = state.optimization.brushes || [];
  if (!label) return;
  if (!brushes.length) {
    label.innerHTML = "";
    if (clear) clear.disabled = true;
    return;
  }
  label.innerHTML = brushes
    .map((brush, index) => {
      const axis = PARALLEL_AXES.find((item) => item.key === brush.axisKey);
      const low = Math.min(brush.start, brush.end);
      const high = Math.max(brush.start, brush.end);
      return `<span class="chip brush-chip">${escapeHtml(axis?.label || brush.axisKey)} ${(low * 100).toFixed(0)}–${(high * 100).toFixed(0)}%<button type="button" data-remove-brush="${index}" aria-label="Remove ${escapeHtml(axis?.label || brush.axisKey)} brush">×</button></span>`;
    })
    .join("");
  label.querySelectorAll("[data-remove-brush]").forEach((button) => {
    button.addEventListener("click", () => removeOptimizationBrush(Number(button.dataset.removeBrush)));
  });
  if (clear) clear.disabled = false;
}

function removeOptimizationBrush(index) {
  const brushes = state.optimization.brushes || [];
  if (!Number.isInteger(index) || index < 0 || index >= brushes.length) return;
  brushes.splice(index, 1);
  drawOptimization();
  persistOptimizationState();
  toast("Brush removed");
}

function beginParallelBrush(event, axisKey) {
  event.preventDefault();
  const svg = $("#parallel-chart");
  if (!svg) return;
  const rect = svg.getBoundingClientRect();
  const normalize = (clientY) => {
    const viewY = ((clientY - rect.top) * 460) / Math.max(rect.height, 1);
    return Math.max(0, Math.min(1, (viewY - PARALLEL_TOP) / PARALLEL_PLOT_HEIGHT));
  };
  const start = normalize(event.clientY);
  const brush = { axisKey, start, end: start };
  const additive = event.shiftKey;
  if (additive) {
    state.optimization.brushes = [...(state.optimization.brushes || []).filter((item) => item.axisKey !== axisKey), brush];
  } else {
    state.optimization.brushes = [brush];
  }
  drawParallelCoordinates();
  const onMove = (moveEvent) => {
    brush.end = normalize(moveEvent.clientY);
    drawParallelCoordinates();
  };
  const onUp = () => {
    document.removeEventListener("pointermove", onMove);
    if (Math.abs(brush.end - brush.start) < 0.01) {
      state.optimization.brushes = (state.optimization.brushes || []).filter((item) => item !== brush);
    }
    drawOptimization();
    toast((state.optimization.brushes || []).length ? "Parallel brushes applied" : "Brush cleared");
  };
  document.addEventListener("pointermove", onMove);
  document.addEventListener("pointerup", onUp, { once: true });
}

function clearOptimizationBrush() {
  state.optimization.brushes = [];
  drawOptimization();
  persistOptimizationState();
  toast("Parallel brushes cleared");
}

function drawParallelCoordinates() {
  const data = state.optimization.data;
  const svg = $("#parallel-chart");
  const count = $("#parallel-count");
  if (!data || !svg) return;
  const points = state.optimization.filtered || [];
  if (count) count.textContent = `${points.length} / ${data.points.length} points · ${PARALLEL_AXES.length} axes`;
  updateParallelBrushLabel();
  if (!points.length) {
    svg.innerHTML = '<text class="parallel-empty" x="500" y="230">No exact points pass the current filters.</text>';
    return;
  }
  const W = 1000;
  const H = 460;
  const left = 48;
  const right = 952;
  const top = 54;
  const bottom = 42;
  const plotHeight = H - top - bottom;
  const xFor = (index) => left + (index * (right - left)) / (PARALLEL_AXES.length - 1);
  const axisValues = {};
  for (const axis of PARALLEL_AXES) {
    if (axis.kind === "control") {
      axisValues[axis.key] = [...new Set((data.points || []).map((point) => optimizationControlValue(point, axis.key)))].sort();
    } else if (axis.key === "goal") {
      axisValues[axis.key] = data.ranges?.goal || [0, 1];
    } else {
      axisValues[axis.key] = data.ranges?.[axis.key] || [0, 1];
    }
  }
  const yFor = (axis, value) => top + parallelAxisNormalized(data, axis.key, value) * plotHeight;
  let markup = "";
  PARALLEL_AXES.forEach((axis, index) => {
    const x = xFor(index);
    const values = axisValues[axis.key];
    markup += `<line class="parallel-axis" x1="${x}" y1="${top}" x2="${x}" y2="${top + plotHeight}"></line>`;
    markup += `<text class="parallel-axis-label" x="${x}" y="22">${escapeHtml(axis.label)}</text>`;
    if (axis.kind === "control") {
      for (const value of values) {
        const y = yFor(axis, value);
        markup += `<text class="parallel-tick" x="${x}" y="${y + 3}">${escapeHtml(shortenParallelLabel(value))}</text>`;
      }
    } else {
      const high = Number(values[1]);
      const low = Number(values[0]);
      markup += `<text class="parallel-tick" x="${x}" y="${top - 8}">${escapeHtml(formatNumber(high, 4))}</text>`;
      markup += `<text class="parallel-tick" x="${x}" y="${top + plotHeight + 13}">${escapeHtml(formatNumber(low, 4))}</text>`;
    }
  });
  const selectedId = state.optimization.selected?.id;
  for (const point of points) {
    const coordinates = PARALLEL_AXES.map((axis, index) => {
      const value = parallelValue(point, axis.key);
      return `${xFor(index)},${yFor(axis, value)}`;
    }).join(" ");
    const classes = ["parallel-line", point.front ? "front" : "dominated"];
    if (point.id === selectedId) classes.push("selected");
    if (point.id === state.optimization.reference?.id) classes.push("reference");
    markup += `<polyline class="${classes.join(" ")}" points="${coordinates}" data-parallel-point="${escapeHtml(point.id)}"><title>${escapeHtml(point.id)} · ${escapeHtml(point.origin || "exact")} · Food ${formatNumber(point.objectives?.food_total_kcal_feas, 4)} · GHG ${formatNumber(point.objectives?.ghg_total_co2e, 4)} · Goal ${formatNumber(point.goal, 4)}</title></polyline>`;
  }
  for (const brush of state.optimization.brushes || []) {
    const axisIndex = PARALLEL_AXES.findIndex((axis) => axis.key === brush.axisKey);
    if (axisIndex >= 0) {
      const x = xFor(axisIndex);
      const low = Math.min(brush.start, brush.end);
      const high = Math.max(brush.start, brush.end);
      markup += `<rect class="parallel-brush" x="${x - 13}" y="${top + low * plotHeight}" width="26" height="${Math.max(2, (high - low) * plotHeight)}"></rect>`;
    }
  }
  PARALLEL_AXES.forEach((axis, index) => {
    const x = xFor(index);
    markup += `<rect class="parallel-brush-hit" x="${x - 13}" y="${top}" width="26" height="${plotHeight}" data-parallel-axis="${escapeHtml(axis.key)}"></rect>`;
  });
  svg.innerHTML = markup;
  svg.querySelectorAll("[data-parallel-point]").forEach((line) => {
    line.addEventListener("click", () => selectOptimizationPoint(line.dataset.parallelPoint));
  });
  svg.querySelectorAll("[data-parallel-axis]").forEach((element) => {
    element.addEventListener("pointerdown", (event) => beginParallelBrush(event, element.dataset.parallelAxis));
  });
}


function setOptimizationReference() {
  const point = state.optimization.selected;
  if (!point) return;
  state.optimization.reference = point;
  renderOptimizationDelta();
  updateOptimizationSelectionMarker();
  drawParallelCoordinates();
  persistOptimizationState();
  toast(`Reference set to ${point.id}`, "good");
}

function clearOptimizationReference() {
  state.optimization.reference = null;
  renderOptimizationDelta();
  updateOptimizationSelectionMarker();
  drawParallelCoordinates();
  persistOptimizationState();
  toast("Reference cleared");
}

function renderOptimizationDelta() {
  const container = $("#pareto-delta");
  if (!container) return;
  const selected = state.optimization.selected;
  const reference = state.optimization.reference;
  const referenceButton = $("#pareto-clear-reference");
  if (referenceButton) referenceButton.disabled = !reference;
  if (!selected || !reference) {
    container.innerHTML = reference
      ? `<p class="hint">Reference ${escapeHtml(reference.id)} is set. Select another point to compare.</p>`
      : '<p class="hint">Set one exact point as the reference to compare another point against it.</p>';
    return;
  }
  const fields = [
    ["Food", "food_total_kcal_feas", "max", "kcal"],
    ["GHG", "ghg_total_co2e", "min", "MtCO2e"],
    ["Land", "land_total_area", "min", "ha"],
    ["Goal", "goal", "min", ""],
  ];
  const cards = fields
    .map(([label, key, direction, unit]) => {
      const selectedValue = Number(key === "goal" ? selected.goal : selected.objectives?.[key]);
      const referenceValue = Number(key === "goal" ? reference.goal : reference.objectives?.[key]);
      const delta = selectedValue - referenceValue;
      const better = direction === "max" ? delta >= 0 : delta <= 0;
      const tone = Math.abs(delta) < 1e-9 ? "" : better ? "delta-good" : "delta-bad";
      return `<div class="delta-card"><span>${escapeHtml(label)}</span><strong class="${tone}">${formatSigned(delta, 4)}${unit ? ` ${escapeHtml(unit)}` : ""}</strong></div>`;
    })
    .join("");
  const controls = ["land_scen", "diet_scen", "fixtrade_scen", "live_scen", "crop_scen", "affor_scen", "livedens_scen"];
  const changes = controls
    .filter((name) => optimizationControlValue(selected, name) !== optimizationControlValue(reference, name))
    .map((name) => `<span class="chip"><b>${escapeHtml(OPTIMIZATION_CONTROL_LABELS[name] || name)}</b>${escapeHtml(optimizationControlValue(reference, name))} → ${escapeHtml(optimizationControlValue(selected, name))}</span>`)
    .join("");
  container.innerHTML = `
    <p class="hint">Selected <strong>${escapeHtml(selected.id)}</strong> vs reference <strong>${escapeHtml(reference.id)}</strong> · delta = selected − reference</p>
    <div class="delta-grid">${cards}</div>
    <div class="selection-list">${changes || '<span class="hint">No changed scenario controls in the displayed set.</span>'}</div>`;
}


const OPTIMIZATION_PRESETS_KEY = "fable-pyculator.optimization-presets.v1";

function loadOptimizationPresets() {
  try {
    const parsed = JSON.parse(localStorage.getItem(OPTIMIZATION_PRESETS_KEY) || "[]");
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((preset) => preset && typeof preset.name === "string" && preset.state && typeof preset.state === "object")
      .slice(0, 20);
  } catch {
    return [];
  }
}

function saveOptimizationPresets(presets) {
  try {
    localStorage.setItem(OPTIMIZATION_PRESETS_KEY, JSON.stringify(presets.slice(0, 20)));
    return true;
  } catch {
    toast("Could not write the local preset library.", "bad");
    return false;
  }
}

function collectOptimizationPreset() {
  const data = state.optimization.data;
  if (!data) return null;
  return {
    version: data.version,
    x: $("#pareto-x").value,
    y: $("#pareto-y").value,
    z: $("#pareto-z").value,
    colour: $("#pareto-colour").value,
    size: $("#pareto-size").value,
    floor_dimension: $("#pareto-floor-dimension").value,
    floor: Number($("#pareto-floor").value || 0),
    front: Boolean($("#pareto-front-only")?.checked),
    warning_free: Boolean($("#pareto-warning-free")?.checked),
    brushes: (state.optimization.brushes || []).map((brush) => ({
      axisKey: brush.axisKey,
      start: brush.start,
      end: brush.end,
    })),
    reference: state.optimization.reference?.id || null,
    point: state.optimization.selected?.id || null,
  };
}

function setOptimizationSelect(id, value) {
  const select = $(`#${id}`);
  if (!select || value === undefined || value === null) return;
  if (Array.from(select.options).some((option) => option.value === String(value))) {
    select.value = String(value);
  }
}

function applyOptimizationPreset(preset) {
  const data = state.optimization.data;
  if (!data || !preset?.state) return;
  if (preset.state.version && String(preset.state.version) !== String(data.version)) {
    toast(`Preset belongs to FABLE ${preset.state.version}; current frontier is ${data.version}.`, "warn");
    return;
  }
  const saved = preset.state;
  setOptimizationSelect("pareto-x", saved.x);
  setOptimizationSelect("pareto-y", saved.y);
  setOptimizationSelect("pareto-z", saved.z);
  setOptimizationSelect("pareto-colour", saved.colour);
  setOptimizationSelect("pareto-size", saved.size);
  setOptimizationSelect("pareto-floor-dimension", saved.floor_dimension);
  const floor = Math.max(0, Math.min(100, Number(saved.floor) || 0));
  const floorInput = $("#pareto-floor");
  if (floorInput) floorInput.value = String(floor);
  const floorOutput = $("#pareto-floor-value");
  if (floorOutput) floorOutput.textContent = floor <= 0 ? "all" : `≥ ${(floor / 100).toFixed(2)}`;
  const front = $("#pareto-front-only");
  if (front) front.checked = Boolean(saved.front);
  const warningFree = $("#pareto-warning-free");
  if (warningFree) warningFree.checked = Boolean(saved.warning_free);
  state.optimization.brushes = (Array.isArray(saved.brushes) ? saved.brushes : [])
    .filter(
      (brush) =>
        brush &&
        PARALLEL_AXES.some((axis) => axis.key === brush.axisKey) &&
        Number.isFinite(Number(brush.start)) &&
        Number.isFinite(Number(brush.end)),
    )
    .map((brush) => ({
      axisKey: brush.axisKey,
      start: Math.max(0, Math.min(1, Number(brush.start))),
      end: Math.max(0, Math.min(1, Number(brush.end))),
    }));
  state.optimization.reference = saved.reference
    ? data.points?.find((point) => point.id === saved.reference) || null
    : null;
  state.optimization.selected = null;
  if (saved.point) {
    const point = data.points?.find((item) => item.id === saved.point);
    if (point) renderOptimizationInfo(point);
  } else {
    $("#pareto-info").innerHTML = '<p class="hint">Select a point to inspect its exact objectives and selections.</p>';
    $("#pareto-load").disabled = true;
    $("#pareto-pin").disabled = true;
    $("#pareto-reference").disabled = true;
  }
  drawOptimization();
  renderOptimizationDelta();
  persistOptimizationState();
  toast(`Loaded preset ${preset.name}`, "good");
}

function renderOptimizationPresets() {
  const select = $("#optimization-preset");
  const count = $("#optimization-preset-count");
  const load = $("#optimization-preset-load");
  const remove = $("#optimization-preset-delete");
  const exportButton = $("#optimization-preset-export");
  const copyLink = $("#optimization-preset-copy-link");
  if (!select) return;
  const presets = loadOptimizationPresets();
  const previous = select.value;
  select.innerHTML = presets.length
    ? presets.map((preset, index) => `<option value="${index}">${escapeHtml(preset.name)}</option>`).join("")
    : '<option value="">No saved views</option>';
  if (previous && presets[Number(previous)]) select.value = previous;
  if (count) count.textContent = String(presets.length);
  if (load) load.disabled = !presets.length;
  if (remove) remove.disabled = !presets.length;
  if (exportButton) exportButton.disabled = !presets.length;
  if (copyLink) copyLink.disabled = !presets.length;
}

function saveOptimizationPreset() {
  const presetState = collectOptimizationPreset();
  if (!presetState) return;
  const input = $("#optimization-preset-name");
  const presets = loadOptimizationPresets();
  const name = (input?.value || "").trim() || `View ${presets.length + 1}`;
  const preset = { name: name.slice(0, 40), saved_at: new Date().toISOString(), state: presetState };
  const existing = presets.findIndex((item) => item.name === preset.name);
  if (existing >= 0) presets[existing] = preset;
  else presets.unshift(preset);
  if (!saveOptimizationPresets(presets)) return;
  renderOptimizationPresets();
  $("#optimization-preset").value = String(existing >= 0 ? existing : 0);
  if (input) input.value = preset.name;
  toast(`Saved view ${preset.name}`, "good");
}

function loadOptimizationPreset() {
  const select = $("#optimization-preset");
  const presets = loadOptimizationPresets();
  const preset = presets[Number(select?.value)];
  if (!preset) {
    toast("No saved view is selected.", "warn");
    return;
  }
  applyOptimizationPreset(preset);
}

function deleteOptimizationPreset() {
  const select = $("#optimization-preset");
  const presets = loadOptimizationPresets();
  const index = Number(select?.value);
  if (!presets[index]) return;
  const [removed] = presets.splice(index, 1);
  if (!saveOptimizationPresets(presets)) return;
  renderOptimizationPresets();
  toast(`Deleted view ${removed.name}`);
}


function normalizeImportedPreset(preset) {
  if (!preset || typeof preset.name !== "string" || !preset.state || typeof preset.state !== "object") return null;
  const name = preset.name.trim().slice(0, 40);
  if (!name) return null;
  const state = preset.state;
  const brushes = (Array.isArray(state.brushes) ? state.brushes : [])
    .filter(
      (brush) =>
        brush &&
        PARALLEL_AXES.some((axis) => axis.key === brush.axisKey) &&
        Number.isFinite(Number(brush.start)) &&
        Number.isFinite(Number(brush.end)),
    )
    .map((brush) => ({
      axisKey: brush.axisKey,
      start: Math.max(0, Math.min(1, Number(brush.start))),
      end: Math.max(0, Math.min(1, Number(brush.end))),
    }));
  return {
    name,
    saved_at: typeof preset.saved_at === "string" ? preset.saved_at : new Date().toISOString(),
    state: {
      version: String(state.version ?? "").slice(0, 16),
      x: String(state.x ?? "").slice(0, 60),
      y: String(state.y ?? "").slice(0, 60),
      z: String(state.z ?? "").slice(0, 60),
      colour: String(state.colour ?? "").slice(0, 60),
      size: String(state.size ?? "").slice(0, 60),
      floor_dimension: String(state.floor_dimension ?? "").slice(0, 60),
      floor: Math.max(0, Math.min(100, Number(state.floor) || 0)),
      front: Boolean(state.front),
      warning_free: Boolean(state.warning_free),
      brushes,
      reference: state.reference ? String(state.reference).slice(0, 20) : null,
      point: state.point ? String(state.point).slice(0, 20) : null,
    },
  };
}

function exportOptimizationPresets() {
  const presets = loadOptimizationPresets();
  if (!presets.length) {
    toast("There are no saved views to export.", "warn");
    return;
  }
  const payload = {
    schema: "fable-pyculator.optimization-presets",
    schema_version: 1,
    exported_at: new Date().toISOString(),
    presets,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fable-optimization-views.json";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  toast(`Exported ${presets.length} saved view${presets.length === 1 ? "" : "s"}`, "good");
}

async function importOptimizationPresets(event) {
  const input = event.target;
  const file = input.files?.[0];
  if (!file) return;
  try {
    const parsed = JSON.parse(await file.text());
    const candidates = Array.isArray(parsed) ? parsed : parsed?.presets;
    if (!Array.isArray(candidates)) throw new Error("JSON must contain a presets array");
    const existing = loadOptimizationPresets();
    const byName = new Map(existing.map((preset) => [preset.name, preset]));
    let imported = 0;
    for (const candidate of candidates) {
      const preset = normalizeImportedPreset(candidate);
      if (!preset) continue;
      byName.set(preset.name, preset);
      imported += 1;
    }
    if (!imported) throw new Error("no valid presets were found");
    const merged = Array.from(byName.values()).slice(0, 20);
    if (!saveOptimizationPresets(merged)) return;
    renderOptimizationPresets();
    toast(`Imported ${imported} saved view${imported === 1 ? "" : "s"}`, "good");
  } catch (error) {
    toast(`Could not import presets: ${error.message}`, "bad");
  } finally {
    input.value = "";
  }
}


async function loadSharedOptimizationPresets() {
  try {
    const presets = await request("optimization/presets");
    state.optimization.sharedPresets = Array.isArray(presets) ? presets : [];
  } catch {
    state.optimization.sharedPresets = [];
  }
  renderSharedOptimizationPresets();
}

function renderSharedOptimizationPresets(selectedName = "") {
  const select = $("#optimization-shared-preset");
  const count = $("#optimization-shared-count");
  const summary = $("#optimization-shared-summary");
  const filter = $("#optimization-shared-filter");
  const load = $("#optimization-shared-load");
  const remove = $("#optimization-shared-delete");
  const mark = $("#optimization-shared-mark-reviewed");
  const exportButton = $("#optimization-shared-export");
  const exportCsv = $("#optimization-shared-export-csv");
  if (!select) return;
  const presets = state.optimization.sharedPresets || [];
  if (filter) filter.value = state.optimization.sharedFilter || "all";
  const filterValue = state.optimization.sharedFilter || "all";
  const drafts = presets.filter((preset) => preset.review_status !== "reviewed").length;
  const reviewed = presets.length - drafts;
  const visible = presets
    .map((preset, index) => ({ preset, index }))
    .filter(({ preset }) => filterValue === "all" || (filterValue === "draft" ? preset.review_status !== "reviewed" : preset.review_status === "reviewed"));
  select.innerHTML = visible.length
    ? visible.map(({ preset, index }) => {
        const author = preset.author ? ` · ${preset.author}` : "";
        const badge = preset.review_status === "reviewed" ? " · reviewed" : " · draft";
        return `<option value="${index}">${escapeHtml(preset.name + author + badge)}</option>`;
      }).join("")
    : `<option value="">${filterValue === "draft" ? "Review queue is clear" : "No shared views"}</option>`;
  if (selectedName) {
    const selected = visible.find(({ preset }) => preset.name === selectedName);
    if (selected) select.value = String(selected.index);
  }
  if (count) count.textContent = `${visible.length} / ${presets.length}`;
  if (summary) summary.textContent = `${drafts} draft · ${reviewed} reviewed`;
  if (load) load.disabled = !visible.length;
  if (remove) remove.disabled = !visible.length;
  if (mark) {
    const selected = select.value === "" ? null : presets[Number(select.value)];
    mark.disabled = !selected || selected.review_status === "reviewed";
  }
  if (exportButton) exportButton.disabled = !presets.length;
  if (exportCsv) exportCsv.disabled = !presets.length;
  renderSharedAudit(presets);
  renderSharedTimeline(presets);
  syncSharedPresetMetadata();
}

async function saveSharedOptimizationPreset() {
  const presetState = collectOptimizationPreset();
  if (!presetState) return;
  const input = $("#optimization-shared-preset-name");
  const presets = state.optimization.sharedPresets || [];
  const name = (input?.value || "").trim() || `Shared View ${presets.length + 1}`;
  const author = ($("#optimization-shared-author")?.value || "").trim().slice(0, 40);
  const note = ($("#optimization-shared-note")?.value || "").trim().slice(0, 200);
  const reviewStatus = $("#optimization-shared-review")?.value === "reviewed" ? "reviewed" : "draft";
  try {
    await request("optimization/presets", {
      method: "POST",
      body: JSON.stringify({
        name: name.slice(0, 40),
        state: presetState,
        author,
        note,
        review_status: reviewStatus,
      }),
    });
    await loadSharedOptimizationPresets();
    renderSharedOptimizationPresets(name.slice(0, 40));
    if (input) input.value = name.slice(0, 40);
    toast(`Saved shared view ${name.slice(0, 40)}`, "good");
  } catch (error) {
    toast(`Could not save shared view: ${error.message}`, "bad");
  }
}

function loadSharedOptimizationPreset() {
  const select = $("#optimization-shared-preset");
  const preset = select?.value === "" ? null : state.optimization.sharedPresets?.[Number(select?.value)];
  if (!preset) {
    toast("No shared view is selected.", "warn");
    return;
  }
  applyOptimizationPreset(preset);
}

async function deleteSharedOptimizationPreset() {
  const select = $("#optimization-shared-preset");
  const preset = select?.value === "" ? null : state.optimization.sharedPresets?.[Number(select?.value)];
  if (!preset) return;
  try {
    await request(`optimization/presets/${encodeURIComponent(preset.name)}`, { method: "DELETE" });
    await loadSharedOptimizationPresets();
    toast(`Deleted shared view ${preset.name}`);
  } catch (error) {
    toast(`Could not delete shared view: ${error.message}`, "bad");
  }
}


function syncSharedPresetMetadata() {
  const select = $("#optimization-shared-preset");
  const value = select?.value;
  const preset = value === "" || value === undefined ? null : state.optimization.sharedPresets?.[Number(value)];
  if (!preset) {
    const statePill = $("#optimization-shared-review-state");
    if (statePill) {
      statePill.textContent = "—";
      statePill.className = "pill muted";
    }
    const mark = $("#optimization-shared-mark-reviewed");
    if (mark) mark.disabled = true;
    renderSharedPresetHistory(null);
    return;
  }
  const author = $("#optimization-shared-author");
  const note = $("#optimization-shared-note");
  const review = $("#optimization-shared-review");
  if (author) author.value = preset.author || "";
  if (note) note.value = preset.note || "";
  if (review) review.value = preset.review_status === "reviewed" ? "reviewed" : "draft";
  const statePill = $("#optimization-shared-review-state");
  if (statePill) {
    statePill.textContent = preset.review_status === "reviewed" ? "reviewed" : "draft";
    statePill.className = preset.review_status === "reviewed" ? "pill good" : "pill warn";
  }
  const mark = $("#optimization-shared-mark-reviewed");
  if (mark) mark.disabled = preset.review_status === "reviewed";
  renderSharedPresetHistory(preset);
}

function renderSharedPresetHistory(preset) {
  const container = $("#optimization-shared-history");
  if (!container) return;
  const history = preset?.history || [];
  if (!history.length) {
    container.innerHTML = '<p class="hint">No history yet.</p>';
    return;
  }
  const entries = history
    .slice()
    .reverse()
    .map((event) => {
      const when = event.at ? new Date(event.at).toLocaleString() : "—";
      const author = event.author ? ` · ${escapeHtml(event.author)}` : "";
      const note = event.note ? `<br><span>${escapeHtml(event.note)}</span>` : "";
      return `<li><b>${escapeHtml(event.action)}</b> · ${escapeHtml(when)}${author}${note}</li>`;
    })
    .join("");
  container.innerHTML = `<ol>${entries}</ol>`;
}

async function markSharedOptimizationPresetReviewed() {
  const select = $("#optimization-shared-preset");
  const preset = select?.value === "" ? null : state.optimization.sharedPresets?.[Number(select?.value)];
  if (!preset || preset.review_status === "reviewed") return;
  try {
    await request("optimization/presets", {
      method: "POST",
      body: JSON.stringify({
        name: preset.name,
        state: preset.state,
        author: ($("#optimization-shared-author")?.value || preset.author || "").trim().slice(0, 40),
        note: preset.note || "",
        review_status: "reviewed",
      }),
    });
    await loadSharedOptimizationPresets();
    renderSharedOptimizationPresets(preset.name);
    toast(`Marked ${preset.name} reviewed`, "good");
  } catch (error) {
    toast(`Could not mark shared view reviewed: ${error.message}`, "bad");
  }
}


function renderSharedAudit(presets) {
  const container = $("#optimization-shared-audit");
  if (!container) return;
  if (!presets.length) {
    container.innerHTML = '<p class="hint">No shared presets loaded.</p>';
    return;
  }
  const rows = presets
    .map((preset) => {
      const latest = (preset.history || []).slice(-1)[0];
      const latestText = latest ? `${latest.action}${latest.at ? ` · ${formatDate(latest.at)}` : ""}` : "—";
      return `<tr><td>${escapeHtml(preset.name)}</td><td>${escapeHtml(preset.author || "—")}</td><td>${escapeHtml(preset.review_status || "draft")}</td><td>${escapeHtml(latestText)}</td><td>${(preset.history || []).length}</td></tr>`;
    })
    .join("");
  container.innerHTML = `<table><thead><tr><th>Name</th><th>Author</th><th>Status</th><th>Latest event</th><th>History</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function exportSharedOptimizationPresets() {
  const presets = state.optimization.sharedPresets || [];
  if (!presets.length) {
    toast("There are no shared presets to export.", "warn");
    return;
  }
  const payload = {
    schema: "fable-pyculator.shared-optimization-presets",
    schema_version: 1,
    exported_at: new Date().toISOString(),
    presets,
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fable-shared-optimization-presets.json";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  toast(`Exported ${presets.length} shared preset${presets.length === 1 ? "" : "s"}`, "good");
}


function sharedAuditEvents(presets) {
  return presets
    .flatMap((preset) =>
      (preset.history || []).map((event) => ({
        preset: preset.name,
        author: preset.author || event.author || "",
        review_status: preset.review_status || "draft",
        action: event.action,
        at: event.at,
        note: event.note || "",
      })),
    )
    .sort((left, right) => String(right.at).localeCompare(String(left.at)));
}

function renderSharedTimeline(presets) {
  const container = $("#optimization-shared-timeline");
  if (!container) return;
  const filter = state.optimization.timelineFilter;
  const allEvents = sharedAuditEvents(presets);
  renderReviewWorkload(presets);
  const authors = [...new Set(allEvents.map((event) => event.author).filter(Boolean))].sort();
  const presetNames = presets.map((preset) => preset.name).sort();
  const authorSelect = $("#optimization-timeline-author");
  const presetSelect = $("#optimization-timeline-preset");
  if (authorSelect) {
    authorSelect.innerHTML = '<option value="">All authors</option>' +
      authors.map((author) => `<option value="${escapeHtml(author)}">${escapeHtml(author)}</option>`).join("");
    authorSelect.value = authors.includes(filter.author) ? filter.author : "";
  }
  if (presetSelect) {
    presetSelect.innerHTML = '<option value="">All presets</option>' +
      presetNames.map((name) => `<option value="${escapeHtml(name)}">${escapeHtml(name)}</option>`).join("");
    presetSelect.value = presetNames.includes(filter.preset) ? filter.preset : "";
  }
  if (!authors.includes(filter.author)) filter.author = "";
  if (!presetNames.includes(filter.preset)) filter.preset = "";
  const windowMs = { "24h": 24 * 60 * 60 * 1000, "7d": 7 * 24 * 60 * 60 * 1000, "30d": 30 * 24 * 60 * 60 * 1000 };
  const now = Date.now();
  const events = allEvents
    .filter((event) => !filter.author || event.author === filter.author)
    .filter((event) => !filter.action || event.action === filter.action)
    .filter((event) => !filter.preset || event.preset === filter.preset)
    .filter((event) => {
      if (filter.window === "all") return true;
      const timestamp = Date.parse(event.at);
      return Number.isFinite(timestamp) && now - timestamp <= windowMs[filter.window];
    })
    .slice(0, 20);
  const count = $("#optimization-timeline-count");
  if (count) count.textContent = `${events.length} event${events.length === 1 ? "" : "s"}`;
  if (!events.length) {
    container.innerHTML = '<p class="hint">No review activity matches these filters.</p>';
    return;
  }
  const rows = events
    .map((event) => {
      const when = event.at ? formatDate(event.at) : "—";
      const author = event.author ? ` · ${escapeHtml(event.author)}` : "";
      const note = event.note ? ` — ${escapeHtml(event.note)}` : "";
      return `<li><b>${escapeHtml(event.preset)}</b> · ${escapeHtml(event.action)} · ${escapeHtml(when)}${author}${note}</li>`;
    })
    .join("");
  container.innerHTML = `<ol>${rows}</ol>`;
}

function renderReviewWorkload(presets) {
  const container = $("#optimization-review-workload");
  if (!container) return;
  const events = sharedAuditEvents(presets);
  if (!events.length) {
    container.innerHTML = '<p class="hint">No workload data.</p>';
    return;
  }
  const byAuthor = new Map();
  for (const event of events) {
    const author = event.author || "Unattributed";
    const entry = byAuthor.get(author) || { author, created: 0, updated: 0, reviewed: 0, total: 0, latest: "" };
    entry[event.action] = (entry[event.action] || 0) + 1;
    entry.total += 1;
    if (!entry.latest || String(event.at) > entry.latest) entry.latest = String(event.at);
    byAuthor.set(author, entry);
  }
  const rows = [...byAuthor.values()]
    .sort((left, right) => right.total - left.total || left.author.localeCompare(right.author))
    .map((entry) => {
      const author = entry.author === "Unattributed" ? "Unattributed" : entry.author;
      const attrs = entry.author === "Unattributed" ? "" : ` data-workload-author="${escapeHtml(entry.author)}"`;
      return `<tr${attrs}><td>${escapeHtml(author)}</td><td>${entry.created}</td><td>${entry.updated}</td><td>${entry.reviewed}</td><td>${entry.total}</td><td>${escapeHtml(formatDate(entry.latest))}</td></tr>`;
    })
    .join("");
  container.innerHTML = `<table><thead><tr><th>Author</th><th>Created</th><th>Updated</th><th>Reviewed</th><th>Total</th><th>Latest</th></tr></thead><tbody>${rows}</tbody></table>`;
  container.querySelectorAll("[data-workload-author]").forEach((row) => {
    row.addEventListener("click", () => {
      const author = row.dataset.workloadAuthor;
      state.optimization.timelineFilter.author = author;
      const select = $("#optimization-timeline-author");
      if (select) select.value = author;
      renderSharedTimeline(state.optimization.sharedPresets || []);
    });
  });
}

function exportSharedAuditCsv() {
  const presets = state.optimization.sharedPresets || [];
  const events = sharedAuditEvents(presets);
  if (!events.length) {
    toast("There is no shared review activity to export.", "warn");
    return;
  }
  const header = ["preset", "author", "review_status", "action", "at", "note"];
  const rows = events.map((event) => [event.preset, event.author, event.review_status, event.action, event.at, event.note]);
  const csv = [header, ...rows].map((row) => row.map(optimizationCsvCell).join(",")).join("\n") + "\n";
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "fable-shared-review-audit.csv";
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  toast(`Exported ${events.length} audit event${events.length === 1 ? "" : "s"}`, "good");
}


const TIMELINE_PRESETS_KEY = "fable-pyculator.timeline-presets.v1";

function loadTimelinePresets() {
  try {
    const parsed = JSON.parse(localStorage.getItem(TIMELINE_PRESETS_KEY) || "[]");
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((preset) => preset && typeof preset.name === "string" && preset.filter && typeof preset.filter === "object")
      .slice(0, 20);
  } catch {
    return [];
  }
}

function saveTimelinePresets(presets) {
  try {
    localStorage.setItem(TIMELINE_PRESETS_KEY, JSON.stringify(presets.slice(0, 20)));
    return true;
  } catch {
    toast("Could not write the saved timeline views.", "bad");
    return false;
  }
}

function renderTimelinePresets(selectedName = "") {
  const select = $("#optimization-timeline-preset");
  const load = $("#optimization-timeline-preset-load");
  const remove = $("#optimization-timeline-preset-delete");
  if (!select) return;
  const presets = loadTimelinePresets();
  select.innerHTML = presets.length
    ? presets.map((preset, index) => `<option value="${index}">${escapeHtml(preset.name)}</option>`).join("")
    : '<option value="">No saved timeline views</option>';
  if (selectedName) {
    const index = presets.findIndex((preset) => preset.name === selectedName);
    if (index >= 0) select.value = String(index);
  }
  if (load) load.disabled = !presets.length;
  if (remove) remove.disabled = !presets.length;
}

function applyTimelineFilter(filter) {
  state.optimization.timelineFilter = {
    author: String(filter?.author || ""),
    action: String(filter?.action || ""),
    preset: String(filter?.preset || ""),
    window: ["all", "24h", "7d", "30d"].includes(filter?.window) ? filter.window : "all",
  };
  $("#optimization-timeline-author").value = state.optimization.timelineFilter.author;
  $("#optimization-timeline-action").value = state.optimization.timelineFilter.action;
  $("#optimization-timeline-preset").value = state.optimization.timelineFilter.preset;
  $("#optimization-timeline-window").value = state.optimization.timelineFilter.window;
  renderSharedTimeline(state.optimization.sharedPresets || []);
}

function saveTimelinePreset() {
  const input = $("#optimization-timeline-preset-name");
  const presets = loadTimelinePresets();
  const name = (input?.value || "").trim() || `Timeline View ${presets.length + 1}`;
  const preset = {
    name: name.slice(0, 40),
    saved_at: new Date().toISOString(),
    filter: { ...state.optimization.timelineFilter },
  };
  const existing = presets.findIndex((item) => item.name === preset.name);
  if (existing >= 0) presets[existing] = preset;
  else presets.unshift(preset);
  if (!saveTimelinePresets(presets)) return;
  renderTimelinePresets(preset.name);
  if (input) input.value = preset.name;
  toast(`Saved timeline view ${preset.name}`, "good");
}

function loadTimelinePreset() {
  const select = $("#optimization-timeline-preset");
  const preset = loadTimelinePresets()[Number(select?.value)];
  if (!preset) {
    toast("No saved timeline view is selected.", "warn");
    return;
  }
  applyTimelineFilter(preset.filter);
  toast(`Loaded timeline view ${preset.name}`, "good");
}

function deleteTimelinePreset() {
  const select = $("#optimization-timeline-preset");
  const presets = loadTimelinePresets();
  const index = Number(select?.value);
  if (!presets[index]) return;
  const [removed] = presets.splice(index, 1);
  if (!saveTimelinePresets(presets)) return;
  renderTimelinePresets();
  toast(`Deleted timeline view ${removed.name}`);
}

function drawOptimization() {
  const chart = ensureOptimizationChart();
  const data = state.optimization.data;
  if (!chart || !data) return;
  const xKey = $("#pareto-x").value;
  const yKey = $("#pareto-y").value;
  const zKey = $("#pareto-z").value;
  const colourMode = $("#pareto-colour").value;
  const sizeKey = $("#pareto-size").value;
  const floorKey = $("#pareto-floor-dimension").value;
  const threshold = Number($("#pareto-floor").value) / 100;
  const frontOnly = $("#pareto-front-only").checked;
  const warningFree = $("#pareto-warning-free")?.checked;
  const filtered = data.points
    .map((point) => ({
      point,
      x: optimizationPointQuality(data, point, xKey),
      y: optimizationPointQuality(data, point, yKey),
      z: optimizationPointQuality(data, point, zKey),
      size: sizeKey === "uniform" ? 0.5 : optimizationPointQuality(data, point, sizeKey),
      floor: optimizationPointQuality(data, point, floorKey),
    }))
    .filter(
      (entry) =>
        (!frontOnly || entry.point.front) &&
        (!warningFree || !(entry.point.warnings || []).length) &&
        (threshold <= 0 || entry.floor >= threshold) &&
        parallelBrushMatches(data, entry.point),
    );
  clearOptimizationMesh();
  state.optimization.filtered = filtered.map((entry) => entry.point);
  if (!filtered.length) {
    $("#pareto-count").textContent = `0 / ${data.points.length}`;
    $("#pareto-info").innerHTML = '<p class="hint">No points pass the current filters. Lower the quality floor, remove a brush, or clear the front filter.</p>';
    drawParallelCoordinates();
    persistOptimizationState();
    chart.renderer.render(chart.scene, chart.camera);
    return;
  }
  const geometry = new THREE.SphereGeometry(0.045, 10, 8);
  const material = new THREE.MeshStandardMaterial({ roughness: 0.42, metalness: 0.08 });
  const mesh = new THREE.InstancedMesh(geometry, material, filtered.length);
  mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  const matrix = new THREE.Matrix4();
  const position = new THREE.Vector3();
  const scale = new THREE.Vector3();
  const quaternion = new THREE.Quaternion();
  const color = new THREE.Color();
  filtered.forEach((entry, index) => {
    position.set((entry.x - 0.5) * 3.2, (entry.y - 0.5) * 3.2, (entry.z - 0.5) * 3.2);
    const size = 0.55 + entry.size * 1.25;
    scale.set(size, size, size);
    matrix.compose(position, quaternion, scale);
    mesh.setMatrixAt(index, matrix);
    if (colourMode === "front") {
      color.set(entry.point.front ? 0x2f7d4f : 0x9fb3c8);
    } else if (colourMode === "origin") {
      color.setHSL(optimizationHue(entry.point.origin) / 360, 0.58, 0.48);
    } else if ((data.controls || []).includes(colourMode)) {
      color.setHSL(optimizationHue(optimizationControlValue(entry.point, colourMode)) / 360, 0.55, 0.5);
    } else {
      color.setHSL(0.58 - optimizationPointQuality(data, entry.point, colourMode) * 0.46, 0.68, 0.48);
    }
    mesh.setColorAt(index, color);
  });
  mesh.instanceMatrix.needsUpdate = true;
  if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
  mesh.userData.points = state.optimization.filtered;
  chart.scene.add(mesh);
  chart.mesh = mesh;
  state.optimization.mesh = mesh;
  const labels = Object.fromEntries((data.dimensions || []).map((dimension) => [dimension.key, dimension.label]));
  labels.goal = "Goal score";
  updateOptimizationAxes(chart, { x: labels[xKey] || xKey, y: labels[yKey] || yKey, z: labels[zKey] || zKey });
  $("#pareto-count").textContent = `${filtered.length} / ${data.points.length}`;
  updateOptimizationRangeNote(data, xKey, yKey, zKey);
  $("#pareto-legend").innerHTML = optimizationLegendHtml(data, colourMode, filtered) +
    `<span>${filtered.length} of ${data.points.length} exact points</span>`;
  updateOptimizationSelectionMarker();
  renderOptimizationDelta();
  drawParallelCoordinates();
  persistOptimizationState();
  chart.renderer.render(chart.scene, chart.camera);
}

function clearOptimizationMesh() {
  const chart = state.optimization.chart;
  if (chart?.mesh) {
    chart.scene.remove(chart.mesh);
    chart.mesh.geometry.dispose();
    chart.mesh.material.dispose();
    chart.mesh = null;
  }
  state.optimization.mesh = null;
}

function renderOptimizationInfo(point) {
  const data = state.optimization.data;
  if (!data) return;
  const dimensions = data.dimensions || [];
  const cards = dimensions
    .map((dimension) => {
      const value = dimension.key === "goal" ? point.goal : point.objectives?.[dimension.key];
      return `<div class="mini-card"><span>${escapeHtml(dimension.label)}</span><strong>${formatNumber(Number(value), 4)}</strong></div>`;
    })
    .join("");
  const selections = Object.entries(point.selections || {})
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([name, value]) => `<span class="chip"><b>${escapeHtml(OPTIMIZATION_CONTROL_LABELS[name] || name)}</b>${escapeHtml(value)}</span>`)
    .join("");
  const warnings = (point.warnings || []).length
    ? `<p class="hint">Provisional warnings: ${(point.warnings || []).map((warning) => `<code>${escapeHtml(warning)}</code>`).join(" ")}</p>`
    : "";
  $("#pareto-info").innerHTML = `
    <div class="mini-grid">${cards}</div>
    <p class="hint">${point.front ? "Exact Pareto member" : "Dominated exact point"} · ${escapeHtml(point.origin || "exact")} · ${escapeHtml(point.id)}</p>
    <div class="selection-list">${selections}</div>
    ${warnings}`;
  state.optimization.selected = point;
  $("#pareto-load").disabled = false;
  $("#pareto-pin").disabled = false;
  $("#pareto-reference").disabled = false;
  renderOptimizationDelta();
  updateOptimizationSelectionMarker();
  drawParallelCoordinates();
}

function pinOptimizationPoint() {
  const point = state.optimization.selected;
  if (!point) return;
  if (state.optimization.pinned.some((item) => item.id === point.id)) return;
  if (state.optimization.pinned.length >= 3) state.optimization.pinned.shift();
  state.optimization.pinned.push(point);
  renderOptimizationCompare();
  toast(`Pinned ${point.id}`);
}

function clearOptimizationPins() {
  state.optimization.pinned = [];
  renderOptimizationCompare();
}

function renderOptimizationCompare() {
  const pinned = state.optimization.pinned || [];
  const button = $("#pareto-clear-pins");
  if (button) button.disabled = pinned.length === 0;
  const container = $("#pareto-compare");
  if (!container) return;
  if (!pinned.length) {
    container.innerHTML = '<p class="hint">Pin up to three points to compare exact objectives and selections.</p>';
    return;
  }
  const data = state.optimization.data;
  const dimensions = (data?.dimensions || []).filter((dimension) => dimension.key !== "land_total_area");
  const header = pinned.map((point) => `<th>${escapeHtml(point.id)}</th>`).join("");
  const rows = dimensions
    .map((dimension) => {
      const cells = pinned
        .map((point) => {
          const value = dimension.key === "goal" ? point.goal : point.objectives?.[dimension.key];
          return `<td>${formatNumber(Number(value), 3)}</td>`;
        })
        .join("");
      return `<tr><td>${escapeHtml(dimension.label)}</td>${cells}</tr>`;
    })
    .join("");
  const controls = ["land_scen", "diet_scen", "fixtrade_scen", "live_scen", "crop_scen", "affor_scen"];
  const controlRows = controls
    .map((name) => `<tr><td>${escapeHtml(OPTIMIZATION_CONTROL_LABELS[name] || name)}</td>${pinned.map((point) => `<td>${escapeHtml(optimizationControlValue(point, name))}</td>`).join("")}</tr>`)
    .join("");
  container.innerHTML = `<table><thead><tr><th>Metric</th>${header}</tr></thead><tbody>${rows}${controlRows}</tbody></table>`;
}

function resetOptimizationView() {
  const chart = state.optimization.chart;
  if (!chart) return;
  chart.camera.position.set(2.8, 2.2, 2.9);
  chart.controls.target.set(0, 0, 0);
  chart.controls.update();
}

function loadOptimizationPointInWorkbench() {
  const point = state.optimization.selected;
  const data = state.optimization.data;
  if (!point || !data) return;
  if (!state.artifacts.some((artifact) => artifact.version === data.version)) {
    toast(`FABLE ${data.version} is not configured in this portal.`, "warn");
    return;
  }
  state.optimization.pending = {
    version: data.version,
    pointId: point.id,
    selections: point.selections,
  };
  state.activeVersion = data.version;
  showPage("workbench");
  toast(`Loading frontier point ${point.id} into the Workbench`);
}

function applyOptimizationPending() {
  const pending = state.optimization.pending;
  if (!pending || !state.spec) return;
  if (String(state.activeVersion) !== String(pending.version)) return;
  let applied = 0;
  for (const [name, value] of Object.entries(pending.selections || {})) {
    const element = $$("[data-control]").find((item) => item.dataset.control === name);
    if (!element) continue;
    if (element.type === "checkbox") element.checked = Boolean(value);
    else element.value = String(value);
    applied += 1;
  }
  const name = $("#scenario-name");
  if (name) name.value = `Frontier ${pending.pointId}`;
  state.optimization.pending = null;
  toast(`Loaded ${applied} frontier selections into the Workbench`, "good");
}


function persistOptimizationState() {
  if (!state.optimization.data) return;
  const data = state.optimization.data;
  const params = new URLSearchParams(location.search);
  params.set("opt_version", data.version);
  const values = {
    opt_x: $("#pareto-x")?.value,
    opt_y: $("#pareto-y")?.value,
    opt_z: $("#pareto-z")?.value,
    opt_colour: $("#pareto-colour")?.value,
    opt_size: $("#pareto-size")?.value,
    opt_floor_dimension: $("#pareto-floor-dimension")?.value,
    opt_floor: $("#pareto-floor")?.value,
  };
  for (const [key, value] of Object.entries(values)) {
    if (value !== undefined && value !== null && value !== "") params.set(key, value);
  }
  if ($("#pareto-front-only")?.checked) params.set("opt_front", "1");
  else params.delete("opt_front");
  if ($("#pareto-warning-free")?.checked) params.set("opt_nowarn", "1");
  else params.delete("opt_nowarn");
  if (state.optimization.selected?.id) params.set("opt_point", state.optimization.selected.id);
  else params.delete("opt_point");
  if (state.optimization.reference?.id) params.set("opt_reference", state.optimization.reference.id);
  else params.delete("opt_reference");
  const brushes = state.optimization.brushes || [];
  if (brushes.length) {
    params.set(
      "opt_brushes",
      brushes
        .map((brush) => `${brush.axisKey}:${Math.min(brush.start, brush.end).toFixed(4)}:${Math.max(brush.start, brush.end).toFixed(4)}`)
        .join(","),
    );
    params.delete("opt_brush");
  } else {
    params.delete("opt_brushes");
    params.delete("opt_brush");
  }
  const search = params.toString();
  history.replaceState(null, "", `${search ? `?${search}` : ""}${location.hash || "#optimization"}`);
}

function restoreOptimizationState() {
  const data = state.optimization.data;
  if (!data) return;
  const params = new URLSearchParams(location.search);
  const setSelect = (id, key) => {
    const select = $(`#${id}`);
    const value = params.get(key);
    if (!select || !value) return;
    if (Array.from(select.options).some((option) => option.value === value)) select.value = value;
  };
  setSelect("pareto-x", "opt_x");
  setSelect("pareto-y", "opt_y");
  setSelect("pareto-z", "opt_z");
  setSelect("pareto-colour", "opt_colour");
  setSelect("pareto-size", "opt_size");
  setSelect("pareto-floor-dimension", "opt_floor_dimension");
  const floor = params.get("opt_floor");
  if (floor !== null) {
    const value = Math.max(0, Math.min(100, Number(floor) || 0));
    const input = $("#pareto-floor");
    if (input) input.value = String(value);
    const output = $("#pareto-floor-value");
    if (output) output.textContent = value <= 0 ? "all" : `≥ ${(value / 100).toFixed(2)}`;
  }
  const front = $("#pareto-front-only");
  if (front) front.checked = params.get("opt_front") === "1";
  const warningFree = $("#pareto-warning-free");
  if (warningFree) warningFree.checked = params.get("opt_nowarn") === "1";
  const brushParam = params.get("opt_brushes") || params.get("opt_brush");
  if (brushParam) {
    const brushes = [];
    for (const part of brushParam.split(",")) {
      const [axisKey, startText, endText] = part.split(":");
      if (!PARALLEL_AXES.some((axis) => axis.key === axisKey)) continue;
      const start = Number(startText);
      const end = Number(endText);
      if (!Number.isFinite(start) || !Number.isFinite(end)) continue;
      brushes.push({
        axisKey,
        start: Math.max(0, Math.min(1, start)),
        end: Math.max(0, Math.min(1, end)),
      });
    }
    state.optimization.brushes = brushes;
  }
  const pointId = params.get("opt_point");
  if (pointId) {
    const point = data.points?.find((item) => item.id === pointId);
    if (point) renderOptimizationInfo(point);
  }
  const referenceId = params.get("opt_reference");
  if (referenceId) {
    const reference = data.points?.find((item) => item.id === referenceId);
    if (reference) {
      state.optimization.reference = reference;
      renderOptimizationDelta();
      updateOptimizationSelectionMarker();
      drawParallelCoordinates();
    }
  }
  const presetName = params.get("opt_preset");
  if (presetName) {
    const presets = loadOptimizationPresets();
    const index = presets.findIndex((preset) => preset.name === presetName);
    if (index >= 0) {
      const select = $("#optimization-preset");
      if (select) select.value = String(index);
      if (!params.get("opt_x")) applyOptimizationPreset(presets[index]);
    } else {
      toast(`Preset "${presetName}" is not in this browser; using the shared state.`, "warn");
    }
  }
}

async function copyTextToClipboard(text, successMessage) {
  try {
    await navigator.clipboard.writeText(text);
    toast(successMessage, "good");
    return;
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.append(area);
    area.select();
    const copied = document.execCommand("copy");
    area.remove();
    toast(copied ? successMessage : "Copy failed; copy the URL from the address bar", copied ? "good" : "warn");
  }
}

async function copyOptimizationLink() {
  persistOptimizationState();
  await copyTextToClipboard(location.href, "View link copied");
}

async function copyOptimizationPresetLink() {
  const select = $("#optimization-preset");
  const presets = loadOptimizationPresets();
  const preset = presets[Number(select?.value)];
  if (!preset) {
    toast("No saved view is selected.", "warn");
    return;
  }
  applyOptimizationPreset(preset);
  const url = new URL(location.href);
  url.searchParams.set("opt_preset", preset.name);
  await copyTextToClipboard(url.toString(), `Preset link copied: ${preset.name}`);
}

function optimizationCsvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function downloadOptimizationCsv() {
  const data = state.optimization.data;
  const points = state.optimization.filtered || [];
  if (!data || !points.length) {
    toast("No exact points are currently visible.", "warn");
    return;
  }
  const metrics = (data.dimensions || []).map((dimension) => dimension.key);
  const controls = data.controls || [];
  const header = ["id", "origin", "front", "warnings", ...metrics, ...controls];
  const rows = points.map((point) => [
    point.id,
    point.origin || "",
    point.front ? "true" : "false",
    (point.warnings || []).join(";"),
    ...metrics.map((key) => (key === "goal" ? point.goal : point.objectives?.[key])),
    ...controls.map((name) => point.selections?.[name]),
  ]);
  const csv = [header, ...rows].map((row) => row.map(optimizationCsvCell).join(",")).join("\n") + "\n";
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `fable-${data.version}-filtered-pareto.csv`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  toast(`Exported ${points.length} filtered points`, "good");
}

function downloadOptimizationJson() {
  const data = state.optimization.data;
  if (!data) return;
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `fable-${data.version}-pareto-frontier.json`;
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function bindOptimizationEvents() {
  if (!$("#pareto-canvas")) return;
  $("#optimization-version").addEventListener("change", () => {
    loadOptimizationFrontier($("#optimization-version").value).catch((error) => toast(error.message, "bad"));
  });
  for (const id of ["pareto-x", "pareto-y", "pareto-z", "pareto-colour", "pareto-size", "pareto-floor-dimension"]) {
    $(`#${id}`).addEventListener("change", drawOptimization);
  }
  $("#pareto-floor").addEventListener("input", () => {
    const value = Number($("#pareto-floor").value) / 100;
    $("#pareto-floor-value").textContent = value <= 0 ? "all" : `≥ ${value.toFixed(2)}`;
    drawOptimization();
  });
  $("#pareto-front-only").addEventListener("change", drawOptimization);
  $("#pareto-warning-free").addEventListener("change", drawOptimization);
  $("#pareto-pin").addEventListener("click", pinOptimizationPoint);
  $("#pareto-reference").addEventListener("click", setOptimizationReference);
  $("#parallel-clear-brush").addEventListener("click", clearOptimizationBrush);
  $("#optimization-preset-save").addEventListener("click", saveOptimizationPreset);
  $("#optimization-preset-load").addEventListener("click", loadOptimizationPreset);
  $("#optimization-preset-delete").addEventListener("click", deleteOptimizationPreset);
  $("#optimization-preset-copy-link").addEventListener("click", copyOptimizationPresetLink);
  $("#optimization-preset-export").addEventListener("click", exportOptimizationPresets);
  $("#optimization-preset-import").addEventListener("click", () => $("#optimization-preset-file").click());
  $("#optimization-preset-file").addEventListener("change", importOptimizationPresets);
  $("#optimization-shared-save").addEventListener("click", saveSharedOptimizationPreset);
  $("#optimization-shared-preset").addEventListener("change", syncSharedPresetMetadata);
  $("#optimization-shared-filter").addEventListener("change", () => {
    state.optimization.sharedFilter = $("#optimization-shared-filter").value;
    renderSharedOptimizationPresets();
  });
  $("#optimization-shared-mark-reviewed").addEventListener("click", markSharedOptimizationPresetReviewed);
  $("#optimization-shared-export").addEventListener("click", exportSharedOptimizationPresets);
  $("#optimization-shared-export-csv").addEventListener("click", exportSharedAuditCsv);
  for (const [id, key] of [
    ["optimization-timeline-author", "author"],
    ["optimization-timeline-action", "action"],
    ["optimization-timeline-preset", "preset"],
    ["optimization-timeline-window", "window"],
  ]) {
    $(`#${id}`).addEventListener("change", () => {
      state.optimization.timelineFilter[key] = $(`#${id}`).value;
      renderSharedTimeline(state.optimization.sharedPresets || []);
    });
  }
  $("#optimization-timeline-recently-reviewed").addEventListener("click", () => {
    state.optimization.timelineFilter = { author: "", action: "reviewed", preset: "", window: "7d" };
    $("#optimization-timeline-author").value = "";
    $("#optimization-timeline-action").value = "reviewed";
    $("#optimization-timeline-preset").value = "";
    $("#optimization-timeline-window").value = "7d";
    renderSharedTimeline(state.optimization.sharedPresets || []);
  });
  $("#optimization-timeline-preset-save").addEventListener("click", saveTimelinePreset);
  $("#optimization-timeline-preset-load").addEventListener("click", loadTimelinePreset);
  $("#optimization-timeline-preset-delete").addEventListener("click", deleteTimelinePreset);
  $("#optimization-timeline-reset").addEventListener("click", () => {
    state.optimization.timelineFilter = { author: "", action: "", preset: "", window: "all" };
    $("#optimization-timeline-author").value = "";
    $("#optimization-timeline-action").value = "";
    $("#optimization-timeline-preset").value = "";
    $("#optimization-timeline-window").value = "all";
    renderSharedTimeline(state.optimization.sharedPresets || []);
  });
  $("#optimization-shared-load").addEventListener("click", loadSharedOptimizationPreset);
  $("#optimization-shared-delete").addEventListener("click", deleteSharedOptimizationPreset);
  $("#pareto-clear-reference").addEventListener("click", clearOptimizationReference);
  $("#pareto-clear-pins").addEventListener("click", clearOptimizationPins);
  $("#pareto-reset").addEventListener("click", resetOptimizationView);
  $("#pareto-load").addEventListener("click", loadOptimizationPointInWorkbench);
  $("#pareto-copy-link").addEventListener("click", copyOptimizationLink);
  $("#pareto-download").addEventListener("click", downloadOptimizationJson);
  $("#pareto-download-csv").addEventListener("click", downloadOptimizationCsv);
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
    applyOptimizationPending();
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
        const checksumState = artifact.model_checksum?.state || "unknown";
        const checksumTone = checksumState === "verified" ? "good" : checksumState === "mismatch" ? "bad" : "muted";
        const canMaterialize =
          artifact.files.compressed_model.exists &&
          (!artifact.files.generated_model.exists || checksumState === "mismatch");
        return `
          <article class="panel artifact-card">
            <div class="panel-head">
              <div><h2>FABLE ${escapeHtml(artifact.version)}</h2><p class="hint">${escapeHtml(artifact.model_source || "no model")} model · ${artifact.can_prepare ? "preparable" : "missing files"}</p></div>
              <div class="button-row">
                ${canMaterialize ? `<button class="button ghost small" type="button" data-materialize="${escapeHtml(artifact.version)}" data-force="${checksumState === "mismatch" ? "true" : "false"}">${checksumState === "mismatch" ? "Re-materialize approved model" : "Materialize model"}</button>` : ""}
                ${pill(`model ${checksumState}`, checksumTone)}
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
          const force = button.dataset.force === "true" ? "?force=true" : "";
          await request(`models/${button.dataset.materialize}/materialize${force}`, { method: "POST" });
          toast(force ? "Approved model re-materialized and verified" : "Generated model materialized", "good");
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
  bindOptimizationEvents();
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
