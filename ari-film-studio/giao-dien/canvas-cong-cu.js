// Ari Film Studio — công cụ thêm cho canvas: kho prompt, bộ chọn máy quay, menu thêm node khi thả dây,
// sao chép/dán node, lịch sử kết quả của node, điền mẫu kiểu hỏi–đáp.
// Dùng chung các hàm của canvas.js (h, fill, S, T, node, changed, post, api, field…). JavaScript thuần, không cần build.
// Ý tưởng tham khảo (không chép mã): Vibe-Workflow (thả dây ra chỗ trống → gợi ý node, lịch sử kết quả),
// Open-Generative-AI (chip máy quay/ống kính ghép prompt), TwitCanva (sao chép/dán node). Xem THAM-KHAO.md.
"use strict";

const PROMPT_KEYS = ["noi_dung", "prompt", "mo_ta", "loi", "yeu_cau"];
const LOAI_PROMPT = { video: "🎬 Video", anh: "🖼 Ảnh", nhac: "🎵 Nhạc", giong: "🎙 Giọng", "hieu-ung": "🔊 Hiệu ứng" };
// Loại prompt → loại node tạo mới khi bấm «Tạo node»
const LOAI_NODE = { video: "tao-video", anh: "tao-anh", nhac: "nhac", giong: "giong-doc", "hieu-ung": "hieu-ung-am" };

// Tham số chứa chữ/prompt chính của một node (null nếu node không có)
function promptKey(n) {
  if (!n) return null;
  const keys = T(n.type).tham_so.map(p => p.key);
  return PROMPT_KEYS.find(k => keys.includes(k)) || null;
}
function setPromptText(n, text, mode = "noi") {
  const k = promptKey(n); if (!k) return false;
  const cur = String(n.params?.[k] || "").trim();
  n.params = { ...(n.params || {}), [k]: mode === "thay" || !cur ? text : cur + "\n" + text };
  changed(); return true;
}
const placeholders = text => [...new Set([...String(text).matchAll(/\{\{\s*([^}]+?)\s*\}\}/g)].map(m => m[1]))];
const fillPlaceholders = (text, vals) => String(text).replace(/\{\{\s*([^}]+?)\s*\}\}/g, (m, k) => (vals[k] || "").trim() || m);
function highlightPh(text) {
  return String(text).split(/(\{\{[^}]+\}\})/g).map(part => part.startsWith("{{") ? h("mark", {}, part) : part);
}
async function copyText(t) {
  try { await navigator.clipboard.writeText(t); setSave("Đã chép prompt"); }
  catch (_) { window.prompt("Chép prompt:", t); }
}

