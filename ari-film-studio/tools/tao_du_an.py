#!/usr/bin/env python3
"""Tạo dự án phim mới:  python tools/tao_du_an.py "Tên phim"

Sinh du-an/<ten>/project.json với đủ 9 khung ở trạng thái "nhap".
Cấu trúc này là hợp đồng chung giữa bảng điều khiển và các agent —
đổi tên trường ở đây thì phải đổi cả giao-dien/app.js và tools/kiem_tra_du_an.py.
"""
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (mã khung, tên hiển thị, agent phụ trách)
KHUNG = [
    ("1_y_tuong", "Ý tưởng", "dao-dien, bien-kich"),
    ("2_phong_cach", "Phong cách & Thể loại", "chi-dao-hinh-anh"),
    ("3_tham_chieu", "Tham chiếu", "chi-dao-hinh-anh"),
    ("4_ep_canh", "Yêu cầu đặc biệt (ép cảnh)", "người dùng"),
    ("5_kich_ban", "Kịch bản", "bien-kich"),
    ("6_storyboard", "Storyboard & Máy quay", "quay-phim, hoa-si-storyboard"),
    ("7_san_xuat", "Sản xuất video", "ky-thuat-vien-ai"),
    ("8_dung_phim", "Dựng phim", "bien-tap-vien"),
    ("9_kiem_dinh", "Kiểm định", "kiem-dinh"),
]

TRANG_THAI = ["nhap", "cho_duyet", "da_duyet", "can_sua"]


def safe_name(text: str) -> str:
    text = unicodedata.normalize("NFD", text).replace("đ", "d").replace("Đ", "D")
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-._").lower()
    return text or "du-an"


def empty_project(ten: str) -> dict:
    now = datetime.now().isoformat(timespec="seconds")
    noi_dung = {
        "1_y_tuong": {"logline": "", "cot_truyen": "", "the_loai": "", "thong_diep": "",
                      "doi_tuong": "", "thoi_luong_giay": 60, "ti_le_khung": "16:9",
                      "nen_tang": "", "phuong_an": []},
        "2_phong_cach": {"phong_cach_chinh": "", "ket_hop": [], "the_loai_chuyen_gia": "",
                         "bang_mau": [], "tinh_than": "", "ghi_chu": ""},
        "3_tham_chieu": {"nhan_vat": [], "trang_phuc": [], "san_pham": [], "boi_canh": [], "khac": []},
        "4_ep_canh": {"toan_phim": [], "theo_canh": []},
        "5_kich_ban": {"canh": []},
        "6_storyboard": {"shots": []},
        "7_san_xuat": {"cong_cu_mac_dinh": "", "nhat_ky": []},
        "8_dung_phim": {"danh_sach": [], "nhac": "", "am_luong_nhac": 0.6, "chuyen_canh_mac_dinh": "cat",
                        "do_phan_giai": "1920x1080", "fps": 24, "xuat": "xuat/phim-hoan-chinh.mp4", "ghi_chu": ""},
        "9_kiem_dinh": {"bao_cao": []},
    }
    return {
        "ten": ten,
        "phien_ban_cau_truc": 1,
        "tao_luc": now,
        "cap_nhat": now,
        "che_do": "tung_buoc",  # tung_buoc = dừng chờ duyệt ở mỗi khung; tu_dong = chạy liền
        "khung": {
            ma: {"ten": ten_khung, "phu_trach": ai, "trang_thai": "nhap", "khoa": False,
                 "noi_dung": noi_dung[ma], "ghi_chu_nguoi_dung": "", "de_xuat_ai": ""}
            for ma, ten_khung, ai in KHUNG
        },
        "nhat_ky": [{"luc": now, "ai": "he-thong", "viec": "Tạo dự án"}],
    }


def create_project(ten: str, projects_dir: Path = ROOT / "du-an") -> str:
    pid = safe_name(ten)
    folder = projects_dir / pid
    if (folder / "project.json").exists():
        raise FileExistsError(pid)
    for sub in ["tham-chieu/nhan-vat", "tham-chieu/trang-phuc", "tham-chieu/san-pham",
                "tham-chieu/boi-canh", "tham-chieu/khac", "storyboard", "video", "xuat"]:
        (folder / sub).mkdir(parents=True, exist_ok=True)
    with open(folder / "project.json", "w", encoding="utf-8") as f:
        json.dump(empty_project(ten), f, ensure_ascii=False, indent=2)
        f.write("\n")
    return pid


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Cách dùng: python tools/tao_du_an.py "Tên phim"')
    try:
        print("Đã tạo: du-an/" + create_project(" ".join(sys.argv[1:])))
    except FileExistsError as e:
        sys.exit(f"Dự án du-an/{e} đã tồn tại.")
