---
name: kiem-tra
description: Kiểm định chất lượng dự án Ari Film Studio — soát cấu trúc, ép cảnh, nhất quán nhân vật/sản phẩm, prompt và video, chấm điểm và ghi báo cáo vào khung 9. Dùng khi người dùng gõ /kiem-tra, hỏi "phim có lỗi gì không", hoặc trước khi tạo video/xuất phim.
---

Tham số: `<id> [khung]` — không ghi khung thì kiểm tra toàn bộ những khung đã có nội dung.

1. Chạy `python tools/kiem_tra_du_an.py <id>` và cho người dùng xem kết quả.
2. Gọi `kiem-dinh` với phạm vi tương ứng.
3. Tóm tắt: điểm, lỗi mức cao (phải sửa), mức vừa, 3 việc nên làm ngay; hỏi người dùng có muốn giao agent phụ trách sửa luôn không.
