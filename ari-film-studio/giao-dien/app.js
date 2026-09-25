// Ari Film Studio — bảng điều khiển. JavaScript thuần, không cần build.
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
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat()) if (kid != null && kid !== false) el.append(kid.nodeType ? kid : document.createTextNode(kid));
  return el;
};

const TRANG_THAI_TEN = { nhap: "Nháp", cho_duyet: "Chờ duyệt", da_duyet: "Đã duyệt", can_sua: "Cần sửa" };
const SHOT_TT_TEN = { ...TRANG_THAI_TEN, dang_tao: "Đang tạo", xong: "Xong", loi: "Lỗi" };
const REF_GROUPS = [
  ["nhan_vat", "Nhân vật / mặt người mẫu", "nhan-vat", "NV"],
  ["trang_phuc", "Trang phục", "trang-phuc", "TP"],
  ["san_pham", "Sản phẩm", "san-pham", "SP"],
  ["boi_canh", "Bối cảnh", "boi-canh", "BC"],
  ["khac", "Khác (phong cách, ánh sáng, moodboard)", "khac", "K"],
];

const state = { pid: null, data: null, version: null, lib: null, active: "1_y_tuong", dirty: false, saving: false, saveTimer: null };

// ---------------- API ----------------
async function api(path, opts = {}) {
  const res = await fetch(path, opts);
  let body = null;
  try { body = await res.json(); } catch (_) {}
  return { ok: res.ok, status: res.status, body, version: res.headers.get("X-Version") };
}

async function loadLibrary() { state.lib = (await api("/api/library")).body; }

async function loadProjects(selectId) {
  const list = (await api("/api/projects")).body || [];
  const sel = $("#projectSelect");
  sel.replaceChildren(h("option", { value: "" }, list.length ? "— Chọn dự án —" : "(chưa có dự án)"),
    ...list.map(p => h("option", { value: p.id }, p.ten)));
  const want = selectId || localStorage.getItem("studio.pid");
  if (want && list.some(p => p.id === want)) { sel.value = want; await openProject(want); }
}

async function openProject(pid) {
  const r = await api(`/api/project/${encodeURIComponent(pid)}`);
  if (!r.ok) { showBanner(r.body?.loi || "Không mở được dự án"); return; }
  state.pid = pid; state.data = r.body; state.version = r.version; state.dirty = false;
  try { localStorage.setItem("studio.pid", pid); } catch (_) {}
  hideBanner(); render();
}

function markDirty() {
  state.dirty = true; setSave("Chưa lưu…");
  clearTimeout(state.saveTimer);
  state.saveTimer = setTimeout(save, 700);
}

async function save() {
  if (!state.pid || state.saving) return;
  state.saving = true;
  const r = await api(`/api/project/${encodeURIComponent(state.pid)}`, {
    method: "PUT", headers: { "Content-Type": "application/json", "If-Match": state.version || "" },
    body: JSON.stringify(state.data),
  });
  state.saving = false;
  if (r.ok) { state.version = r.version; state.dirty = false; setSave("Đã lưu " + new Date().toLocaleTimeString()); }
  else if (r.status === 409) {
    setSave("Xung đột");
    showBanner("Claude vừa cập nhật dự án trong lúc bạn đang sửa. Thay đổi mới nhất của bạn chưa được lưu.",
      [["Tải bản của Claude", () => openProject(state.pid)], ["Ghi đè bằng bản của tôi", async () => { state.version = r.version; hideBanner(); await save(); }]]);
  } else setSave("Lỗi lưu: " + (r.body?.loi || r.status));
}

// Theo dõi khi Claude Code sửa project.json
setInterval(async () => {
  if (!state.pid || state.saving) return;
  const r = await api(`/api/version/${encodeURIComponent(state.pid)}`);
  if (!r.ok || !r.body?.version || r.body.version === state.version) return;
  if (!state.dirty) { await openProject(state.pid); setSave("Đã tải bản mới từ Claude"); }
  else showBanner("Claude vừa cập nhật dự án.", [["Tải lại (bỏ thay đổi chưa lưu)", () => openProject(state.pid)]]);
}, 3000);

