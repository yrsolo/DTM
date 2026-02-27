const state = {
  fixture: null,
};

const refs = {
  loadBtn: document.getElementById("loadFixtureBtn"),
  fileInput: document.getElementById("fixtureFile"),
  loadStatus: document.getElementById("loadStatus"),
  designerFilter: document.getElementById("designerFilter"),
  statusFilter: document.getElementById("statusFilter"),
  dateFromFilter: document.getElementById("dateFromFilter"),
  dateToFilter: document.getElementById("dateToFilter"),
  timelineView: document.getElementById("timelineView"),
  designerView: document.getElementById("designerView"),
  taskDetailsView: document.getElementById("taskDetailsView"),
};

function readJsonFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      try {
        resolve(JSON.parse(reader.result));
      } catch (err) {
        reject(err);
      }
    };
    reader.onerror = reject;
    reader.readAsText(file);
  });
}

function getSample() {
  return (state.fixture && state.fixture.sample) || {};
}

function getFilterValue(el) {
  return String(el.value || "").trim();
}

function applyFilters(items) {
  const designer = getFilterValue(refs.designerFilter);
  const status = getFilterValue(refs.statusFilter);
  const dateFrom = getFilterValue(refs.dateFromFilter);
  const dateTo = getFilterValue(refs.dateToFilter);

  return (items || []).filter((item) => {
    const itemDesigner = String(item.designer || "").trim();
    const itemStatus = String(item.status || "").trim();
    const itemDate = String(item.due_date || item.start_date || "").trim();

    if (designer && itemDesigner !== designer) return false;
    if (status && itemStatus !== status) return false;
    if (dateFrom && itemDate && itemDate < dateFrom) return false;
    if (dateTo && itemDate && itemDate > dateTo) return false;
    return true;
  });
}

function renderEmpty(container, text) {
  container.innerHTML = `<div class="empty">${text}</div>`;
}

function renderTimeline() {
  const timeline = applyFilters(getSample().timeline || []);
  if (!timeline.length) return renderEmpty(refs.timelineView, "no timeline items");
  refs.timelineView.innerHTML = timeline
    .map(
      (item) =>
        `<div class="item"><strong>${item.task_name || item.task_id || "task"}</strong><br>` +
        `designer: ${item.designer || "-"}<br>` +
        `status: ${item.status || "-"}<br>` +
        `start: ${item.start_date || "-"} / due: ${item.due_date || "-"}</div>`
    )
    .join("");
}

function renderDesignerBoard() {
  const board = getSample().by_designer || {};
  const selectedDesigner = getFilterValue(refs.designerFilter);
  const entries = Object.entries(board).filter(([designer]) => !selectedDesigner || designer === selectedDesigner);
  if (!entries.length) return renderEmpty(refs.designerView, "no designer rows");
  refs.designerView.innerHTML = entries
    .map(([designer, tasks]) => {
      const list = applyFilters(tasks || [])
        .map((task) => `${task.task_name || task.task_id || "task"} (${task.status || "-"})`)
        .join(", ");
      return `<div class="item"><strong>${designer}</strong><br>${list || "no tasks"}</div>`;
    })
    .join("");
}

function renderTaskDetails() {
  const details = applyFilters(getSample().task_details || []);
  if (!details.length) return renderEmpty(refs.taskDetailsView, "no task details");
  refs.taskDetailsView.innerHTML = details
    .map(
      (item) =>
        `<div class="item"><strong>${item.task_name || item.task_id || "task"}</strong><br>` +
        `designer: ${item.designer || "-"}<br>` +
        `stage: ${item.stage || "-"}<br>` +
        `status: ${item.status || "-"}<br>` +
        `timing: ${item.timing_raw || "-"}</div>`
    )
    .join("");
}

function refreshViews() {
  renderTimeline();
  renderDesignerBoard();
  renderTaskDetails();
}

function fillFilterOptions() {
  const sample = getSample();
  const designers = new Set();
  const statuses = new Set();

  (sample.timeline || []).forEach((item) => {
    if (item.designer) designers.add(item.designer);
    if (item.status) statuses.add(item.status);
  });
  (sample.task_details || []).forEach((item) => {
    if (item.designer) designers.add(item.designer);
    if (item.status) statuses.add(item.status);
  });
  Object.keys(sample.by_designer || {}).forEach((name) => designers.add(name));

  refs.designerFilter.innerHTML = `<option value="">all</option>${[...designers]
    .sort()
    .map((name) => `<option value="${name}">${name}</option>`)
    .join("")}`;
  refs.statusFilter.innerHTML = `<option value="">all</option>${[...statuses]
    .sort()
    .map((status) => `<option value="${status}">${status}</option>`)
    .join("")}`;
}

async function onLoadFixture() {
  const file = refs.fileInput.files && refs.fileInput.files[0];
  if (!file) {
    refs.loadStatus.textContent = "select fixture file first";
    return;
  }
  try {
    const payload = await readJsonFile(file);
    state.fixture = payload.fixture_bundle || payload;
    refs.loadStatus.textContent = `loaded: ${file.name}`;
    fillFilterOptions();
    refreshViews();
  } catch (err) {
    refs.loadStatus.textContent = `load failed: ${err}`;
  }
}

refs.loadBtn.addEventListener("click", onLoadFixture);
[refs.designerFilter, refs.statusFilter, refs.dateFromFilter, refs.dateToFilter].forEach((el) =>
  el.addEventListener("change", refreshViews)
);

async function tryAutoLoadPrototypePayload() {
  try {
    const resp = await fetch("prototype_payload.json", { cache: "no-store" });
    if (!resp.ok) return;
    const payload = await resp.json();
    state.fixture = payload.fixture_bundle || payload;
    refs.loadStatus.textContent = `loaded: prototype_payload.json (${payload.source_mode || "filesystem"})`;
    fillFilterOptions();
    refreshViews();
  } catch (_err) {
    // manual file load remains available
  }
}

tryAutoLoadPrototypePayload();
