---
name: hoc-hoi
description: Cho Ari Film Studio học và tự nâng cấp — thêm phong cách mới từ video mẫu, thêm công cụ/thể loại mới, ghi bài học từ dự án, cập nhật hướng dẫn agent. Dùng khi người dùng gõ /hoc-hoi, gửi phim mẫu để "học phong cách", nói "thêm công cụ X", "ghi nhớ điều này", "nâng cấp studio".
---

1. Xác định loại việc: phong cách mới (có video/ảnh mẫu) · công cụ mới · thể loại mới · bài học từ dự án · sửa hướng dẫn agent · thêm lựa chọn menu.
2. Gọi `thu-thu` kèm đầy đủ đầu vào (đường dẫn video mẫu, tên công cụ, id dự án, lời người dùng).
3. Với bài học và sửa agent: trình đề xuất, **chờ người dùng đồng ý** rồi mới ghi.
4. Báo lại danh sách file đã thêm/sửa. Nhắc: khởi động lại Claude Code nếu vừa sửa file trong `.claude/agents/` để agent nhận hướng dẫn mới; tải lại bảng điều khiển để thấy phong cách/công cụ mới.