function setSave(t) { $("#saveState").textContent = t; }
function showBanner(msg, actions = []) {
  const b = $("#banner");
  b.replaceChildren(h("span", {}, msg), ...actions.map(([t, fn]) => h("button", { class: "btn small", onclick: fn }, t)));
  b.classList.remove("hidden");
}
function hideBanner() { $("#banner").classList.add("hidden"); }

// ---------------- helpers ----------------
const K = code => state.data.khung[code];
const ND = code => K(code).noi_dung;
function libOptions(kind) { return (state.lib?.[kind] || []).map(x => ({ value: x.id, label: x.ten })); }
function opt(list) { return (state.lib?.tuy_chon?.[list] || []).map(v => ({ value: v, label: v })); }
function fileUrl(rel) { return rel ? `/files/${encodeURIComponent(state.pid)}/${rel.split("/").map(encodeURIComponent).join("/")}` : ""; }

function input(obj, key, type = "text", extra = {}) {
  if (type === "textarea") return h("textarea", { ...extra, oninput: e => { obj[key] = e.target.value; markDirty(); } }, obj[key] ?? "");
  if (type === "number") return h("input", { type: "number", step: "any", value: obj[key] ?? "", ...extra, oninput: e => { obj[key] = e.target.value === "" ? null : Number(e.target.value); markDirty(); } });
  if (type === "bool") return h("input", { type: "checkbox", checked: obj[key], ...extra, onchange: e => { obj[key] = e.target.checked; markDirty(); render(); } });
  return h("input", { type: "text", value: obj[key] ?? "", ...extra, oninput: e => { obj[key] = e.target.value; markDirty(); } });
}

// Ô chọn có danh sách gợi ý nhưng vẫn cho gõ tự do
let dlCounter = 0;
function combo(obj, key, options, extra = {}) {
  const id = "dl" + (++dlCounter);
  return h("div", { class: "combo" }, h("input", { type: "text", list: id, value: obj[key] ?? "", ...extra, oninput: e => { obj[key] = e.target.value; markDirty(); } }),
    h("datalist", { id }, options.map(o => h("option", { value: o.value }, o.label !== o.value ? o.label : null))));
}
function select(obj, key, options, onchange) {
  return h("select", { onchange: e => { obj[key] = e.target.value; markDirty(); onchange && onchange(); } },
    h("option", { value: "" }, "—"), options.map(o => h("option", { value: o.value, selected: obj[key] === o.value }, o.label)));
}
function field(label, control, wide) { return h("label", { class: "field" + (wide ? " wide" : "") }, h("span", {}, label), control); }
function strList(arr, placeholder) {
  const wrap = h("div", { class: "options-list" });
  const draw = () => wrap.replaceChildren(
    ...arr.map((v, i) => h("div", { class: "chips" },
      h("input", { type: "text", value: v, placeholder, style: "flex:1", oninput: e => { arr[i] = e.target.value; markDirty(); } }),
      h("button", { class: "btn small danger", onclick: () => { arr.splice(i, 1); markDirty(); draw(); } }, "Xoá"))),
    h("button", { class: "btn small", onclick: () => { arr.push(""); markDirty(); draw(); } }, "+ Thêm"));
  draw(); return wrap;
}

