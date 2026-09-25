#!/usr/bin/env python3
"""Kiểm tra cấu trúc và độ nhất quán của một dự án:  python tools/kiem_tra_du_an.py <id>

In ra LỖI (phải sửa — dữ liệu hỏng) và CẢNH BÁO (nên xem lại). Mã thoát 1 nếu có LỖI.
Đây là kiểm tra máy móc; kiểm tra nghề (cảm xúc, nhịp, giải phẫu…) do agent kiem-dinh làm.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from tao_du_an import KHUNG, TRANG_THAI  # noqa: E402

SHOT_TT = TRANG_THAI + ["dang_tao", "xong", "loi"]


def check(pid: str):
    errors, warns = [], []
    folder = ROOT / "du-an" / pid
    f = folder / "project.json"
    if not f.is_file():
        return [f"Không có {f}"], []
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"project.json sai cú pháp JSON: {e}"], []

    khung = d.get("khung", {})
    for ma, ten, _ in KHUNG:
        k = khung.get(ma)
        if not isinstance(k, dict):
            errors.append(f"Thiếu khung {ma} ({ten})")
            continue
        if k.get("trang_thai") not in TRANG_THAI:
            errors.append(f"{ma}: trang_thai '{k.get('trang_thai')}' không hợp lệ (dùng {TRANG_THAI})")
        if not isinstance(k.get("noi_dung"), dict):
            errors.append(f"{ma}: thiếu noi_dung")
    if errors:
        return errors, warns

    nd = {ma: khung[ma]["noi_dung"] for ma, _, _ in KHUNG}

    # Tham chiếu
    ref_ids = set()
    for group in ["nhan_vat", "trang_phuc", "san_pham", "boi_canh", "khac"]:
        for r in nd["3_tham_chieu"].get(group, []):
            rid = r.get("id")
            if not rid:
                errors.append(f"3_tham_chieu.{group}: có thẻ thiếu id")
                continue
            if rid in ref_ids:
                errors.append(f"Tham chiếu trùng id {rid}")
            ref_ids.add(rid)
            for a in r.get("anh", []):
                if not (folder / a).is_file():
                    warns.append(f"Tham chiếu {rid}: không thấy file ảnh {a}")
            if r.get("anh") and not r.get("mo_ta"):
                warns.append(f"Tham chiếu {rid}: có ảnh nhưng chưa có mô tả (Chỉ Đạo Hình Ảnh cần viết)")

    # Kịch bản
    canh = nd["5_kich_ban"].get("canh", [])
    canh_ids = [c.get("id") for c in canh]
    if len(set(canh_ids)) != len(canh_ids):
        errors.append("5_kich_ban: trùng id cảnh")
    canh_by_id = {c.get("id"): c for c in canh}
    for c in canh:
        for nv in c.get("nhan_vat", []):
            if nv not in ref_ids:
                warns.append(f"Cảnh {c.get('id')}: nhân vật {nv} chưa có thẻ ở khung 3")
    target = nd["1_y_tuong"].get("thoi_luong_giay") or 0
    total_canh = sum(float(c.get("thoi_luong_giay") or 0) for c in canh)
    if canh and target and abs(total_canh - target) > 0.1 * target:
        warns.append(f"Tổng thời lượng kịch bản {total_canh:g}s lệch mục tiêu {target}s quá 10%")

    # Shot
    shots = nd["6_storyboard"].get("shots", [])
    shot_ids = [s.get("id") for s in shots]
    if len(set(shot_ids)) != len(shot_ids):
        errors.append("6_storyboard: trùng id shot")
    per_canh = {}
    clips = {}
    for s in shots:
        sid = s.get("id")
        if s.get("canh") and s["canh"] not in canh_by_id:
            warns.append(f"Shot {sid}: cảnh {s['canh']} không có trong kịch bản")
        if s.get("trang_thai") and s["trang_thai"] not in SHOT_TT:
            errors.append(f"Shot {sid}: trang_thai '{s['trang_thai']}' không hợp lệ")
        if not isinstance(s.get("tham_chieu", []), list):
            errors.append(f"Shot {sid}: tham_chieu phải là danh sách")
        for r in s.get("tham_chieu", []) or []:
            if r not in ref_ids:
                warns.append(f"Shot {sid}: tham chiếu {r} không tồn tại ở khung 3")
        for key in ["anh_storyboard", "video"]:
            if s.get(key) and not (folder / s[key]).is_file():
                warns.append(f"Shot {sid}: không thấy file {key} = {s[key]}")
        per_canh[s.get("canh")] = per_canh.get(s.get("canh"), 0) + float(s.get("thoi_luong") or 0)
        if s.get("clip"):
            clips.setdefault(s["clip"], []).append(s)
    for cid, sec in per_canh.items():
        c = canh_by_id.get(cid)
        if c and c.get("thoi_luong_giay") and abs(sec - float(c["thoi_luong_giay"])) > max(1.0, 0.2 * float(c["thoi_luong_giay"])):
            warns.append(f"Cảnh {cid}: tổng shot {sec:g}s khác thời lượng cảnh {c['thoi_luong_giay']}s")
    for c in canh:
        if shots and c.get("id") not in per_canh:
            warns.append(f"Cảnh {c.get('id')} chưa có shot nào")
    for clip, ss in clips.items():
        sec = sum(float(s.get("thoi_luong") or 0) for s in ss)
        tools = {s.get("cong_cu") for s in ss if s.get("cong_cu")}
        if len(tools) > 1:
            warns.append(f"Clip {clip}: các shot dùng công cụ khác nhau {sorted(tools)}")
        if sec > 30:
            warns.append(f"Clip {clip}: {sec:g}s — vượt giới hạn 30s của công cụ mạnh nhất hiện có")

    # Ép cảnh trỏ đúng chỗ
    for e in nd["4_ep_canh"].get("theo_canh", []):
        if e.get("canh") and e["canh"] not in canh_by_id and e["canh"] not in shot_ids:
            warns.append(f"Ép cảnh trỏ tới '{e['canh']}' nhưng không có cảnh/shot này")

    # Dựng
    for i, t in enumerate(nd["8_dung_phim"].get("danh_sach", []), 1):
        if t.get("video") and not (folder / t["video"]).is_file():
            warns.append(f"Timeline dòng {i}: không thấy video {t['video']}")
        if t.get("shot") and t["shot"] not in shot_ids:
            warns.append(f"Timeline dòng {i}: shot {t['shot']} không có trong storyboard")
    for tr in nd["8_dung_phim"].get("am_thanh", []) or []:
        if tr.get("file") and not (folder / tr["file"]).is_file():
            warns.append(f"Track âm thanh {tr.get('id', '?')}: không thấy file {tr['file']}")
        if not tr.get("file") and tr.get("noi_dung"):
            warns.append(f"Track âm thanh {tr.get('id', '?')}: có lời nhưng chưa tạo file (Kỹ Sư Âm Thanh)")

    # Bảng kết nối: mảnh ghép chưa chọn (người dùng phải tự chọn)
    try:
        cfg = json.loads((ROOT / "thu-vien" / "bang-ket-noi.json").read_text(encoding="utf-8"))
        chon = d.get("bang_ket_noi", {})
        thieu = [m["ten"] for m in cfg["manh_ghep"] if not chon.get(m["id"], {}).get("nguon")]
        if thieu:
            warns.append("Bảng kết nối — chưa chọn: " + ", ".join(thieu))
    except (OSError, json.JSONDecodeError, KeyError):
        warns.append("Không đọc được thu-vien/bang-ket-noi.json")

    # Ngân sách credit
    sx = nd["7_san_xuat"]
    budget, used = sx.get("ngan_sach_credit"), sx.get("da_dung_credit") or 0
    if budget not in (None, "") and float(used) > float(budget):
        warns.append(f"Đã dùng {used} credit, vượt ngân sách {budget}")
    elif budget not in (None, "") and float(used) > 0.8 * float(budget):
        warns.append(f"Đã dùng {used}/{budget} credit (trên 80% ngân sách)")

    # Mã Higgsfield của tham chiếu
    for group in ["nhan_vat", "trang_phuc", "san_pham", "boi_canh"]:
        for r in nd["3_tham_chieu"].get(group, []):
            if r.get("anh") and not (r.get("element_id") or r.get("soul_id")) and khung["6_storyboard"]["trang_thai"] == "da_duyet":
                warns.append(f"Tham chiếu {r.get('id')}: chưa có element_id/soul_id trên Higgsfield — nhân vật/sản phẩm dễ lệch giữa các clip")
    return errors, warns


def main():
    if len(sys.argv) < 2:
        sys.exit("Cách dùng: python tools/kiem_tra_du_an.py <id-du-an>")
    errors, warns = check(sys.argv[1])
    for e in errors:
        print("LỖI:", e)
    for w in warns:
        print("CẢNH BÁO:", w)
    if not errors and not warns:
        print("OK — không phát hiện vấn đề cấu trúc.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
