"""ElevenLabs: giọng đọc (TTS), nhạc, hiệu ứng âm thanh."""
from . import LoiNCC, key
from .http import request

BASE = "https://api.elevenlabs.io"
FMT = "mp3_44100_128"


def _voice_id(name: str, auth: dict) -> str:
    """Nhận voice_id, hoặc tìm theo tên giọng trong tài khoản."""
    if not name:
        raise LoiNCC("Chưa chọn giọng — nhập voice_id hoặc tên giọng ElevenLabs trong node")
    if len(name) >= 18 and " " not in name:
        return name
    res = request("GET", f"{BASE}/v2/voices?page_size=100&search={name.replace(' ', '%20')}", auth)
    for v in res.get("voices", []):
        if v.get("name", "").lower() == name.lower() or name.lower() in v.get("name", "").lower():
            return v["voice_id"]
    raise LoiNCC(f"Không tìm thấy giọng «{name}» trong tài khoản ElevenLabs")


def run(ctx) -> dict:
    from workflow import texts
    t, p = ctx.node.get("type"), ctx.params
    auth = {"xi-api-key": key("elevenlabs")}
    if t == "giong-doc":
        text = "\n".join(x for x in [texts(ctx.inputs, "text"), p.get("loi", "")] if x and x.strip()).strip()
        if not text:
            raise LoiNCC("Chưa có lời đọc")
        model = ctx.model or "eleven_v3"
        if model == "eleven_multilingual_v2":
            ctx.log("Lưu ý: eleven_multilingual_v2 không hỗ trợ tiếng Việt")
        body = {"text": text, "model_id": model}
        if model != "eleven_multilingual_v2":
            body["language_code"] = p.get("ngon_ngu") or "vi"
        ctx.log("Đang tạo giọng…")
        audio = request("POST", f"{BASE}/v1/text-to-speech/{_voice_id(p.get('giong', ''), auth)}?output_format={FMT}",
                        auth, body, timeout=300, raw=True)
        name = "giong.mp3"
    elif t == "nhac":
        prompt = "\n".join(x for x in [texts(ctx.inputs, "text"), p.get("mo_ta", "")] if x and x.strip()).strip()
        if not prompt:
            raise LoiNCC("Chưa có mô tả nhạc")
        body = {"prompt": prompt, "music_length_ms": int(float(p.get("thoi_luong") or 30) * 1000)}
        if ctx.model:
            body["model_id"] = ctx.model
        ctx.log("Đang sáng tác nhạc…")
        audio = request("POST", f"{BASE}/v1/music?output_format={FMT}", auth, body, timeout=900, raw=True)
        name = "nhac.mp3"
    else:
        text = "\n".join(x for x in [texts(ctx.inputs, "text"), p.get("mo_ta", "")] if x and x.strip()).strip()
        if not text:
            raise LoiNCC("Chưa có mô tả tiếng động")
        body = {"text": text, "model_id": ctx.model or "eleven_text_to_sound_v2"}
        if p.get("thoi_luong") not in (None, ""):
            body["duration_seconds"] = max(0.5, min(30, float(p["thoi_luong"])))
        ctx.log("Đang tạo hiệu ứng…")
        audio = request("POST", f"{BASE}/v1/sound-generation?output_format={FMT}", auth, body, timeout=300, raw=True)
        name = "sfx.mp3"
    out = ctx.out_dir / name
    out.write_bytes(audio)
    return ctx.out("audio", "audio", out)
