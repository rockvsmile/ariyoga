"""Higgsfield API (bằng Key ID + Secret): tạo ảnh / video.

Model = đường dẫn model của Higgsfield, vd:
  bytedance/seedance-2.5          → tự thêm /text-to-video | /image-to-video | /reference-to-video
  kling-video/v3.0/std            → tự thêm /text-to-video | /image-to-video
  higgsfield/cinema-studio/4.0    (gửi thẳng)
  higgsfield-ai/soul/v2/standard  (ảnh)
Tên trường của từng model có thể khác — nếu API báo lỗi trường, xem docs.higgsfield.ai/docs/models.
"""
from pathlib import Path

from . import LoiNCC, key
from .http import download, mime, poll, request

BASE = "https://api.higgsfield.ai"
TASKS = {"bytedance/seedance-2.5": ("text-to-video", "image-to-video", "reference-to-video"),
         "bytedance/seedance-2.0": ("text-to-video", "image-to-video", "reference-to-video"),
         "kling-video/v3.0/std": ("text-to-video", "image-to-video", None)}


def _auth():
    return {"Authorization": f"Key {key('higgsfield', 'key_id')}:{key('higgsfield', 'key_secret')}"}


def _upload(path: Path) -> str:
    up = request("POST", f"{BASE}/files/generate-upload-url", _auth(), {"content_type": mime(path)})
    if not up.get("upload_url"):
        raise LoiNCC("Higgsfield không cấp link tải lên: " + str(up)[:300])
    request("PUT", up["upload_url"], {"Content-Type": mime(path), **(up.get("upload_headers") or {})}, path.read_bytes(), timeout=600, raw=True)
    return up["public_url"]


def run(ctx) -> dict:
    from workflow import combined_prompt, files
    p, is_video = ctx.params, ctx.node.get("type") == "tao-video"
    model = (ctx.model or ("bytedance/seedance-2.5" if is_video else "higgsfield-ai/soul/v2/standard")).strip("/")
    prompt = combined_prompt(ctx.node, ctx.inputs)
    body = {"prompt": prompt} if prompt else {}
    if p.get("ti_le"):
        body["aspect_ratio"] = p["ti_le"]
    if p.get("do_phan_giai"):
        body["resolution"] = p["do_phan_giai"]
    path = model
    if is_video:
        first, last = files(ctx.pid, ctx.inputs, "khung_dau"), files(ctx.pid, ctx.inputs, "khung_cuoi")
        refs = files(ctx.pid, ctx.inputs, "tham_chieu")
        if p.get("thoi_luong") not in (None, ""):
            body["duration"] = int(float(p["thoi_luong"]))
        if p.get("am_thanh") is not None and p.get("am_thanh") != "":
            body["generate_audio"] = bool(p["am_thanh"])
        ctx.log("Đang tải ảnh lên Higgsfield…" if (first or refs) else "Đang gửi yêu cầu…")
        task = "text-to-video"
        if first:
            body["image_url"] = _upload(first[0])
            if last:
                body["end_image_url" if "seedance" in model else "last_image_url"] = _upload(last[0])
            task = "image-to-video"
        elif refs:
            body["image_urls"] = [_upload(r) for r in refs[:9]]
            task = "reference-to-video"
        fam = TASKS.get(model)
        if fam:
            if task == "reference-to-video" and not fam[2]:
                raise LoiNCC("Model này không nhận ảnh tham chiếu — nối vào «Khung đầu» hoặc chọn Seedance")
            path = f"{model}/{task}"
        elif first or refs:
            body.setdefault("image_urls", [body.get("image_url")] if body.get("image_url") else body.get("image_urls"))
    else:
        refs = files(ctx.pid, ctx.inputs, "tham_chieu")
        if refs:
            body["image_urls"] = [_upload(r) for r in refs[:9]]
    if not body.get("prompt") and not body.get("image_url") and not body.get("image_urls"):
        raise LoiNCC("Cần prompt hoặc ảnh")
    res = request("POST", f"{BASE}/{path}", _auth(), body, timeout=120)
    rid = res.get("request_id")
    if not rid:
        raise LoiNCC("Higgsfield không trả mã công việc: " + str(res)[:300])
    st = poll(lambda: request("GET", f"{BASE}/requests/{rid}/status", _auth()),
              lambda r: r.get("status") not in ("queued", "in_progress"), every=8, log=ctx.log)
    if st.get("status") != "completed":
        raise LoiNCC(f"Higgsfield: {st.get('status')} — {st.get('error') or ''}")
    if is_video:
        url = (st.get("video") or {}).get("url")
        if not url:
            raise LoiNCC("Higgsfield không trả video: " + str(st)[:300])
        return ctx.out("video", "video", download(url, ctx.out_dir / "video.mp4"))
    imgs = st.get("images") or []
    if not imgs:
        raise LoiNCC("Higgsfield không trả ảnh: " + str(st)[:300])
    return ctx.out("image", "image", download(imgs[0]["url"], ctx.out_dir / "anh.png"))
