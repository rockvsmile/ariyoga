---
name: tiep-tuc
description: Làm khung kế tiếp của một dự án phim trong Ari Film Studio (ý tưởng, phong cách, tham chiếu, ép cảnh, kịch bản, storyboard) bằng đúng agent chuyên biệt, tôn trọng khoá và cổng duyệt. Dùng khi người dùng gõ /tiep-tuc, "làm tiếp", "duyệt rồi", "sửa lại khung X", hoặc vừa chỉnh trên bảng điều khiển.
---

Tham số: `<id-dự-án> [số khung]`. Không có id → nếu chỉ có một dự án thì dùng nó, nhiều dự án thì hỏi.

1. Đọc `du-an/<id>/project.json`. Chạy `python tools/kiem_tra_du_an.py <id>`.
2. **Xác định việc cần làm** (theo thứ tự ưu tiên):
   - Người dùng chỉ định khung → làm khung đó.
   - Có khung `can_sua` → làm lại khung đó theo `ghi_chu_nguoi_dung`.
   - Ngược lại → khung đầu tiên chưa `da_duyet` và chưa khoá. Chế độ `tung_buoc`: khung trước nó phải `da_duyet` (khung 4 tuỳ chọn); nếu chưa, nhắc người dùng duyệt trên bảng điều khiển và dừng.
   - Khung 7 trở đi → chuyển sang `/tao-video`, `/dung-phim`.
3. **Kiểm tra Bảng kết nối:** các mảnh ghép thuộc khung sắp làm (xem trường `khung` trong `thu-vien/bang-ket-noi.json`) đã có `nguon` chưa. Thiếu → liệt kê, hỏi người dùng chọn (có thể kèm gợi ý), dừng. Mảnh chọn `nguoi_dung` → agent chỉ kiểm tra/góp ý; `tat` → bỏ qua.
4. **Giao đúng agent** (xem bảng trong CLAUDE.md), truyền: id, khung, lời người dùng vừa nói. Khung 1: `dao-dien` rồi `bien-kich`. Khung 3: `chi-dao-hinh-anh` rồi hỏi người dùng có muốn `chuyen-gia-nhan-vat` khoá danh tính trên Higgsfield không (rất nên với phim nhiều cảnh). Khung 5: `bien-kich` rồi `dao-dien` duyệt nội bộ. Khung 6: `quay-phim`, rồi hỏi người dùng có muốn `hoa-si-storyboard` vẽ ảnh không (tốn credit) hay chỉ lấy prompt.
5. Sau khi agent xong: chạy lại `kiem_tra_du_an.py`. Tóm tắt cho người dùng 3–6 dòng: đã làm gì, lựa chọn chính, cần họ quyết định gì. Nhắc xem và duyệt trên bảng điều khiển.
6. Chế độ `tu_dong`: lặp lại bước 2–5 cho các khung chưa khoá, dừng trước khung 7.
