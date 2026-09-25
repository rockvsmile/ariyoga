---
name: dung-phim
description: Dựng và xuất phim hoàn chỉnh cho dự án Ari Film Studio (khung 8) — Biên Tập Viên sắp timeline, chuyển cảnh, nhạc rồi ghép bằng ffmpeg. Dùng khi người dùng gõ /dung-phim, muốn ghép các clip, đổi thứ tự/nhịp, hoặc xuất bản cuối.
---

Tham số: `<id>`.

1. Kiểm tra các shot đã có `video`. Thiếu → liệt kê shot thiếu, hỏi người dùng muốn dựng tạm (bỏ qua chỗ trống) hay chờ.
2. Nếu timeline (`8_dung_phim.danh_sach`) đang trống hoặc khung ở `can_sua` → gọi `bien-tap-vien` lập timeline. Nếu người dùng đã tự sắp trên bảng điều khiển → giữ nguyên, chỉ xuất.
3. Chạy `python tools/ghep_phim.py <id>` (Biên Tập Viên có thể tự chạy). Lỗi ffmpeg → `pip install imageio-ffmpeg` rồi thử lại.
4. Gọi `kiem-dinh` xem bản xuất (trích khung hình). Báo người dùng: đường dẫn file, tổng thời lượng, nhận xét nhịp, việc còn lại ở hậu kỳ (chữ, logo, chỉnh màu, mix nhạc).
