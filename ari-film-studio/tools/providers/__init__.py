"""Nhà cung cấp cho node workflow.

run(ctx) chọn hàm theo (provider, loại node) và trả về {cong_ra: {"kieu", "gia_tri"}}.
Lỗi thân thiện: raise LoiNCC("…") — thông báo hiện thẳng trên node.
API key đọc từ cai-dat/khoa-api.json (không đưa lên git) hoặc biến môi trường.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
KEY_FILE = ROOT / "cai-dat" / "khoa-api.json"
KEY_FIELDS = {
    "openai": ["key"], "google": ["key"], "elevenlabs": ["key"], "tripo": ["key"],
    "higgsfield": ["key_id", "key_secret"],
}
ENV = {"openai": {"key": "OPENAI_API_KEY"}, "google": {"key": "GEMINI_API_KEY"},
       "elevenlabs": {"key": "ELEVENLABS_API_KEY"}, "tripo": {"key": "TRIPO_API_KEY"},
       "higgsfield": {"key_id": "HF_API_KEY_ID", "key_secret": "HF_API_KEY_SECRET"}}


class LoiNCC(RuntimeError):
    friendly = True


def load_keys() -> dict:
    data = {}
    if KEY_FILE.is_file():
        try:
            data = json.loads(KEY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    for svc, fields in ENV.items():
        for field, env in fields.items():
            if not data.get(svc, {}).get(field) and os.environ.get(env):
                data.setdefault(svc, {})[field] = os.environ[env]
    return data


def key(svc: str, field: str = "key") -> str:
    val = load_keys().get(svc, {}).get(field)
    if not val:
        raise LoiNCC(f"Chưa có API key {svc} — nhập ở ⚙ Cài đặt trên canvas")
    return val


def save_keys(incoming: dict):
    """Chỉ ghi những ô người dùng thực sự nhập (ô để trống / dạng ••• giữ nguyên key cũ)."""
    data = {}
    if KEY_FILE.is_file():
        try:
            data = json.loads(KEY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    for svc, fields in KEY_FIELDS.items():
        for f in fields:
            v = (incoming.get(svc) or {}).get(f)
            if v is None or v == "" or "•" in v:
                continue
            if v == "-":
                data.get(svc, {}).pop(f, None)
            else:
                data.setdefault(svc, {})[f] = v.strip()
    KEY_FILE.parent.mkdir(exist_ok=True)
    KEY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def masked_keys() -> dict:
    keys = load_keys()
    return {svc: {f: (("••••" + keys[svc][f][-4:]) if keys.get(svc, {}).get(f) else "") for f in fields}
            for svc, fields in KEY_FIELDS.items()}


def run(ctx) -> dict:
    prov, typ = ctx.node.get("provider"), ctx.node.get("type")
    if prov == "ffmpeg":
        from . import local
        return local.run(ctx)
    if prov == "openai" and typ == "tao-anh":
        from . import openai_img
        return openai_img.run(ctx)
    if prov == "google-image" and typ == "tao-anh":
        from . import google
        return google.image(ctx)
    if prov == "google-veo" and typ == "tao-video":
        from . import google
        return google.veo(ctx)
    if prov == "google-omni" and typ in ("tao-video", "sua-video"):
        from . import google
        return google.omni(ctx)
    if prov == "elevenlabs" and typ in ("giong-doc", "nhac", "hieu-ung-am"):
        from . import elevenlabs
        return elevenlabs.run(ctx)
    if prov == "tripo" and typ == "tao-3d":
        from . import tripo
        return tripo.run(ctx)
    if prov == "higgsfield" and typ in ("tao-anh", "tao-video"):
        from . import higgsfield
        return higgsfield.run(ctx)
    raise LoiNCC(f"Nhà cung cấp «{prov}» chưa hỗ trợ node «{typ}»")