// Bảng lưới dùng chung: cols = [{key,label,type,options,cls}]
function grid(rows, cols, { newRow, lockable = true, filter } = {}) {
  const wrap = h("div", { class: "gridwrap" });
  const draw = () => {
    const head = h("tr", {}, lockable ? h("th", {}, "🔒") : null, cols.map(c => h("th", { title: c.help || "" }, c.label)), h("th", {}, ""));
    const body = rows.map((row, i) => {
      if (filter && !filter(row)) return null;
      const locked = lockable && row.khoa;
      return h("tr", { class: locked ? "locked" : "" },
        lockable ? h("td", { title: "Khoá dòng: AI sẽ không sửa dòng này" }, input(row, "khoa", "bool")) : null,
        cols.map(c => h("td", { class: c.cls || "" }, cell(row, c))),
        h("td", { class: "rowops" },
          h("button", { class: "btn small", title: "Lên", onclick: () => { if (i > 0) { [rows[i - 1], rows[i]] = [rows[i], rows[i - 1]]; markDirty(); draw(); } } }, "↑"),
          h("button", { class: "btn small", title: "Xuống", onclick: () => { if (i < rows.length - 1) { [rows[i + 1], rows[i]] = [rows[i], rows[i + 1]]; markDirty(); draw(); } } }, "↓"),
          h("button", { class: "btn small", title: "Nhân bản", onclick: () => { rows.splice(i + 1, 0, { ...structuredClone(row), id: (row.id || "") + "b", khoa: false }); markDirty(); draw(); } }, "⧉"),
          h("button", { class: "btn small danger", title: "Xoá", onclick: () => { if (confirm("Xoá dòng này?")) { rows.splice(i, 1); markDirty(); draw(); } } }, "✕")));
    });
    wrap.replaceChildren(h("table", { class: "grid" }, h("thead", {}, head), h("tbody", {}, body)),
      newRow ? h("div", { style: "padding:6px" }, h("button", { class: "btn small", onclick: () => { rows.push(newRow(rows)); markDirty(); draw(); } }, "+ Thêm dòng")) : null);
  };
  draw(); return wrap;
}

function cell(row, c) {
  switch (c.type) {
    case "textarea": return input(row, c.key, "textarea");
    case "number": return input(row, c.key, "number");
    case "combo": return combo(row, c.key, c.options());
    case "select": return select(row, c.key, c.options());
    case "list": return h("input", { type: "text", value: (row[c.key] || []).join(", "), placeholder: c.placeholder || "", oninput: e => { row[c.key] = e.target.value.split(",").map(s => s.trim()).filter(Boolean); markDirty(); } });
    case "image": return row[c.key] ? h("a", { href: fileUrl(row[c.key]), target: "_blank" }, h("img", { class: "thumb", src: fileUrl(row[c.key]), alt: "" })) : h("span", { class: "status" }, "—");
    case "video": return row[c.key] ? h("video", { class: "thumb", src: fileUrl(row[c.key]), controls: true, preload: "metadata" }) : h("span", { class: "status" }, "—");
    case "readonly": return h("span", { class: "status" }, String(row[c.key] ?? ""));
    default: return input(row, c.key);
  }
}

// ---------------- khung ----------------
const SHOT_TT = () => Object.entries(SHOT_TT_TEN).map(([value, label]) => ({ value, label }));
const sceneIds = () => ND("5_kich_ban").canh.map(c => ({ value: c.id, label: `${c.id} ${c.tieu_de || ""}` }));
const refIds = () => REF_GROUPS.flatMap(([g]) => ND("3_tham_chieu")[g].map(r => ({ value: r.id, label: `${r.id} ${r.ten || ""}` })));

