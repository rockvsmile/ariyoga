#!/usr/bin/env python3
"""Bộ máy chạy Workflow dạng node của Ari Film Studio.

Mỗi dự án có du-an/<id>/workflow.json:
  {"phien_ban": 1,
   "nodes": [{"id", "type", "x", "y", "ten", "provider", "model", "params": {}, "khoa", "ghi_chu",
              # các trường do bộ máy/Claude ghi (không sửa tay):
              "trang_thai", "loi", "chi_tiet", "ket_qua": {"<cong>": {"kieu", "gia_tri"}}, "luc_chay"}],
   "edges": [{"id", "tu": {"node", "cong"}, "den": {"node", "cong"}}]}

trang_thai: chua_chay | dang_chay | xong | loi | cho_claude | cho_nguoi_dung | cho_duyet
Kết quả dạng file nằm trong du-an/<id>/wf/<node>/, gia_tri là đường dẫn tương đối so với thư mục dự án.

Dòng lệnh (cho Claude Code và người dùng):
  python tools/workflow.py danh-sach <id>                 liệt kê node + trạng thái
  python tools/workflow.py cho-claude <id>                node đang chờ Claude (kèm đầu vào đã giải)
  python tools/workflow.py dau-vao <id> <node>            đầu vào + tham số của một node (JSON)
  python tools/workflow.py ghi <id> <node> <cong> <kieu> <gia_tri|@file>   ghi kết quả, đánh dấu xong
  python tools/workflow.py loi <id> <node> "<thông báo>"  đánh dấu lỗi
  python tools/workflow.py chay <id> [tat_ca|node|den] [node]   chạy (api/máy) — node Claude/thủ công sẽ chờ
"""
import json
import os
import shutil
import sys
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "du-an"
sys.path.insert(0, str(Path(__file__).parent))

RUNTIME = ("trang_thai", "loi", "chi_tiet", "ket_qua", "luc_chay", "cau_hinh_luc_chay")
_locks: dict = {}
_running: dict = {}


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def registry() -> dict:
    with open(ROOT / "thu-vien" / "node-types.json", encoding="utf-8") as f:
        reg = json.load(f)
    reg["_by_id"] = {n["id"]: n for n in reg["node"]}
    return reg


# ---------------------------------------------------------------- lưu / khoá file
class FileLock:
    """Khoá liên tiến trình đơn giản bằng file (chạy được cả Windows lẫn macOS/Linux)."""

    def __init__(self, path: Path, timeout: float = 15):
        self.path, self.timeout = path.with_suffix(".lock"), timeout

    def __enter__(self):
        t0 = time.time()
        while True:
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return self
            except FileExistsError:
                if time.time() - t0 > self.timeout:
                    try:  # khoá mồ côi (tiến trình chết) — gỡ
                        if time.time() - self.path.stat().st_mtime > self.timeout:
                            self.path.unlink()
                            continue
                    except FileNotFoundError:
                        continue
                    raise TimeoutError(f"Đang có tiến trình khác ghi {self.path.name}")
                time.sleep(0.05)

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def wf_path(pid: str) -> Path:
    return PROJECTS / pid / "workflow.json"


def empty_workflow() -> dict:
    # meta: mẫu đã dùng, ngành, thể loại, phong cách, kỹ năng (skill) — agent AI đọc để làm đúng phong cách
    return {"phien_ban": 1, "meta": {}, "nodes": [], "edges": []}


def load(pid: str) -> dict:
    p = wf_path(pid)
    if not p.is_file():
        return empty_workflow()
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _write(pid: str, wf: dict):
    p = wf_path(pid)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def _thread_lock(pid: str) -> threading.Lock:
    return _locks.setdefault(pid, threading.Lock())


def update(pid: str, fn):
    """Đọc – sửa – ghi an toàn. fn(wf) sửa tại chỗ; trả về wf."""
    with _thread_lock(pid), FileLock(wf_path(pid)):
        wf = load(pid)
        fn(wf)
        _write(pid, wf)
        return wf


def save_from_ui(pid: str, incoming: dict) -> dict:
    """Bảng điều khiển gửi cả workflow; giữ nguyên các trường chạy trên đĩa (bộ máy/Claude mới được ghi)."""
    def merge(wf):
        disk = {n["id"]: n for n in wf.get("nodes", [])}
        nodes = []
        for n in incoming.get("nodes", []):
            old = disk.get(n.get("id"))
            n = {k: v for k, v in n.items() if k not in RUNTIME}
            for k in RUNTIME:
                if old and k in old:
                    n[k] = old[k]
            n.setdefault("trang_thai", "chua_chay")
            nodes.append(n)
        wf["nodes"] = nodes
        wf["edges"] = incoming.get("edges", [])
        if "meta" in incoming:
            wf["meta"] = incoming["meta"]
        wf["phien_ban"] = incoming.get("phien_ban", 1)
        wf["cap_nhat"] = now()
    return update(pid, merge)


