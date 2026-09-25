// Ari Film Studio — canvas Workflow dạng node. JavaScript thuần, không cần build.
"use strict";

const $ = (s, el = document) => el.querySelector(s);
const h = (tag, attrs = {}, ...kids) => {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else if (k === "class") el.className = v;
    else if (k === "value") el.value = v;
    else if (k === "checked") el.checked = !!v;
    else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat(3)) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(kid));
  return el;
};
const clean = kids => kids.flat(4).filter(k => k != null && k !== false);
const fill = (el, ...kids) => el.replaceChildren(...clean(kids));
const add = (el, ...kids) => el.append(...clean(kids));
const svg = (tag, attrs = {}) => { const el = document.createElementNS("http://www.w3.org/2000/svg", tag); for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v); return el; };

const RUNTIME = ["trang_thai", "loi", "chi_tiet", "ket_qua", "luc_chay", "cau_hinh_luc_chay"];
const TT = { chua_chay: "Chưa chạy", dang_chay: "Đang chạy…", xong: "Xong", loi: "Lỗi", cho_claude: "Chờ Claude Code", cho_nguoi_dung: "Chờ bạn làm tay", cho_duyet: "Chờ bạn duyệt" };
const GROUP_COLOR = { "Đầu vào": "#8a8a8a", "AI vai trò": "#7b61d9", "Tạo sinh": "#e0613a", "Âm thanh": "#2f9e66", "Chỉnh sửa & hậu kỳ": "#3a86ff", "Dựng & xuất": "#b0643c", "Điều khiển": "#c9a227" };

let wireDraft = null; // dây đang kéo (giữ lại sau khi S.drag bị xoá ở pointerup)
const S = { pid: null, reg: null, wf: { phien_ban: 1, nodes: [], edges: [] }, version: null, view: { x: 60, y: 40, k: 1 },
  sel: null, selEdge: null, dirty: false, saveTimer: null, undo: [], drag: null, running: false, tpl: null, lib: null };
const CLAUDE_SKILLS = ["cinematic-techniques", "tvc-thoi-trang"]; // skill Claude có sẵn; thêm skill mới qua /hoc-hoi

// ---------------------------------------------------------------- API
async function api(path, opts = {}) {
  const r = await fetch(path, opts); let body = null;
  try { body = await r.json(); } catch (_) {}
  return { ok: r.ok, status: r.status, body, version: r.headers.get("X-Version") };
}
const post = (path, body) => api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
const T = id => S.reg._types[id] || { ten: id, vao: [], ra: [], tham_so: [], nha_cung_cap: [] };
const node = id => S.wf.nodes.find(n => n.id === id);
const fileUrl = rel => rel ? `/files/${encodeURIComponent(S.pid)}/${rel.split("/").map(encodeURIComponent).join("/")}` : "";
const portColor = k => (S.reg.kieu_cong[k] || {}).mau || "#999";
const setSave = t => { $("#saveState").textContent = t; };

// ---------------------------------------------------------------- tải / lưu
async function init() {
  S.reg = (await api("/api/node-types")).body;
  S.reg._types = Object.fromEntries(S.reg.node.map(n => [n.id, n]));
  S.lib = (await api("/api/library")).body;
  buildPalette();
  await loadProjects();
  setInterval(poll, 1500);
}

async function loadProjects(want) {
  const list = (await api("/api/projects")).body || [];
  const sel = $("#projectSelect");
  fill(sel, h("option", { value: "" }, list.length ? "— Chọn dự án —" : "(chưa có dự án)"), list.map(p => h("option", { value: p.id }, p.ten)));
  want = want || (() => { try { return localStorage.getItem("studio.pid"); } catch (_) { return null; } })();
  if (want && list.some(p => p.id === want)) { sel.value = want; await openProject(want); } else render();
}

async function openProject(pid) {
  const r = await api(`/api/workflow/${encodeURIComponent(pid)}`);
  if (!r.ok) return alert(r.body?.loi || "Không mở được workflow");
  S.pid = pid; S.wf = r.body; S.version = r.version; S.sel = null; S.selEdge = null; S.undo = []; S.dirty = false;
  try { localStorage.setItem("studio.pid", pid); } catch (_) {}
  const saved = (() => { try { return JSON.parse(localStorage.getItem("studio.view." + pid)); } catch (_) { return null; } })();
  if (saved) S.view = saved; else fit();
  render();
}

