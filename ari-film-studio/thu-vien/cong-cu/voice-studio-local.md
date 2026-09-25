# App giọng trên máy (Voice Studio và các app giọng local khác)

Bạn có nhiều app tạo giọng chạy trên máy; mỗi video chọn app phù hợp ở **Bảng kết nối → Lồng tiếng → App giọng trên máy tôi → tên app** (từng track cũng chọn app riêng được ở Khung 8). Cách kết nối giống nhau cho mọi app:

- **Kết nối:** **trao đổi file** — cách này chạy được với mọi app giọng nói trên máy, không cần app có API.
  1. Kỹ Sư Âm Thanh xuất lời thoại ra `du-an/<id>/am-thanh/kich-ban-giong/`:
     - `A01.txt`, `A02.txt`… — mỗi file một câu/đoạn, đúng mã track.
     - `danh-sach.csv` — cột `ma,loai,canh,giong,bat_dau,loi` để bạn nhìn tổng thể.
  2. Bạn mở app đã chọn, tạo giọng cho từng file, xuất ra `du-an/<id>/am-thanh/A01.wav` (hoặc `.mp3`) — **tên file = mã track**.
  3. Bấm **Quét file mới** trên bảng điều khiển (Khung 8) → studio tự gắn file vào track.
- **Ghi chú theo từng app:** thêm mục `## <Tên app>` bên dưới (giọng hay dùng, định dạng xuất, mẹo đọc tiếng Việt) — Kỹ Sư Âm Thanh đọc để soạn file lời đúng kiểu app đó (vd app cần dấu ngắt nghỉ riêng).
- **Nâng cấp sau:** nếu app nào có API trên máy (vd địa chỉ `http://localhost:…`) hoặc chạy được bằng dòng lệnh, cho Claude biết tên app và tài liệu — Thủ Thư sẽ thêm cách gọi trực tiếp cho app đó, không cần làm tay.
- **Chọn khi:** bạn đã có giọng ưng ý trong app riêng, muốn làm offline, hoặc không muốn tốn credit dịch vụ online.

## Các app của bạn
<!-- Thủ Thư thêm từng app ở đây khi bạn giới thiệu: tên, định dạng xuất, giọng hay dùng, có API không. -->
