# Gemini Omni Flash (Google)

- **Truy cập:** app Gemini, Google AI Studio, Gemini API (developer từ 30/06/2026).
- **Độ dài:** clip **3–10 giây**, 720p, 24 fps, tỉ lệ 16:9 hoặc 9:16 (bản preview 06/2026).
- **Đầu vào:** kết hợp chữ, ảnh, âm thanh, video trong một prompt.
- **Mạnh nhất ở:** **sửa video bằng lời qua nhiều lượt** ("đổi áo sang màu đỏ", "cho trời mưa") mà không phải tạo lại từ đầu; vật lý chuyển động tốt; giữ nhất quán nhân vật.
- **Giá tham khảo:** ~0,10 USD / giây video (API, 06/2026).
- **Lưu ý:** mọi clip gắn watermark SynthID (vô hình). 720p — cần upscale nếu xuất 1080p/4K.
- **Chọn khi:** shot ngắn cần chỉnh sửa lặp lại nhiều lần theo góp ý; cảnh cần vật lý chân thật (nước, vải, tóc); bản nháp nhanh để duyệt nhịp phim.

## Cách viết prompt
- Một đoạn mô tả liền mạch cho 1 shot: chủ thể → hành động → bối cảnh → máy quay (cỡ cảnh, góc, chuyển động, ống kính) → ánh sáng → phong cách → âm thanh.
- Sau khi có clip, sửa bằng câu lệnh ngắn, mỗi lượt một thay đổi.

Nguồn: deepmind.google/models/model-cards/gemini-omni-flash · buildfastwithai.com (review 2026) · wavespeed.ai/blog (Gemini Omni Flash shipped)
