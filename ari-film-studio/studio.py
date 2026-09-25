#!/usr/bin/env python3
"""Ari Film Studio — bảng điều khiển local.

Chạy:  python studio.py        rồi mở http://127.0.0.1:8765
Chỉ dùng thư viện chuẩn của Python, không cần cài thêm gì.

Mỗi dự án là một thư mục trong du-an/<ten>/ với file project.json là
"nguồn sự thật duy nhất": cả bảng điều khiển lẫn các agent trong Claude Code
đều đọc/ghi file này.
"""
import base64
import json
import mimetypes
import os
import re
import shutil
import sys
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT / "du-an"
LIBRARY = ROOT / "thu-vien"
UI = ROOT / "giao-dien"
PORT = int(os.environ.get("STUDIO_PORT", "8765"))

sys.path.insert(0, str(ROOT / "tools"))
from tao_du_an import bang_ket_noi_rong, create_project, safe_name  # noqa: E402
import providers  # noqa: E402
import workflow  # noqa: E402

TEMPLATES = LIBRARY / "mau-workflow"
MAX_UPLOAD = 1024 * 1024 * 1024  # 1 GB


def read_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def project_file(name: str) -> Path:
    return PROJECTS / safe_name(name) / "project.json"


def version_of(path: Path) -> str:
    return str(path.stat().st_mtime_ns)


