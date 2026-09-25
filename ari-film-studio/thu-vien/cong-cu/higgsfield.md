# Higgsfield (qua MCP)

- **Truy cập:** MCP "higgsfield" trong Claude (đã kết nối trên tài khoản claude.ai của bạn). Trả bằng credit Higgsfield.
- **Là gì:** một cổng gom nhiều model tạo ảnh/video/âm thanh. Đây là đường **tự động** duy nhất của studio v1 — Claude gọi trực tiếp, không phải dán tay.
- **Công cụ MCP hay dùng:**
  - `models_explore` (action `recommend`) — hỏi model nào hợp với yêu cầu trước khi tạo.
  - `generate_image` — vẽ storyboard, ảnh nhân vật chuẩn (character sheet khi người dùng yêu cầu).
  - `generate_video` / `generate_video_batch` — tạo clip; nhiều clip độc lập thì dùng batch rồi `jobs_wait`.
  - `media_upload` / `media_import_url` — đưa ảnh tham chiếu lên để lấy `media_id`.
  - `balance` — xem credit còn lại trước khi chạy loạt lớn.
- **Chọn khi:** muốn Claude tự tạo video/ảnh không cần thao tác tay; cần storyboard ảnh nhanh.
- **Lưu ý:** tên model và giới hạn độ dài phụ thuộc model được chọn bên trong Higgsfield — luôn gọi `models_explore` để xác nhận, không đoán. Báo người dùng số credit dự kiến trước khi tạo hàng loạt.
