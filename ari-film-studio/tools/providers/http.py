"""Gọi HTTP bằng thư viện chuẩn: JSON, multipart, tải file, chờ việc chạy nền."""
import base64
import json
import mimetypes
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from . import LoiNCC

UA = "AriFilmStudio/1.0"


def _err_text(e: urllib.error.HTTPError) -> str:
    try:
        body = e.read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001
        body = ""
    try:
        j = json.loads(body)
        msg = j.get("error", j)
        if isinstance(msg, dict):
            msg = msg.get("message") or msg.get("detail") or json.dumps(msg, ensure_ascii=False)
        body = str(msg)
    except (json.JSONDecodeError, AttributeError):
        pass
    return f"HTTP {e.code}: {body[:600]}"


def request(method: str, url: str, headers=None, body=None, timeout: float = 120, raw: bool = False):
    data = None
    hdrs = {"User-Agent": UA, **(headers or {})}
    if body is not None and not isinstance(body, (bytes, bytearray)):
        data = json.dumps(body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    elif body is not None:
        data = bytes(body)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            content = r.read()
            if raw:
                return content
            return json.loads(content.decode("utf-8")) if content else {}
    except urllib.error.HTTPError as e:
        raise LoiNCC(_err_text(e)) from e
    except urllib.error.URLError as e:
        raise LoiNCC(f"Không kết nối được {url.split('/')[2]}: {e.reason}") from e


def multipart(fields: dict, files: list) -> tuple:
    """files: [(tên_trường, Path)] — trả về (body, content_type)."""
    boundary = "----ari" + uuid.uuid4().hex
    out = bytearray()
    for k, v in fields.items():
        if v in (None, ""):
            continue
        out += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode("utf-8")
    for k, path in files:
        path = Path(path)
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{path.name}\"\r\n"
                f"Content-Type: {ctype}\r\n\r\n").encode("utf-8")
        out += path.read_bytes() + b"\r\n"
    out += f"--{boundary}--\r\n".encode("utf-8")
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def download(url: str, dest: Path, headers=None, timeout: float = 600) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(request("GET", url, headers=headers, timeout=timeout, raw=True))
    return dest


def b64(path: Path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("ascii")


def mime(path: Path) -> str:
    return mimetypes.guess_type(Path(path).name)[0] or "application/octet-stream"


def poll(fn, done, every: float = 8, timeout: float = 1800, log=None):
    """Gọi fn() lặp lại tới khi done(kết_quả) trả True; báo tiến độ qua log()."""
    t0 = time.time()
    while True:
        res = fn()
        if done(res):
            return res
        waited = int(time.time() - t0)
        if waited > timeout:
            raise LoiNCC(f"Quá thời gian chờ ({timeout // 60} phút) — kiểm tra lại trên trang của nhà cung cấp")
        if log:
            log(f"Đang chờ kết quả… {waited // 60}:{waited % 60:02d}")
        time.sleep(every)
