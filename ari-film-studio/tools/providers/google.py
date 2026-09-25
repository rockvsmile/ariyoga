"""Google Gemini API: Nano Banana (ảnh), Veo 3.1 (video), Gemini Omni Flash (tạo & sửa video)."""
import base64

from . import LoiNCC, key
from .http import b64, download, mime, poll, request

BASE = "https://generativelanguage.googleapis.com/v1beta"


def _auth():
    return {"x-goog-api-key": key("google")}


# ---------------------------------------------------------------- Nano Banana
def image(ctx) -> dict:
    from workflow import combined_prompt, files
    prompt = combined_prompt(ctx.node, ctx.inputs)
    if not prompt:
        raise LoiNCC("Chưa có prompt")
    model = ctx.model or "gemini-3.1-flash-image"
    parts = [{"text": prompt}] + [{"inlineData": {"mimeType": mime(p), "data": b64(p)}} for p in files(ctx.pid, ctx.inputs, "tham_chieu")[:14]]
    cfg = {"responseModalities": ["TEXT", "IMAGE"]}
    if ctx.params.get("ti_le"):
        cfg["imageConfig"] = {"aspectRatio": ctx.params["ti_le"]}
    ctx.log("Đang tạo ảnh…")
    res = request("POST", f"{BASE}/models/{model}:generateContent", _auth(),
                  {"contents": [{"role": "user", "parts": parts}], "generationConfig": cfg}, timeout=300)
    cands = res.get("candidates") or []
    imgs = [p["inlineData"] for p in (cands[0].get("content", {}).get("parts", []) if cands else [])
            if p.get("inlineData") and not p.get("thought")]
    if not imgs:
        reason = (cands[0].get("finishReason") if cands else None) or res.get("promptFeedback") or res
        raise LoiNCC("Gemini không trả về ảnh: " + str(reason)[:300])
    out = ctx.out_dir / "anh.png"
    out.write_bytes(base64.b64decode(imgs[-1]["data"]))
    return ctx.out("image", "image", out)


# ---------------------------------------------------------------- Veo 3.1
def _img(path):
    return {"bytesBase64Encoded": b64(path), "mimeType": mime(path)}


def veo(ctx) -> dict:
    from workflow import combined_prompt, files
    p = ctx.params
    prompt = combined_prompt(ctx.node, ctx.inputs)
    first, last = files(ctx.pid, ctx.inputs, "khung_dau"), files(ctx.pid, ctx.inputs, "khung_cuoi")
    refs = files(ctx.pid, ctx.inputs, "tham_chieu")
    mode = p.get("che_do") or "tu-dong"
    inst = {"prompt": prompt}
    if mode in ("tu-dong", "khung-dau", "dau-cuoi") and first:
        inst["image"] = _img(first[0])
        if last and mode != "khung-dau":
            inst["lastFrame"] = _img(last[0])
    elif mode in ("tu-dong", "tham-chieu") and refs:
        inst["referenceImages"] = [{"image": _img(r), "referenceType": "asset"} for r in refs[:3]]
    if mode == "noi-dai":
        raise LoiNCC("Nối dài trên Veo cần video gốc do chính Veo tạo — dùng Gemini Omni Flash hoặc Higgsfield để nối dài video bất kỳ")
    if not prompt and "image" not in inst:
        raise LoiNCC("Cần prompt hoặc ảnh khung đầu")
    params = {"aspectRatio": p.get("ti_le") if p.get("ti_le") in ("16:9", "9:16") else "16:9", "sampleCount": 1, "personGeneration": "allow_adult"}
    res_ = p.get("do_phan_giai")
    if res_:
        params["resolution"] = res_
    dur = p.get("thoi_luong")
    if dur not in (None, ""):
        params["durationSeconds"] = min((4, 6, 8), key=lambda d: abs(d - float(dur)))
    if res_ in ("1080p", "4k") or "referenceImages" in inst:
        params["durationSeconds"] = 8
    if p.get("prompt_am"):
        params["negativePrompt"] = p["prompt_am"]
    model = ctx.model or "veo-3.1-generate-preview"
    ctx.log("Đã gửi yêu cầu tới Veo…")
    op = request("POST", f"{BASE}/models/{model}:predictLongRunning", _auth(), {"instances": [inst], "parameters": params})
    name = op.get("name")
    if not name:
        raise LoiNCC("Veo không trả về mã công việc: " + str(op)[:300])
    op = poll(lambda: request("GET", f"{BASE}/{name}", _auth()), lambda r: r.get("done"), every=10, log=ctx.log)
    if op.get("error"):
        raise LoiNCC("Veo báo lỗi: " + str(op["error"].get("message", op["error"]))[:400])
    resp = op.get("response", {}).get("generateVideoResponse", {})
    samples = resp.get("generatedSamples") or []
    if not samples:
        raise LoiNCC("Veo không trả video (có thể bị bộ lọc an toàn chặn): " + str(resp.get("raiMediaFilteredReasons") or resp)[:300])
    out = download(samples[0]["video"]["uri"], ctx.out_dir / "video.mp4", _auth())
    return ctx.out("video", "video", out)


