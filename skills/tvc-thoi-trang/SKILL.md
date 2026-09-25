---
name: tvc-thoi-trang
description: Kỹ năng làm phim quảng cáo (TVC) AI cho người mẫu, thời trang, trang sức, túi xách, phụ kiện và sản phẩm làm đẹp — phân tích một TVC tham chiếu theo 9 yếu tố (màu sắc, phong cách, góc quay, chuyển cảnh, chuyển động máy, tiêu cự, phong cách chữ, ánh sáng, cảm xúc) và viết prompt Seedance 2.5 dùng ảnh tham chiếu sản phẩm/người mẫu. Dùng skill này bất cứ khi nào người dùng muốn làm video quảng cáo thời trang, lookbook, fashion film, video trang sức/túi/giày/mỹ phẩm, "TVC", "phim quảng cáo", gửi ảnh sản phẩm kèm yêu cầu làm video, gửi một video quảng cáo mẫu để học phong cách, hoặc nhắc tới Seedance / Kling / Veo / Sora cho nội dung thời trang — kể cả khi họ không nói chữ "TVC".
---

# TVC thời trang bằng AI — thư viện phong cách

Skill này là một **thư viện phong cách làm phim**. Mỗi phong cách là một file riêng trong `references/phong-cach/`, được bóc tách từ một TVC thật theo cùng một khung 9 yếu tố, kèm shot list và prompt mẫu. Người dùng (chủ Ari Yoga, làm thêm marketing) sẽ bổ sung phong cách mới theo thời gian, nên hãy giữ cấu trúc nhất quán để các phong cách có thể so sánh và kết hợp với nhau.

## Danh mục phong cách hiện có

| Mã | Tên | Hợp với | File |
|---|---|---|---|
| 01 | Quiet Luxury Kiến Trúc (Skyspace) | Trang sức, túi da, đồng hồ, nước hoa, thời trang tối giản cao cấp | `references/phong-cach/01-quiet-luxury-kien-truc.md` |

Khi thêm phong cách mới: tạo file `NN-ten-phong-cach.md` theo đúng mẫu ở mục "Khung phân tích 9 yếu tố" bên dưới, rồi thêm một dòng vào bảng này.

Luật viết prompt cho Seedance 2.5 (cú pháp ảnh tham chiếu, cấu trúc nhiều shot, giới hạn 30 giây) nằm ở `references/seedance-2-5.md` — đọc file này mỗi khi phải viết prompt.

## Chọn quy trình theo yêu cầu

**A. Người dùng gửi một TVC mẫu để học phong cách** → phân tích và tạo file phong cách mới.
1. Xem video từng khung hình (trích khung mỗi 0,5 giây; phát hiện điểm cắt cảnh để đếm số shot và nhịp dựng). Nghe phần âm thanh: có lời thoại không, nhạc kiểu gì, cao trào ở giây nào.
2. Lập shot list có mốc thời gian (cỡ cảnh, góc, chuyển động, ống kính ước lượng, nội dung).
3. Viết phân tích theo đủ 9 yếu tố của khung bên dưới — cụ thể, đo được (mã màu, mm ống kính, số shot, độ dài trung bình mỗi shot), không chung chung kiểu "đẹp, sang".
4. Rút ra **công thức cấu trúc** (các "hồi" của phim) để áp dụng cho sản phẩm khác, không phải để chép lại video gốc.
5. Viết prompt Seedance 2.5 mẫu dạng template có chỗ trống cho sản phẩm.
6. Lưu thành file phong cách mới và cập nhật bảng danh mục.

**B. Người dùng gửi ảnh sản phẩm/người mẫu và muốn làm TVC** → viết prompt.
1. Hỏi (hoặc suy ra) phong cách muốn dùng; nếu chưa rõ, đề xuất 1 phong cách hợp nhất với loại sản phẩm và giải thích ngắn vì sao.
2. Đọc file phong cách tương ứng và `references/seedance-2-5.md`.
3. Gán vai trò cho từng ảnh tham chiếu (@image1 = sản phẩm A, @image2 = người mẫu...). Nói rõ ảnh nào cùng là một vật thể để AI không nhân bản sản phẩm.
4. Viết prompt hoàn chỉnh 30 giây (một lần tạo), chia shot có mốc thời gian, kèm phần âm thanh.
5. Kèm ghi chú dựng hậu kỳ: chèn logo/chữ tiếng Việt sau (AI hay viết sai chữ và logo), gợi ý nhạc.

**C. Kết hợp phong cách** → lấy khung cấu trúc và nhịp dựng của một phong cách, bảng màu/ánh sáng của phong cách kia. Nói rõ yếu tố nào lấy từ đâu để người dùng kiểm soát được.

## Khung phân tích 9 yếu tố

Mỗi file phong cách dùng đúng thứ tự này để dễ đối chiếu:

1. **Màu sắc** — bảng màu chủ đạo (có mã HEX ước lượng), độ bão hoà, tương phản, chất phim (grain, halation), màu da.
2. **Phong cách** — thể loại hình ảnh, cảm hứng nghệ thuật/kiến trúc, styling người mẫu (tóc, trang điểm, trang phục), bối cảnh.
3. **Góc quay** — các góc chủ đạo và tỉ lệ sử dụng, vì sao góc đó phục vụ thông điệp.
4. **Chuyển cảnh** — kiểu cắt (cut on beat, match cut theo hình khối, texture wipe, flare...), số shot, độ dài trung bình.
5. **Chuyển động máy** — push in, tilt, arc, drift, locked-off...; tốc độ; chuyển động của chủ thể (tóc bay, vải, nước).
6. **Tiêu cự** — ống kính ước lượng theo loại shot, độ sâu trường ảnh, macro.
7. **Phong cách chữ** — font, cỡ, vị trí, thời điểm xuất hiện, hiệu ứng.
8. **Ánh sáng** — nguồn chính, hướng, độ cứng/mềm, backlight/rim, cách làm trang sức "bắt sáng".
9. **Cảm xúc** — cảm xúc chủ đạo, ánh mắt/biểu cảm người mẫu, nhạc và sound design, đường cong cảm xúc theo thời gian.

Sau 9 yếu tố luôn có: **Shot list gốc**, **Công thức cấu trúc**, **Prompt template Seedance 2.5**, **Lỗi thường gặp và cách tránh**.

## Nguyên tắc
- Học phong cách, không sao chép thương hiệu: không đưa logo, tên hãng, monogram của TVC gốc vào prompt; dùng sản phẩm của người dùng qua ảnh tham chiếu.
- Mỗi shot chỉ một ý hình ảnh chính. Phim trang sức sống nhờ nhịp xen kẽ: toàn cảnh kiến trúc → cận sản phẩm → chân dung, lặp lại và tăng tốc về cuối.
- Viết prompt bằng tiếng Anh (Seedance hiểu tốt nhất), giải thích và ghi chú cho người dùng bằng tiếng Việt.
- Khi dùng skill `cinematic-techniques` cùng lúc: skill đó cung cấp kho thuật ngữ góc máy/ánh sáng; skill này quyết định cấu trúc TVC và cách xử lý sản phẩm.
