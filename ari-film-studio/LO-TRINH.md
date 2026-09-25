# Lộ trình Ari Film Studio

## Đã có
- Canvas node: kéo thả, nối/cắt dây, phóng to/thu nhỏ, hoàn tác, nhân bản, khoá node, duyệt, xem trước kết quả trên node.
- Chạy node: API trực tiếp (OpenAI ảnh, Google Nano Banana / Veo 3.1 / Gemini Omni Flash, ElevenLabs giọng–nhạc–SFX, Tripo3D v3, Higgsfield API), trên máy (trích khung, cắt, dựng, xuất), qua Claude Code (AI vai trò, Higgsfield MCP), làm tay (Google Flow, ChatGPT app, Dreamina, app giọng trên máy).
- Thư viện template theo ngành (yoga, spa, cà phê, bán hàng online, nail/salon, phim ngắn, kỹ thuật nối cảnh) — dùng, sửa, lưu mẫu mới; mỗi mẫu gắn ngành, thể loại, phong cách, skill.
- Kho prompt theo ngành (ô điền nhanh, chèn vào node, lưu prompt của tôi), bộ chọn máy quay/ống kính/ánh sáng, lịch sử kết quả từng node, menu thêm node khi thả dây/chuột phải, chép–dán node, điền mẫu kiểu hỏi–đáp. Ý tưởng tham khảo từ các dự án mã nguồn mở — xem `THAM-KHAO.md`.
- Trợ lý chính trong Claude Code: `/thiet-ke-mau`, `/chay-workflow`, `/hoc-hoi`.

## Tiếp theo (đề xuất)
0. **Phiên bản cho nhiều người dùng (web app):** đưa studio lên máy chủ — tài khoản người dùng, gói credit / thanh toán, API key đặt ở server (người dùng không cần key riêng), hàng đợi chạy node, kho lưu video/ảnh (S3/R2), thư viện mẫu dùng chung có video minh hoạ, phân quyền mẫu miễn phí / trả phí. Nền tảng gợi ý: giữ bộ máy workflow Python hiện tại làm backend (FastAPI), canvas hiện tại làm frontend; mẫu và node giữ nguyên định dạng JSON nên chuyển lên dễ.
1. **Chạy thử thật với API key** của bạn cho từng nhà cung cấp, sửa theo phản hồi thực tế (mục cần kiểm chứng: định dạng thời lượng Omni, tên trường từng model Higgsfield API).
2. **Cửa sổ quản lý skill**: bật/tắt, thêm, xem skill/phong cách/thể loại/agent; gắn nhanh vào template.
2b. **Storyboard tự động từ kịch bản** (ý tưởng từ TwitCanva): một node nhận kịch bản → trả về «DNA nhân vật» + «neo phong cách» + danh sách cảnh (góc máy, chuyển động, ánh sáng), rồi tự sinh cụm node ảnh → video cho từng cảnh.
2c. **Mini-map** góc canvas và **chọn nhiều node** (kéo khung) để di chuyển/chép cả cụm.
3. **Nhóm node theo cảnh** (khung "Cảnh 1, Cảnh 2" kéo cả cụm), nhân bản cả cụm cảnh.
4. **Ước tính chi phí** trước khi chạy (Higgsfield `get_cost`, bảng giá từng API).
5. **Xuất timeline sang DaVinci Resolve** (FCPXML) cho bản hoàn thiện.
6. **Văn phòng 3D**: các nhân viên AI (Giám đốc/Nhà Sản Xuất, Đạo Diễn, Biên Kịch, Quay Phim, Kỹ Thuật Viên, Kỹ Sư Âm Thanh, Biên Tập Viên, Kiểm Định, Thủ Thư) là nhân vật 3D tí hon đi lại trong công ty, góc nhìn thứ 3 kiểu game; bấm vào nhân viên để xem việc đang làm, đổi mô hình 3D (tạo bằng Tripo3D), đổi agent/skill; nhân viên "làm việc" khi node tương ứng đang chạy. Làm bằng Three.js chạy trong trình duyệt, nối với trạng thái workflow.