// ---------------------------------------------------------------- 💡 Kho prompt
async function openPrompts(target) {
  const data = (await api("/api/kho-prompt")).body || [];
  const tgt = target ? node(target) : node(S.sel);
  const canInsert = !!promptKey(tgt);
  let tab = (() => { try { return localStorage.getItem("studio.khoPrompt") || ""; } catch (_) { return ""; } })();
  if (!data.some(g => g.id === tab)) tab = S.wf.meta?.nganh ? (data.find(g => g.nganh.toLowerCase().includes(String(S.wf.meta.nganh).toLowerCase()))?.id || data[0]?.id) : data[0]?.id;
  let q = "", loai = "";
  const tabs = h("div", { class: "row tabs" }), list = h("div", { class: "plist" }), loaiRow = h("div", { class: "row" });
  const draw = () => {
    fill(tabs, data.map(g => h("button", { class: "btn small" + (g.id === tab && !q ? " on" : ""), onclick: () => { tab = g.id; q = ""; srch.value = ""; try { localStorage.setItem("studio.khoPrompt", tab); } catch (_) {} draw(); } },
      g.nganh + ` (${g.prompts.length})`)));
    fill(loaiRow, h("button", { class: "btn small" + (!loai ? " on" : ""), onclick: () => { loai = ""; draw(); } }, "Mọi loại"),
      Object.entries(LOAI_PROMPT).map(([k, v]) => h("button", { class: "btn small" + (loai === k ? " on" : ""), onclick: () => { loai = k; draw(); } }, v)));
    const groups = q ? data : data.filter(g => g.id === tab);
    const items = groups.flatMap(g => g.prompts.map(p => ({ ...p, _g: g })))
      .filter(p => (!loai || p.loai === loai) && (!q || (p.ten + " " + p.prompt + " " + (p.ghi_chu || "") + " " + p._g.nganh).toLowerCase().includes(q)));
    const g0 = groups.length === 1 ? groups[0] : null;
    fill(list, g0?.mo_ta ? h("p", { class: "muted" }, g0.mo_ta) : null,
      items.length ? items.map(p => promptCard(p, tgt, canInsert)) : h("p", { class: "muted" }, tab === "cua-toi" ? "Chưa có prompt nào. Bấm ⭐ Lưu vào kho ở một node để lưu." : "Không tìm thấy prompt."));
  };
  const srch = h("input", { type: "search", placeholder: "Tìm trong mọi ngành…", oninput: e => { q = e.target.value.toLowerCase(); draw(); } });
  dlg.classList.add("wide");
  fill(dlg, h("div", { class: "row" }, h("h3", { style: { flex: 1, margin: 0 } }, "💡 Kho prompt"),
      canInsert ? h("span", { class: "chipk" }, "Chèn vào: " + (tgt.ten || T(tgt.type).ten)) : h("span", { class: "muted" }, "Chọn một node trước để chèn thẳng vào node"),
      h("button", { class: "btn", onclick: () => dlg.close() }, "✕")),
    h("div", { style: { margin: "10px 0 6px" } }, srch), tabs, loaiRow, list,
    h("p", { class: "muted" }, "Ô {{…}} là chỗ điền thông tin của bạn. Prompt viết tiếng Anh cho model; giọng đọc viết tiếng Việt. Thêm prompt: sửa thu-vien/kho-prompt/*.json hoặc bấm ⭐ ở node."));
  draw(); if (!dlg.open) dlg.showModal();
}
function promptCard(p, tgt, canInsert) {
  const phs = placeholders(p.prompt), vals = {};
  const out = () => fillPlaceholders(p.prompt, vals);
  const inputs = phs.length ? h("div", { class: "phs" }, phs.map(k => h("input", { type: "text", placeholder: k, oninput: e => { vals[k] = e.target.value; } }))) : null;
  const createNode = () => {
    const type = LOAI_NODE[p.loai] || "prompt";
    addNode(type); const n = node(S.sel);
    if (n) { setPromptText(n, out(), "thay"); if (p.ti_le && n.params && "ti_le" in n.params) n.params.ti_le = p.ti_le; changed(); }
    dlg.close();
  };
  return h("div", { class: "pcard" },
    h("div", { class: "row" }, h("b", { style: { flex: 1 } }, p.ten),
      h("span", { class: "chipk" }, LOAI_PROMPT[p.loai] || p.loai), p.ti_le ? h("span", { class: "chipk" }, p.ti_le) : null,
      p._g && p._g.id !== "cua-toi" ? null : h("button", { class: "btn small danger", title: "Xoá khỏi prompt của tôi", onclick: async () => {
        if (!confirm("Xoá prompt «" + p.ten + "»?")) return; await post("/api/kho-prompt", { xoa: p.id }); openPrompts(tgt?.id); } }, "🗑")),
    (p.cong_cu || []).length ? h("div", { class: "muted" }, "Hợp với: " + p.cong_cu.join(", ")) : null,
    h("div", { class: "ptext" }, highlightPh(p.prompt)),
    p.ghi_chu ? h("div", { class: "muted" }, "💬 " + p.ghi_chu) : null,
    inputs,
    h("div", { class: "row" },
      canInsert ? h("button", { class: "btn small primary", onclick: () => { setPromptText(tgt, out()); dlg.close(); } }, "➕ Chèn vào node") : null,
      S.pid || S.tpl ? h("button", { class: "btn small", onclick: createNode }, "✚ Tạo node mới") : null,
      h("button", { class: "btn small", onclick: () => copyText(out()) }, "📋 Chép")));
}
async function savePromptFromNode(n) {
  const k = promptKey(n), text = String(n?.params?.[k] || "").trim();
  if (!text) return alert("Node chưa có nội dung để lưu");
  const ten = window.prompt("Tên prompt (để tìm lại sau):", (n.ten || T(n.type).ten)); if (ten === null) return;
  const loai = { "tao-anh": "anh", "nhac": "nhac", "giong-doc": "giong", "hieu-ung-am": "hieu-ung" }[n.type] || "video";
  const r = await post("/api/kho-prompt", { ten, prompt: text, loai, ti_le: n.params?.ti_le || "", cong_cu: n.provider ? [S.reg.nha_cung_cap[n.provider]?.ten || n.provider] : [] });
  setSave(r.ok ? "Đã lưu vào 💡 Kho prompt › Của tôi" : "Lỗi lưu prompt");
}

