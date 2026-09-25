# 🎬 Ari Film Studio

Xưởng phim AI tạo sinh chạy trên máy của bạn. Một bộ phim vài phút được lắp từ nhiều **mảnh ghép** — đạo diễn, kịch bản, nhân vật, quay phim, storyboard, tạo sinh, chỉnh sửa, lồng tiếng, nhạc, dựng, hậu kỳ, kiểm định. Trên **Bảng kết nối**, **bạn chọn** công cụ cho từng mảnh (Higgsfield, Google Flow Veo/Omni, ElevenLabs, các app giọng trên máy, DaVinci Resolve…); các **AI chuyên biệt** trong **Claude Code** làm đúng theo lựa chọn đó, qua **9 khung** có cổng duyệt.

```
Ý tưởng → Phong cách → Tham chiếu → Ép cảnh → Kịch bản → Storyboard & Máy quay → Sản xuất video → Dựng phim → Kiểm định
```

## Canvas Workflow (cách làm chính)
Mở `mo-studio.bat` (hoặc `python studio.py`) → trình duyệt mở canvas.

- **📋 Mẫu workflow:** thư viện template dạng lưới, lọc theo ngành (Yoga, Spa, Cà phê, Bán hàng online, Nail/Salon, Phim ngắn, Kỹ thuật nối cảnh), rê chuột để xem **video minh hoạ**. Bấm vào mẫu → trang chi tiết: video lớn, các bước, công cụ, và **form Điền thông tin** (ảnh, prompt…) → **🎬 Tạo video từ mẫu này** tạo dự án đã điền sẵn. **✎ Sửa mẫu** để chỉnh node, tải video minh hoạ / ảnh bìa (hoặc lấy phim đã xuất của một dự án); **💾 Lưu làm mẫu** biến workflow đang làm thành mẫu mới.
- **💡 Kho prompt:** prompt mẫu theo ngành (Yoga, Spa, Cà phê, Bán hàng online, Nail/Salon, Thời trang, Dùng chung) cho video, ảnh, nhạc, giọng, hiệu ứng. Ô `{{…}}` điền nhanh, rồi **Chèn vào node** đang chọn, **Tạo node mới**, hoặc **Chép**. Ở node bấm **⭐ Lưu vào kho** để giữ prompt hay của bạn (mục «Của tôi»). Thêm prompt: sửa `thu-vien/kho-prompt/*.json`.
- **🎥 Máy quay** (trong bảng chi tiết node tạo ảnh/video): bấm chọn cỡ cảnh, góc máy, chuyển động, ống kính, độ sâu, ánh sáng, màu phim, tốc độ → app ghép thành câu tiếng Anh thêm vào prompt. Danh sách ở `thu-vien/may-quay.json`.
- **🕘 Các bản trước:** mỗi lần chạy lại một node, bản cũ được giữ (tối đa 12) — bấm **↩ Dùng** để lấy lại bản cũ mà không phải trả tiền tạo lại.
- **💬 Hỏi từng câu** (trang chi tiết mẫu): trợ lý hỏi từng thông tin một kiểu trò chuyện thay cho form — hợp với khách không rành công nghệ.
- **Node:** kéo từ bảng bên trái. **Thả dây ra chỗ trống** hoặc **chuột phải** trên canvas → menu gợi ý node hợp kiểu, tự nối dây. **Ctrl+C / Ctrl+V** chép–dán node (dán được sang dự án khác). Nối dây từ chấm bên phải (đầu ra) sang chấm bên trái (đầu vào) — chỉ nối được đúng kiểu (chữ, ảnh, video, âm thanh, 3D). Nhấc đầu dây ra khỏi đầu vào để cắt; bấm dây + Delete (hoặc ✂) để xoá; Ctrl+Z hoàn tác; Ctrl+D nhân bản.
- **Mỗi node bạn chọn nhà cung cấp + model:**
  - ⚡ **API** (app chạy ngay bằng API key của bạn): OpenAI (ChatGPT ảnh), Google Nano Banana / Veo 3.1 / Gemini Omni Flash, ElevenLabs (giọng, nhạc, hiệu ứng), Tripo3D, Higgsfield API.
  - 💻 **Trên máy**: trích khung hình (nối cảnh), cắt video, dựng phim, xuất.
  - 🤖 **Claude Code**: node AI vai trò (Đạo Diễn, Biên Kịch, Quay Phim, Viết prompt, Kiểm Định) và Higgsfield qua MCP → gõ `/chay-workflow <dự án>` trong Claude Code.
  - ✋ **Làm tay**: Google Flow, ChatGPT app, Dreamina, app giọng trên máy → node tự soạn gói việc, bạn làm xong thì thả file vào node.
