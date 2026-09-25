# Seedance 2.5 (ByteDance)

- **Truy cập:** **qua Higgsfield — model `seedance_2_5`** (tự động, ưu tiên). Ngoài ra: web Dreamina/CapCut, API BytePlus (dán tay).
- **Chế độ trên Higgsfield:** `t2v` (chỉ chữ), `omni_reference` (ảnh/video/âm thanh tham chiếu), `video_edit` (sửa một video), `video_extension` (nối dài trước/sau). Bản 2.0 (`seedance_2_0`, 4–15s) hỗ trợ Elements để giữ nhân vật.
- **Độ dài:** tối đa **30 giây một lần tạo**, có âm thanh gốc; nối dài nhiều lượt (beta) tới ~180 giây.
- **Tham chiếu:** tối đa ~50 (khoảng 30 ảnh, 10 video, 10 âm thanh) — gọi `@image1`, `@video1`, `@audio1`.
- **Mạnh nhất ở:** nhiều shot trong một clip (multi-shot có nhãn và mốc giờ), giữ nhất quán sản phẩm/nhân vật nhờ nhiều ảnh tham chiếu, TVC thời trang/sản phẩm.
- **Chọn khi:** một cảnh gồm nhiều shot liền nhau cần cùng bối cảnh và nhân vật → gom thành một **clip** ≤ 30s.

## Cách viết prompt
```
REFERENCES:
@image1 defines only <vật/người>: <điều cần giữ>. Ignore the background of this image.
(Nhiều góc của cùng một vật: "... Both images define one single <vật>. There is only ever one <vật> in the video.")
STYLE: <định dạng, tỉ lệ, bối cảnh, bảng màu, ánh sáng, người mẫu, cảm xúc>
SHOTS:
Shot 1 (0-4s): <cỡ cảnh + góc>, <hành động>, <chuyển động máy>. Hard cut.
...
AUDIO: <nhạc, tiếng động, lời thoại>
Do not add any logos, brand names or text.
```
- Mỗi ảnh một vai trò; nói rõ phần cần bỏ qua (nền, tay người, vật lạ).
- Mốc thời gian các shot cộng lại đúng độ dài clip.
- Chữ/logo chèn ở hậu kỳ.

Nguồn: rundiffusion.com/seedance-2-5-prompt-guide · openart.ai/blog/seedance-2-5-prompt-guide · vidmuse.ai/blog/seedance-2-5-guide
