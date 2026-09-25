"""Node chạy trên máy bằng ffmpeg: trích khung, cắt, dựng phim, xuất."""
import re
import shutil

from ghep_phim import LoiDung, assemble, extract_one, trim

from . import LoiNCC


def _one(ctx, port: str, kieu: str):
    fs = [v for v in ctx.inputs.get(port, []) if v.get("kieu") == kieu or kieu == "any"]
    if not fs:
        raise LoiNCC(f"Chưa nối đầu vào «{port}»")
    return ctx.folder / fs[0]["gia_tri"]


def run(ctx) -> dict:
    t, p = ctx.node.get("type"), ctx.params
    try:
        if t == "trich-khung":
            out = extract_one(_one(ctx, "video", "video"), ctx.out_dir / "khung.png", p.get("vi_tri") or "cuoi", p.get("giay") or 0)
            return ctx.out("image", "image", out)
        if t == "cat-video":
            out = trim(_one(ctx, "video", "video"), ctx.out_dir / "cat.mp4", p.get("tu") or 0, p.get("den"))
            return ctx.out("video", "video", out)
        if t == "dung-phim":
            vids = [v for v in ctx.inputs.get("video", []) if v.get("kieu") == "video"]
            if not vids:
                raise LoiNCC("Nối ít nhất một video vào cổng «Các đoạn» (xếp trái → phải = thứ tự phát)")
            tr, dur = p.get("chuyen_canh") or "cat", p.get("do_dai_chuyen") or 0.5
            clips = [{"path": ctx.folder / v["gia_tri"], "tr": tr, "dur": dur} for v in vids]
            starts = [float(x) for x in re.findall(r"\d+(?:[.,]\d+)?", str(p.get("bat_dau_am_thanh") or "").replace(",", "."))]
            extras = []
            for i, a in enumerate(v for v in ctx.inputs.get("audio", []) if v.get("kieu") == "audio"):
                extras.append({"path": ctx.folder / a["gia_tri"], "start": starts[i] if i < len(starts) else 0, "vol": 1.0})
            for m in ctx.inputs.get("nhac", [])[:1]:
                vol = p.get("am_luong_nhac")
                extras.append({"path": ctx.folder / m["gia_tri"], "start": 0, "vol": 0.6 if vol in (None, "") else float(vol), "fade": True})
            ov = p.get("am_luong_goc")
            size = str(p.get("do_phan_giai") or "").strip() or "1920x1080"
            total = assemble(clips, extras, ctx.out_dir / "phim.mp4", size, 24, 1.0 if ov in (None, "") else float(ov))
            ctx.log(f"Đã dựng {total:.1f}s")
            return ctx.out("video", "video", ctx.out_dir / "phim.mp4")
        if t == "xuat":
            src = _one(ctx, "video", "video")
            name = re.sub(r"[^\w.-]+", "-", (p.get("ten_file") or "phim-hoan-chinh").strip()) or "phim"
            if not name.lower().endswith(".mp4"):
                name += ".mp4"
            dest = ctx.folder / "xuat" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            return {"file": {"kieu": "video", "gia_tri": ctx.rel(dest)}}
    except LoiDung as e:
        raise LoiNCC(str(e)) from e
    raise LoiNCC(f"Node «{t}» không chạy trên máy được")