- **▶ trên node**: chạy node đó và những gì nó cần. **▶ Chạy tất cả**: chạy mọi node đủ đầu vào. Trước khi gọi API trả phí, app luôn hỏi lại.
- **Duyệt**: node Duyệt dừng quy trình để bạn xem, bấm ✓ để đi tiếp.
- **⚙ Cài đặt**: nhập API key (lưu ở `cai-dat/khoa-api.json` trên máy bạn, không lên GitHub).
- Bấm vào chỗ trống → **Thông tin workflow**: ngành, thể loại, phong cách, skill — các node AI dùng để làm đúng phong cách của khách.
- **Trợ lý chính (Claude Code):** `/thiet-ke-mau` — kể nhu cầu khách, Claude dựng/sửa template; `/hoc-hoi` — học phong cách mới từ video mẫu, thêm công cụ.

### Cần chuẩn bị
| Thứ | Để làm gì |
|---|---|
| Python 3.10+ và `pip install imageio-ffmpeg` | Chạy studio, dựng phim trên máy |
| OpenAI API key (platform.openai.com) | Vẽ ảnh bằng ChatGPT (GPT Image) |
| Tripo3D API key (bản v3) | Tạo mô hình 3D |
| Google Gemini API key (aistudio.google.com) | Nano Banana, Veo 3.1, Gemini Omni Flash |
| ElevenLabs API key | Giọng tiếng Việt (`eleven_v3`, `eleven_flash_v2_5`), nhạc, hiệu ứng |
| Higgsfield Key ID + Secret (cloud.higgsfield.ai) | Higgsfield API; hoặc dùng Higgsfield qua MCP trong Claude Code không cần key |
| Claude Code (Claude desktop app → Code) | Node AI vai trò, Higgsfield MCP, trợ lý thiết kế mẫu |

## Hồ sơ phim & Bảng kết nối (bổ trợ, trang 🗂 Hồ sơ phim)
| Mảnh ghép | Lựa chọn |
|---|---|
| Đạo diễn · Kịch bản · Quay phim | Tôi tự làm / AI làm nháp để tôi duyệt |
| Nhân vật nhất quán | Higgsfield Elements · Higgsfield Soul · Google Flow Ingredients · chỉ ảnh + mô tả |
| Ảnh storyboard | Higgsfield (chọn model) · Google Flow Nano Banana · tôi tự tải · không làm |
| Tạo sinh video | **Higgsfield** (chọn model: Cinema Studio, Seedance, Kling, Veo, Omni, Wan…) · **Google Flow** (Veo 3.1 Quality/Fast, Gemini Omni Flash) · Dreamina |
| Chỉnh sửa video | Higgsfield edit/Genjutsu · Google Flow Omni/Extend · tạo lại · không |
| Lồng tiếng | **ElevenLabs** (MCP) · Higgsfield Seed Audio · **app giọng trên máy tôi** (chọn tên app) · giọng gốc trong video · tôi tự thu |
| Nhạc & hiệu ứng | ElevenLabs · file của tôi · âm thanh gốc · không |
| Dựng phim | Studio tự ghép (ffmpeg) · Higgsedit · Flow Scenebuilder · DaVinci Resolve (tôi tự dựng) |
| Hậu kỳ | Higgsfield (chữ, phụ đề, upscale, đổi tỉ lệ) · DaVinci Resolve · không |
| Kiểm định | Kiểm Định AI · + dự đoán viral · tôi tự kiểm tra |

- **⚡ Tự động:** Claude gọi thẳng qua MCP (Higgsfield, ElevenLabs).
- **✋ Thủ công:** Claude soạn **gói việc** trong `du-an/<ten>/goi-viec/` (prompt, ảnh cần tải, cài đặt). Bạn làm trên app (Google Flow, Dreamina, app giọng trên máy), lưu file đặt tên theo mã (`video/S03.mp4`, `video/K02.mp4`, `am-thanh/A01.wav`), rồi bấm **⟳ Quét file mới** — studio tự gắn vào đúng shot/track.
- Mảnh nào chưa chọn, AI **dừng lại hỏi** — không tự chọn thay bạn. Từng shot/track vẫn đổi riêng tuyến/model/app được.
- Thêm công cụ hoặc app mới: bảo `/hoc-hoi thêm app giọng X` hoặc sửa `thu-vien/bang-ket-noi.json`.

## Đội ngũ AI

