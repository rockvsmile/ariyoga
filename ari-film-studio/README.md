# 🎬 Ari Film Studio

Xưởng phim AI chạy trên máy của bạn. Mỗi bộ phim đi qua **9 khung**, mỗi khung có **AI chuyên biệt** phụ trách. Bạn xem, sửa, khoá, duyệt mọi thứ trên **bảng điều khiển dạng lưới**; các AI làm việc trong **Claude Code** (dùng gói Claude Max bạn đang có).

```
Ý tưởng → Phong cách → Tham chiếu → Ép cảnh → Kịch bản → Storyboard & Máy quay → Sản xuất video → Dựng phim → Kiểm định
```

## Đội ngũ AI

| Agent | Vai trò |
|---|---|
| **Nhà Sản Xuất** (Claude chính) | Điều phối, giao việc, dừng chờ bạn duyệt |
| **Đạo Diễn** `dao-dien` | Tầm nhìn tổng thể, duyệt kịch bản, ghi nhận ép cảnh |
| **Biên Kịch** `bien-kich` | 3 phương án ý tưởng, kịch bản phân cảnh, lời thoại |
| **Chỉ Đạo Hình Ảnh** `chi-dao-hinh-anh` | Phong cách, bảng màu, hồ sơ nhân vật/sản phẩm từ ảnh |
| **Quay Phim** `quay-phim` | Chia shot, cỡ cảnh, góc máy, chuyển động, ống kính, máy quay, ánh sáng |
| **Họa Sĩ Storyboard** `hoa-si-storyboard` | Vẽ ảnh storyboard từng shot (qua Higgsfield) |
| **Kỹ Thuật Viên AI** `ky-thuat-vien-ai` | Chọn công cụ (Seedance 2.5, Gemini Omni Flash, Veo 3.1, Higgsfield…), viết prompt, tạo video |
| **Biên Tập Viên** `bien-tap-vien` | Dựng timeline, nhịp, chuyển cảnh, nhạc, xuất phim |
| **Kiểm Định** `kiem-dinh` | Soi lỗi, chấm điểm, báo cáo |
| **Thủ Thư** `thu-thu` | Học phong cách mới, cập nhật công cụ, ghi bài học, nâng cấp agent |

## Cài đặt (làm một lần)

1. **Python 3.10 trở lên** (máy bạn đã có 3.14).
2. **Claude Code** — dùng Claude desktop app (mục Code) hoặc bản dòng lệnh, đăng nhập tài khoản Claude Max.
3. **ffmpeg** để ghép phim — cách dễ nhất:
   ```
   pip install imageio-ffmpeg
   ```
4. Tải thư mục `ari-film-studio` về máy (clone repo `rockvsmile/ariyoga` bằng GitHub Desktop).
5. **Kết nối Higgsfield cho Claude Code** (để AI tự tạo ảnh/video): nếu Claude Code đăng nhập cùng tài khoản claude.ai đã kết nối Higgsfield, connector thường có sẵn — gõ `/mcp` trong Claude Code để kiểm tra. Nếu chưa có, thêm theo hướng dẫn MCP của Higgsfield. Không có Higgsfield studio vẫn chạy: AI viết prompt để bạn dán vào Dreamina / Gemini / Flow.

## Mỗi lần làm phim

1. **Mở bảng điều khiển:** bấm đúp `mo-studio.bat` (Windows) hoặc chạy `python studio.py` → trình duyệt mở http://127.0.0.1:8765
2. **Mở Claude Code** trong thư mục `ari-film-studio`.
3. Gõ `/phim-moi Tên phim` và kể ý tưởng, hoặc bấm **+ Dự án mới** trên bảng điều khiển.
4. Vòng lặp mỗi khung:
   - Gõ lệnh hiện ở thanh dưới bảng điều khiển (vd `/tiep-tuc ten-du-an`) vào Claude Code.
   - AI làm xong → bảng điều khiển **tự cập nhật** sau vài giây.
   - Bạn xem, sửa trực tiếp trong lưới, **khoá** dòng muốn giữ, ghi **lời nhắn cho AI**, rồi bấm **Duyệt khung** hoặc **Yêu cầu sửa**.
5. Khung 7: `/tao-video` — AI báo chi phí, chờ bạn đồng ý rồi mới tạo.
6. Khung 8: `/dung-phim` — ghép thành phim trong `du-an/<ten>/xuat/`.
7. Bất cứ lúc nào: `/kiem-tra` để soi lỗi.

## Kiểm soát
- **Chế độ Từng bước** (mặc định): AI dừng ở mỗi khung chờ duyệt. **Tự động**: AI chạy liền tới trước khi tạo video.
- **Khoá khung / khoá dòng:** AI không được sửa những gì bạn đã khoá.
- **Ép cảnh (khung 4)** và ô **Ép cảnh** từng shot: yêu cầu bắt buộc, AI phải làm theo hoặc giải thích vì sao không được.
- **Tiền thật luôn hỏi trước:** tạo ảnh/video trả phí luôn chờ bạn đồng ý.

## Tự học & nâng cấp — `/hoc-hoi`
- Gửi một video mẫu: *"/hoc-hoi thêm phong cách từ video này"* → phong cách mới trong `thu-vien/phong-cach/`, xuất hiện ngay trong menu Khung 2.
- *"/hoc-hoi thêm công cụ Kling 3"* → hồ sơ công cụ mới cho Kỹ Thuật Viên.
- *"/hoc-hoi ghi bài học từ dự án X"* → quy tắc mới vào `thu-vien/bai-hoc.md` (hỏi bạn trước).
- Thủ Thư có thể đề xuất sửa hướng dẫn của chính các agent — chỉ sửa khi bạn đồng ý.

## Cấu trúc thư mục
```
ari-film-studio/
├── CLAUDE.md                 luật điều phối cho Nhà Sản Xuất
├── .claude/agents/           9 agent chuyên biệt
├── .claude/skills/           lệnh tắt /phim-moi /tiep-tuc /tao-video /dung-phim /kiem-tra /hoc-hoi
├── studio.py                 máy chủ bảng điều khiển (chỉ dùng thư viện chuẩn Python)
├── giao-dien/                bảng điều khiển (HTML/JS/CSS)
├── thu-vien/                 phong cách · thể loại · công cụ · lựa chọn menu · sổ bài học
├── tools/                    tạo dự án · kiểm tra dự án · ghép phim
└── du-an/<ten>/              project.json + tham-chieu/ storyboard/ video/ xuat/
```

## Giới hạn của bản đầu
- Tạo video **tự động** chỉ qua Higgsfield MCP; Seedance (Dreamina), Gemini Omni Flash, Veo làm qua prompt dán tay. Kết nối API trực tiếp sẽ thêm ở bản sau.
- Ghép phim cơ bản (cắt, hoà tan, qua đen, nhạc nền). Chữ, logo, chỉnh màu, mix âm thanh làm tiếp trong CapCut/Premiere.
- Các agent chưa được chạy thử trong một dự án thật — lần đầu dùng hãy làm từng bước và góp ý để Thủ Thư tinh chỉnh.