const PANELS = {
  "1_y_tuong": () => {
    const n = ND("1_y_tuong");
    const chosen = n.phuong_an.findIndex(p => p.chon);
    return [
      h("div", { class: "form" },
        field("Logline (1 câu tóm tắt câu chuyện)", input(n, "logline"), true),
        field("Cốt truyện / ý tưởng chi tiết", input(n, "cot_truyen", "textarea", { rows: 5 }), true),
        field("Thể loại", combo(n, "the_loai", libOptions("the_loai"))),
        field("Thông điệp", input(n, "thong_diep")),
        field("Khán giả mục tiêu", input(n, "doi_tuong")),
        field("Nền tảng đăng", input(n, "nen_tang", "text", { placeholder: "Facebook, TikTok, YouTube, TV…" })),
        field("Thời lượng (giây)", input(n, "thoi_luong_giay", "number")),
        field("Tỉ lệ khung hình", combo(n, "ti_le_khung", opt("ti_le_khung")))),
      h("h3", {}, "Phương án ý tưởng do AI đề xuất"),
      n.phuong_an.length ? h("div", { class: "options-list" }, n.phuong_an.map((p, i) =>
        h("div", { class: "option" + (i === chosen ? " chosen" : "") },
          h("input", { type: "radio", name: "pa", checked: i === chosen, onchange: () => { n.phuong_an.forEach((x, j) => x.chon = j === i); markDirty(); render(); } }),
          h("div", {}, h("b", {}, p.tieu_de || `Phương án ${i + 1}`), h("div", {}, p.mo_ta || ""))))) :
        h("p", { class: "sub" }, "Chưa có. Gõ ý tưởng thô vào ô cốt truyện rồi chạy /tiep-tuc — Đạo Diễn và Biên Kịch sẽ đề xuất 3 phương án để bạn chọn."),
    ];
  },

  "2_phong_cach": () => {
    const n = ND("2_phong_cach");
    const styles = libOptions("phong_cach");
    const cur = state.lib.phong_cach.find(s => s.id === n.phong_cach_chinh);
    return [
      h("div", { class: "form" },
        field("Phong cách chính (từ thư viện)", select(n, "phong_cach_chinh", styles, render)),
        field("Chuyên gia thể loại", select(n, "the_loai_chuyen_gia", libOptions("the_loai"))),
        field("Tinh thần / mood", input(n, "tinh_than", "text", { placeholder: "tĩnh lặng, sang trọng, hoài niệm…" }), true)),
      cur ? h("p", { class: "sub" }, "Xem chi tiết: ", h("a", { href: "/" + cur.file, target: "_blank" }, cur.file)) : null,
      h("h3", {}, "Kết hợp thêm phong cách (lấy một phần yếu tố)"),
      h("div", { class: "chips" }, styles.filter(s => s.value !== n.phong_cach_chinh).map(s =>
        h("label", { class: "chip" }, h("input", { type: "checkbox", checked: n.ket_hop.includes(s.value), onchange: e => {
          n.ket_hop = e.target.checked ? [...n.ket_hop, s.value] : n.ket_hop.filter(x => x !== s.value); markDirty(); } }), s.label)),
        styles.length <= 1 ? h("span", { class: "sub" }, "Thư viện mới có 1 phong cách — thêm bằng lệnh /hoc-hoi kèm video mẫu.") : null),
      h("h3", {}, "Bảng màu"),
      colorChips(n.bang_mau),
      field("Ghi chú phong cách", input(n, "ghi_chu", "textarea"), true),
    ];
  },

  "3_tham_chieu": () => {
    const n = ND("3_tham_chieu");
    return REF_GROUPS.map(([key, title, folder, prefix]) => h("div", { class: "refgroup" },
      h("h3", {}, title),
      h("div", { class: "refcards" },
        n[key].map((r, i) => h("div", { class: "refcard" },
          h("div", { class: "chips" }, h("b", {}, r.id), input(r, "ten", "text", { placeholder: "Tên", style: "flex:1" })),
          input(r, "mo_ta", "textarea", { placeholder: "Mô tả chi tiết (AI dùng để giữ nhất quán)", rows: 3 }),
          h("div", { class: "imgs" }, (r.anh || []).map((a, j) => h("span", { title: a },
            h("img", { src: fileUrl(a), alt: "", onclick: () => { if (confirm("Bỏ ảnh này khỏi thẻ?")) { r.anh.splice(j, 1); markDirty(); render(); } } })))),
          dropZone(folder, path => { (r.anh ||= []).push(path); markDirty(); render(); }),
          h("button", { class: "btn small danger", onclick: () => { if (confirm("Xoá thẻ " + r.id + "?")) { n[key].splice(i, 1); markDirty(); render(); } } }, "Xoá thẻ"))),
        h("button", { class: "btn", onclick: () => { n[key].push({ id: nextId(n[key], prefix), ten: "", mo_ta: "", anh: [] }); markDirty(); render(); } }, "+ Thêm thẻ"))));
  },

  "4_ep_canh": () => {
    const n = ND("4_ep_canh");
    return [
      h("p", { class: "sub" }, "Những điều AI bắt buộc phải làm theo. Mọi agent đọc khung này trước khi làm việc và không được bỏ qua."),
      h("h3", {}, "Áp dụng cho toàn phim"),
      strList(n.toan_phim, "VD: Người mẫu luôn đeo bông tai SP1 bên tai trái"),
      h("h3", {}, "Áp dụng cho cảnh / shot cụ thể"),
      grid(n.theo_canh, [
        { key: "canh", label: "Cảnh hoặc shot", type: "combo", options: () => [...sceneIds(), ...ND("6_storyboard").shots.map(s => ({ value: s.id, label: s.id }))] },
        { key: "yeu_cau", label: "Yêu cầu bắt buộc", type: "textarea" },
      ], { newRow: () => ({ canh: "", yeu_cau: "" }), lockable: false }),
    ];
  },

  "5_kich_ban": () => {
    const n = ND("5_kich_ban");
    const total = n.canh.reduce((s, c) => s + (Number(c.thoi_luong_giay) || 0), 0);
    return [
      h("p", { class: "sub" }, `${n.canh.length} cảnh · tổng ${total}s / mục tiêu ${ND("1_y_tuong").thoi_luong_giay || "?"}s`),
      grid(n.canh, [
        { key: "id", label: "Mã", cls: "w-xs" },
        { key: "tieu_de", label: "Tiêu đề" },
        { key: "dia_diem", label: "Địa điểm" },
        { key: "thoi_diem", label: "Thời điểm" },
        { key: "tom_tat", label: "Diễn biến", type: "textarea" },
        { key: "thoai", label: "Lời thoại / VO", type: "textarea" },
        { key: "cam_xuc", label: "Cảm xúc" },
        { key: "am_thanh", label: "Âm thanh", type: "textarea" },
        { key: "nhan_vat", label: "Nhân vật", type: "list", placeholder: "NV1, NV2" },
        { key: "thoi_luong_giay", label: "Giây", type: "number", cls: "w-xs" },
      ], { newRow: rows => ({ id: nextId(rows, "C"), tieu_de: "", dia_diem: "", thoi_diem: "", tom_tat: "", thoai: "", cam_xuc: "", am_thanh: "", nhan_vat: [], thoi_luong_giay: 5, khoa: false }) }),
    ];
  },

  "6_storyboard": () => shotsPanel([
    { key: "id", label: "Shot", cls: "w-xs" },
    { key: "canh", label: "Cảnh", type: "select", options: sceneIds },
    { key: "thoi_luong", label: "Giây", type: "number", cls: "w-xs" },
    { key: "anh_storyboard", label: "Storyboard", type: "image" },
    { key: "noi_dung", label: "Nội dung hình ảnh", type: "textarea" },
    { key: "co_canh", label: "Cỡ cảnh", type: "combo", options: () => opt("co_canh") },
    { key: "goc_may", label: "Góc máy", type: "combo", options: () => opt("goc_may") },
    { key: "chuyen_dong", label: "Chuyển động", type: "combo", options: () => opt("chuyen_dong") },
    { key: "tieu_cu", label: "Tiêu cự", type: "combo", options: () => opt("tieu_cu") },
    { key: "thiet_bi", label: "Máy / phụ kiện", type: "combo", options: () => [...opt("thiet_bi"), ...opt("phu_kien_may")] },
    { key: "anh_sang", label: "Ánh sáng", type: "combo", options: () => opt("anh_sang") },
    { key: "tham_chieu", label: "Tham chiếu", type: "list", placeholder: "NV1, SP1" },
    { key: "ep_canh", label: "Ép cảnh (bắt buộc)", type: "textarea" },
    { key: "trang_thai", label: "Trạng thái", type: "select", options: SHOT_TT },
  ]),

  "7_san_xuat": () => {
    const n = ND("7_san_xuat");
    return [
      h("div", { class: "form" }, field("Công cụ mặc định", select(n, "cong_cu_mac_dinh", libOptions("cong_cu")))),
      h("p", { class: "sub" }, "Các shot có cùng mã Clip sẽ được tạo chung trong một lần (VD: Seedance 2.5 tạo nhiều shot liền trong 30s)."),
      shotsPanel([
        { key: "id", label: "Shot", cls: "w-xs" },
        { key: "clip", label: "Clip", cls: "w-xs" },
        { key: "thoi_luong", label: "Giây", type: "number", cls: "w-xs" },
        { key: "anh_storyboard", label: "Storyboard", type: "image" },
        { key: "cong_cu", label: "Công cụ", type: "select", options: () => libOptions("cong_cu") },
        { key: "prompt", label: "Prompt", type: "textarea" },
        { key: "video", label: "Video", type: "video" },
        { key: "trang_thai", label: "Trạng thái", type: "select", options: SHOT_TT },
        { key: "ghi_chu_nguoi_dung", label: "Nhắn AI", type: "textarea" },
      ], false),
      h("h3", {}, "Nhật ký sản xuất"),
      h("div", { class: "log" }, n.nhat_ky.slice().reverse().map(l => h("div", {}, `${l.luc || ""} · ${l.shot || l.clip || ""} · ${l.cong_cu || ""} · ${l.ket_qua || ""}`))),
    ];
  },

  "8_dung_phim": () => {
    const n = ND("8_dung_phim");
    return [
      h("div", { class: "form" },
        field("Nhạc nền (đường dẫn trong dự án)", input(n, "nhac", "text", { placeholder: "am-thanh/nhac.mp3" })),
        field("Âm lượng nhạc (0–1)", input(n, "am_luong_nhac", "number")),
        field("Chuyển cảnh mặc định", select(n, "chuyen_canh_mac_dinh", Object.entries(state.lib.tuy_chon.chuyen_canh_mo_ta).map(([value, label]) => ({ value, label })))),
        field("Độ phân giải", input(n, "do_phan_giai")),
        field("FPS", input(n, "fps", "number")),
        field("File xuất", input(n, "xuat")),
        field("Ghi chú dựng (nhịp, cảm xúc, màu)", input(n, "ghi_chu", "textarea"), true)),
      h("h3", {}, "Timeline"),
      grid(n.danh_sach, [
        { key: "shot", label: "Shot", type: "combo", options: () => ND("6_storyboard").shots.map(s => ({ value: s.id, label: s.id })) },
        { key: "video", label: "Video", type: "video" },
        { key: "cat_dau", label: "Cắt đầu (s)", type: "number", cls: "w-xs" },
        { key: "cat_cuoi", label: "Cắt cuối (s)", type: "number", cls: "w-xs" },
        { key: "chuyen_canh", label: "Chuyển sang shot sau", type: "select", options: () => Object.entries(state.lib.tuy_chon.chuyen_canh_mo_ta).map(([value, label]) => ({ value, label })) },
        { key: "do_dai_chuyen", label: "Độ dài chuyển (s)", type: "number", cls: "w-xs" },
      ], { newRow: () => ({ shot: "", video: "", cat_dau: 0, cat_cuoi: null, chuyen_canh: "", do_dai_chuyen: 0.5 }), lockable: false }),
      h("h3", {}, "Bản xuất"),
      h("video", { src: fileUrl(n.xuat) + "?t=" + Date.now(), controls: true, style: "max-width:100%;max-height:360px", onerror: e => e.target.replaceWith(h("p", { class: "sub" }, "Chưa có bản xuất — chạy /dung-phim trong Claude Code.")) }),
    ];
  },

  "9_kiem_dinh": () => {
    const n = ND("9_kiem_dinh");
    return n.bao_cao.length ? n.bao_cao.slice().reverse().map(b => h("div", { class: "report" },
      h("b", {}, `${b.luc || ""} · ${b.khung || "toàn phim"} · điểm ${b.diem ?? "?"}/10`),
      h("ul", {}, (b.van_de || []).map(v => h("li", {}, h("span", { class: "sev-" + (v.muc_do || "thap") }, `[${v.muc_do || "thấp"}] `), v.mo_ta, v.de_xuat ? ` → ${v.de_xuat}` : ""))),
      b.ket_luan ? h("div", {}, b.ket_luan) : null)) :
      h("p", { class: "sub" }, "Chưa có báo cáo. Chạy /kiem-tra trong Claude Code — Kiểm Định sẽ đối chiếu kịch bản, tham chiếu, ép cảnh và video.");
  },
};