| Agent | Vai trò |
|---|---|
| **Nhà Sản Xuất** (Claude chính) | Điều phối, giao việc, dừng chờ bạn duyệt |
| **Đạo Diễn** `dao-dien` | Tầm nhìn tổng thể, duyệt kịch bản, ghi nhận ép cảnh |
| **Biên Kịch** `bien-kich` | 3 phương án ý tưởng, kịch bản phân cảnh, lời thoại |
| **Chỉ Đạo Hình Ảnh** `chi-dao-hinh-anh` | Phong cách, bảng màu, hồ sơ nhân vật/sản phẩm từ ảnh |
| **Chuyên Gia Nhân Vật** `chuyen-gia-nhan-vat` | Khoá danh tính: Elements/Soul (Higgsfield) hoặc Ingredients (Flow) |
| **Quay Phim** `quay-phim` | Chia shot, cỡ cảnh, góc máy, chuyển động, ống kính, máy quay, ánh sáng |
| **Họa Sĩ Storyboard** `hoa-si-storyboard` | Vẽ ảnh storyboard từng shot (qua Higgsfield) |
| **Kỹ Thuật Viên AI** `ky-thuat-vien-ai` | Viết prompt đúng tuyến/model bạn chọn, tạo video (Higgsfield) hoặc soạn gói việc (Flow, Dreamina), sửa video lỗi |
| **Kỹ Sư Âm Thanh** `ky-su-am-thanh` | Giọng dẫn, thoại, nhạc qua ElevenLabs / Higgsfield / app giọng trên máy |
| **Biên Tập Viên** `bien-tap-vien` | Dựng timeline, nhịp, chuyển cảnh, nhạc, xuất bản sạch |
| **Hậu Kỳ AI** `hau-ky-ai` | Chữ, phụ đề, upscale, đổi tỉ lệ từng nền tảng, thumbnail |
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
5. **Kết nối các dịch vụ tự động** (chỉ cần những cái bạn dùng):
   - **Higgsfield:** nếu Claude Code đăng nhập cùng tài khoản claude.ai đã kết nối Higgsfield, connector thường có sẵn — gõ `/mcp` để kiểm tra; chưa có thì thêm theo hướng dẫn MCP của Higgsfield.
   - **ElevenLabs:** `claude mcp add --transport http elevenlabs https://api.elevenlabs.io/v1/mcp` rồi gõ `/mcp` để đăng nhập tài khoản ElevenLabs.
   - **Google Flow, Dreamina, app giọng trên máy:** không cần kết nối — dùng gói việc + Quét file.

## Mỗi lần làm phim

1. **Mở bảng điều khiển:** bấm đúp `mo-studio.bat` (Windows) hoặc chạy `python studio.py` → trình duyệt mở http://127.0.0.1:8765
2. **Mở Claude Code** trong thư mục `ari-film-studio`.
3. Gõ `/phim-moi Tên phim` và kể ý tưởng, hoặc bấm **+ Dự án mới** trên bảng điều khiển.
4. Mở **Bảng kết nối** (ô đầu tiên trên thanh quy trình) và chọn công cụ cho từng mảnh ghép.
5. Vòng lặp mỗi khung:
   - Gõ lệnh hiện ở thanh dưới bảng điều khiển (vd `/tiep-tuc ten-du-an`) vào Claude Code.
   - AI làm xong → bảng điều khiển **tự cập nhật** sau vài giây.
   - Bạn xem, sửa trực tiếp trong lưới, **khoá** dòng muốn giữ, ghi **lời nhắn cho AI**, rồi bấm **Duyệt khung** hoặc **Yêu cầu sửa**.
6. Khung 7: `/tao-video` — tuyến tự động: AI báo chi phí, chờ bạn đồng ý rồi mới tạo; tuyến thủ công: AI soạn gói việc, bạn làm rồi bấm Quét.
7. Khung 8: `/dung-phim` — lồng tiếng, dựng, hậu kỳ theo lựa chọn của bạn; phim nằm trong `du-an/<ten>/xuat/`.
8. Bất cứ lúc nào: `/kiem-tra` để soi lỗi.

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
├── .claude/agents/           12 agent chuyên biệt
├── .claude/skills/           lệnh tắt /phim-moi /tiep-tuc /tao-video /dung-phim /kiem-tra /hoc-hoi
├── studio.py                 máy chủ bảng điều khiển (chỉ dùng thư viện chuẩn Python)
├── giao-dien/                bảng điều khiển (HTML/JS/CSS)
├── thu-vien/                 bảng kết nối · phong cách · thể loại · công cụ · lựa chọn menu · sổ bài học
├── tools/                    tạo dự án · kiểm tra dự án · ghép phim
└── du-an/<ten>/              project.json + tham-chieu/ storyboard/ video/ xuat/
```

## Giới hạn của bản đầu
- Tuyến **tự động**: Higgsfield và ElevenLabs (qua MCP). Google Flow, Dreamina và app giọng trên máy là **thủ công** (gói việc + Quét file) vì chưa có kết nối trực tiếp; app nào có API trên máy thì có thể nâng cấp thành tự động.
- Studio tự ghép (ffmpeg) ở mức cơ bản: cắt, hoà tan, qua đen, nhạc nền, track giọng theo thời điểm. Chữ, phụ đề, upscale làm ở Hậu kỳ (Higgsfield) hoặc DaVinci Resolve.
- Các agent chưa được chạy thử trong một dự án thật — lần đầu dùng hãy làm từng bước và góp ý để Thủ Thư tinh chỉnh.