def md_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def list_library(folder: str):
    out = []
    for p in sorted((LIBRARY / folder).glob("*.md")):
        if p.name.startswith("_"):
            continue
        out.append({"id": p.stem, "ten": md_title(p), "file": f"thu-vien/{folder}/{p.name}"})
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI), **kwargs)

    def log_message(self, fmt, *args):
        if args and "/api/" in str(args[0]):
            sys.stderr.write("[studio] " + fmt % args + "\n")

    # ---------- helpers ----------
    def send_json(self, data, status=HTTPStatus.OK, headers=None):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        n = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def send_file(self, path: Path):
        if not path.is_file():
            return self.send_error(HTTPStatus.NOT_FOUND)
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    # ---------- routes ----------
    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/projects":
            items = []
            for p in sorted(PROJECTS.glob("*/project.json")):
                try:
                    d = read_json(p)
                    items.append({"id": p.parent.name, "ten": d.get("ten", p.parent.name),
                                  "cap_nhat": d.get("cap_nhat", "")})
                except (OSError, json.JSONDecodeError):
                    items.append({"id": p.parent.name, "ten": p.parent.name + " (lỗi JSON)"})
            return self.send_json(items)
        if path == "/api/library":
            return self.send_json({
                "phong_cach": list_library("phong-cach"),
                "the_loai": list_library("the-loai"),
                "cong_cu": list_library("cong-cu"),
                "tuy_chon": read_json(LIBRARY / "tuy-chon.json"),
                "bang_ket_noi": read_json(LIBRARY / "bang-ket-noi.json"),
            })
        m = re.fullmatch(r"/api/project/([^/]+)", path)
        if m:
            f = project_file(m.group(1))
            if not f.is_file():
                return self.send_json({"loi": "Không tìm thấy dự án"}, HTTPStatus.NOT_FOUND)
            try:
                data = read_json(f)
            except json.JSONDecodeError as e:
                return self.send_json({"loi": f"project.json bị lỗi cú pháp: {e}"}, HTTPStatus.CONFLICT)
            for k, v in bang_ket_noi_rong().items():  # dự án cũ / mảnh ghép mới thêm
                data.setdefault("bang_ket_noi", {}).setdefault(k, v)
            return self.send_json(data, headers={"X-Version": version_of(f)})
        if path == "/api/node-types":
            return self.send_json(workflow.registry() | {"_by_id": None})
        if path == "/api/cai-dat/khoa":
            return self.send_json(providers.masked_keys())
        if path == "/api/mau-workflow":
            out = []
            for p in sorted(TEMPLATES.glob("*.json")):
                d = read_json(p)
                out.append({"id": p.stem, "ten": d.get("ten", p.stem), "mo_ta": d.get("mo_ta", ""), "meta": d.get("meta", {}),
                            "so_node": len(d.get("nodes", [])), "video_minh_hoa": d.get("video_minh_hoa", ""),
                            "anh_bia": d.get("anh_bia", ""), "cap_nhat": d.get("cap_nhat", "")})
            return self.send_json(out)
        m = re.fullmatch(r"/api/mau-workflow/([^/]+)", path)
        if m:
            f = TEMPLATES / (safe_name(m.group(1)) + ".json")
            return self.send_json(read_json(f)) if f.is_file() else self.send_json({"loi": "Không có mẫu"}, HTTPStatus.NOT_FOUND)
        m = re.fullmatch(r"/api/workflow/([^/]+)", path)
        if m:
            pid = safe_name(m.group(1))
            if not (PROJECTS / pid).is_dir():
                return self.send_json({"loi": "Không tìm thấy dự án"}, HTTPStatus.NOT_FOUND)
            f = workflow.wf_path(pid)
            return self.send_json(workflow.load(pid), headers={"X-Version": version_of(f) if f.is_file() else "0"})
        m = re.fullmatch(r"/api/wf-state/([^/]+)", path)
        if m:
            pid = safe_name(m.group(1))
            f = workflow.wf_path(pid)
            return self.send_json({"version": version_of(f) if f.is_file() else "0", "dang_chay": workflow.is_running(pid)})
        m = re.fullmatch(r"/api/version/([^/]+)", path)
        if m:
            f = project_file(m.group(1))
            return self.send_json({"version": version_of(f) if f.is_file() else None})
        m = re.fullmatch(r"/files/([^/]+)/(.+)", path)
        if m:
            base = (PROJECTS / safe_name(m.group(1))).resolve()
            target = (base / m.group(2)).resolve()
            if base not in target.parents:
                return self.send_error(HTTPStatus.FORBIDDEN)
            return self.send_file(target)
        m = re.fullmatch(r"/mau-media/([^/]+)/([^/]+)", path)
        if m:
            base = (TEMPLATES / "media").resolve()
            target = (base / safe_name(m.group(1)) / m.group(2)).resolve()
            if base not in target.parents:
                return self.send_error(HTTPStatus.FORBIDDEN)
            return self.send_file(target)
        m = re.fullmatch(r"/api/xuat/([^/]+)", path)
        if m:  # phim đã xuất của dự án — để chọn làm video minh hoạ cho mẫu
            folder = PROJECTS / safe_name(m.group(1))
            vids = sorted([p for p in (folder / "xuat").glob("*.mp4")] + [p for p in (folder / "wf").glob("*/*.mp4")],
                          key=lambda p: p.stat().st_mtime, reverse=True)
            return self.send_json([p.relative_to(folder).as_posix() for p in vids[:30]])
        if path.startswith("/thu-vien/"):
            target = (ROOT / path.lstrip("/")).resolve()
            if LIBRARY.resolve() not in target.parents:
                return self.send_error(HTTPStatus.FORBIDDEN)
            return self.send_file(target)
        if path in ("/", "/index.html"):
            return self.send_file(UI / "canvas.html")
        return super().do_GET()

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/projects":
            body = self.read_body()
            ten = (body.get("ten") or "").strip()
            if not ten:
                return self.send_json({"loi": "Cần tên dự án"}, HTTPStatus.BAD_REQUEST)
            try:
                pid = create_project(ten, PROJECTS)
            except FileExistsError:
                return self.send_json({"loi": "Dự án đã tồn tại"}, HTTPStatus.CONFLICT)
            return self.send_json({"id": pid})
        m = re.fullmatch(r"/api/wf-run/([^/]+)", path)
        if m:
            pid = safe_name(m.group(1))
            body = self.read_body()
            ok = workflow.run_async(pid, body.get("mode") or "tat_ca", body.get("node"))
            return self.send_json({"ok": ok, "loi": "" if ok else "Workflow đang chạy — chờ xong rồi chạy tiếp"})
        m = re.fullmatch(r"/api/wf-node/([^/]+)/([^/]+)", path)
        if m:
            return self.node_action(safe_name(m.group(1)), m.group(2), self.read_body())
        m = re.fullmatch(r"/api/mau-workflow/([^/]+)/media", path)
        if m:
            tid = safe_name(m.group(1))
            f = TEMPLATES / (tid + ".json")
            if not f.is_file():
                return self.send_json({"loi": "Không có mẫu"}, HTTPStatus.NOT_FOUND)
            body = self.read_body()
            loai = "video_minh_hoa" if body.get("loai") == "video" else "anh_bia"
            dest_dir = TEMPLATES / "media" / tid
            dest_dir.mkdir(parents=True, exist_ok=True)
            if body.get("tu_du_an"):  # lấy phim đã xuất của một dự án
                src = (PROJECTS / safe_name(body["tu_du_an"]) / body.get("file", "")).resolve()
                if (PROJECTS.resolve() not in src.parents) or not src.is_file():
                    return self.send_json({"loi": "Không thấy file"}, HTTPStatus.BAD_REQUEST)
                dest = dest_dir / ("minh-hoa" + src.suffix.lower() if loai == "video_minh_hoa" else "bia" + src.suffix.lower())
                shutil.copy2(src, dest)
            else:
                name = Path(body.get("ten_file") or "file.bin")
                raw = base64.b64decode((body.get("du_lieu") or "").split(",", 1)[-1])
                if len(raw) > MAX_UPLOAD:
                    return self.send_json({"loi": "File quá lớn"}, HTTPStatus.BAD_REQUEST)
                dest = dest_dir / (("minh-hoa" if loai == "video_minh_hoa" else "bia") + name.suffix.lower())
                dest.write_bytes(raw)
            d = read_json(f)
            d[loai] = f"{tid}/{dest.name}"
            write_json(f, d)
            return self.send_json({"ok": True, loai: d[loai]})
        m = re.fullmatch(r"/api/workflow/([^/]+)/tu-mau", path)
        if m:
            pid = safe_name(m.group(1))
            tpl = TEMPLATES / (safe_name(self.read_body().get("mau", "")) + ".json")
            if not tpl.is_file():
                return self.send_json({"loi": "Không có mẫu này"}, HTTPStatus.NOT_FOUND)
            data = read_json(tpl)
            meta = {**data.get("meta", {}), "mau": tpl.stem, "ten_mau": data.get("ten", "")}
            workflow.save_from_ui(pid, {"phien_ban": 1, "nodes": data["nodes"], "edges": data["edges"], "meta": meta})
            return self.send_json({"ok": True})
        if path == "/api/mau-workflow":
            body = self.read_body()
            ten = (body.get("ten") or "").strip()
            src = safe_name(body.get("tu_du_an", ""))
            if not ten or not workflow.wf_path(src).is_file():
                return self.send_json({"loi": "Cần tên mẫu và dự án nguồn"}, HTTPStatus.BAD_REQUEST)
            wf = workflow.load(src)
            nodes = [{k: v for k, v in n.items() if k not in workflow.RUNTIME} for n in wf["nodes"]]
            for n in nodes:  # mẫu không mang theo file riêng của dự án
                n["params"] = {k: ("" if k == "file" else v) for k, v in (n.get("params") or {}).items()}
            TEMPLATES.mkdir(exist_ok=True)
            meta = {k: v for k, v in {**wf.get("meta", {}), **(body.get("meta") or {})}.items() if k not in ("mau", "ten_mau")}
            write_json(TEMPLATES / (safe_name(ten) + ".json"), {"ten": ten, "mo_ta": body.get("mo_ta", ""), "meta": meta, "nodes": nodes, "edges": wf["edges"]})
            return self.send_json({"ok": True})
        m = re.fullmatch(r"/api/quet/([^/]+)", path)
        if m:
            return self.scan_files(m.group(1))
        m = re.fullmatch(r"/api/upload/([^/]+)", path)
        if m:
            # body: {"loai": "nhan-vat|trang-phuc|san-pham|boi-canh|khac", "ten_file": "...", "du_lieu": "<base64>"}
            body = self.read_body()
            folder = safe_name(body.get("loai") or "khac")
            fname = safe_name(Path(body.get("ten_file") or "anh.png").stem) + Path(body.get("ten_file") or ".png").suffix.lower()
            dest_dir = PROJECTS / safe_name(m.group(1)) / "tham-chieu" / folder
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / fname
            i = 1
            while dest.exists():
                dest = dest_dir / f"{Path(fname).stem}-{i}{Path(fname).suffix}"
                i += 1
            raw = body.get("du_lieu", "")
            dest.write_bytes(base64.b64decode(raw.split(",", 1)[-1]))
            rel = dest.relative_to(PROJECTS / safe_name(m.group(1))).as_posix()
            return self.send_json({"duong_dan": rel})
        return self.send_error(HTTPStatus.NOT_FOUND)

    def scan_files(self, pid: str):
        """Gắn file người dùng thả vào thư mục dự án (tên file = mã shot/clip/track) vào ô còn trống."""
        folder = PROJECTS / safe_name(pid)
        f = folder / "project.json"
        if not f.is_file():
            return self.send_json({"loi": "Không tìm thấy dự án"}, HTTPStatus.NOT_FOUND)
        d = read_json(f)

        def find(sub, key, exts):
            for ext in exts:
                for cand in (folder / sub).glob(f"{key}{ext}"):
                    return cand.relative_to(folder).as_posix()
            return None

        vids, auds = (".mp4", ".mov", ".webm", ".MP4", ".MOV"), (".mp3", ".wav", ".m4a", ".aac", ".ogg", ".MP3", ".WAV")
        found = []
        for s in d["khung"]["6_storyboard"]["noi_dung"].get("shots", []):
            if s.get("khoa"):
                continue
            if not s.get("video"):
                rel = (find("video", s.get("id", ""), vids) if s.get("id") else None) or \
                      (find("video", s["clip"], vids) if s.get("clip") else None)
                if rel:
                    s["video"] = rel
                    s["trang_thai"] = "xong"
                    found.append(f"{s['id']} ← {rel}")
            if not s.get("anh_storyboard") and s.get("id"):
                rel = find("storyboard", s["id"], (".png", ".jpg", ".jpeg", ".webp", ".PNG", ".JPG"))
                if rel:
                    s["anh_storyboard"] = rel
                    found.append(f"{s['id']} ← {rel}")
        for t in d["khung"]["8_dung_phim"]["noi_dung"].get("am_thanh", []) or []:
            if t.get("khoa") or t.get("file") or not t.get("id"):
                continue
            rel = find("am-thanh", t["id"], auds)
            if rel:
                t["file"] = rel
                found.append(f"{t['id']} ← {rel}")
        if found:
            d["cap_nhat"] = datetime.now().isoformat(timespec="seconds")
            d.setdefault("nhat_ky", []).append({"luc": d["cap_nhat"], "ai": "bang-dieu-khien", "viec": f"Quét file: {len(found)} file mới"})
            write_json(f, d)
        return self.send_json({"tim_thay": found}, headers={"X-Version": version_of(f)})

    def node_action(self, pid: str, nid: str, body: dict):
        act = body.get("action")
        folder = PROJECTS / pid
        if act in ("tai_file", "ket_qua"):
            name = Path(body.get("ten_file") or "file.bin")
            fname = safe_name(name.stem) + name.suffix.lower()
            dest_dir = folder / "wf" / re.sub(r"[^\w-]", "", nid)
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / fname
            raw = base64.b64decode((body.get("du_lieu") or "").split(",", 1)[-1])
            if len(raw) > MAX_UPLOAD:
                return self.send_json({"loi": "File quá lớn"}, HTTPStatus.BAD_REQUEST)
            dest.write_bytes(raw)
            rel = dest.relative_to(folder).as_posix()
            if act == "ket_qua":
                cong, kieu = body.get("cong"), body.get("kieu")

                def fn(wf):
                    for n in wf["nodes"]:
                        if n["id"] == nid:
                            n.setdefault("ket_qua", {})[cong] = {"kieu": kieu, "gia_tri": rel}
                            n.update(trang_thai="xong", loi="", chi_tiet="", luc_chay=workflow.now())
                workflow.update(pid, fn)
            return self.send_json({"duong_dan": rel})
        fields = {"duyet": {"trang_thai": "xong", "chi_tiet": "Đã duyệt"},
                  "dat_lai": {"trang_thai": "chua_chay", "ket_qua": {}, "loi": "", "chi_tiet": ""},
                  "tu_choi": {"trang_thai": "loi", "loi": body.get("ly_do") or "Bị từ chối khi duyệt"}}.get(act)
        if not fields:
            return self.send_json({"loi": "Hành động không hợp lệ"}, HTTPStatus.BAD_REQUEST)
        workflow.set_fields(pid, nid, **fields)
        return self.send_json({"ok": True})

    def do_PUT(self):
        path = unquote(urlparse(self.path).path)
        m = re.fullmatch(r"/api/workflow/([^/]+)", path)
        if m:
            pid = safe_name(m.group(1))
            if not (PROJECTS / pid).is_dir():
                return self.send_json({"loi": "Không tìm thấy dự án"}, HTTPStatus.NOT_FOUND)
            workflow.save_from_ui(pid, self.read_body())
            return self.send_json({"ok": True}, headers={"X-Version": version_of(workflow.wf_path(pid))})
        m = re.fullmatch(r"/api/mau-workflow/([^/]+)", path)
        if m:
            f = TEMPLATES / (safe_name(m.group(1)) + ".json")
            if not f.is_file():
                return self.send_json({"loi": "Không có mẫu"}, HTTPStatus.NOT_FOUND)
            body = self.read_body()
            nodes = [{k: v for k, v in n.items() if k not in workflow.RUNTIME} for n in body.get("nodes", [])]
            old = read_json(f)
            write_json(f, {"ten": body.get("ten") or old.get("ten"), "mo_ta": body.get("mo_ta", ""),
                           "video_minh_hoa": old.get("video_minh_hoa", ""), "anh_bia": old.get("anh_bia", ""),
                           "meta": body.get("meta", {}), "nodes": nodes, "edges": body.get("edges", [])})
            return self.send_json({"ok": True})
        if path == "/api/cai-dat/khoa":
            providers.save_keys(self.read_body())
            return self.send_json(providers.masked_keys())
        m = re.fullmatch(r"/api/project/([^/]+)", path)
        if not m:
            return self.send_error(HTTPStatus.NOT_FOUND)
        f = project_file(m.group(1))
        if not f.is_file():
            return self.send_json({"loi": "Không tìm thấy dự án"}, HTTPStatus.NOT_FOUND)
        expected = self.headers.get("If-Match")
        if expected and expected != version_of(f):
            # Claude (hoặc tab khác) vừa sửa file — không ghi đè
            return self.send_json({"loi": "Dự án vừa được cập nhật ở nơi khác. Tải lại để xem bản mới."},
                                  HTTPStatus.CONFLICT, headers={"X-Version": version_of(f)})
        data = self.read_body()
        data["cap_nhat"] = datetime.now().isoformat(timespec="seconds")
        write_json(f, data)
        return self.send_json({"ok": True}, headers={"X-Version": version_of(f)})


def main():
    PROJECTS.mkdir(exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"Ari Film Studio đang chạy tại {url}  (Ctrl+C để tắt)")
    if "--no-browser" not in sys.argv:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã tắt studio.")


if __name__ == "__main__":
    main()