# ---------------------------------------------------------------- đồ thị
def node_map(wf) -> dict:
    return {n["id"]: n for n in wf.get("nodes", [])}


def upstream(wf, nid: str) -> set:
    return {e["tu"]["node"] for e in wf.get("edges", []) if e["den"]["node"] == nid}


def ancestors(wf, nid: str) -> set:
    seen, stack = set(), [nid]
    while stack:
        for u in upstream(wf, stack.pop()):
            if u not in seen:
                seen.add(u)
                stack.append(u)
    return seen


def resolve_inputs(wf, nid: str) -> dict:
    """{cong_vao: [{"kieu", "gia_tri", "tu"}]} — nhiều nguồn xếp theo vị trí node nguồn (trái → phải, trên → dưới)."""
    nodes = node_map(wf)
    out: dict = {}
    for e in wf.get("edges", []):
        if e["den"]["node"] != nid:
            continue
        src = nodes.get(e["tu"]["node"])
        if not src:
            continue
        val = (src.get("ket_qua") or {}).get(e["tu"]["cong"])
        if val is None and src.get("type") == "duyet":
            val = (src.get("ket_qua") or {}).get("any")
        if val is None:
            continue
        out.setdefault(e["den"]["cong"], []).append(
            {**val, "tu": src["id"], "_x": src.get("x", 0), "_y": src.get("y", 0)})
    for k in out:
        out[k].sort(key=lambda v: (v["_x"], v["_y"]))
        for v in out[k]:
            v.pop("_x", None)
            v.pop("_y", None)
    return out


def inputs_ready(wf, nid: str) -> bool:
    nodes = node_map(wf)
    return all(nodes.get(u, {}).get("trang_thai") == "xong" for u in upstream(wf, nid))


def texts(inputs: dict, port: str) -> str:
    return "\n\n".join(str(v["gia_tri"]) for v in inputs.get(port, []) if v.get("kieu") == "text" and v.get("gia_tri"))


def files(pid: str, inputs: dict, port: str) -> list:
    base = PROJECTS / pid
    return [base / v["gia_tri"] for v in inputs.get(port, []) if v.get("kieu") != "text" and v.get("gia_tri")]


def combined_prompt(node: dict, inputs: dict, port: str = "prompt", key: str = "prompt") -> str:
    parts = [texts(inputs, port), (node.get("params") or {}).get(key, "")]
    return "\n\n".join(p.strip() for p in parts if p and p.strip())


# ---------------------------------------------------------------- chạy
class Ctx:
    """Thông tin cho một lần chạy node — truyền vào nhà cung cấp."""

    def __init__(self, pid, wf, node, reg):
        self.pid, self.node, self.reg = pid, node, reg
        self.folder = PROJECTS / pid
        self.out_dir = self.folder / "wf" / node["id"]
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.inputs = resolve_inputs(wf, node["id"])
        self.params = node.get("params") or {}
        self.model = node.get("model") or ""
        self.type = reg["_by_id"].get(node.get("type"), {})

    def rel(self, path: Path) -> str:
        return Path(path).resolve().relative_to(self.folder.resolve()).as_posix()

    def out(self, port: str, kieu: str, path_or_text) -> dict:
        val = path_or_text if kieu == "text" else self.rel(path_or_text)
        return {port: {"kieu": kieu, "gia_tri": val}}

    def log(self, msg: str):
        set_fields(self.pid, self.node["id"], chi_tiet=msg)


def set_fields(pid: str, nid: str, **fields):
    def fn(wf):
        for n in wf.get("nodes", []):
            if n["id"] == nid:
                n.update(fields)
    update(pid, fn)


def config_sig(node) -> str:
    """Chữ ký cấu hình lúc chạy — bảng điều khiển so sánh để báo «đã sửa sau lần chạy» (khớp JSON.stringify)."""
    return json.dumps([node.get("provider"), node.get("model"), node.get("params")], ensure_ascii=False, separators=(",", ":"))


def ctx_note(pid: str, nid: str) -> str:
    """Giữ ghi chú cuối cùng của nhà cung cấp (vd «Đã dựng 12.3s») nếu không phải thông báo tiến độ."""
    n = node_map(load(pid)).get(nid, {})
    note = n.get("chi_tiet") or ""
    return "" if note.startswith(("Đang", "Đã gửi")) else note


def provider_kind(reg, node) -> str:
    t = reg["_by_id"].get(node.get("type"), {})
    if node.get("type") == "duyet":
        return "duyet"
    if not t.get("nha_cung_cap"):
        return "dau_vao"
    prov = reg["nha_cung_cap"].get(node.get("provider") or "")
    return prov["chay"] if prov else "chua_chon"