# ---------------------------------------------------------------- Gemini Omni Flash
def _upload_file(path, log):
    """Files API: tải video lên để Omni sửa; trả về uri khi file sẵn sàng."""
    data = path.read_bytes()
    start = request("POST", "https://generativelanguage.googleapis.com/upload/v1beta/files",
                    {**_auth(), "X-Goog-Upload-Protocol": "raw", "Content-Type": mime(path)}, data, timeout=600)
    f = start.get("file", start)
    name = f.get("name")
    if not name:
        raise LoiNCC("Không tải được video lên Google: " + str(start)[:300])
    f = poll(lambda: request("GET", f"{BASE}/{name}", _auth()), lambda r: r.get("state") in ("ACTIVE", "FAILED"), every=3, timeout=600, log=log)
    if f.get("state") != "ACTIVE":
        raise LoiNCC("Google không xử lý được video tải lên")
    return f["uri"]


def omni(ctx) -> dict:
    from workflow import combined_prompt, files, texts
    p = ctx.params
    editing = ctx.node.get("type") == "sua-video"
    prompt = (texts(ctx.inputs, "prompt") + "\n\n" + (p.get("yeu_cau") or "")).strip() if editing else combined_prompt(ctx.node, ctx.inputs)
    if not prompt:
        raise LoiNCC("Chưa có prompt / yêu cầu sửa")
    parts, task = [], None
    if editing:
        vids = files(ctx.pid, ctx.inputs, "video")
        if not vids:
            raise LoiNCC("Nối video cần sửa vào node")
        ctx.log("Đang tải video lên Google…")
        parts.append({"type": "document", "uri": _upload_file(vids[0], ctx.log)})
        for r in files(ctx.pid, ctx.inputs, "tham_chieu")[:4]:
            parts.append({"type": "image", "data": b64(r), "mime_type": mime(r)})
        task = "edit"
    else:
        first, last = files(ctx.pid, ctx.inputs, "khung_dau"), files(ctx.pid, ctx.inputs, "khung_cuoi")
        refs = files(ctx.pid, ctx.inputs, "tham_chieu")
        vid = files(ctx.pid, ctx.inputs, "video_goc")
        if vid:
            ctx.log("Đang tải video lên Google…")
            parts.append({"type": "document", "uri": _upload_file(vid[0], ctx.log)})
            task = "extend"
        elif first:
            parts += [{"type": "image", "data": b64(i), "mime_type": mime(i)} for i in (first[:1] + last[:1])]
            task = "image_to_video"
        elif refs:
            parts += [{"type": "image", "data": b64(i), "mime_type": mime(i)} for i in refs[:5]]
            task = "reference_to_video"
        else:
            task = "text_to_video"
    parts.append({"type": "text", "text": prompt})
    fmt = {"type": "video", "aspect_ratio": p.get("ti_le") if p.get("ti_le") in ("16:9", "9:16") else "16:9", "delivery": "inline"}
    if p.get("do_phan_giai"):
        fmt["resolution"] = p["do_phan_giai"]
    if p.get("thoi_luong") not in (None, "") and not editing:
        fmt["duration"] = f"{max(3, min(10, int(float(p['thoi_luong']))))}s"
    body = {"model": ctx.model or "gemini-omni-1.1-flash", "input": parts, "response_format": fmt,
            "generation_config": {"video_config": {"task": task}}, "background": True}
    ctx.log("Đã gửi yêu cầu tới Gemini Omni…")
    res = request("POST", f"{BASE}/interactions", _auth(), body, timeout=600)
    if res.get("status") not in ("completed", "failed", "cancelled", "incomplete", "budget_exceeded") and res.get("id"):
        rid = res["id"]
        res = poll(lambda: request("GET", f"{BASE}/interactions/{rid}", _auth()),
                   lambda r: r.get("status") not in ("queued", "in_progress"), every=10, log=ctx.log)
    if res.get("status") != "completed":
        raise LoiNCC(f"Omni kết thúc với trạng thái {res.get('status')}: " + str(res.get("error") or "")[:300])
    video = None
    for step in reversed(res.get("steps") or []):
        if step.get("type") == "model_output":
            vids = [c for c in step.get("content") or [] if c.get("type") == "video"]
            if vids:
                video = vids[-1]
                break
    if not video:
        raise LoiNCC("Omni không trả về video")
    out = ctx.out_dir / "video.mp4"
    if video.get("data"):
        out.write_bytes(base64.b64decode(video["data"]))
    else:
        uri = video["uri"]
        download(uri if "alt=media" in uri else uri + ":download?alt=media", out, _auth())
    return ctx.out("video", "video", out)
