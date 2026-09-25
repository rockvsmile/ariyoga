#!/usr/bin/env python3
"""Sinh các template workflow khởi đầu vào thu-vien/mau-workflow/.

    python tools/tao_mau.py            tạo các mẫu còn thiếu (không ghi đè mẫu đã có)
    python tools/tao_mau.py --ghi-de   tạo lại tất cả

Mẫu của bạn (lưu từ canvas) nằm cùng thư mục và không bị đụng tới trừ khi trùng tên file.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "thu-vien" / "mau-workflow"


class Mau:
    def __init__(self, fid, ten, mo_ta, nganh, the_loai="", phong_cach="", ky_nang=(), ti_le="9:16", thoi_luong=30):
        self.fid = fid
        self.data = {"ten": ten, "mo_ta": mo_ta, "meta": {"nganh": nganh, "the_loai": the_loai, "phong_cach": phong_cach,
                     "ky_nang": list(ky_nang), "ti_le": ti_le, "thoi_luong": thoi_luong}, "nodes": [], "edges": []}
        self.k = {}

    def n(self, key, typ, col, row, ten=None, provider="", model="", **params):
        nid = f"n{len(self.data['nodes']) + 1}"
        self.k[key] = nid
        self.data["nodes"].append({"id": nid, "type": typ, "x": col * 290, "y": row * 250, "ten": ten or "", "provider": provider,
                                   "model": model, "params": params, "khoa": False, "ghi_chu": ""})
        return self

    def e(self, a, pa, b, pb):
        self.data["edges"].append({"id": f"e{len(self.data['edges']) + 1}", "tu": {"node": self.k[a], "cong": pa}, "den": {"node": self.k[b], "cong": pb}})
        return self

    def save(self, force):
        OUT.mkdir(parents=True, exist_ok=True)
        f = OUT / f"{self.fid}.json"
        if f.exists() and not force:
            return False
        f.write_text(json.dumps(self.data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return True


def mau_khoi_dau():
    m = []
    # 1. Kỹ thuật nối cảnh: ảnh đầu (ChatGPT) + ảnh cuối (Nano Banana) → Veo đầu–cuối → trích khung cuối → cảnh sau
    t = Mau("ky-thuat-noi-canh-dau-cuoi", "Kỹ thuật — Nối cảnh bằng khung đầu & khung cuối",
            "Ảnh mở cảnh bằng ChatGPT, ảnh kết cảnh bằng Nano Banana → Veo 3.1 tạo chuyển động giữa hai ảnh → trích khung cuối làm khung đầu cho cảnh sau (Kling qua Higgsfield). Dùng làm khung xương cho mọi phim nhiều cảnh.",
            "Chung", ky_nang=["cinematic-techniques"], ti_le="16:9", thoi_luong=20)
    t.n("pA", "prompt", 0, 0, "Prompt ảnh mở cảnh", noi_dung="Mô tả khung hình mở đầu cảnh 1…")
    t.n("pB", "prompt", 0, 1, "Prompt ảnh kết cảnh", noi_dung="Mô tả khung hình kết thúc cảnh 1…")
    t.n("pV", "prompt", 0, 2, "Prompt chuyển động cảnh 1", noi_dung="Máy quay và hành động giữa hai khung…")
    t.n("iA", "tao-anh", 1, 0, "Khung đầu (ChatGPT)", "openai", "gpt-image-2.5-flare", ti_le="16:9")
    t.n("iB", "tao-anh", 1, 1, "Khung cuối (Nano Banana)", "google-image", "gemini-3.1-flash-image", ti_le="16:9")
    t.n("v1", "tao-video", 2, 0.5, "Cảnh 1 — Veo đầu/cuối", "google-veo", "veo-3.1-generate-preview", che_do="dau-cuoi", thoi_luong=8, ti_le="16:9")
    t.n("tk", "trich-khung", 3, 0, "Khung cuối cảnh 1", "ffmpeg", vi_tri="cuoi")
    t.n("p2", "prompt", 3, 1.2, "Prompt cảnh 2", noi_dung="Cảnh 2 tiếp nối từ khung cuối cảnh 1…")
    t.n("v2", "tao-video", 4, 0.5, "Cảnh 2 — nối tiếp", "higgsfield-mcp", "kling3_0", che_do="khung-dau", thoi_luong=5, ti_le="16:9")
    t.n("nh", "nhac", 4, 2, "Nhạc nền", "elevenlabs", mo_ta="Nhạc điện ảnh nhẹ nhàng, dâng dần", thoi_luong=20)
    t.n("dp", "dung-phim", 5, 1, "Dựng", "ffmpeg", chuyen_canh="cat", do_phan_giai="1920x1080")
    t.n("dy", "duyet", 6, 1, "Duyệt bản dựng")
    t.n("xu", "xuat", 7, 1, "Xuất", "ffmpeg", ten_file="phim-noi-canh")
    t.e("pA", "text", "iA", "prompt").e("pB", "text", "iB", "prompt").e("iA", "image", "v1", "khung_dau").e("iB", "image", "v1", "khung_cuoi")
    t.e("pV", "text", "v1", "prompt").e("v1", "video", "tk", "video").e("tk", "image", "v2", "khung_dau").e("p2", "text", "v2", "prompt")
    t.e("v1", "video", "dp", "video").e("v2", "video", "dp", "video").e("nh", "audio", "dp", "nhac").e("dp", "video", "dy", "any").e("dy", "any", "xu", "video")
    m.append(t)

    # 2. Yoga Inside Flow Reels
    t = Mau("yoga-inside-flow-reels", "Yoga — Inside Flow Reels 30s",
            "Cô giáo (Nhân vật) + phòng tập → 3 shot flow mượt theo nhạc, giọng dẫn nhẹ, phụ đề. Chuyển động máy trôi, ánh giờ vàng.",
            "Yoga", "video-yoga-wellness", ky_nang=["cinematic-techniques"], ti_le="9:16", thoi_luong=30)
    t.n("nv", "nhan-vat", 0, 0, "Cô giáo / học viên", mo_ta="(tải ảnh chuẩn + mô tả khuôn mặt, tóc, trang phục tập)")
    t.n("bc", "anh", 0, 1, "Ảnh phòng tập")
    t.n("p1", "prompt", 1, 0, "Shot 1 — hơi thở mở đầu", noi_dung="Static wide shot, golden hour window light, she sits in easy pose breathing slowly, dust motes, warm amber grade, 9:16")
    t.n("p2", "prompt", 1, 1, "Shot 2 — dòng chảy", noi_dung="Steadicam slow orbit, she flows from downward dog into warrior II in one continuous smooth movement, anatomically correct pose, soft rim light")
    t.n("p3", "prompt", 1, 2, "Shot 3 — cao trào", noi_dung="Low angle, slow push in, she opens arms in a heart-opening pose, sun flare behind, peaceful confident smile")
    for i, (row, name) in enumerate([(0, "Shot 1"), (1, "Shot 2"), (2, "Shot 3")], 1):
        t.n(f"v{i}", "tao-video", 2, row, name, "higgsfield-mcp", "seedance_2_0", che_do="tham-chieu", thoi_luong=8, ti_le="9:16")
        t.e("nv", "image", f"v{i}", "tham_chieu").e("bc", "image", f"v{i}", "tham_chieu").e(f"p{i}", "text", f"v{i}", "prompt").e("nv", "text", f"v{i}", "prompt")
    t.n("vo", "giong-doc", 2, 3, "Giọng dẫn", "elevenlabs", "eleven_v3", loi="Hít vào… và để cơ thể tự chảy theo hơi thở. Inside Flow cùng Ari Yoga.")
    t.n("nh", "nhac", 2, 4, "Nhạc", "tu-lam", mo_ta="Nhạc Inside Flow của lớp (file có bản quyền)")
    t.n("dp", "dung-phim", 3, 1.5, "Dựng", "ffmpeg", chuyen_canh="mo", do_dai_chuyen=0.6, do_phan_giai="1080x1920", bat_dau_am_thanh="2")
    t.n("hk", "hau-ky", 4, 1.5, "Phụ đề", "higgsfield-mcp", viec="phu-de")
    t.n("kd", "kiem-dinh", 4, 3, "Soi tư thế", "claude", tieu_chi="Tư thế yoga đúng giải phẫu, không thừa/thiếu ngón, gương mặt nhất quán")
    t.n("dy", "duyet", 5, 1.5, "Duyệt")
    t.n("xu", "xuat", 6, 1.5, "Xuất", "ffmpeg", ten_file="yoga-reels")
    t.e("v1", "video", "dp", "video").e("v2", "video", "dp", "video").e("v3", "video", "dp", "video").e("vo", "audio", "dp", "audio").e("nh", "audio", "dp", "nhac")
    t.e("dp", "video", "hk", "video").e("dp", "video", "kd", "any").e("hk", "video", "dy", "any").e("dy", "any", "xu", "video")
    m.append(t)

    # 3. Spa
    t = Mau("spa-thu-gian-sang-trong", "Spa — Thư giãn sang trọng 30s",
            "Không gian spa → cận tay kỹ thuật viên & sản phẩm → khách thư giãn → kết quả, giọng nữ nhẹ + nhạc thiền. Phong cách quiet luxury ấm.",
            "Spa", "spa-lam-dep", "01-quiet-luxury-kien-truc", ["cinematic-techniques", "tvc-thoi-trang"], "9:16", 30)
    t.n("sp", "anh", 0, 0, "Ảnh sản phẩm / liệu trình")
    t.n("kg", "anh", 0, 1, "Ảnh không gian spa")
    t.n("id", "prompt", 0, 2, "Ý tưởng", noi_dung="Video 30s giới thiệu liệu trình chăm sóc da thư giãn…")
    t.n("wp", "viet-prompt", 1, 2, "Viết prompt 3 shot", "claude", cho_cong_cu="Veo 3.1", phong_cach="01-quiet-luxury-kien-truc")
    t.n("k1", "tao-anh", 1, 0, "Khung mở (Nano Banana)", "google-image", "gemini-3-pro-image-preview", prompt="Warm candlelit spa room, steam, towels, stones, natural skin texture, soft top light", ti_le="9:16")
    t.n("v1", "tao-video", 2, 0, "Shot không gian", "google-veo", "veo-3.1-generate-preview", che_do="khung-dau", thoi_luong=8, ti_le="9:16")
    t.n("v2", "tao-video", 2, 1, "Shot tay & sản phẩm", "google-veo", "veo-3.1-generate-preview", che_do="tham-chieu", thoi_luong=8, ti_le="9:16")
    t.n("v3", "tao-video", 2, 2, "Shot khách thư giãn", "google-omni", "gemini-omni-1.1-flash", thoi_luong=8, ti_le="9:16")
    t.n("vo", "giong-doc", 2, 3, "Giọng nữ nhẹ", "elevenlabs", "eleven_v3", loi="Dành cho bạn một khoảng lặng…")
    t.n("nh", "nhac", 2, 4, "Nhạc thiền", "elevenlabs", mo_ta="Ambient spa music, soft piano, water, wind chimes, slow", thoi_luong=30)
    t.n("dp", "dung-phim", 3, 2, "Dựng", "ffmpeg", chuyen_canh="mo", do_dai_chuyen=0.8, do_phan_giai="1080x1920", am_luong_nhac=0.5)
    t.n("dy", "duyet", 4, 2, "Duyệt")
    t.n("xu", "xuat", 5, 2, "Xuất", "ffmpeg", ten_file="spa-reels")
    t.e("id", "text", "wp", "text").e("sp", "image", "wp", "image").e("wp", "text", "v1", "prompt").e("k1", "image", "v1", "khung_dau")
    t.e("sp", "image", "v2", "tham_chieu").e("wp", "text", "v2", "prompt").e("kg", "image", "v3", "tham_chieu").e("wp", "text", "v3", "prompt")
    t.e("v1", "video", "dp", "video").e("v2", "video", "dp", "video").e("v3", "video", "dp", "video").e("vo", "audio", "dp", "audio").e("nh", "audio", "dp", "nhac")
    t.e("dp", "video", "dy", "any").e("dy", "any", "xu", "video")
    m.append(t)

    # 4. Coffee shop
    t = Mau("ca-phe-khong-gian-do-uong", "Coffee shop — Đồ uống & không gian 15s",
            "Ảnh ly signature → packshot Nano Banana → 3 shot: rót/latte art (vật lý chất lỏng tốt: Veo), không gian nắng sáng, hero shot; tiếng rót ASMR + lo-fi.",
            "Cà phê", "ca-phe", ky_nang=["cinematic-techniques"], ti_le="9:16", thoi_luong=15)
    t.n("ly", "anh", 0, 0, "Ảnh ly signature thật")
    t.n("kg", "anh", 0, 1, "Ảnh không gian quán")
    t.n("pk", "tao-anh", 1, 0, "Packshot", "google-image", "gemini-3.1-flash-image", prompt="Hero packshot of this exact drink on a wooden table, morning side light, steam, shallow depth of field", ti_le="9:16")
    t.n("v1", "tao-video", 2, 0, "Rót sữa / latte art", "google-veo", "veo-3.1-generate-preview", prompt="Top-down macro slow motion, milk pouring into espresso forming latte art, realistic fluid physics", thoi_luong=6, ti_le="9:16")
    t.n("v2", "tao-video", 2, 1, "Không gian quán", "higgsfield-mcp", "kling3_0", che_do="tham-chieu", prompt="Slow dolly through the cafe, sunlight through windows, plants, customers chatting softly", thoi_luong=5, ti_le="9:16")
    t.n("v3", "tao-video", 2, 2, "Hero shot ly", "google-veo", "veo-3.1-fast-generate-preview", che_do="khung-dau", prompt="Slow push in on the drink, condensation drops, warm light, cozy mood", thoi_luong=4, ti_le="9:16")
    t.n("sf", "hieu-ung-am", 2, 3, "Tiếng rót, cốc chạm", "elevenlabs", mo_ta="Coffee pouring, cup clink, espresso machine hiss, cafe ambience", thoi_luong=6)
    t.n("nh", "nhac", 2, 4, "Lo-fi", "elevenlabs", mo_ta="Warm lo-fi acoustic cafe music", thoi_luong=15)
    t.n("dp", "dung-phim", 3, 1.5, "Dựng", "ffmpeg", chuyen_canh="cat", do_phan_giai="1080x1920", bat_dau_am_thanh="0")
    t.n("hk", "hau-ky", 4, 1.5, "Chữ tên quán, giờ mở cửa", "higgsfield-mcp", viec="chu-tieu-de", gia_tri="Tên quán · địa chỉ · giờ mở cửa")
    t.n("xu", "xuat", 5, 1.5, "Xuất", "ffmpeg", ten_file="cafe-reels")
    t.e("ly", "image", "pk", "tham_chieu").e("ly", "image", "v1", "tham_chieu").e("kg", "image", "v2", "tham_chieu").e("pk", "image", "v3", "khung_dau")
    t.e("v1", "video", "dp", "video").e("v2", "video", "dp", "video").e("v3", "video", "dp", "video").e("sf", "audio", "dp", "audio").e("nh", "audio", "dp", "nhac")
    t.e("dp", "video", "hk", "video").e("hk", "video", "xu", "video")
    m.append(t)

    # 5. Bán hàng online
    t = Mau("ban-hang-online-tvc-san-pham", "Bán hàng online — TVC sản phẩm 30s",
            "Ảnh sản phẩm + người mẫu → AI viết prompt Seedance nhiều shot → một clip 15s qua Higgsfield + cận sản phẩm; giọng đọc bán hàng, nhạc trending, chữ lợi ích & giá ở hậu kỳ.",
            "Bán hàng online", "ban-hang-online", ky_nang=["tvc-thoi-trang", "cinematic-techniques"], ti_le="9:16", thoi_luong=30)
    t.n("sp", "nhan-vat", 0, 0, "Sản phẩm", mo_ta="(ảnh sản phẩm nền trơn + mô tả: chất liệu, màu, kích thước)")
    t.n("nm", "nhan-vat", 0, 1, "Người mẫu", mo_ta="(ảnh người mẫu + mô tả)")
    t.n("br", "prompt", 0, 2, "Brief bán hàng", noi_dung="Sản phẩm…, 3 lợi ích…, ưu đãi…, đối tượng…")
    t.n("wp", "viet-prompt", 1, 1, "Viết prompt đa shot", "claude", cho_cong_cu="Seedance 2.5")
    t.n("v1", "tao-video", 2, 0.5, "Clip chính 15s", "higgsfield-mcp", "seedance_2_5", che_do="tham-chieu", thoi_luong=15, ti_le="9:16")
    t.n("v2", "tao-video", 2, 1.7, "Cận sản phẩm 360°", "higgsfield", "bytedance/seedance-2.5", che_do="tham-chieu", prompt="Slow 360 orbit around the product on a clean pastel background, crisp details", thoi_luong=5, ti_le="9:16")
    t.n("kd", "kiem-dinh", 3, 0, "Soi sản phẩm", "claude", tieu_chi="Sản phẩm giống ảnh thật (màu, logo, hình dạng), không nhân bản sản phẩm")
    t.n("vo", "giong-doc", 2, 3, "Giọng bán hàng", "elevenlabs", "eleven_flash_v2_5", loi="Bạn đã thử…? …")
    t.n("nh", "nhac", 2, 4, "Nhạc trending", "tu-lam")
    t.n("dp", "dung-phim", 3, 2, "Dựng", "ffmpeg", chuyen_canh="cat", do_phan_giai="1080x1920", am_luong_goc=0.3, am_luong_nhac=0.4)
    t.n("hk", "hau-ky", 4, 2, "Chữ lợi ích + giá", "higgsfield-mcp", viec="chu-tieu-de", gia_tri="3 lợi ích · giá · ưu đãi")
    t.n("dy", "duyet", 5, 2, "Duyệt")
    t.n("xu", "xuat", 6, 2, "Xuất", "ffmpeg", ten_file="tvc-san-pham")
    t.e("sp", "image", "wp", "image").e("nm", "image", "wp", "image").e("sp", "text", "wp", "text").e("nm", "text", "wp", "text").e("br", "text", "wp", "text")
    t.e("wp", "text", "v1", "prompt").e("sp", "image", "v1", "tham_chieu").e("nm", "image", "v1", "tham_chieu").e("sp", "image", "v2", "tham_chieu")
    t.e("v1", "video", "kd", "any").e("v1", "video", "dp", "video").e("v2", "video", "dp", "video").e("vo", "audio", "dp", "audio").e("nh", "audio", "dp", "nhac")
    t.e("dp", "video", "hk", "video").e("hk", "video", "dy", "any").e("dy", "any", "xu", "video")
    m.append(t)

    # 6. Nail / Salon trước – sau
    t = Mau("nail-salon-truoc-sau", "Nail / Salon — Trước & sau 15s",
            "Ảnh 'trước' thật → ChatGPT sửa thành 'sau' theo mẫu → Veo tạo chuyển động biến đổi từ trước sang sau → cận chi tiết lấp lánh → chữ giá & đặt lịch.",
            "Nail / Salon", "nail-salon", ky_nang=["cinematic-techniques"], ti_le="9:16", thoi_luong=15)
    t.n("tr", "anh", 0, 0, "Ảnh TRƯỚC (thật)")
    t.n("mau", "anh", 0, 1, "Ảnh mẫu thiết kế")
    t.n("sa", "tao-anh", 1, 0.5, "Ảnh SAU (ChatGPT sửa ảnh)", "openai", "gpt-image-2.5-sunburst",
        prompt="Apply the nail design from the second image onto the hands in the first image. Keep the same hands, skin tone, lighting and framing.", ti_le="9:16")
    t.n("v1", "tao-video", 2, 0.5, "Biến đổi trước → sau", "google-veo", "veo-3.1-generate-preview", che_do="dau-cuoi",
        prompt="Magical sparkle transition sweeping across the hands, revealing the finished design, slow motion, beauty lighting", thoi_luong=8, ti_le="9:16")
    t.n("v2", "tao-video", 2, 1.7, "Cận chi tiết", "google-omni", "gemini-omni-1.1-flash", che_do="khung-dau",
        prompt="Macro slider shot across the nails, glitter catching the light, hand slowly rotating", thoi_luong=5, ti_le="9:16")
    t.n("nh", "nhac", 2, 3, "Nhạc trending", "tu-lam")
    t.n("sf", "hieu-ung-am", 2, 4, "SFX lấp lánh", "elevenlabs", mo_ta="Magical sparkle shimmer, soft ting", thoi_luong=2)
    t.n("dp", "dung-phim", 3, 1.5, "Dựng", "ffmpeg", chuyen_canh="cat", do_phan_giai="1080x1920", bat_dau_am_thanh="3")
    t.n("hk", "hau-ky", 4, 1.5, "Chữ giá & đặt lịch", "higgsfield-mcp", viec="chu-tieu-de", gia_tri="Tên mẫu · giá · đặt lịch")
    t.n("kd", "kiem-dinh", 4, 3, "Soi bàn tay", "claude", tieu_chi="Đủ 5 ngón, móng không méo, da tự nhiên")
    t.n("xu", "xuat", 5, 1.5, "Xuất", "ffmpeg", ten_file="nail-truoc-sau")
    t.e("tr", "image", "sa", "tham_chieu").e("mau", "image", "sa", "tham_chieu").e("tr", "image", "v1", "khung_dau").e("sa", "image", "v1", "khung_cuoi")
    t.e("sa", "image", "v2", "khung_dau").e("v1", "video", "dp", "video").e("v2", "video", "dp", "video").e("sf", "audio", "dp", "audio").e("nh", "audio", "dp", "nhac")
    t.e("dp", "video", "hk", "video").e("dp", "video", "kd", "any").e("hk", "video", "xu", "video")
    m.append(t)

    # 7. Phim ngắn với đội AI
    t = Mau("phim-ngan-doi-ai", "Phim ngắn — Đội AI (Đạo diễn → Biên kịch → Quay phim)",
            "Ý tưởng qua Đạo Diễn, Biên Kịch, Quay Phim, Kiểm Định (Claude) → Viết prompt từng cảnh → video → giọng dẫn → dựng. Nhân bản cụm 'cảnh' để thêm cảnh.",
            "Chung", "phim-ngan-tu-su", ky_nang=["cinematic-techniques"], ti_le="16:9", thoi_luong=90)
    t.n("yt", "prompt", 0, 0, "Ý tưởng", noi_dung="Câu chuyện về…")
    t.n("dd", "dao-dien", 1, 0, "Đạo Diễn", "claude")
    t.n("bk", "bien-kich", 2, 0, "Biên Kịch", "claude", thoi_luong=90)
    t.n("qp", "quay-phim", 3, 0, "Quay Phim", "claude")
    t.n("kd", "kiem-dinh", 4, 0, "Kiểm Định kịch bản", "claude")
    t.n("nv", "nhan-vat", 2, 1.2, "Nhân vật chính", mo_ta="(ảnh + mô tả)")
    t.n("w1", "viet-prompt", 4, 1.2, "Prompt cảnh 1", "claude", cho_cong_cu="Veo 3.1", yeu_cau="Chỉ cảnh 1 trong shot list")
    t.n("w2", "viet-prompt", 4, 2.4, "Prompt cảnh 2", "claude", cho_cong_cu="Veo 3.1", yeu_cau="Chỉ cảnh 2 trong shot list")
    t.n("v1", "tao-video", 5, 1.2, "Cảnh 1", "google-veo", "veo-3.1-generate-preview", che_do="tham-chieu", thoi_luong=8, ti_le="16:9")
    t.n("v2", "tao-video", 5, 2.4, "Cảnh 2", "google-veo", "veo-3.1-generate-preview", che_do="tham-chieu", thoi_luong=8, ti_le="16:9")
    t.n("vo", "giong-doc", 5, 3.6, "Giọng dẫn", "elevenlabs", "eleven_v3")
    t.n("dp", "dung-phim", 6, 2, "Dựng", "ffmpeg", chuyen_canh="mo", do_phan_giai="1920x1080")
    t.n("dy", "duyet", 7, 2, "Duyệt")
    t.n("xu", "xuat", 8, 2, "Xuất", "ffmpeg", ten_file="phim-ngan")
    t.e("yt", "text", "dd", "text").e("dd", "text", "bk", "text").e("yt", "text", "bk", "text").e("bk", "text", "qp", "text").e("qp", "text", "kd", "any").e("bk", "text", "kd", "any")
    t.e("qp", "text", "w1", "text").e("qp", "text", "w2", "text").e("nv", "text", "w1", "text").e("nv", "text", "w2", "text")
    t.e("w1", "text", "v1", "prompt").e("w2", "text", "v2", "prompt").e("nv", "image", "v1", "tham_chieu").e("nv", "image", "v2", "tham_chieu")
    t.e("bk", "text", "vo", "text").e("v1", "video", "dp", "video").e("v2", "video", "dp", "video").e("vo", "audio", "dp", "audio")
    t.e("dp", "video", "dy", "any").e("dy", "any", "xu", "video")
    m.append(t)

    return m


if __name__ == "__main__":
    force = "--ghi-de" in sys.argv
    for t in mau_khoi_dau():
        print(("Đã tạo  " if t.save(force) else "Bỏ qua  ") + t.data["ten"])
