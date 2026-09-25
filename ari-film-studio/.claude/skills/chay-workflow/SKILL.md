---
name: chay-workflow
description: Thực hiện các node trên canvas Workflow của Ari Film Studio đang ở trạng thái "Chờ Claude Code" — node AI vai trò (Đạo Diễn, Biên Kịch, Quay Phim, Viết prompt, Kiểm Định) và node dùng Higgsfield qua MCP (tạo ảnh/video, sửa video, khớp môi, hậu kỳ, 3D) — rồi cho workflow chạy tiếp. Dùng khi người dùng gõ /chay-workflow, nói "chạy workflow", "làm các node đang chờ", hoặc canvas báo node chờ Claude.
---

Tham số: `<id-dự-án>` (không có → nếu chỉ một dự án có workflow thì dùng nó, không thì hỏi).

## 1. Xem việc
`python tools/workflow.py cho-claude <id>` → danh sách node chờ, kèm `dau_vao` (chữ + đường dẫn file đã giải từ các node phía trước), `params`, `model`, và cổng cần ghi kết quả. Đọc thêm `du-an/<id>/workflow.json` → mục `meta` (ngành, thể loại, phong cách, kỹ năng) để làm đúng phong cách của mẫu.

Làm theo thứ tự trái → phải (node phía trước xong mới tới node sau). **Không tự đổi nhà cung cấp/model người dùng đã chọn.**

## 2. Làm từng node
**Node AI vai trò** (loại `dao-dien`, `bien-kich`, `quay-phim`, `viet-prompt`, `kiem-dinh`): giao cho agent cùng tên (`viet-prompt` → `ky-thuat-vien-ai`) với:
- đầu vào chữ / ảnh của node, `params` (yêu cầu thêm, thời lượng, công cụ đích, tiêu chí…), `ghi_chu` của node;
- `meta` của workflow: đọc `thu-vien/the-loai/<the_loai>.md`, `thu-vien/phong-cach/<phong_cach>.md`, các skill trong `ky_nang` (vd `cinematic-techniques`, `tvc-thoi-trang` — dùng nếu có trong phiên), `thu-vien/bai-hoc.md`.
- Yêu cầu agent **trả về văn bản kết quả** (không sửa project.json). Kết quả `viet-prompt` là prompt tiếng Anh dán thẳng được vào công cụ đích (theo `thu-vien/cong-cu/`). Kết quả `kiem-dinh` là báo cáo có điểm/10, lỗi mức cao/vừa/thấp và cách sửa.
Ghi: lưu văn bản ra file tạm rồi `python tools/workflow.py ghi <id> <node> text text @<file>`.

**Node Higgsfield qua MCP** (`provider = higgsfield-mcp`): đọc `thu-vien/cong-cu/higgsfield.md`.
- **Báo chi phí trước** (`get_cost: true`) cho tất cả node sắp chạy, chờ người dùng đồng ý; không tự dùng `use_unlim`.
- File đầu vào: `media_upload` → PUT → `media_confirm` (hoặc dùng `job_id` nếu file đó do Higgsfield tạo trước đó).
- `tao-anh` → `generate_image`; `tao-video` → `generate_video` (model = `node.model`; `che_do` quyết định vai trò ảnh: khung đầu `start_image`, khung cuối `end_image`, tham chiếu `image`/`image_references`; kiểm tra `models_explore get`); `sua-video` → model edit tương ứng; `khop-moi` → `sync_so`; `hau-ky` → `upscale_video` / `reframe` / workflow `subtitles` / workflow `video-editing` theo `params.viec`; `tao-3d` → `generate_3d`. Nhiều node độc lập → dùng batch + `jobs_wait`.
- Tải kết quả về `du-an/<id>/wf/<node>/` (`curl -L -o`), rồi `python tools/workflow.py ghi <id> <node> <cong> <kieu> @<file>` (vd cổng `video` kiểu `video`).

Lỗi / không làm được → `python tools/workflow.py loi <id> <node> "<lý do ngắn, cách sửa>"`.

## 3. Chạy tiếp
Sau khi ghi xong: `python tools/workflow.py chay <id>` để các node API/trên máy phía sau chạy tiếp (lệnh này tự dừng lại ở node Claude/làm tay/Duyệt tiếp theo). Nếu còn node chờ Claude mới xuất hiện → lặp lại từ bước 1 (hỏi người dùng trước nếu tốn credit). Tóm tắt cho người dùng: node nào xong, node nào lỗi, còn chờ gì (duyệt, làm tay) — canvas tự cập nhật.