// ---------------------------------------------------------------- 🎥 Bộ chọn máy quay
let MAY_QUAY = null;
async function openCamera(nid) {
  const n = node(nid); if (!promptKey(n)) return;
  MAY_QUAY ||= (await api("/thu-vien/may-quay.json")).body;
  const pick = {}; // nhóm → Set giá trị
  const preview = h("div", { class: "ptext" });
  const text = () => MAY_QUAY.nhom.flatMap(g => [...(pick[g.id] || [])]).join(", ");
  const upd = () => { preview.textContent = text() || "Chọn các mục bên dưới…"; };
  const groups = MAY_QUAY.nhom.map(g => h("div", { class: "field" }, h("span", {}, g.ten + (g.mot ? "" : " (chọn nhiều)")),
    h("div", { class: "row" }, g.lua_chon.map(o => {
      const b = h("button", { class: "btn small chip", title: o.gia_tri, onclick: () => {
        const set = (pick[g.id] ||= new Set());
        if (set.has(o.gia_tri)) set.delete(o.gia_tri);
        else { if (g.mot) { set.clear(); b.parentElement.querySelectorAll(".chip.on").forEach(x => x.classList.remove("on")); } set.add(o.gia_tri); }
        b.classList.toggle("on", set.has(o.gia_tri)); upd(); } }, o.ten);
      return b;
    }))));
  dlg.classList.add("wide");
  fill(dlg, h("div", { class: "row" }, h("h3", { style: { flex: 1, margin: 0 } }, "🎥 Máy quay, ống kính, ánh sáng"), h("span", { class: "chipk" }, n.ten || T(n.type).ten), h("button", { class: "btn", onclick: () => dlg.close() }, "✕")),
    h("p", { class: "muted" }, "Bấm chọn — studio ghép thành câu tiếng Anh và thêm vào cuối prompt của node. Rê chuột lên nút để xem chữ tiếng Anh."),
    groups, h("h4", {}, "Sẽ thêm vào prompt:"), preview,
    h("div", { class: "row" }, h("button", { class: "btn primary", onclick: () => { const t = text(); if (t) setPromptText(n, t.charAt(0).toUpperCase() + t.slice(1) + "."); dlg.close(); } }, "➕ Thêm vào prompt"),
      h("button", { class: "btn", onclick: () => copyText(text()) }, "📋 Chép"), h("button", { class: "btn", onclick: () => dlg.close() }, "Huỷ")));
  upd(); if (!dlg.open) dlg.showModal();
}

// Nút công cụ prompt trong bảng chi tiết node
function promptTools(n) {
  if (!promptKey(n)) return null;
  const cam = ["tao-anh", "tao-video", "prompt", "viet-prompt", "sua-video", "quay-phim"].includes(n.type);
  return h("div", { class: "row" },
    h("button", { class: "btn small", onclick: () => openPrompts(n.id) }, "💡 Kho prompt"),
    cam ? h("button", { class: "btn small", onclick: () => openCamera(n.id) }, "🎥 Máy quay") : null,
    h("button", { class: "btn small", title: "Lưu nội dung node vào 💡 Kho prompt › Của tôi", onclick: () => savePromptFromNode(n) }, "⭐ Lưu vào kho"));
}

// ---------------------------------------------------------------- 🕘 Lịch sử kết quả của node
function historyPanel(n) {
  const hs = n.lich_su || [];
  if (!hs.length) return null;
  const thumb = kq => {
    const v = Object.values(kq || {})[0]; if (!v) return h("span", { class: "muted" }, "—");
    if (v.kieu === "image") return h("img", { src: fileUrl(v.gia_tri), alt: "" });
    if (v.kieu === "video") return h("video", { src: fileUrl(v.gia_tri) + "#t=0.1", muted: true, preload: "metadata", onmouseenter: e => e.target.play().catch(() => {}), onmouseleave: e => e.target.pause() });
    if (v.kieu === "audio") return h("audio", { src: fileUrl(v.gia_tri), controls: true, preload: "none" });
    if (v.kieu === "text") return h("div", { class: "txt" }, String(v.gia_tri).slice(0, 160));
    return h("a", { href: fileUrl(v.gia_tri), target: "_blank" }, v.gia_tri.split("/").pop());
  };
  return h("details", { class: "hist" }, h("summary", {}, `🕘 Các bản trước (${hs.length})`),
    h("div", { class: "hgrid" }, hs.map((x, i) => h("div", { class: "hitem" }, thumb(x.ket_qua),
      h("div", { class: "row" }, h("small", { class: "muted", style: { flex: 1 } }, (x.luc_chay || "").replace("T", " ").slice(0, 16)),
        h("button", { class: "btn small", title: "Dùng bản này làm kết quả (bản hiện tại chuyển vào lịch sử)", onclick: () => useHistory(n.id, i) }, "↩ Dùng"))))),
    h("p", { class: "muted" }, "Mỗi lần chạy lại, bản cũ được giữ ở đây (tối đa 12 bản) — không mất tiền tạo lại."));
}
async function useHistory(nid, idx) {
  if (S.tpl) return;
  if (S.dirty) await save();
  const r = await post(`/api/wf-node/${encodeURIComponent(S.pid)}/${encodeURIComponent(nid)}`, { action: "dung_lich_su", idx });
  if (!r.ok) alert("Không dùng lại được bản này");
  S.version = null; poll();
}