def run_input_node(ctx: Ctx) -> dict:
    t, p = ctx.node.get("type"), ctx.params
    if t in ("prompt", "ghi-chu"):
        return ctx.out("text", "text", p.get("noi_dung", ""))
    if t == "nhan-vat":
        res = {}
        if p.get("file"):
            if not (ctx.folder / p["file"]).is_file():
                raise RuntimeError("Không thấy file ảnh — tải lại ảnh cho node")
            res.update(ctx.out("image", "image", ctx.folder / p["file"]))
        desc = p.get("mo_ta", "")
        if p.get("element_id"):
            desc += f"\n(Higgsfield Element: <<<{p['element_id']}>>>)"
        if p.get("soul_id"):
            desc += f"\n(Higgsfield Soul: {p['soul_id']})"
        res.update(ctx.out("text", "text", desc.strip()))
        return res
    port = ctx.type["ra"][0]
    if not p.get("file"):
        raise RuntimeError("Chưa có file — kéo thả file vào node")
    path = ctx.folder / p["file"]
    if not path.is_file():
        raise RuntimeError(f"Không thấy file {p['file']}")
    return ctx.out(port["id"], port["kieu"], path)


def work_packet(ctx: Ctx, cho: str) -> str:
    """Soạn hướng dẫn cho node làm tay hoặc chờ Claude."""
    prov = ctx.reg["nha_cung_cap"].get(ctx.node.get("provider"), {})
    lines = [f"# {ctx.node.get('ten') or ctx.type.get('ten')} — {prov.get('ten', '')}",
             f"Node: {ctx.node['id']} · loại: {ctx.node.get('type')} · model: {ctx.model or '(mặc định)'}", ""]
    for port, vals in ctx.inputs.items():
        for v in vals:
            if v["kieu"] == "text":
                lines += [f"## Đầu vào «{port}» (chữ, từ {v['tu']})", str(v["gia_tri"]), ""]
            else:
                lines.append(f"- Đầu vào «{port}» ({v['kieu']}, từ {v['tu']}): {v['gia_tri']}")
    lines += ["", "## Tham số"] + [f"- {k}: {v}" for k, v in ctx.params.items() if v not in ("", None)]
    if cho == "cho_nguoi_dung":
        outs = ", ".join(f"{o['ten']} ({o['kieu']})" for o in ctx.type.get("ra", []))
        lines += ["", "## Việc của bạn",
                  f"Làm trên {prov.get('ten', 'app')}, rồi kéo thả file kết quả ({outs}) vào node này trên canvas."]
    text = "\n".join(lines)
    (ctx.out_dir / "goi-viec.md").write_text(text, encoding="utf-8")
    return text


def execute_node(pid: str, nid: str, reg=None):
    reg = reg or registry()
    wf = load(pid)
    node = node_map(wf)[nid]
    kind = provider_kind(reg, node)
    ctx = Ctx(pid, wf, node, reg)
    if kind == "chua_chon":
        set_fields(pid, nid, trang_thai="loi", loi="Chưa chọn nhà cung cấp cho node này", luc_chay=now())
        return
    if kind == "duyet":
        val = next(iter(next(iter(ctx.inputs.values()), [])), None)
        set_fields(pid, nid, trang_thai="cho_duyet", chi_tiet="Chờ bạn xem và bấm Duyệt",
                   ket_qua={"any": {k: val[k] for k in ("kieu", "gia_tri")}} if val else {}, luc_chay=now())
        return
    if kind in ("claude", "thu_cong"):
        status = "cho_claude" if kind == "claude" else "cho_nguoi_dung"
        work_packet(ctx, status)
        msg = ("Chờ Claude Code: gõ /chay-workflow trong Claude Code" if kind == "claude"
               else "Làm theo gói việc rồi kéo thả file kết quả vào node")
        set_fields(pid, nid, trang_thai=status, loi="", chi_tiet=msg, luc_chay=now())
        return
    set_fields(pid, nid, trang_thai="dang_chay", loi="", chi_tiet="Đang chạy…", luc_chay=now())
    try:
        if kind == "dau_vao":
            result = run_input_node(ctx)
        else:
            import providers
            result = providers.run(ctx)
        set_fields(pid, nid, trang_thai="xong", ket_qua=result, loi="", chi_tiet=ctx_note(pid, nid), luc_chay=now(),
                   cau_hinh_luc_chay=config_sig(node))
    except Exception as e:  # noqa: BLE001 — mọi lỗi đều báo lên node
        msg = str(e) or e.__class__.__name__
        if not getattr(e, "friendly", False) and not isinstance(e, RuntimeError):
            msg += "\n" + traceback.format_exc(limit=3)
        set_fields(pid, nid, trang_thai="loi", loi=msg[:2000], chi_tiet="", luc_chay=now())


