---
name: phim-moi
description: Tạo một dự án phim mới trong Ari Film Studio và bắt đầu khung Ý tưởng. Dùng khi người dùng gõ /phim-moi hoặc nói muốn làm một phim/video/TVC mới.
---

1. Lấy tên phim từ tham số (vd `/phim-moi TVC Ari Legacy`); nếu không có, hỏi một tên ngắn.
2. Chạy `python tools/tao_du_an.py "<tên>"` → in ra id dự án.
3. Nếu người dùng đã kể ý tưởng trong chat, ghi nguyên văn vào `khung.1_y_tuong.noi_dung.cot_truyen` và các thông tin suy ra được (thời lượng, tỉ lệ, nền tảng).
4. Hỏi người dùng muốn chế độ **từng bước** (mặc định, dừng duyệt ở mỗi khung) hay **tự động**; ghi vào `che_do`.
5. Nhắc người dùng mở bảng điều khiển: chạy `python studio.py` ở cửa sổ khác (hoặc bấm đúp `mo-studio.bat` trên Windows) → http://127.0.0.1:8765, chọn dự án, tải ảnh tham chiếu ở Khung 3.
6. Nếu đã có ý tưởng, làm luôn khung 1 theo quy trình của `/tiep-tuc`.
