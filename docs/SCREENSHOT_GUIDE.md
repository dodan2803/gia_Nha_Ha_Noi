# Hướng dẫn chụp ảnh minh chứng

Dùng ảnh chụp trực tiếp từ ứng dụng đang chạy, không dựng giao diện giả. Trên macOS nhấn **Shift–Command–4** để chọn vùng, hoặc **Shift–Command–5** để chụp/capture cửa sổ. Lưu PNG vào thư mục `screenshots/` theo tên dưới đây. Trước khi chụp, đóng hộp thoại không liên quan và bảo đảm thấy rõ tiêu đề/trạng thái.

1. `01-khoi-dong.png` — Terminal có lệnh `streamlit run streamlit_app.py` và trang app mở.
2. `02-du-lieu-tho.png` — mở `data/hanoi_housing_raw.csv`, thấy giá trị thiếu và tên quận/loại chưa chuẩn.
3. `03-lam-sach.png` — trang **Làm sạch dữ liệu**, tải CSV thô; chụp phần preview, báo cáo và nút tải CSV sạch.
4. `04-import.png` — trang **Quản lý dữ liệu**, chọn CSV/XLSX, xác nhận nhập và số bản ghi cập nhật.
5. `05-crud-them.png` — form thêm, sau lưu thấy bản ghi trong SQLite-backed table.
6. `06-crud-sua.png` — chọn ID, đổi một trường, lưu và xác nhận giá trị đã cập nhật.
7. `07-crud-xoa.png` — chọn ID xóa và chụp bảng sau khi dòng biến mất.
8. `08-tim-kiem-loc.png` — từ khóa, quận hoặc loại nhà đang chọn cùng bảng kết quả.
9. `09-dashboard.png` — KPI và các biểu đồ diện tích, quận, loại nhà, tuổi nhà.
10. `10-tien-ich-tuong-quan.png` — so sánh tiện ích và heatmap Pearson.
11. `11-export.png` — chụp nút tải CSV/XLSX và tệp tải mở trong Numbers/Excel.
12. `12-tableau.png` — Tableau Desktop đang dùng CSV/XLSX hoặc dashboard thật trong vùng embed nếu URL có quyền truy cập.

Đối với thao tác CRUD, dùng một bản ghi thử có mã ghi chú riêng, rồi xóa sau khi chụp để không ảnh hưởng bộ dữ liệu nộp. Không đưa URL Tableau riêng tư hoặc thông tin tài khoản vào ảnh. Gắn các ảnh này vào phần Phụ lục B của báo cáo Word.