function snapshot() {
  S.undo.push(JSON.stringify({ nodes: S.wf.nodes, edges: S.wf.edges }));
  if (S.undo.length > 40) S.undo.shift();
}
function changed(structural = true) {
  S.dirty = true; setSave("Chưa lưu…");
  clearTimeout(S.saveTimer); S.saveTimer = setTimeout(save, 600);
  if (structural) render();
}
async function save() {
  if (S.tpl) return saveTemplate();
  if (!S.pid) return;
  const payload = { phien_ban: 1, meta: S.wf.meta || {}, nodes: S.wf.nodes.map(n => Object.fromEntries(Object.entries(n).filter(([k]) => !RUNTIME.includes(k)))), edges: S.wf.edges };
  const r = await api(`/api/workflow/${encodeURIComponent(S.pid)}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (r.ok) { S.version = r.version; S.dirty = false; setSave("Đã lưu " + new Date().toLocaleTimeString()); }
  else setSave("Lỗi lưu: " + (r.body?.loi || r.status));
}

async function saveTemplate() {
  const r = await api(`/api/mau-workflow/${encodeURIComponent(S.tpl.id)}`, { method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ten: S.tpl.ten, mo_ta: S.tpl.mo_ta, meta: S.wf.meta || {}, nodes: S.wf.nodes, edges: S.wf.edges }) });
  if (r.ok) { S.dirty = false; setSave("Đã lưu mẫu " + new Date().toLocaleTimeString()); } else setSave("Lỗi lưu mẫu");
}
async function editTemplate(id) {
  if (S.dirty) await save();
  const r = await api(`/api/mau-workflow/${encodeURIComponent(id)}`);
  if (!r.ok) return alert("Không mở được mẫu");
  S.tpl = { id, ten: r.body.ten, mo_ta: r.body.mo_ta || "", backPid: S.pid };
  S.wf = { phien_ban: 1, meta: r.body.meta || {}, nodes: r.body.nodes, edges: r.body.edges };
  S.sel = null; S.selEdge = null; S.undo = []; S.dirty = false;
  document.body.classList.add("tpl-mode");
  $("#tplBanner").textContent = "✎ Đang sửa mẫu: " + S.tpl.ten;
  fit(); render();
}
async function exitTemplate() {
  if (S.dirty) await save();
  const back = S.tpl?.backPid; S.tpl = null; document.body.classList.remove("tpl-mode");
  if (back) await openProject(back); else { S.wf = { phien_ban: 1, nodes: [], edges: [] }; render(); }
}

// Bộ máy / Claude cập nhật trạng thái node → lấy về, giữ nguyên cấu hình đang sửa
async function poll() {
  if (!S.pid || S.drag || S.tpl) return;
  const r = await api(`/api/wf-state/${encodeURIComponent(S.pid)}`);
  if (!r.ok) return;
  S.running = r.body.dang_chay;
  $("#runState").textContent = S.running ? "⏳ đang chạy…" : "";
  if (r.body.version === S.version) return;
  const w = await api(`/api/workflow/${encodeURIComponent(S.pid)}`);
  if (!w.ok) return;
  const srv = Object.fromEntries(w.body.nodes.map(n => [n.id, n]));
  if (!S.dirty) S.wf = w.body;
  else for (const n of S.wf.nodes) if (srv[n.id]) for (const k of RUNTIME) n[k] = srv[n.id][k];
  S.version = w.version;
  render();
}

// ---------------------------------------------------------------- bảng node
function buildPalette() {
  const q = ($("#paletteSearch").value || "").toLowerCase();
  const list = $("#paletteList"); list.replaceChildren();
  for (const g of S.reg.nhom) {
    const items = S.reg.node.filter(t => t.nhom === g && (!q || (t.ten + " " + t.id).toLowerCase().includes(q)));
    if (!items.length) continue;
    add(list, h("h4", {}, g), items.map(t => h("div", { class: "pitem", draggable: "true", style: { "--c": GROUP_COLOR[g] },
      title: describeType(t), onclick: () => addNode(t.id), ondragstart: e => e.dataTransfer.setData("text/node-type", t.id) }, t.ten)));
  }
}
function describeType(t) {
  const io = p => p.map(x => `${x.ten} (${S.reg.kieu_cong[x.kieu]?.ten})`).join(", ") || "—";
  return `Vào: ${io(t.vao)}\nRa: ${io(t.ra)}\nNhà cung cấp: ${(t.nha_cung_cap || []).map(p => S.reg.nha_cung_cap[p]?.ten).join(", ") || "—"}`;
}
$("#paletteSearch").addEventListener("input", buildPalette);

function nextId(prefix = "n") {
  let m = 0; for (const n of S.wf.nodes) { const x = String(n.id).match(/(\d+)$/); if (x) m = Math.max(m, +x[1]); }
  return prefix + (m + 1);
}
function addNode(type, at) {
  if (!S.pid) return alert("Chọn hoặc tạo dự án trước");
  snapshot();
  const t = T(type), st = $("#stage").getBoundingClientRect();
  const p = at || toWorld(st.left + st.width / 2 - 118, st.top + st.height / 2 - 60);
  const params = {};
  for (const ts of t.tham_so) if (ts.loai === "select") params[ts.key] = ts.lua_chon?.[0] ?? "";
  const n = { id: nextId(), type, ten: t.ten, x: Math.round(p.x), y: Math.round(p.y), provider: (t.nha_cung_cap || [])[0] === "claude" || (t.nha_cung_cap || []).length === 1 ? t.nha_cung_cap[0] : "",
    model: "", params, khoa: false, ghi_chu: "", trang_thai: "chua_chay" };
  S.wf.nodes.push(n); S.sel = n.id; S.selEdge = null; changed();
}
function removeNode(id) {
  snapshot();
  S.wf.nodes = S.wf.nodes.filter(n => n.id !== id);
  S.wf.edges = S.wf.edges.filter(e => e.tu.node !== id && e.den.node !== id);
  if (S.sel === id) S.sel = null; changed();
}
function duplicateNode(id) {
  const src = node(id); if (!src) return;
  snapshot();
  const n = JSON.parse(JSON.stringify(src)); n.id = nextId(); n.x += 30; n.y += 30;
  for (const k of RUNTIME) delete n[k]; n.trang_thai = "chua_chay"; n.khoa = false;
  S.wf.nodes.push(n); S.sel = n.id; changed();
}

// ---------------------------------------------------------------- toạ độ, phóng to
function applyView() {
  $("#world").style.transform = `translate(${S.view.x}px, ${S.view.y}px) scale(${S.view.k})`;
  $("#stage").style.backgroundPosition = `${S.view.x}px ${S.view.y}px`;
  $("#stage").style.backgroundSize = `${22 * S.view.k}px ${22 * S.view.k}px`;
  $("#zoomLabel").textContent = Math.round(S.view.k * 100) + "%";
  if (S.pid) try { localStorage.setItem("studio.view." + S.pid, JSON.stringify(S.view)); } catch (_) {}
}
function toWorld(cx, cy) { const r = $("#stage").getBoundingClientRect(); return { x: (cx - r.left - S.view.x) / S.view.k, y: (cy - r.top - S.view.y) / S.view.k }; }
function fit() {
  const ns = S.wf.nodes; const st = $("#stage").getBoundingClientRect();
  if (!ns.length) { S.view = { x: 60, y: 40, k: 1 }; return applyView(); }
  const minX = Math.min(...ns.map(n => n.x)), minY = Math.min(...ns.map(n => n.y));
  const maxX = Math.max(...ns.map(n => n.x + 240)), maxY = Math.max(...ns.map(n => n.y + 260));
  const k = Math.max(0.25, Math.min(1.2, Math.min(st.width / (maxX - minX + 80), st.height / (maxY - minY + 80))));
  S.view = { k, x: (st.width - (maxX - minX) * k) / 2 - minX * k, y: (st.height - (maxY - minY) * k) / 2 - minY * k };
  applyView();
}
$("#fitBtn").addEventListener("click", () => { fit(); drawEdges(); });

const stage = $("#stage");
stage.addEventListener("wheel", e => {
  e.preventDefault();
  const r = stage.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top;
  const k = Math.max(0.2, Math.min(2.2, S.view.k * (e.deltaY < 0 ? 1.1 : 1 / 1.1)));
  S.view.x = mx - (mx - S.view.x) * (k / S.view.k); S.view.y = my - (my - S.view.y) * (k / S.view.k); S.view.k = k;
  applyView();
}, { passive: false });
stage.addEventListener("pointerdown", e => {
  if (e.target !== stage && e.target !== $("#world") && e.target !== $("#edges") && e.target.id !== "nodes") return;
  S.sel = null; S.selEdge = null; render();
  S.drag = { kind: "pan", sx: e.clientX, sy: e.clientY, vx: S.view.x, vy: S.view.y }; stage.classList.add("panning");
  stage.setPointerCapture(e.pointerId);
});
stage.addEventListener("dragover", e => e.preventDefault());
stage.addEventListener("drop", e => {
  const type = e.dataTransfer.getData("text/node-type");
  if (type) { e.preventDefault(); const p = toWorld(e.clientX, e.clientY); addNode(type, { x: p.x - 118, y: p.y - 20 }); }
});
window.addEventListener("pointermove", e => {
  const d = S.drag; if (!d) return;
  if (d.kind === "pan") { S.view.x = d.vx + e.clientX - d.sx; S.view.y = d.vy + e.clientY - d.sy; applyView(); }
  else if (d.kind === "node") {
    const n = node(d.id); n.x = Math.round(d.nx + (e.clientX - d.sx) / S.view.k); n.y = Math.round(d.ny + (e.clientY - d.sy) / S.view.k);
    const el = document.querySelector(`.node[data-id="${d.id}"]`); el.style.left = n.x + "px"; el.style.top = n.y + "px"; drawEdges(); d.moved = true;
  } else if (d.kind === "wire") { d.cur = toWorld(e.clientX, e.clientY); highlightTargets(e); drawEdges(); }
});
window.addEventListener("pointerup", e => {
  const d = S.drag; if (!d) return; S.drag = null; stage.classList.remove("panning");
  if (d.kind === "node" && d.moved) changed(false);
  if (d.kind === "wire") finishWire(e);
});

// ---------------------------------------------------------------- dây nối
function portPos(nid, dir, pid) {
  const el = document.querySelector(`.node[data-id="${nid}"] .pdot[data-dir="${dir}"][data-port="${pid}"]`);
  const n = node(nid); if (!el || !n) return null;
  const r = el.getBoundingClientRect(), w = toWorld(r.left + r.width / 2, r.top + r.height / 2);
  return w;
}
function curve(a, b) { const dx = Math.max(40, Math.abs(b.x - a.x) * 0.5); return `M${a.x},${a.y} C${a.x + dx},${a.y} ${b.x - dx},${b.y} ${b.x},${b.y}`; }
function drawEdges() {
  const g = $("#edges"); g.replaceChildren();
  for (const e of S.wf.edges) {
    const a = portPos(e.tu.node, "out", e.tu.cong), b = portPos(e.den.node, "in", e.den.cong);
    if (!a || !b) continue;
    const src = T(node(e.tu.node)?.type).ra.find(p => p.id === e.tu.cong);
    const d = curve(a, b), sel = S.selEdge === e.id;
    const hit = svg("path", { d, class: "hit" });
    hit.addEventListener("pointerdown", ev => { ev.stopPropagation(); if (ev.altKey) return cutEdge(e.id); S.selEdge = e.id; S.sel = null; render(); });
    g.append(svg("path", { d, class: sel ? "sel" : "", style: `stroke:${sel ? "" : portColor(src?.kieu)}` }), hit);
    if (sel) {
      const m = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
      const c = svg("g", { class: "cut" });
      c.append(svg("circle", { cx: m.x, cy: m.y, r: 11, fill: "var(--st-loi)" }));
      const t = svg("text", { x: m.x, y: m.y + 4, "text-anchor": "middle", fill: "#fff", "font-size": "12" }); t.textContent = "✂"; c.append(t);
      c.addEventListener("pointerdown", ev => { ev.stopPropagation(); cutEdge(e.id); });
      g.append(c);
    }
  }
  const d = S.drag;
  if (d && d.kind === "wire" && d.cur) {
    const a = portPos(d.from.node, "out", d.from.cong);
    if (a) g.append(svg("path", { d: curve(a, d.cur), class: "temp", style: `stroke:${portColor(d.kieu)}` }));
  }
}
function cutEdge(id) { snapshot(); S.wf.edges = S.wf.edges.filter(e => e.id !== id); S.selEdge = null; changed(); }
const compatible = (a, b) => a === "any" || b === "any" || a === b;

function startWire(e, nid, dir, port) {
  e.stopPropagation(); e.preventDefault();
  if (dir === "in") { // nhấc dây đang cắm ở đầu vào ra để nối chỗ khác hoặc thả ra ngoài để cắt
    const ex = [...S.wf.edges].reverse().find(x => x.den.node === nid && x.den.cong === port.id);
    if (!ex) return;
    snapshot(); S.wf.edges = S.wf.edges.filter(x => x !== ex);
    const src = T(node(ex.tu.node).type).ra.find(p => p.id === ex.tu.cong);
    S.drag = { kind: "wire", from: ex.tu, kieu: src.kieu, cur: toWorld(e.clientX, e.clientY), lifted: true };
    render(); return;
  }
  S.drag = { kind: "wire", from: { node: nid, cong: port.id }, kieu: port.kieu, cur: toWorld(e.clientX, e.clientY) };
}
function highlightTargets(e) {
  document.querySelectorAll(".pdot.ok").forEach(x => x.classList.remove("ok"));
  const t = document.elementFromPoint(e.clientX, e.clientY);
  if (t?.classList.contains("pdot") && t.dataset.dir === "in" && compatible(S.drag.kieu, t.dataset.kieu)) t.classList.add("ok");
}
function finishWire(e) {
  const t = document.elementFromPoint(e.clientX, e.clientY);
  const w = wireDraft; wireDraft = null;
  document.querySelectorAll(".pdot.ok").forEach(x => x.classList.remove("ok"));
  if (!w) return render();
  if (t?.classList.contains("pdot") && t.dataset.dir === "in") {
    const nid = t.closest(".node").dataset.id, portId = t.dataset.port;
    const port = T(node(nid).type).vao.find(p => p.id === portId);
    if (nid === w.from.node) return render();
    if (!compatible(w.kieu, port.kieu)) { alert(`Không nối được: đầu ra là ${S.reg.kieu_cong[w.kieu].ten}, đầu vào cần ${S.reg.kieu_cong[port.kieu].ten}`); return render(); }
    if (createsCycle(w.from.node, nid)) { alert("Không nối được: tạo thành vòng lặp"); return render(); }
    if (!w.lifted) snapshot();
    if (!port.nhieu) S.wf.edges = S.wf.edges.filter(x => !(x.den.node === nid && x.den.cong === portId));
    if (!S.wf.edges.some(x => x.tu.node === w.from.node && x.tu.cong === w.from.cong && x.den.node === nid && x.den.cong === portId))
      S.wf.edges.push({ id: "e" + Date.now().toString(36) + Math.random().toString(36).slice(2, 5), tu: w.from, den: { node: nid, cong: portId } });
    return changed();
  }
  if (w.lifted) return changed(); // thả ra ngoài = cắt dây
  render();
}
function createsCycle(from, to) {
  const seen = new Set([to]), stack = [to];
  while (stack.length) { const x = stack.pop(); if (x === from) return true; for (const e of S.wf.edges) if (e.tu.node === x && !seen.has(e.den.node)) { seen.add(e.den.node); stack.push(e.den.node); } }
  return false;
}

// ---------------------------------------------------------------- vẽ node
function preview(n, big = false) {
  const kq = n.ket_qua || {}; const vals = Object.values(kq);
  if (!vals.length) return null;
  return h("div", { class: "preview" }, vals.slice(0, big ? 5 : 1).map(v => {
    if (v.kieu === "image") return h("a", { href: fileUrl(v.gia_tri), target: "_blank" }, h("img", { src: fileUrl(v.gia_tri), alt: "" }));
    if (v.kieu === "video") return h("video", { src: fileUrl(v.gia_tri) + "#t=0.1", controls: big, muted: !big, preload: "metadata", onmouseenter: e => !big && e.target.play().catch(() => {}), onmouseleave: e => !big && e.target.pause() });
    if (v.kieu === "audio") return h("audio", { src: fileUrl(v.gia_tri), controls: true, preload: "none" });
    if (v.kieu === "model3d") return h("a", { href: fileUrl(v.gia_tri), download: "" }, "⬇ Tải mô hình 3D");
    return h("div", { class: "txt", style: big ? { maxHeight: "none" } : {} }, String(v.gia_tri ?? ""));
  }));
}
function configSig(n) { return JSON.stringify([n.provider, n.model, n.params]); }

function renderNode(n) {
  const t = T(n.type), color = GROUP_COLOR[t.nhom] || "#999";
  const provs = t.nha_cung_cap || [];
  const models = (t.model || {})[n.provider] || [];
  const st = n.trang_thai || "chua_chay";
  const isInput = !provs.length && t.nhom === "Đầu vào";
  const inRow = p => h("div", { class: "port" }, h("span", { class: "pdot" + (p.nhieu ? " multi" : ""), "data-dir": "in", "data-port": p.id, "data-kieu": p.kieu,
    style: { "--pc": portColor(p.kieu) }, title: `${p.ten} — ${S.reg.kieu_cong[p.kieu].ten}${p.nhieu ? " (nhiều)" : ""}`, onpointerdown: e => { startWire(e, n.id, "in", p); wireDraft = S.drag; } }), p.ten);
  const outRow = p => h("div", { class: "port" }, p.ten, h("span", { class: "pdot", "data-dir": "out", "data-port": p.id, "data-kieu": p.kieu,
    style: { "--pc": portColor(p.kieu) }, title: `${p.ten} — ${S.reg.kieu_cong[p.kieu].ten}`, onpointerdown: e => { startWire(e, n.id, "out", p); wireDraft = S.drag; } }));
  const stale = st === "xong" && n.cau_hinh_luc_chay && n.cau_hinh_luc_chay !== configSig(n);
  const el = h("div", { class: "node" + (S.sel === n.id ? " sel" : "") + (n.khoa ? " locked" : ""), "data-id": n.id, style: { left: n.x + "px", top: n.y + "px", "--c": color },
    onpointerdown: e => { if (S.sel !== n.id) { S.sel = n.id; S.selEdge = null; render(); } e.stopPropagation(); } },
    h("div", { class: "nhead", onpointerdown: e => { if (e.button !== 0 || e.target.closest("button")) return; e.stopPropagation(); if (S.sel !== n.id) { S.sel = n.id; S.selEdge = null; render(); }
        snapshot(); S.drag = { kind: "node", id: n.id, sx: e.clientX, sy: e.clientY, nx: n.x, ny: n.y }; } },
      h("span", { class: "dot " + st, title: TT[st] }), h("span", { class: "t", title: n.ten }, (n.khoa ? "🔒 " : "") + (n.ten || t.ten)),
      provs.length && !["duyet"].includes(n.type) ? h("button", { class: "btn small", title: "Chạy node này (và những gì nó cần)", onclick: () => runNode(n.id, "den") }, "▶") : null),
    h("div", { class: "nbody" },
      provs.length > 1 ? h("select", { onchange: e => { n.provider = e.target.value; n.model = ""; changed(); } },
        h("option", { value: "" }, "— Chọn nhà cung cấp —"), provs.map(p => h("option", { value: p, selected: n.provider === p }, S.reg.nha_cung_cap[p]?.ten || p))) : null,
      provs.length && (models.length || ["higgsfield", "tripo"].includes(n.provider)) ? modelInput(n, models) : null,
      n.type === "prompt" || n.type === "ghi-chu" ? h("textarea", { placeholder: n.type === "prompt" ? "Nhập prompt / nội dung…" : "Ghi chú, tên cảnh…", oninput: e => { n.params.noi_dung = e.target.value; changed(false); } }, n.params?.noi_dung || "") : null,
      isInput && n.type !== "prompt" ? fileDrop(n, "tai_file") : null,
      h("div", { class: "ports" }, h("div", { class: "pcol in" }, t.vao.map(inRow)), h("div", { class: "pcol out" }, t.ra.map(outRow))),
      preview(n),
      st === "cho_nguoi_dung" ? fileDrop(n, "ket_qua") : null,
      st === "cho_duyet" ? h("div", { class: "row" }, h("button", { class: "btn small primary", onclick: () => nodeAction(n.id, "duyet") }, "✓ Duyệt"), h("button", { class: "btn small danger", onclick: () => nodeAction(n.id, "tu_choi") }, "✗ Chưa đạt")) : null,
      stale ? h("div", { class: "stale" }, "⚠ Đã sửa sau lần chạy — bấm ▶ để chạy lại") : null,
      n.trang_thai === "loi" ? h("div", { class: "status loi" }, n.loi) : n.chi_tiet ? h("div", { class: "status" }, n.chi_tiet) : null));
  return el;
}
function modelInput(n, models) {
  const id = "ml-" + n.id;
  return h("span", {}, h("input", { type: "text", list: id, value: n.model || "", placeholder: "Model (trống = mặc định)", oninput: e => { n.model = e.target.value; changed(false); } }),
    h("datalist", { id }, models.map(m => h("option", { value: m }))));
}
function fileDrop(n, action) {
  const t = T(n.type);
  const outPort = t.ra[0];
  const accept = outPort ? ({ image: "image/*", video: "video/*", audio: "audio/*", model3d: ".glb,.gltf,.fbx,.obj" }[outPort.kieu] || "*/*") : "*/*";
  const inp = h("input", { type: "file", accept, class: "hidden", onchange: e => upload([...e.target.files]) });
  const label = action === "ket_qua" ? "Thả file kết quả vào đây" : (n.params?.file ? "Đổi file: " + n.params.file.split("/").pop() : "Thả file vào đây / bấm để chọn");
  const z = h("div", { class: "drop", onclick: () => inp.click(), ondragover: e => { e.preventDefault(); e.stopPropagation(); z.classList.add("over"); },
    ondragleave: () => z.classList.remove("over"), ondrop: e => { e.preventDefault(); e.stopPropagation(); z.classList.remove("over"); upload([...e.dataTransfer.files]); } }, label, inp);
  async function upload(fs) {
    const f = fs[0]; if (!f) return;
    setSave("Đang tải lên…");
    const data = await new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f); });
    const r = await post(`/api/wf-node/${encodeURIComponent(S.pid)}/${encodeURIComponent(n.id)}`, { action, ten_file: f.name, du_lieu: data, cong: outPort?.id, kieu: outPort?.kieu });
    if (!r.ok) return alert("Tải lên lỗi: " + (r.body?.loi || r.status));
    if (action === "tai_file") { n.params = { ...(n.params || {}), file: r.body.duong_dan }; changed(); }
    else { setSave("Đã nhận file"); S.version = null; poll(); }
  }
  return z;
}

function render() {
  $("#empty").classList.toggle("hidden", !!(S.pid && S.wf.nodes.length));
  const box = $("#nodes"); box.replaceChildren(...S.wf.nodes.map(renderNode));
  applyView(); drawEdges(); renderInspector();
}

// ---------------------------------------------------------------- bảng chi tiết
function field(label, control) { return h("label", { class: "field" }, h("span", {}, label), control); }
function paramControl(n, p) {
  const v = n.params?.[p.key] ?? "";
  const set = val => { n.params = { ...(n.params || {}), [p.key]: val }; changed(false); };
  if (p.loai === "textarea") return h("textarea", { rows: 5, oninput: e => set(e.target.value) }, v);
  if (p.loai === "number") return h("input", { type: "number", step: "any", value: v, oninput: e => set(e.target.value === "" ? "" : Number(e.target.value)) });
  if (p.loai === "bool") return h("input", { type: "checkbox", checked: !!v, onchange: e => set(e.target.checked) });
  if (p.loai === "select") return h("select", { onchange: e => set(e.target.value) }, (p.lua_chon || []).map(o => h("option", { value: o, selected: v === o }, (p.mo_ta || {})[o] || o || "(mặc định)")));
  if (p.loai === "file") return h("div", { class: "muted" }, v ? v : "Kéo thả file vào node trên canvas");
  const id = "dl-" + n.id + p.key;
  return h("span", {}, h("input", { type: "text", list: p.goi_y ? id : null, value: v, oninput: e => set(e.target.value) }), p.goi_y ? h("datalist", { id }, p.goi_y.map(g => h("option", { value: g }))) : null);
}
function renderInspector() {
  const box = $("#inspector");
  if (S.selEdge) {
    const e = S.wf.edges.find(x => x.id === S.selEdge);
    box.classList.remove("hidden");
    return fill(box, h("h3", {}, "Dây nối"), h("div", { class: "box" }, `${e.tu.node}.${e.tu.cong} → ${e.den.node}.${e.den.cong}`),
      h("button", { class: "btn danger", onclick: () => cutEdge(e.id) }, "✂ Cắt dây"), h("p", { class: "muted" }, "Mẹo: Alt + bấm vào dây để cắt nhanh; nhấn Delete để xoá dây đang chọn."));
  }
  const n = node(S.sel);
  if (!n) { if (S.pid || S.tpl) return renderMeta(box); box.classList.add("hidden"); return; }
  box.classList.remove("hidden");
  const t = T(n.type), prov = S.reg.nha_cung_cap[n.provider];
  fill(box,
    h("div", { class: "row" }, h("h3", { style: { flex: 1 } }, t.ten), h("button", { class: "btn small", onclick: () => { S.sel = null; render(); } }, "✕")),
    field("Tên node", h("input", { type: "text", value: n.ten || "", oninput: e => { n.ten = e.target.value; changed(false); document.querySelector(`.node[data-id="${n.id}"] .t`).textContent = e.target.value; } })),
    h("div", { class: "row" }, h("span", { class: "chipk" }, TT[n.trang_thai || "chua_chay"]), prov ? h("span", { class: "chipk" }, { api: "⚡ API", claude: "🤖 Claude Code", local: "💻 trên máy", thu_cong: "✋ làm tay" }[prov.chay]) : null,
      t.agent ? h("span", { class: "chipk" }, "agent: " + t.agent) : null),
    (t.nha_cung_cap || []).length > 1 ? field("Nhà cung cấp", h("select", { onchange: e => { n.provider = e.target.value; n.model = ""; changed(); } },
      h("option", { value: "" }, "— Chọn —"), t.nha_cung_cap.map(p => h("option", { value: p, selected: n.provider === p }, S.reg.nha_cung_cap[p]?.ten || p)))) : null,
    (t.nha_cung_cap || []).length ? field("Model", modelInput(n, (t.model || {})[n.provider] || [])) : null,
    t.tham_so.filter(p => !(p.key === "noi_dung" && ["prompt", "ghi-chu"].includes(n.type))).map(p => field(p.ten, paramControl(n, p))),
    field("Ghi chú cho AI / cho mình", h("textarea", { rows: 2, oninput: e => { n.ghi_chu = e.target.value; changed(false); } }, n.ghi_chu || "")),
    h("div", { class: "row" },
      (t.nha_cung_cap || []).length ? h("button", { class: "btn primary", onclick: () => runNode(n.id, "node") }, "▶ Chạy lại node") : null,
      (t.nha_cung_cap || []).length ? h("button", { class: "btn", onclick: () => runNode(n.id, "den") }, "⏭ Chạy tới đây") : null,
      h("button", { class: "btn", onclick: () => nodeAction(n.id, "dat_lai") }, "↺ Xoá kết quả")),
    h("div", { class: "row" },
      h("label", { class: "chipk" }, h("input", { type: "checkbox", checked: n.khoa, onchange: e => { n.khoa = e.target.checked; changed(); } }), " Khoá (không chạy lại)"),
      h("button", { class: "btn small", onclick: () => duplicateNode(n.id) }, "⧉ Nhân bản"),
      h("button", { class: "btn small danger", onclick: () => removeNode(n.id) }, "🗑 Xoá node")),
    n.loi ? h("div", { class: "box", style: { color: "var(--st-loi)" } }, n.loi) : null,
    ["cho_claude", "cho_nguoi_dung"].includes(n.trang_thai) ? h("div", { class: "box" },
      n.trang_thai === "cho_claude" ? "Node này do Claude Code thực hiện. Mở Claude Code trong thư mục ari-film-studio và gõ:\n/chay-workflow " + S.pid
        : "Làm theo gói việc (bấm để xem), rồi thả file kết quả vào node.", h("br"),
      h("a", { href: fileUrl(`wf/${n.id}/goi-viec.md`), target: "_blank" }, "📄 Xem gói việc")) : null,
    preview(n, true));
}

function renderMeta(box) {
  box.classList.remove("hidden");
  const m = (S.wf.meta ||= {});
  const set = (k, v) => { m[k] = v; changed(false); };
  const libOpts = kind => (S.lib?.[kind] || []).map(x => ({ value: x.id, label: x.ten }));
  const sel = (k, opts) => h("select", { onchange: e => set(k, e.target.value) }, h("option", { value: "" }, "—"), opts.map(o => h("option", { value: o.value, selected: m[k] === o.value }, o.label)));
  const skills = [...CLAUDE_SKILLS.map(s => ({ value: s, label: "skill: " + s })), ...libOpts("phong_cach").map(o => ({ ...o, label: "phong cách: " + o.label })),
    ...libOpts("the_loai").map(o => ({ ...o, label: "thể loại: " + o.label }))];
  const cur = new Set(m.ky_nang || []);
  fill(box,
    h("h3", {}, S.tpl ? "Thông tin mẫu" : "Thông tin workflow"),
    S.tpl ? [field("Tên mẫu", h("input", { type: "text", value: S.tpl.ten, oninput: e => { S.tpl.ten = e.target.value; $("#tplBanner").textContent = "✎ Đang sửa mẫu: " + e.target.value; changed(false); } })),
      field("Mô tả", h("textarea", { rows: 3, oninput: e => { S.tpl.mo_ta = e.target.value; changed(false); } }, S.tpl.mo_ta))]
      : m.ten_mau ? h("div", { class: "box" }, "Tạo từ mẫu: " + m.ten_mau) : null,
    field("Ngành / khách hàng", h("input", { type: "text", value: m.nganh || "", placeholder: "Yoga, Spa, Cà phê, Nail…", oninput: e => set("nganh", e.target.value) })),
    field("Thể loại (hồ sơ nghề)", sel("the_loai", libOpts("the_loai"))),
    field("Phong cách hình ảnh", sel("phong_cach", libOpts("phong_cach"))),
    h("div", { class: "row" }, field("Tỉ lệ", sel("ti_le", ["16:9", "9:16", "1:1", "4:5"].map(v => ({ value: v, label: v })))),
      field("Thời lượng (s)", h("input", { type: "number", value: m.thoi_luong ?? "", oninput: e => set("thoi_luong", e.target.value === "" ? "" : Number(e.target.value)) }))),
    h("div", { class: "field" }, h("span", {}, "Kỹ năng (skill) AI dùng cho workflow này"),
      skills.map(s => h("label", { class: "check" }, h("input", { type: "checkbox", checked: cur.has(s.value), onchange: e => {
        const k = new Set(m.ky_nang || []); e.target.checked ? k.add(s.value) : k.delete(s.value); set("ky_nang", [...k]); } }), s.label))),
    h("p", { class: "muted" }, "Các node AI (Đạo Diễn, Biên Kịch, Viết prompt, Kiểm Định…) đọc thông tin này để làm đúng ngành và phong cách. Bấm vào một node để xem chi tiết node."),
    S.tpl ? templateMediaEditor() : null,
    S.tpl ? h("div", { class: "row" }, h("button", { class: "btn primary", onclick: async () => { await save(); exitTemplate(); } }, "💾 Lưu & thoát"), h("button", { class: "btn", onclick: exitTemplate }, "Thoát")) : null);
}
function templateMediaEditor() {
  const box = h("div", { class: "field" }, h("span", {}, "Video minh hoạ & ảnh bìa (hiện trong thư viện mẫu)"));
  const cur = h("div", { class: "tmedia small" });
  const refresh = async () => { const t = (await api(`/api/mau-workflow/${encodeURIComponent(S.tpl.id)}`)).body || {}; fill(cur, mediaBox(t, true)); };
  const up = loai => h("input", { type: "file", accept: loai === "video" ? "video/*" : "image/*", onchange: async e => {
    const f = e.target.files[0]; if (!f) return; setSave("Đang tải lên…");
    const data = await new Promise(res => { const rd = new FileReader(); rd.onload = () => res(rd.result); rd.readAsDataURL(f); });
    const r = await post(`/api/mau-workflow/${encodeURIComponent(S.tpl.id)}/media`, { loai, ten_file: f.name, du_lieu: data });
    setSave(r.ok ? "Đã cập nhật minh hoạ" : "Lỗi tải lên"); refresh(); } });
  const projSel = h("select", {}, h("option", { value: "" }, "— Lấy phim đã xuất từ dự án —"));
  const fileSel = h("select", { class: "hidden" });
  api("/api/projects").then(r => (r.body || []).forEach(p => projSel.append(h("option", { value: p.id }, p.ten))));
  projSel.addEventListener("change", async () => {
    const vids = (await api(`/api/xuat/${encodeURIComponent(projSel.value)}`)).body || [];
    fill(fileSel, h("option", { value: "" }, vids.length ? "— Chọn video —" : "(dự án chưa có video)"), vids.map(v => h("option", { value: v }, v)));
    fileSel.classList.remove("hidden");
  });
  fileSel.addEventListener("change", async () => {
    if (!fileSel.value) return;
    const r = await post(`/api/mau-workflow/${encodeURIComponent(S.tpl.id)}/media`, { loai: "video", tu_du_an: projSel.value, file: fileSel.value });
    setSave(r.ok ? "Đã đặt video minh hoạ" : (r.body?.loi || "Lỗi")); refresh();
  });
  add(box, cur, h("div", { class: "row" }, h("span", { class: "muted" }, "Video:"), up("video")), h("div", { class: "row" }, h("span", { class: "muted" }, "Ảnh bìa:"), up("anh")), projSel, fileSel);
  refresh();
  return box;
}

// ---------------------------------------------------------------- chạy
function paidNodes(ids) {
  return S.wf.nodes.filter(n => (!ids || ids.has(n.id)) && !n.khoa && S.reg.nha_cung_cap[n.provider]?.chay === "api" && n.trang_thai !== "xong");
}
function ancestorsOf(id) {
  const seen = new Set([id]), st = [id];
  while (st.length) { const x = st.pop(); for (const e of S.wf.edges) if (e.den.node === x && !seen.has(e.tu.node)) { seen.add(e.tu.node); st.push(e.tu.node); } }
  return seen;
}
async function confirmRun(ids) {
  const missing = S.wf.nodes.filter(n => (!ids || ids.has(n.id)) && (T(n.type).nha_cung_cap || []).length && !n.provider);
  if (missing.length) { alert("Chưa chọn nhà cung cấp cho: " + missing.map(n => n.ten || n.id).join(", ")); return false; }
  const paid = paidNodes(ids);
  if (!paid.length) return true;
  return confirm("Các node sau sẽ gọi API trả phí:\n\n" + paid.map(n => `• ${n.ten || n.id} — ${S.reg.nha_cung_cap[n.provider].ten}${n.model ? " · " + n.model : ""}`).join("\n") + "\n\nTiếp tục?");
}
async function runAll() {
  if (!S.pid || S.tpl) return;
  if (S.dirty) await save();
  if (!(await confirmRun(null))) return;
  const r = await post(`/api/wf-run/${encodeURIComponent(S.pid)}`, { mode: "tat_ca" });
  if (!r.body?.ok) alert(r.body?.loi || "Không chạy được");
  poll();
}
async function runNode(id, mode) {
  if (S.tpl) return alert("Đang sửa mẫu — thoát chế độ sửa mẫu và dùng mẫu trong một dự án để chạy");
  if (S.dirty) await save();
  const ids = mode === "den" ? ancestorsOf(id) : new Set([id]);
  if (!(await confirmRun(ids))) return;
  const r = await post(`/api/wf-run/${encodeURIComponent(S.pid)}`, { mode, node: id });
  if (!r.body?.ok) alert(r.body?.loi || "Không chạy được");
  poll();
}
async function nodeAction(id, action) {
  let ly_do;
  if (action === "tu_choi") { ly_do = prompt("Chưa đạt ở đâu? (ghi chú cho lần chạy lại)") || "Chưa đạt"; }
  if (S.dirty) await save();
  await post(`/api/wf-node/${encodeURIComponent(S.pid)}/${encodeURIComponent(id)}`, { action, ly_do });
  S.version = null; poll();
}
$("#runAll").addEventListener("click", runAll);

// ---------------------------------------------------------------- phím tắt
window.addEventListener("keydown", e => {
  if (e.target.closest("input, textarea, select")) return;
  if ((e.key === "Delete" || e.key === "Backspace") && (S.selEdge || S.sel)) { e.preventDefault(); if (S.selEdge) cutEdge(S.selEdge); else removeNode(S.sel); }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" && S.undo.length) {
    e.preventDefault(); const prev = JSON.parse(S.undo.pop());
    const rt = Object.fromEntries(S.wf.nodes.map(n => [n.id, n]));
    S.wf.nodes = prev.nodes.map(n => ({ ...n, ...Object.fromEntries(RUNTIME.filter(k => rt[n.id] && k in rt[n.id]).map(k => [k, rt[n.id][k]])) }));
    S.wf.edges = prev.edges; changed();
  }
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "d" && S.sel) { e.preventDefault(); duplicateNode(S.sel); }
});

// ---------------------------------------------------------------- dự án, mẫu, cài đặt
$("#projectSelect").addEventListener("change", e => e.target.value && openProject(e.target.value));
$("#newProject").addEventListener("click", async () => {
  const ten = prompt("Tên phim / dự án:"); if (!ten) return;
  const r = await post("/api/projects", { ten });
  if (!r.ok) return alert(r.body?.loi || "Không tạo được");
  await loadProjects(r.body.id); openTemplates();
});
const dlg = $("#dlg");
const mediaUrl = rel => rel ? "/mau-media/" + rel.split("/").map(encodeURIComponent).join("/") : "";
const INPUT_TYPES = ["prompt", "anh", "video-vao", "am-thanh-vao", "nhan-vat"];
// Ô nhập của mẫu = các node đầu vào (xếp trên → dưới, trái → phải); người dùng điền form thay vì sửa node
function templateFields(tpl) {
  const out = [];
  for (const n of [...tpl.nodes].filter(n => INPUT_TYPES.includes(n.type)).sort((a, b) => a.y - b.y || a.x - b.x)) {
    const label = n.ten || T(n.type).ten;
    if (n.type === "prompt") out.push({ node: n.id, param: "noi_dung", loai: "textarea", ten: label, mac_dinh: n.params?.noi_dung || "", goi_y: n.ghi_chu });
    else if (n.type === "nhan-vat") {
      out.push({ node: n.id, param: "file", loai: "image", ten: label + " — ảnh", goi_y: n.ghi_chu });
      out.push({ node: n.id, param: "mo_ta", loai: "textarea", ten: label + " — mô tả", mac_dinh: n.params?.mo_ta || "" });
    } else out.push({ node: n.id, param: "file", loai: { anh: "image", "video-vao": "video", "am-thanh-vao": "audio" }[n.type], ten: label, goi_y: n.ghi_chu });
  }
  return out;
}
function mediaBox(m, big) {
  if (m.video_minh_hoa) return h("video", { src: mediaUrl(m.video_minh_hoa) + (big ? "" : "#t=0.5"), poster: m.anh_bia ? mediaUrl(m.anh_bia) : null, muted: !big, controls: big, loop: !big, playsinline: true, preload: "metadata",
    onmouseenter: e => !big && e.target.play().catch(() => {}), onmouseleave: e => { if (!big) { e.target.pause(); e.target.currentTime = 0.5; } } });
  if (m.anh_bia) return h("img", { src: mediaUrl(m.anh_bia), alt: "" });
  return h("div", { class: "noimg" }, "🎬", h("small", {}, "Chưa có video minh hoạ"));
}
async function openTemplates() {
  const list = (await api("/api/mau-workflow")).body || [];
  const nganh = [...new Set(list.map(m => m.meta?.nganh || "Khác"))].sort();
  let filter = "", q = "";
  const grid = h("div", { class: "tgrid" });
  const draw = () => fill(grid, list.filter(m => (!filter || (m.meta?.nganh || "Khác") === filter) && (!q || (m.ten + " " + m.mo_ta + " " + (m.meta?.nganh || "")).toLowerCase().includes(q)))
    .map(m => h("div", { class: "tcard", onclick: () => openTemplateDetail(m.id) },
      h("div", { class: "tmedia r" + String(m.meta?.ti_le || "9:16").replace(":", "x") }, mediaBox(m, false)),
      h("div", { class: "tinfo" }, h("b", {}, m.ten),
        h("div", { class: "row" }, h("span", { class: "chipk" }, m.meta?.nganh || "Khác"), m.meta?.ti_le ? h("span", { class: "chipk" }, m.meta.ti_le) : null,
          m.meta?.thoi_luong ? h("span", { class: "chipk" }, m.meta.thoi_luong + "s") : null)))));
  dlg.classList.add("wide");
  fill(dlg, h("div", { class: "row" }, h("h3", { style: { flex: 1, margin: 0 } }, "📋 Thư viện mẫu"), h("button", { class: "btn", onclick: () => dlg.close() }, "✕")),
    h("input", { type: "search", placeholder: "Tìm mẫu theo tên, ngành…", style: { margin: "10px 0 6px" }, oninput: e => { q = e.target.value.toLowerCase(); draw(); } }),
    h("div", { class: "row", style: { marginBottom: "10px" } }, h("button", { class: "btn small", onclick: () => { filter = ""; draw(); } }, "Tất cả"),
      nganh.map(g => h("button", { class: "btn small", onclick: () => { filter = g; draw(); } }, g))),
    grid,
    h("p", { class: "muted" }, "Mẫu mới: dựng workflow trong một dự án rồi bấm 💾 Lưu làm mẫu — hoặc nhờ trợ lý trong Claude Code: /thiet-ke-mau. Video minh hoạ: ✎ Sửa mẫu → tải video lên."));
  draw(); if (!dlg.open) dlg.showModal();
}
async function openTemplateDetail(id) {
  const tpl = (await api(`/api/mau-workflow/${encodeURIComponent(id)}`)).body;
  if (!tpl) return;
  const meta = tpl.meta || {}, fields = templateFields(tpl), values = {}, files = {};
  const tools = [...new Set(tpl.nodes.map(n => S.reg.nha_cung_cap[n.provider]?.ten).filter(Boolean))];
  const steps = tpl.nodes.filter(n => !INPUT_TYPES.includes(n.type) && n.type !== "ghi-chu").sort((a, b) => a.x - b.x || a.y - b.y);
  const nameInp = h("input", { type: "text", value: `${tpl.ten} — ${new Date().toLocaleDateString("vi-VN")}` });
  const runNow = h("input", { type: "checkbox" });
  const form = fields.map((f, i) => {
    const key = f.node + "." + f.param;
    if (f.loai === "textarea") { values[key] = f.mac_dinh || ""; return field(f.ten, h("textarea", { rows: 3, placeholder: f.goi_y || "", oninput: e => { values[key] = e.target.value; } }, f.mac_dinh || "")); }
    const accept = { image: "image/*", video: "video/*", audio: "audio/*" }[f.loai];
    const info = h("span", { class: "muted" }, "Chưa chọn file");
    return field(f.ten + (f.goi_y ? " — " + f.goi_y : ""), h("div", { class: "row" },
      h("input", { type: "file", accept, onchange: e => { files[key] = e.target.files[0]; info.textContent = files[key]?.name || ""; } }), info));
  });
  fill(dlg,
    h("div", { class: "row" }, h("button", { class: "btn small", onclick: openTemplates }, "← Thư viện"), h("h3", { style: { flex: 1, margin: 0 } }, tpl.ten), h("button", { class: "btn", onclick: () => dlg.close() }, "✕")),
    h("div", { class: "tdetail" },
      h("div", { class: "tmedia big r" + String(meta.ti_le || "9:16").replace(":", "x") }, mediaBox(tpl, true)),
      h("div", { class: "tside" },
        h("p", {}, tpl.mo_ta),
        h("div", { class: "row" }, h("span", { class: "chipk" }, meta.nganh || "Khác"), meta.ti_le ? h("span", { class: "chipk" }, meta.ti_le) : null, meta.thoi_luong ? h("span", { class: "chipk" }, meta.thoi_luong + "s") : null,
          h("span", { class: "chipk" }, `${tpl.nodes.length} node`)),
        h("div", { class: "muted" }, "Công cụ: " + (tools.join(", ") || "—")),
        h("details", {}, h("summary", {}, `Các bước (${steps.length})`), h("ol", {}, steps.map(n => h("li", {}, (n.ten || T(n.type).ten) + (n.provider ? ` — ${S.reg.nha_cung_cap[n.provider]?.ten || n.provider}` : ""))))),
        h("h4", {}, "Điền thông tin"),
        field("Tên dự án", nameInp),
        form,
        h("label", { class: "check" }, runNow, "Chạy luôn sau khi tạo (các bước trả phí vẫn hỏi lại)"),
        h("div", { class: "row" },
          h("button", { class: "btn primary", onclick: () => createFromTemplate(tpl, id, nameInp.value, fields, values, files, runNow.checked) }, "🎬 Tạo video từ mẫu này"),
          S.pid && !S.tpl ? h("button", { class: "btn", onclick: () => createFromTemplate(tpl, id, null, fields, values, files, runNow.checked) }, "Áp vào dự án đang mở") : null,
          h("button", { class: "btn", onclick: () => { dlg.close(); dlg.classList.remove("wide"); editTemplate(id); } }, "✎ Sửa mẫu")))));
}
async function createFromTemplate(tpl, id, projectName, fields, values, files, runNow) {
  if (projectName !== null) {
    if (!projectName.trim()) return alert("Nhập tên dự án");
    const r = await post("/api/projects", { ten: projectName.trim() });
    if (!r.ok) return alert(r.body?.loi || "Không tạo được dự án");
    await loadProjects(r.body.id);
  } else if (S.wf.nodes.length && !confirm("Thay workflow hiện tại của dự án bằng mẫu «" + tpl.ten + "»?")) return;
  setSave("Đang áp mẫu…");
  await post(`/api/workflow/${encodeURIComponent(S.pid)}/tu-mau`, { mau: id });
  await openProject(S.pid);
  for (const f of fields) {
    const key = f.node + "." + f.param, n = node(f.node);
    if (!n) continue;
    if (f.loai === "textarea") { n.params = { ...(n.params || {}), [f.param]: values[key] ?? "" }; continue; }
    const file = files[key];
    if (!file) continue;
    setSave("Đang tải " + file.name + "…");
    const data = await new Promise(res => { const rd = new FileReader(); rd.onload = () => res(rd.result); rd.readAsDataURL(file); });
    const r = await post(`/api/wf-node/${encodeURIComponent(S.pid)}/${encodeURIComponent(n.id)}`, { action: "tai_file", ten_file: file.name, du_lieu: data });
    if (r.ok) n.params = { ...(n.params || {}), file: r.body.duong_dan };
  }
  await save();
  dlg.close(); dlg.classList.remove("wide");
  fit(); render();
  if (runNow) runAll();
}
$("#tplBtn").addEventListener("click", openTemplates);
$("#tplExit").addEventListener("click", exitTemplate);
$("#saveTpl").addEventListener("click", async () => {
  if (S.tpl) { await save(); return alert("Đã lưu mẫu"); }
  if (!S.pid || !S.wf.nodes.length) return alert("Workflow đang trống");
  const ten = prompt("Tên mẫu:"); if (!ten) return;
  if (S.dirty) await save();
  const r = await post("/api/mau-workflow", { ten, tu_du_an: S.pid, mo_ta: prompt("Mô tả ngắn (tuỳ chọn):") || "", meta: S.wf.meta || {} });
  alert(r.ok ? "Đã lưu mẫu «" + ten + "»" : (r.body?.loi || "Lỗi"));
});
$("#settingsBtn").addEventListener("click", async () => {
  const keys = (await api("/api/cai-dat/khoa")).body || {};
  const rows = [["openai", "key", "OpenAI API key"], ["google", "key", "Google Gemini API key"], ["elevenlabs", "key", "ElevenLabs API key"],
    ["tripo", "key", "Tripo3D API key"], ["higgsfield", "key_id", "Higgsfield Key ID"], ["higgsfield", "key_secret", "Higgsfield Key Secret"]];
  const inputs = {};
  fill(dlg, h("h3", {}, "⚙ API key"),
    h("p", { class: "muted" }, "Key chỉ lưu trên máy bạn (cai-dat/khoa-api.json), không đưa lên GitHub. Để trống = giữ key cũ; gõ dấu - để xoá."),
    h("div", { class: "keys" }, rows.map(([svc, f, label]) => { const i = h("input", { type: "password", placeholder: keys[svc]?.[f] || "chưa có", autocomplete: "off" }); (inputs[svc] ||= {})[f] = i; return [h("span", {}, label), i]; })),
    h("p", { class: "muted" }, "Higgsfield qua MCP (không cần key) vẫn dùng được bằng nhà cung cấp «Higgsfield (qua Claude/MCP)»."),
    h("div", { class: "row" }, h("button", { class: "btn primary", onclick: async () => {
      const body = {}; for (const [svc, fs] of Object.entries(inputs)) for (const [f, i] of Object.entries(fs)) if (i.value) (body[svc] ||= {})[f] = i.value;
      await api("/api/cai-dat/khoa", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); dlg.close();
    } }, "Lưu"), h("button", { class: "btn", onclick: () => dlg.close() }, "Huỷ")));
  dlg.showModal();
});
window.addEventListener("beforeunload", e => { if (S.dirty) { e.preventDefault(); e.returnValue = ""; } });
window.addEventListener("resize", () => drawEdges());

init();
