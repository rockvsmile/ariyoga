# Veo 3.1 (Google)

- **Truy cập:** Gemini API, Vertex AI, Google Flow, app Gemini.
- **Độ dài:** tối đa **8 giây** mỗi clip; 720p / 1080p / 4K; có âm thanh gốc (thoại, tiếng động, nhạc).
- **Tham chiếu:** tối đa **3 ảnh** để giữ nhất quán nhân vật/phong cách; hỗ trợ khung đầu – khung cuối.
- **Mạnh nhất ở:** chất lượng hình ảnh điện ảnh cao, **lời thoại khớp môi**, xuất 4K.
- **Chọn khi:** shot hero cần độ nét cao nhất; cảnh có nhân vật nói thoại; cần khung đầu/cuối cố định để nối shot liền mạch.

## Cách viết prompt
- Một shot mỗi prompt: `[cỡ cảnh + góc + chuyển động máy] of [chủ thể] [hành động] in [bối cảnh], [ánh sáng], [phong cách/film look]. Audio: [thoại trong ngoặc kép], [tiếng động], [nhạc].`
- Lời thoại đặt trong ngoặc kép và ghi rõ ai nói.
- Dùng ảnh khung cuối của shot trước làm khung đầu shot sau để nối liền.

Nguồn: ai.google.dev/gemini-api/docs/veo · developers.googleblog.com (Introducing Veo 3.1)