// ---------------------------------------------------------------- Menu thêm node (thả dây ra chỗ trống / chuột phải)
const nmenu = h("div", { class: "nmenu hidden" });
document.body.append(nmenu);
function closeNodeMenu() { nmenu.classList.add("hidden"); }
window.addEventListener("pointerdown", e => { if (!nmenu.contains(e.target)) closeNodeMenu(); }, true);
window.addEventListener("keydown", e => { if (e.key === "Escape") closeNodeMenu(); });
function openNodeMenu(cx, cy, wire) {
  if (!S.pid && !S.tpl) return;
  const at = toWorld(cx, cy);
  // Dây đang kéo từ một đầu ra → chỉ gợi ý node có đầu vào hợp kiểu
  const fits = t => !wire || t.vao.some(p => compatible(wire.kieu, p.kieu));
  const types = S.reg.node.filter(fits);
  let q = "";
  const list = h("div", { class: "nlist" });
  const draw = () => fill(list, S.reg.nhom.map(g => {
    const items = types.filter(t => t.nhom === g && (!q || (t.ten + " " + t.id).toLowerCase().includes(q)));
    return items.length ? [h("h4", {}, g), items.map(t => h("div", { class: "pitem", style: { "--c": GROUP_COLOR[g] }, onclick: () => pick(t) }, t.ten))] : null;
  }));
  const pick = t => {
    closeNodeMenu();
    addNode(t.id, { x: at.x - (wire ? 0 : 118), y: at.y - 20 });
    const n = node(S.sel);
    if (wire && n) {
      const port = t.vao.find(p => p.kieu === wire.kieu) || t.vao.find(p => compatible(wire.kieu, p.kieu));
      if (port) S.wf.edges.push({ id: "e" + Date.now().toString(36) + Math.random().toString(36).slice(2, 5), tu: wire.from, den: { node: n.id, cong: port.id } });
      changed();
    }
  };
  const inp = h("input", { type: "search", placeholder: wire ? `Nối ${S.reg.kieu_cong[wire.kieu]?.ten || ""} vào…` : "Thêm node…", oninput: e => { q = e.target.value.toLowerCase(); draw(); },
    onkeydown: e => { if (e.key === "Enter") { const first = types.find(t => !q || (t.ten + " " + t.id).toLowerCase().includes(q)); if (first) pick(first); } } });
  fill(nmenu, inp, list); draw();
  nmenu.classList.remove("hidden");
  const w = 230, hgt = Math.min(420, window.innerHeight - 20);
  Object.assign(nmenu.style, { left: Math.min(cx, window.innerWidth - w - 10) + "px", top: Math.max(10, Math.min(cy, window.innerHeight - hgt - 10)) + "px", maxHeight: hgt + "px" });
  setTimeout(() => inp.focus(), 0);
}
$("#stage").addEventListener("contextmenu", e => {
  if (e.target.closest(".node")) return;
  e.preventDefault(); openNodeMenu(e.clientX, e.clientY, null);
});

// ---------------------------------------------------------------- Sao chép / dán node (Ctrl+C, Ctrl+V — dán được sang dự án khác)
let lastMouse = null;
$("#stage").addEventListener("pointermove", e => { lastMouse = { x: e.clientX, y: e.clientY }; });
function copyNode(id) {
  const n = node(id); if (!n) return;
  const c = { ...Object.fromEntries(Object.entries(n).filter(([k]) => !RUNTIME.includes(k))), _pid: S.pid };
  try { localStorage.setItem("studio.clip", JSON.stringify(c)); } catch (_) {}
  S.clip = c; setSave("Đã chép node «" + (n.ten || n.type) + "» — Ctrl+V để dán");
}
function pasteNode() {
  let c = S.clip; try { c = JSON.parse(localStorage.getItem("studio.clip")) || c; } catch (_) {}
  if (!c || (!S.pid && !S.tpl)) return;
  snapshot();
  const n = JSON.parse(JSON.stringify(c)); n.id = nextId(); n.trang_thai = "chua_chay"; n.khoa = false;
  const p = lastMouse ? toWorld(lastMouse.x, lastMouse.y) : { x: c.x + 40, y: c.y + 40 };
  n.x = Math.round(p.x - 118); n.y = Math.round(p.y - 20);
  if (n.params?.file && !S.tpl && c._pid !== S.pid) n.params.file = ""; // file thuộc dự án khác
  delete n._pid;
  S.wf.nodes.push(n); S.sel = n.id; S.selEdge = null; changed();
}
window.addEventListener("keydown", e => {
  if (e.target.closest("input, textarea, select") || !(e.ctrlKey || e.metaKey)) return;
  const k = e.key.toLowerCase();
  if (k === "c" && S.sel && !window.getSelection()?.toString()) { e.preventDefault(); copyNode(S.sel); }
  if (k === "v") { e.preventDefault(); pasteNode(); }
});

