# Google Flow — Veo 3.1 & Gemini Omni Flash

- **Là gì:** xưởng làm phim AI của Google (web, labs.google/flow), tái ra mắt dạng không gian làm việc thống nhất 02/2026. Dùng gói Google AI (Pro/Ultra) — tính bằng credit của Google.
- **Kết nối với studio:** **thủ công**. Chưa có MCP/API cho chính ứng dụng Flow → Kỹ Thuật Viên AI soạn **gói việc** (`du-an/<id>/goi-viec/flow-<clip>.md`), bạn làm trong Flow, tải video về và thả vào `du-an/<id>/video/` đặt tên theo mã shot/clip (vd `S03.mp4`, `K02.mp4`), rồi bấm **Quét file mới** trên bảng điều khiển.
- **Model trong Flow:**
  - **Veo 3.1** (Quality / Fast): clip tới 8s, âm thanh gốc đồng bộ (thoại khớp môi, tiếng môi trường, nhạc), vật lý chân thật.
  - **Gemini Omni Flash:** tạo 3–10s và **sửa video bằng lời** từng bước ("đổi áo sang màu be", "cho nắng chiều") mà giữ nguyên phần không sửa.
  - **Nano Banana:** tạo/sửa ảnh ngay trong Flow (storyboard, khung đầu).
- **Tính năng Flow:**
  - **Text to Video** — chỉ prompt.
  - **Frames to Video** — khung đầu (và khung cuối) → video; dùng ảnh storyboard đã duyệt để giữ bố cục.
  - **Ingredients to Video** — ảnh nhân vật/đồ vật/bối cảnh làm "nguyên liệu" để giữ nhất quán (thường tối đa 3 ảnh mỗi lần — kiểm tra trên giao diện).
  - **Extend** — nối dài clip từ khung cuối, giữ liền mạch.
  - **Camera Controls** — chọn chuyển động máy.
  - **Scenebuilder** — xếp các clip thành timeline, nối cảnh.
  - Âm thanh đã có trong Ingredients, Frames và Extend.
- **Chọn khi:** cần chất siêu thực của Veo, thoại khớp môi, hoặc sửa lặp nhiều lần bằng Omni; bạn đã có credit Google.

## Gói việc cho mỗi clip (Kỹ Thuật Viên AI soạn)
```
# Flow — clip K02 (shot S03, S04) · 8s · 16:9 · Veo 3.1 Quality
Chế độ: Ingredients to Video
Nguyên liệu (tải lên theo thứ tự): 1) tham-chieu/nhan-vat/lan.jpg  2) tham-chieu/trang-phuc/bo-legacy.jpg  3) tham-chieu/boi-canh/phong-tap.jpg
Camera: slow dolly in, eye level
Prompt (dán nguyên văn):
<prompt tiếng Anh>
Lưu file: video/K02.mp4
Nếu cần sửa: dùng Omni với câu lệnh "<câu sửa>"
```

## Cách viết prompt cho Veo trong Flow
- Một shot mỗi prompt: `[cỡ cảnh, góc, chuyển động máy] of [chủ thể] [hành động] in [bối cảnh], [ánh sáng], [phong cách/film look]. Audio: [thoại trong ngoặc kép, ghi ai nói], [tiếng động], [nhạc].`
- Mô tả nhân vật giống hệt nhau ở mọi prompt (copy từ khung 3) dù đã có Ingredients.
- Không yêu cầu chữ/logo trong hình.

Nguồn: blog.google (Introducing Flow; Veo 3.1 updates in Flow) · blog.google (Introducing Gemini Omni) · ai.google.dev/gemini-api/docs/omni — tra 09/2026.
