---
name: dung-phim
description: Hoàn thiện phim cho dự án Ari Film Studio (khung 8) — Kỹ Sư Âm Thanh tạo giọng dẫn/thoại, Biên Tập Viên sắp timeline và dựng bản sạch, Hậu Kỳ AI thêm chữ, phụ đề, upscale, xuất nhiều tỉ lệ bằng Higgsfield. Dùng khi người dùng gõ /dung-phim, muốn ghép các clip, đổi thứ tự/nhịp, hoặc xuất bản cuối.
---

Tham số: `<id>`.

1. Kiểm tra các shot đã có `video`. Thiếu → liệt kê shot thiếu, hỏi người dùng muốn dựng tạm (bỏ qua chỗ trống) hay chờ.
2. Theo **Bảng kết nối** (`long_tieng`, `nhac`, `dung_phim`, `hau_ky`) — mảnh chưa chọn thì hỏi. Phim có lời dẫn/thoại mà track chưa có file → gọi `ky-su-am-thanh` (ElevenLabs / Higgsfield: báo chi phí, chờ đồng ý; app giọng trên máy: xuất file lời, chờ người dùng thả file và bấm Quét).
3. Nếu timeline (`8_dung_phim.danh_sach`) đang trống hoặc khung ở `can_sua` → gọi `bien-tap-vien` lập timeline. Nếu người dùng đã tự sắp trên bảng điều khiển → giữ nguyên, chỉ xuất.
4. Chạy `python tools/ghep_phim.py <id>` (Biên Tập Viên có thể tự chạy). Lỗi ffmpeg → `pip install imageio-ffmpeg` rồi thử lại.
5. Gọi `kiem-dinh` xem bản xuất (trích khung hình). Báo người dùng: đường dẫn file, tổng thời lượng, nhận xét nhịp, việc còn lại.
6. Bản sạch được duyệt → theo `bang_ket_noi.hau_ky`: `higgsfield` → hỏi các bước (chữ/tiêu đề, phụ đề, upscale, tỉ lệ khác, thumbnail) rồi gọi `hau-ky-ai`; `davinci-resolve` → đưa người dùng bản sạch + danh sách việc cần làm; `tat` → xong.