// ---------------------------------------------------------------- 💬 Điền mẫu kiểu hỏi–đáp
function chatFill(tpl, fields, values, files, onDone) {
  let i = 0;
  const log = h("div", { class: "chat" });
  const box = h("div", { class: "chatbox" });
  const say = (who, ...kids) => { add(log, h("div", { class: "msg " + who }, kids)); log.scrollTop = log.scrollHeight; };
  const questionFor = f => {
    if (f.loai === "textarea") return `${f.ten}?` + (f.goi_y ? ` (${f.goi_y})` : "") + (f.mac_dinh ? "\nGợi ý sẵn: " + f.mac_dinh : "");
    return `Bạn gửi giúp ${f.loai === "image" ? "ảnh" : f.loai === "video" ? "video" : "file âm thanh"}: ${f.ten}` + (f.goi_y ? ` — ${f.goi_y}` : "");
  };
  const next = () => {
    if (i >= fields.length) {
      say("bot", "Xong rồi! Mình đã có đủ thông tin cho mẫu «" + tpl.ten + "». Bấm 🎬 Tạo video từ mẫu này để bắt đầu.");
      fill(box); onDone(); return;
    }
    const f = fields[i], key = f.node + "." + f.param;
    say("bot", questionFor(f));
    const skip = h("button", { class: "btn small", onclick: () => { say("me", h("i", {}, "(bỏ qua)")); i++; next(); } }, "Bỏ qua");
    if (f.loai === "textarea") {
      const ta = h("textarea", { rows: 2, placeholder: "Trả lời…", onkeydown: e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } } }, "");
      const send = () => { const v = ta.value.trim() || f.mac_dinh || ""; values[key] = v; say("me", v || h("i", {}, "(để trống)")); i++; next(); };
      fill(box, ta, h("div", { class: "row" }, h("button", { class: "btn small primary", onclick: send }, "Gửi ↵"),
        f.mac_dinh ? h("button", { class: "btn small", onclick: () => { ta.value = f.mac_dinh; send(); } }, "Dùng gợi ý sẵn") : null, skip,
        h("button", { class: "btn small", title: "Chọn từ kho prompt", onclick: () => pickFromLibrary(ta) }, "💡")));
      setTimeout(() => ta.focus(), 0);
    } else {
      const accept = { image: "image/*", video: "video/*", audio: "audio/*" }[f.loai];
      fill(box, h("div", { class: "row" }, h("input", { type: "file", accept, onchange: e => {
        const file = e.target.files[0]; if (!file) return; files[key] = file;
        say("me", f.loai === "image" ? h("img", { src: URL.createObjectURL(file), alt: "" }) : "📎 " + file.name); i++; next(); } }), skip));
    }
  };
  say("bot", `Chào bạn 👋 Mình hỏi ${fields.length} câu ngắn để làm video theo mẫu «${tpl.ten}».`);
  next();
  return h("div", { class: "chatwrap" }, log, box);
}
// Chọn nhanh một prompt (chữ) từ kho để trả lời trong hỏi–đáp
async function pickFromLibrary(ta) {
  const data = (await api("/api/kho-prompt")).body || [];
  const all = data.flatMap(g => g.prompts.map(p => ({ ...p, g: g.nganh })));
  const menu = h("div", { class: "nmenu", style: { position: "static", maxHeight: "260px" } },
    all.map(p => h("div", { class: "pitem", onclick: () => { ta.value = fillPlaceholders(p.prompt, {}); menu.remove(); ta.focus(); } }, `${p.g} › ${p.ten}`)));
  ta.parentElement.append(menu);
}
$("#promptBtn").addEventListener("click", () => openPrompts());
