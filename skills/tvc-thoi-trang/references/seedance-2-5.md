# Luật viết prompt Seedance 2.5

Tổng hợp từ các hướng dẫn công khai (09/2026). Khi phần mềm của người dùng có giao diện khác, ưu tiên cách đặt tên ảnh của phần mềm đó.

## Khả năng
- Tạo **tối đa 30 giây trong một lần**, có âm thanh gốc (nhạc, tiếng động, lời thoại). Có thể nối dài nhiều lượt (beta).
- Nhận **nhiều tham chiếu**: ảnh, video, âm thanh — gọi bằng `@image1`, `@image2`, `@video1`, `@audio1`...
- Hiểu tốt cấu trúc nhiều shot có nhãn và mốc thời gian.

## Tham chiếu ảnh — quan trọng nhất cho TVC sản phẩm
1. **Mỗi ảnh một vai trò, nói rõ bằng một câu:** `@image1 defines only the earring: its exact shape, metal color, stone and proportions.`
2. **Nói rõ phần cần bỏ qua:** nền, da, tay người, vật khác trong ảnh sẽ "rò" vào video nếu không loại trừ — `Ignore the background of this image.`
3. **Nhiều góc của cùng một sản phẩm:** `@image1 defines the front of the bag. @image2 defines the side of the same bag. Both images define one single bag. There is only ever one bag in the video.` — thiếu câu cuối, AI có thể tạo ra nhiều túi.
4. **Ít mà đúng:** một ảnh cho mỗi thứ cần giữ nhất quán (mặt người mẫu, từng sản phẩm, bối cảnh, phong cách). Không nhồi quá nhiều ảnh.
5. **Ảnh sản phẩm tốt nhất:** nền trơn, đủ sáng, rõ chi tiết khóa/kim loại/viên đá, không bị che.

## Cấu trúc prompt nhiều shot
```
REFERENCES: (vai trò từng @image)
STYLE: (định dạng, bối cảnh, bảng màu, ánh sáng, người mẫu, cảm xúc — áp dụng cho cả phim)
SHOTS:
Shot 1 (0-4s): [cỡ cảnh + góc], [hành động], [chuyển động máy]. Hard cut.
Shot 2 (4-6s): ...
AUDIO: (nhạc, tiếng động, lời thoại nếu có)
```
- Mỗi shot ghi **cỡ cảnh, góc máy, hành động, chuyển động máy, điểm kết thúc**, rồi `Hard cut.` (hoặc `Match cut to…`, `Dissolve to…`).
- Tổng mốc thời gian phải khớp đúng độ dài video.
- Nên để mỗi shot từ khoảng 1,5–3 giây trở lên: gộp các shot cắt rất nhanh của video gốc lại cho AI kịp thể hiện từng ý. Muốn nhịp nhanh hơn thì cắt ngắn ở hậu kỳ. (Kinh nghiệm chung, chưa kiểm chứng riêng cho Seedance — điều chỉnh theo kết quả thực tế.)
- Chuyển cảnh mơ hồ là nguyên nhân số một làm mất nhất quán.

## Ngôn ngữ
- Viết prompt bằng **tiếng Anh**, câu mô tả cụ thể, ưu tiên danh từ hình ảnh và thuật ngữ quay phim (low angle, 100mm macro, slow push in, rim light).
- Tránh tính từ rỗng ("beautiful", "amazing"); thay bằng mô tả ánh sáng, chất liệu, chuyển động.
- Chữ trên màn hình và logo: AI hay sai, đặc biệt tiếng Việt có dấu → chèn ở hậu kỳ.

## Nguồn
- https://www.rundiffusion.com/seedance-2-5-prompt-guide
- https://openart.ai/blog/seedance-2-5-prompt-guide/
- https://vidmuse.ai/blog/seedance-2-5-guide
- https://www.kapwing.com/resources/how-to-prompt-seedance-2-5-a-guide-for-ai-video-creators/