def targets_for(wf, mode: str, nid) -> set:
    if mode == "node":
        return {nid}
    if mode == "den":
        return ancestors(wf, nid) | {nid}
    return set(node_map(wf))


def run(pid: str, mode: str = "tat_ca", nid=None, max_workers: int = 3) -> dict:
    """Chạy theo từng đợt: node nào đủ đầu vào thì chạy (song song tới max_workers)."""
    reg = registry()
    if mode == "node" and nid:  # chạy lại node được chọn
        set_fields(pid, nid, trang_thai="chua_chay", ket_qua={}, loi="", chi_tiet="")
    # Node đầu vào (prompt, ảnh, video có sẵn…) luôn đọc lại để lấy nội dung mới nhất
    wf = load(pid)
    for i in targets_for(wf, mode if mode != "node" else "den", nid):
        n = node_map(wf).get(i)
        if n and not n.get("khoa") and provider_kind(reg, n) == "dau_vao":
            execute_node(pid, i, reg)
    done_any, tried = False, set()
    while True:
        wf = load(pid)
        nodes = node_map(wf)
        todo = [i for i in targets_for(wf, mode, nid)
                if i in nodes and i not in tried and not nodes[i].get("khoa") and nodes[i].get("type") != "ghi-chu"
                and nodes[i].get("trang_thai", "chua_chay") in ("chua_chay", "loi")
                and inputs_ready(wf, i)]
        if mode == "node":
            todo = [i for i in todo if i == nid]
        if not todo:
            break
        tried.update(todo)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            list(pool.map(lambda i: execute_node(pid, i, reg), todo))
        done_any = True
        if mode == "node":
            break
    return {"da_chay": done_any}


def run_async(pid: str, mode: str, nid=None) -> bool:
    if _running.get(pid):
        return False
    _running[pid] = True

    def job():
        try:
            run(pid, mode, nid)
        finally:
            _running[pid] = False
    threading.Thread(target=job, daemon=True).start()
    return True


def is_running(pid: str) -> bool:
    return bool(_running.get(pid))


# ---------------------------------------------------------------- dòng lệnh
def _cli():
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "danh-sach":
        wf = load(a[1])
        for n in wf["nodes"]:
            print(f"{n['id']:6} {n.get('type', ''):14} {n.get('provider', ''):16} {n.get('trang_thai', 'chua_chay'):15} {n.get('ten', '')}")
        return
    if len(a) >= 2 and a[0] == "cho-claude":
        wf = load(a[1])
        out = []
        for n in wf["nodes"]:
            if n.get("trang_thai") == "cho_claude":
                out.append({"node": n["id"], "type": n.get("type"), "ten": n.get("ten"), "provider": n.get("provider"),
                            "model": n.get("model"), "params": n.get("params"), "dau_vao": resolve_inputs(wf, n["id"]),
                            "ghi_ket_qua_vao": [o["id"] + ":" + o["kieu"] for o in registry()["_by_id"].get(n.get("type"), {}).get("ra", [])],
                            "thu_muc_ket_qua": f"du-an/{a[1]}/wf/{n['id']}/"})
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    if len(a) >= 3 and a[0] == "dau-vao":
        wf = load(a[1])
        n = node_map(wf)[a[2]]
        print(json.dumps({"node": n, "dau_vao": resolve_inputs(wf, a[2])}, ensure_ascii=False, indent=2))
        return
    if len(a) >= 6 and a[0] == "ghi":
        pid, nid, port, kieu, val = a[1:6]
        folder = PROJECTS / pid
        if val.startswith("@"):
            src = Path(val[1:]).resolve()
            if kieu == "text":
                val = src.read_text(encoding="utf-8")
            else:
                dest = folder / "wf" / nid / src.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                if src != dest.resolve():
                    shutil.copy2(src, dest)
                val = dest.relative_to(folder).as_posix()

        def fn(wf):
            for n in wf["nodes"]:
                if n["id"] == nid:
                    n.setdefault("ket_qua", {})[port] = {"kieu": kieu, "gia_tri": val}
                    n.update(trang_thai="xong", loi="", chi_tiet="", luc_chay=now())
        update(pid, fn)
        print(f"Đã ghi {nid}.{port}")
        return
    if len(a) >= 4 and a[0] == "loi":
        set_fields(a[1], a[2], trang_thai="loi", loi=a[3], luc_chay=now())
        return
    if len(a) >= 2 and a[0] == "chay":
        mode = a[2] if len(a) > 2 else "tat_ca"
        print(run(a[1], mode, a[3] if len(a) > 3 else None))
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    _cli()
