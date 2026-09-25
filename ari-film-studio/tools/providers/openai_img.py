"""OpenAI Images (ChatGPT ảnh): tạo ảnh từ chữ, hoặc từ ảnh tham chiếu (images/edits)."""
import base64

from . import LoiNCC, key
from .http import multipart, request

BASE = "https://api.openai.com/v1"
SIZES = {"16:9": "1536x864", "9:16": "864x1536", "1:1": "1024x1024", "4:3": "1344x1008", "3:4": "1008x1344", "21:9": "1792x768"}


def run(ctx) -> dict:
    from workflow import combined_prompt, files
    prompt = combined_prompt(ctx.node, ctx.inputs)
    if not prompt:
        raise LoiNCC("Chưa có prompt (gõ trong node hoặc nối node Prompt vào)")
    model = ctx.model or "gpt-image-2.5-flare"
    size = SIZES.get(ctx.params.get("ti_le") or "", "auto")
    quality = ctx.params.get("chat_luong") or "auto"
    auth = {"Authorization": f"Bearer {key('openai')}"}
    refs = files(ctx.pid, ctx.inputs, "tham_chieu")[:16]
    ctx.log("Đang tạo ảnh…")
    if refs:
        body, ctype = multipart({"model": model, "prompt": prompt, "size": size, "quality": quality, "output_format": "png"},
                                [("image[]", p) for p in refs])
        res = request("POST", f"{BASE}/images/edits", {**auth, "Content-Type": ctype}, body, timeout=300)
    else:
        res = request("POST", f"{BASE}/images/generations", auth,
                      {"model": model, "prompt": prompt, "size": size, "quality": quality, "output_format": "png"}, timeout=300)
    data = (res.get("data") or [{}])[0]
    if not data.get("b64_json"):
        raise LoiNCC("OpenAI không trả về ảnh: " + str(res)[:300])
    out = ctx.out_dir / "anh.png"
    out.write_bytes(base64.b64decode(data["b64_json"]))
    return ctx.out("image", "image", out)
