"""Tripo3D API v3: tạo mô hình 3D (.glb) từ chữ hoặc ảnh."""
from pathlib import Path

from . import LoiNCC, key
from .http import download, multipart, poll, request

BASE = "https://openapi.tripo3d.ai/v3"
DEFAULT_MODEL = "v3.1-20260211"


def run(ctx) -> dict:
    from workflow import combined_prompt, files
    auth = {"Authorization": f"Bearer {key('tripo')}"}
    model = ctx.model or DEFAULT_MODEL
    imgs = files(ctx.pid, ctx.inputs, "image")
    if imgs:
        img = Path(imgs[0])
        body, ctype = multipart({}, [("file", img)])
        ctx.log("Đang tải ảnh lên Tripo…")
        up = request("POST", f"{BASE}/files", {**auth, "Content-Type": ctype}, body, timeout=300)
        token = (up.get("data") or {}).get("file_token")
        if not token:
            raise LoiNCC("Tripo không nhận ảnh: " + str(up)[:300])
        ext = img.suffix.lower().lstrip(".").replace("jpeg", "jpg") or "png"
        res = request("POST", f"{BASE}/generation/image-to-model", auth,
                      {"model": model, "file": {"type": ext, "file_token": token}, "texture": True, "pbr": True})
    else:
        prompt = combined_prompt(ctx.node, ctx.inputs)
        if not prompt:
            raise LoiNCC("Cần prompt hoặc ảnh")
        res = request("POST", f"{BASE}/generation/text-to-model", auth, {"model": model, "prompt": prompt[:1024], "texture": True, "pbr": True})
    task = (res.get("data") or {}).get("task_id")
    if not task:
        raise LoiNCC("Tripo không trả mã công việc: " + str(res)[:300])
    ctx.log("Tripo đang dựng mô hình…")
    st = poll(lambda: request("GET", f"{BASE}/tasks/{task}", auth),
              lambda r: (r.get("data") or {}).get("status") not in ("queued", "running", None), every=6, log=ctx.log)
    data = st.get("data") or {}
    if data.get("status") != "success":
        raise LoiNCC(f"Tripo: {data.get('status')} — {data.get('error_message') or data.get('error_code') or ''}")
    url = (data.get("output") or {}).get("model_url")
    if not url:
        raise LoiNCC("Tripo không trả link mô hình")
    out = download(url, ctx.out_dir / "mo-hinh.glb")
    return ctx.out("model3d", "model3d", out)
