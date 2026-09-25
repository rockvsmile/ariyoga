# Gemini Omni Flash (Google)

- **Truy cập:** **qua Higgsfield — model `gemini_omni_flash_1_1`** (mode `text-to-video` / `image-to-video` / `reference-to-video` / `edit`; 3–10s, edit tới 30s; tới 4K trên Higgsfield). Ngoài ra: app Gemini, Google AI Studio, Gemini API.
- **Độ dài:** clip **3–10 giây**, tỉ lệ 16:9 hoặc 9:16. Bản preview 06/2026 chỉ 720p; bản 1.1 trên Higgsfield có 360p–4K.
- **Đầu vào:** kết hợp chữ, ảnh, âm thanh, video trong một prompt.
- **Mạnh nhất ở:** **sửa video bằng lời qua nhiều lượt** ("đổi áo sang màu đỏ", "cho trời mưa") mà không phải tạo lại từ đầu; vật lý chuyển động tốt; giữ nhất quán nhân vật.
- **Giá tham khảo:** ~0,10 USD / giây video (API, 06/2026).
- **Lưu ý:** mọi clip gắn watermark SynthID (vô hình). Bản 720p cần upscale nếu xuất 1080p/4K.
- **Chọn khi:** shot ngắn cần chỉnh sửa lặp lại nhiều lần theo góp ý; cảnh cần vật lý chân thật (nước, vải, tóc); bản nháp nhanh để duyệt nhịp phim.

## Cách viết prompt
- Một đoạn mô tả liền mạch cho 1 shot: chủ thể → hành động → bối cảnh → máy quay (cỡ cảnh, góc, chuyển động, ống kính) → ánh sáng → phong cách → âm thanh.
- Sau khi có clip, sửa bằng câu lệnh ngắn, mỗi lượt một thay đổi.

Nguồn: deepmind.google/models/model-cards/gemini-omni-flash · buildfastwithai.com (review 2026) · wavespeed.ai/blog (Gemini Omni Flash shipped)