function shotsPanel(cols, withAdd = true) {
  const shots = ND("6_storyboard").shots;
  const total = shots.reduce((s, x) => s + (Number(x.thoi_luong) || 0), 0);
  const filterSel = h("select", { onchange: e => { state.sceneFilter = e.target.value; render(); } },
    h("option", { value: "" }, "Tất cả cảnh"), sceneIds().map(o => h("option", { value: o.value, selected: state.sceneFilter === o.value }, o.label)));
  return h("div", {},
    h("div", { class: "chips", style: "margin-bottom:8px" }, filterSel, h("span", { class: "sub", style: "margin:0" }, `${shots.length} shot · ${total}s`)),
    grid(shots, cols, {
      newRow: withAdd ? rows => ({ id: nextId(rows, "S"), canh: state.sceneFilter || "", clip: "", thoi_luong: 3, noi_dung: "", co_canh: "", goc_may: "", chuyen_dong: "", tieu_cu: "", thiet_bi: "", anh_sang: "", tham_chieu: [], ep_canh: "", cong_cu: "", prompt: "", anh_storyboard: "", video: "", trang_thai: "nhap", ghi_chu_nguoi_dung: "", khoa: false }) : null,
      filter: state.sceneFilter ? r => r.canh === state.sceneFilter : null,
    }));
}

