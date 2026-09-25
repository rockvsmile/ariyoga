---
name: tao-video
description: Sản xuất video cho dự án Ari Film Studio (khung 7) — chọn công cụ, gom clip, viết prompt, báo chi phí, tạo video qua Higgsfield hoặc hướng dẫn dán vào Seedance/Dreamina, Gemini Omni Flash, Veo. Dùng khi người dùng gõ /tao-video hoặc muốn tạo/tạo lại video cho các shot.
---

Tham số: `<id> [shot hoặc clip…]` — không ghi shot thì làm mọi shot chưa `xong` và chưa khoá.

1. Kiểm tra khung 6 đã `da_duyet` (chế độ từng bước). Chưa → nhắc duyệt storyboard trước.
2. Gọi `kiem-dinh` nhanh cho khung 6–7 nếu chưa có báo cáo gần đây; lỗi mức `cao` → báo người dùng trước.
3. Tuyến/model theo **Bảng kết nối** (`tao_sinh`, `chinh_sua`) và ô riêng của từng shot — thiếu thì hỏi người dùng, không tự chọn. Gọi `ky-thuat-vien-ai` phần **chọn model + gom clip + viết prompt + tính credit** (chưa tạo). Mặc định lượt `nhap` (rẻ, duyệt nhịp) trước; lượt `ban_dep` chỉ cho shot đã duyệt.
4. Tuyến thủ công (Google Flow, Dreamina): Kỹ Thuật Viên soạn gói việc trong `goi-viec/`; chỉ cho người dùng mở file nào, làm gì, lưu video tên gì, rồi bấm "Quét file mới" (Khung 7). Tuyến tự động: trình người dùng bảng: clip · shot · công cụ · giây · chi phí ước tính · cách tạo (tự động qua Higgsfield / dán tay). **Chờ đồng ý.** Cho phép họ đổi công cụ từng clip.
5. Đồng ý → gọi lại `ky-thuat-vien-ai` phần **tạo video** cho các clip được duyệt.
6. Xong → gọi `kiem-dinh` soi video vừa tạo. Tóm tắt: clip nào đạt, clip nào cần sửa (và cách sửa rẻ nhất: replace_object / motion_control / edit / extension) hay phải tạo lại. Người dùng đồng ý → `ky-thuat-vien-ai` sửa.
