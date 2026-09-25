#!/usr/bin/env python3
"""Ghép phim theo timeline khung 8 bằng ffmpeg.

  python tools/ghep_phim.py <id>                       xuất phim theo 8_dung_phim
  python tools/ghep_phim.py --khung <id> <video>       trích 6 khung hình để agent xem (du-an/<id>/tmp-khung/)
  python tools/ghep_phim.py --khung-video <video> <thu-muc>   trích 2 khung/giây (học phong cách)

Cần ffmpeg trong PATH, hoặc gói Python imageio-ffmpeg (pip install imageio-ffmpeg).
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("Không tìm thấy ffmpeg. Cài bằng:  pip install imageio-ffmpeg")


def run(args):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        sys.exit("ffmpeg lỗi:\n" + p.stderr[-2000:])
    return p


def duration(ff: str, path: Path) -> float:
    p = subprocess.run([ff, "-hide_banner", "-i", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", p.stderr)
    if not m:
        sys.exit(f"Không đọc được thời lượng của {path}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def has_audio(ff: str, path: Path) -> bool:
    p = subprocess.run([ff, "-hide_banner", "-i", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return "Audio:" in p.stderr


def extract_frames(video: Path, out_dir: Path, fps: str):
    ff = ffmpeg_bin()
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("khung_*.jpg"):
        old.unlink()
    run([ff, "-loglevel", "error", "-i", str(video), "-vf", f"fps={fps},scale=640:-2", "-q:v", "3", str(out_dir / "khung_%03d.jpg")])
    files = sorted(out_dir.glob("khung_*.jpg"))
    print(f"Đã trích {len(files)} khung vào {out_dir}")
    for f in files:
        print(f)


def build(pid: str):
    folder = ROOT / "du-an" / pid
    d = json.loads((folder / "project.json").read_text(encoding="utf-8"))
    cfg = d["khung"]["8_dung_phim"]["noi_dung"]
    items = [t for t in cfg.get("danh_sach", []) if t.get("video")]
    if not items:
        sys.exit("Timeline trống (khung 8 chưa có dòng nào có video).")
    ff = ffmpeg_bin()
    w, h = (int(x) for x in str(cfg.get("do_phan_giai") or "1920x1080").lower().split("x"))
    fps = int(cfg.get("fps") or 24)
    default_tr = cfg.get("chuyen_canh_mac_dinh") or "cat"

    inputs, filters, segs = [], [], []
    for i, t in enumerate(items):
        src = folder / t["video"]
        if not src.is_file():
            sys.exit(f"Không thấy video {src}")
        full = duration(ff, src)
        start = float(t.get("cat_dau") or 0)
        end = float(t["cat_cuoi"]) if t.get("cat_cuoi") not in (None, "") else full
        end = min(end, full)
        if end - start < 0.1:
            sys.exit(f"Dòng {i + 1} ({t.get('shot')}): đoạn cắt quá ngắn ({start}–{end}s)")
        inputs += ["-i", str(src)]
        filters.append(
            f"[{i}:v]trim={start}:{end},setpts=PTS-STARTPTS,scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={fps},format=yuv420p,settb=AVTB[v{i}]")
        if has_audio(ff, src):
            filters.append(f"[{i}:a]atrim={start}:{end},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[a{i}]")
        else:
            filters.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{end - start}[a{i}]")
        segs.append({"len": end - start, "tr": t.get("chuyen_canh") or default_tr, "dur": float(t.get("do_dai_chuyen") or 0.5)})

    # Nối lần lượt: cắt thẳng = concat, hoà tan = xfade fade, qua đen = xfade fadeblack
    v, a, total = "v0", "a0", segs[0]["len"]
    for i in range(1, len(segs)):
        tr = segs[i - 1]["tr"]
        dur = min(segs[i - 1]["dur"], segs[i - 1]["len"] / 2, segs[i]["len"] / 2)
        if tr in ("mo", "den") and dur > 0.05:
            kind = "fade" if tr == "mo" else "fadeblack"
            filters.append(f"[{v}][v{i}]xfade=transition={kind}:duration={dur}:offset={total - dur}[vx{i}]")
            filters.append(f"[{a}][a{i}]acrossfade=d={dur}[ax{i}]")
            total += segs[i]["len"] - dur
        else:
            filters.append(f"[{v}][{a}][v{i}][a{i}]concat=n=2:v=1:a=1[vc{i}][ax{i}]")
            filters.append(f"[vc{i}]settb=AVTB[vx{i}]")
            total += segs[i]["len"]
        v, a = f"vx{i}", f"ax{i}"

    # Nhạc nền (kéo dài hết phim, tự mờ dần) + các track âm thanh đặt theo thời điểm
    extra = []
    music = cfg.get("nhac")
    if music:
        mpath = folder / music
        if not mpath.is_file():
            sys.exit(f"Không thấy file nhạc {mpath}")
        vol = float(cfg.get("am_luong_nhac") if cfg.get("am_luong_nhac") is not None else 0.6)
        extra.append({"file": mpath, "start": 0.0, "vol": vol, "fade": True})
    for tr in cfg.get("am_thanh", []) or []:
        if not tr.get("file"):
            continue
        tpath = folder / tr["file"]
        if not tpath.is_file():
            sys.exit(f"Không thấy file âm thanh {tpath} (track {tr.get('id', '?')})")
        vol = float(tr["am_luong"]) if tr.get("am_luong") not in (None, "") else 1.0
        extra.append({"file": tpath, "start": float(tr.get("bat_dau") or 0), "vol": vol, "fade": False})
    if extra:
        labels = [a]
        for j, e in enumerate(extra):
            idx = len(items) + j
            inputs += ["-i", str(e["file"])]
            chain = f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume={e['vol']}"
            if e["fade"]:
                fade_out = min(2.0, total / 4)
                chain += f",atrim=0:{total},asetpts=PTS-STARTPTS,afade=t=out:st={total - fade_out}:d={fade_out}"
            if e["start"] > 0:
                ms = int(e["start"] * 1000)
                chain += f",adelay={ms}|{ms}"
            filters.append(chain + f"[ex{j}]")
            labels.append(f"ex{j}")
        filters.append("".join(f"[{l}]" for l in labels) +
                       f"amix=inputs={len(labels)}:duration=first:normalize=0,atrim=0:{total}[afinal]")
        a = "afinal"

    out = folder / (cfg.get("xuat") or "xuat/phim-hoan-chinh.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)
    run([ff, "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
         "-map", f"[{v}]", "-map", f"[{a}]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    print(f"Đã xuất: {out}  ({total:.1f}s, {len(items)} đoạn)")


def main():
    a = sys.argv[1:]
    if len(a) == 3 and a[0] == "--khung":
        folder = ROOT / "du-an" / a[1]
        return extract_frames(folder / a[2], folder / "tmp-khung", "6/" + str(max(1, round(duration(ffmpeg_bin(), folder / a[2])))))
    if len(a) == 3 and a[0] == "--khung-video":
        return extract_frames(Path(a[1]), Path(a[2]), "2")
    if len(a) == 1 and not a[0].startswith("-"):
        return build(a[0])
    sys.exit(__doc__)


if __name__ == "__main__":
    main()
