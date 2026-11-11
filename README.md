# Hanoi Housing Lab

Ứng dụng Streamlit phục vụ đồ án phân tích dữ liệu giá nhà tại Hà Nội. Bộ dữ liệu đi kèm gồm 600 hồ sơ **mô phỏng theo quy tắc**, không lấy từ tin đăng hoặc giao dịch thật, không phản ánh chính xác mặt bằng giá và không dùng để định giá.

## Chạy trên macOS

1. Cài Python 3.10+ (khuyến nghị Python 3.12/3.13), tải/giải nén dự án.
2. Mở Terminal, chuyển đến thư mục dự án, tạo môi trường ảo:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. Sinh CSV mẫu và Excel (script có đường dự phòng tạo XLSX bằng thư viện chuẩn nếu openpyxl chưa cài):

   ```bash
   python generate_data.py
   ```

4. Khởi chạy giao diện:

   ```bash
   streamlit run streamlit_app.py
   ```

5. Mở URL localhost hiện trong Terminal (thường là `http://localhost:8501`). Dừng bằng `Control-C`.

SQLite được tạo tại `data/housing.db`. Xóa file này để đặt lại cơ sở dữ liệu từ `data/hanoi_housing_clean.csv`. Mọi thay đổi trên app lưu xuống SQLite.

## Chức năng

- Dashboard với scatter, box, violin, histogram, bar chart tiện ích và heatmap tương quan.
- Tìm kiếm/lọc theo từ khóa, quận, loại nhà, diện tích.
- Thêm, sửa, xóa bản ghi; nhập CSV/XLSX và tải dữ liệu CSV/XLSX.
- Trang làm sạch cho xem trước trước/sau, thống kê số ô điền, trùng lặp và dòng loại bỏ.
- Tableau: xuất CSV/XLSX tương thích Tableau Desktop và hiển thị URL embed HTTPS mà người dùng có quyền truy cập.

## Quy tắc xử lý dữ liệu

`src/housing/cleaning.py` chuẩn hóa tên cột/biến thể tiếng Việt, khoảng trắng, kiểu số và nhãn quận/loại nhà; suy ra đơn giá hoặc tổng giá khi thiếu và các trường liên quan có dữ liệu; điền thiếu bằng trung vị (giá/diện tích/tuổi) hoặc giá trị mặc định; loại hồ sơ lặp và diện tích/giá không hợp lệ. Phần mềm không tự giả định dữ liệu mẫu là dữ liệu thật.

## Tableau

1. Trên trang **Tableau**, tải CSV/XLSX.
2. Trong Tableau Desktop, chọn kết nối Text File hoặc Microsoft Excel.
3. Tạo worksheet/dashboard; ví dụ biểu đồ đơn giá trung vị theo quận, scatter diện tích-giá, filter loại nhà và tiện ích.
4. Từ Tableau Public/Server, lấy URL embed được phép chia sẻ; dán URL bắt đầu bằng HTTPS vào trang Tableau trong Streamlit.
5. Nếu dashboard private hoặc máy chủ không cho phép nhúng, dashboard vẫn hoạt động trong Tableau nhưng không hiển thị trong iframe.

## Cấu trúc

```text
streamlit_app.py        Giao diện, biểu đồ, CRUD, import/export, Tableau
src/housing/cleaning.py Chuẩn hóa và báo cáo chất lượng dữ liệu
src/housing/storage.py SQLite CRUD
generate_data.py        Sinh dữ liệu minh họa
data/                   CSV thô, CSV sạch, XLSX và SQLite
docs/                   Báo cáo Word và hướng dẫn minh chứng
outputs/                Tệp bàn giao
```