function colorChips(arr) {
  const wrap = h("div", { class: "chips" });
  const draw = () => wrap.replaceChildren(...arr.map((c, i) => h("span", { class: "chip" },
    h("input", { type: "color", value: /^#[0-9a-f]{6}$/i.test(c.ma || "") ? c.ma : "#cccccc", oninput: e => { c.ma = e.target.value; markDirty(); } }),
    h("input", { type: "text", value: c.ten || "", placeholder: "tên màu", style: "width:110px", oninput: e => { c.ten = e.target.value; markDirty(); } }),
    h("button", { class: "btn small danger", onclick: () => { arr.splice(i, 1); markDirty(); draw(); } }, "✕"))),
    h("button", { class: "btn small", onclick: () => { arr.push({ ma: "#cccccc", ten: "" }); markDirty(); draw(); } }, "+ Màu"));
  draw(); return wrap;
}

function dropZone(folder, onDone) {
  const inputEl = h("input", { type: "file", accept: "image/*,video/*", multiple: true, class: "hidden", onchange: e => upload([...e.target.files]) });
  const zone = h("div", { class: "drop", onclick: () => inputEl.click(),
    ondragover: e => { e.preventDefault(); zone.classList.add("over"); },
    ondragleave: () => zone.classList.remove("over"),
    ondrop: e => { e.preventDefault(); zone.classList.remove("over"); upload([...e.dataTransfer.files]); } }, "Kéo ảnh vào đây hoặc bấm để chọn", inputEl);
  async function upload(files) {
    for (const f of files) {
      const data = await new Promise(res => { const r = new FileReader(); r.onload = () => res(r.result); r.readAsDataURL(f); });
      const r = await api(`/api/upload/${encodeURIComponent(state.pid)}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ loai: folder, ten_file: f.name, du_lieu: data }) });
      if (r.ok) onDone(r.body.duong_dan); else alert("Tải lên lỗi: " + (r.body?.loi || r.status));
    }
  }
  return zone;
}

function nextId(rows, prefix) {
  let max = 0;
  for (const r of rows) { const m = String(r.id || "").match(/(\d+)/); if (m) max = Math.max(max, Number(m[1])); }
  return prefix + String(max + 1).padStart(2, "0");
}

// ---------------- render ----------------
const CMD = {
  "1_y_tuong": ["/tiep-tuc", "Đạo Diễn + Biên Kịch đề xuất 3 phương án ý tưởng"],
  "2_phong_cach": ["/tiep-tuc", "Chỉ Đạo Hình Ảnh đề xuất phong cách, bảng màu"],
  "3_tham_chieu": ["/tiep-tuc", "Chỉ Đạo Hình Ảnh viết hồ sơ nhân vật/sản phẩm từ ảnh"],
  "4_ep_canh": ["/tiep-tuc", "Đạo Diễn ghi nhận yêu cầu bắt buộc"],
  "5_kich_ban": ["/tiep-tuc", "Biên Kịch viết kịch bản theo cảnh"],
  "6_storyboard": ["/tiep-tuc", "Quay Phim chia shot, chọn máy/ống kính; Họa Sĩ vẽ storyboard"],
  "7_san_xuat": ["/tao-video", "Kỹ Thuật Viên AI chọn công cụ, viết prompt, tạo video"],
  "8_dung_phim": ["/dung-phim", "Biên Tập Viên sắp timeline và xuất phim"],
  "9_kiem_dinh": ["/kiem-tra", "Kiểm Định chấm điểm và báo lỗi"],
};

function render() {
  const d = state.data;
  $("#empty").classList.toggle("hidden", !!d);
  $("#panel").classList.toggle("hidden", !d);
  if (!d) { $("#pipeline").replaceChildren(); return; }
  $("#modeSelect").value = d.che_do || "tung_buoc";

  $("#pipeline").replaceChildren(...Object.entries(d.khung).map(([code, k], i) =>
    h("button", { class: "step" + (code === state.active ? " active" : ""), onclick: () => { state.active = code; render(); } },
      h("span", { class: "dot st-" + k.trang_thai, title: TRANG_THAI_TEN[k.trang_thai] }),
      h("div", { class: "num" }, `Khung ${i + 1}`), h("div", { class: "name" }, k.ten), h("div", { class: "who" }, k.phu_trach),
      k.khoa ? h("span", { class: "lock-ico", title: "Đã khoá" }, "🔒") : null)));

  const k = K(state.active);
  const [cmd, hint] = CMD[state.active];
  $("#cmdText").textContent = `${cmd} ${state.pid}`;
  $("#cmdHint").textContent = hint;

  $("#panel").replaceChildren(
    h("h2", {}, k.ten), h("p", { class: "sub" }, `Phụ trách: ${k.phu_trach} · Trạng thái: ${TRANG_THAI_TEN[k.trang_thai]}${k.khoa ? " · 🔒 Đã khoá (AI không được sửa)" : ""}`),
    ...[PANELS[state.active]()].flat(),
    h("div", { class: "footer" },
      field("Lời nhắn của bạn cho AI ở khung này", input(k, "ghi_chu_nguoi_dung", "textarea", { placeholder: "VD: Cảnh 3 cho mưa, bỏ nhân vật phụ…" })),
      h("div", { class: "field" }, h("span", {}, "AI đề xuất / giải thích"), h("div", { class: "ai-note" }, k.de_xuat_ai || "—")),
      h("div", { class: "actions" },
        h("button", { class: "btn primary", onclick: () => { k.trang_thai = "da_duyet"; markDirty(); render(); } }, "✓ Duyệt khung"),
        h("button", { class: "btn", onclick: () => { k.trang_thai = "can_sua"; markDirty(); render(); } }, "↺ Yêu cầu sửa"),
        h("label", { class: "chip", title: "Khoá: AI không được thay đổi nội dung khung này" }, input(k, "khoa", "bool"), "Khoá khung"),
        h("span", { class: "sub", style: "margin:0" }, "Mẹo: khoá từng dòng trong bảng để giữ nguyên, AI chỉ sửa các dòng chưa khoá."))));
}

// ---------------- init ----------------
$("#projectSelect").addEventListener("change", e => e.target.value ? openProject(e.target.value) : null);
$("#modeSelect").addEventListener("change", e => { if (state.data) { state.data.che_do = e.target.value; markDirty(); } });
$("#newProjectBtn").addEventListener("click", async () => {
  const ten = prompt("Tên phim / dự án:");
  if (!ten) return;
  const r = await api("/api/projects", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ten }) });
  if (!r.ok) return alert(r.body?.loi || "Không tạo được");
  state.active = "1_y_tuong"; await loadProjects(r.body.id);
});
$("#copyCmd").addEventListener("click", () => navigator.clipboard?.writeText($("#cmdText").textContent).then(() => setSave("Đã sao chép lệnh")));
window.addEventListener("beforeunload", e => { if (state.dirty) { e.preventDefault(); e.returnValue = ""; } });

(async () => { await loadLibrary(); await loadProjects(); render(); })();
