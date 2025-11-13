# Hệ Thống Điều Khiển Đo Lường Điện Hóa

Repository này chứa ứng dụng desktop và firmware nhúng dùng để điều khiển và giám sát hệ thống đo lường điện hóa dựa trên phương pháp Cyclic Voltammetry (CV).  
Ứng dụng Python cung cấp giao diện đồ họa để cấu hình thí nghiệm, hiển thị dữ liệu trực tiếp, lưu kết quả và đồng bộ các chỉ số quan trọng qua MQTT/Firebase. Các sketch firmware điều khiển phần cứng potentiostat (ESP32 + LMP91000 + ADS1115) qua kết nối không dây hoặc serial.

## Cấu Trúc Repository

- `ControlSoftware/` – Ứng dụng desktop CV dựa trên Tkinter (các quy trình làm việc: wireless, serial và import CSV).
- `ControlCircuit/` – Các sketch Arduino/ESP32 cho bộ điều khiển potentiostat và các tiện ích hỗ trợ.
- `*.pdf` – Tài liệu hỗ trợ (biên bản họp, hướng dẫn sử dụng, v.v.).

## Yêu Cầu Hệ Thống

- Python 3.10+ trên Windows (đã kiểm thử với `python` từ Microsoft Store hoặc trình cài đặt từ python.org).
- Git, PowerShell hoặc terminal có quyền truy cập `pip`.
- Tùy chọn: Arduino IDE / PlatformIO để nạp firmware trong `ControlCircuit/`.

### Các Thư Viện Python Cần Thiết

Tất cả các phụ thuộc runtime được liệt kê trong `ControlSoftware/requirements.txt` (Matplotlib, SciPy, Pandas, PySerial, Pyrebase, Paho MQTT, v.v.).  
Một số gói này có sẵn bản native wheels; việc cài đặt dễ dàng nhất trên Windows khi sử dụng phiên bản Python gần đây.

## Bắt Đầu (Phần Mềm Điều Khiển)

1. **Tạo và kích hoạt môi trường ảo (khuyến nghị):**
   ```powershell
   cd D:\k1ch\coli\ecma
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
2. **Cài đặt các thư viện phụ thuộc:**
   ```powershell
   pip install -r ControlSoftware\requirements.txt
   ```
3. **Cấu hình thông tin xác thực Firebase (tùy chọn):**
   - Chỉnh sửa `ControlSoftware/authfirebase.py` và điền thông tin vào từ điển `firebaseConfig` với các khóa dự án của bạn.
   - Cung cấp đường dẫn JSON tài khoản dịch vụ nếu bạn muốn tải biểu đồ lên Firebase Storage.
4. **Chạy ứng dụng:**
   ```powershell
   python ControlSoftware\main.py
   ```
   Cửa sổ giao diện (`Electrochemical Measurement Application`) sẽ mở với ba tab:
   - **WIRELESS** – Kết nối với broker MQTT và nhận dữ liệu CV từ ESP32.
   - **SERIAL** – Truyền dữ liệu CV qua USB/serial từ Arduino/ESP32.
   - **IMPORT** – Tải các bộ dữ liệu CSV đã lưu trước đó để phân tích, lọc và đồng bộ MQTT/Firebase.

### Quy Trình Làm Việc Wireless

- Cung cấp IP broker, tên người dùng và mật khẩu, sau đó nhấn `Login`.
- Sau khi kết nối thành công, ứng dụng đăng ký các topic:
  - `CV/values` – mẫu dữ liệu trực tiếp (Điện thế mV ; Dòng điện µA).
  - `CV/status_plot` – trạng thái run/done.
  - `CV/statusESP` – trạng thái sẵn sàng của ESP32.
- Sử dụng panel **Configure** để thiết lập điện thế bắt đầu/kết thúc, kích thước bước, tốc độ quét, số lần lặp lại (≤5) và tần số cắt.
- Nhấn `START` để xuất bản lệnh đến topic `CV/command`. Sketch ESP32 trong `ControlCircuit/esp_cv/` phân tích và thực thi lệnh này, sau đó truyền kết quả trở lại GUI theo thời gian thực.
- Khi quá trình chạy kết thúc, GUI có thể lưu biểu đồ thô & đã lọc và các tệp CSV vào `data/<solution>/<concentration>/<date>/<measurement>/`.
- Nếu thông tin xác thực Firebase hợp lệ, biểu đồ đã lọc (`_lowpass.png`) sẽ tự động tải lên Cloud Storage.

### Quy Trình Làm Việc Serial

- Chọn cổng COM từ menu thả xuống và nhấn `Connect`. Tốc độ serial mặc định là 115200 baud.
- Cấu hình điện thế, bước, tốc độ quét, số lần lặp lại và tần số cắt tương tự như chế độ wireless.
- Nhấn `START` để truyền mẫu trực tiếp qua serial. Dữ liệu được vẽ theo thời gian thực; hỗ trợ tạm dừng/tiếp tục.
- Sau khi lọc, lưu phiên làm việc hoặc tính toán nồng độ qua công cụ `Calculate cM` (chuyển đổi tuyến tính từ dòng đỉnh).

### Quy Trình Làm Việc Import

- Nhấp `Browse Data Set` để chọn CSV được tạo bởi một trong hai quy trình làm việc.
- Chế độ xem bảng hiển thị tất cả các cột (`mV_x`, `uA_x`, `filter_uA_x`) và tạo bảng tóm tắt min/max.
- Các hành động bổ sung:
  - `Plot Filtered Figure` – xuất biểu đồ so sánh cho tín hiệu thô và đã lọc.
  - `Calculate CM` – tính toán giá trị nồng độ từ dòng đỉnh và xuất bản chúng qua MQTT nếu được yêu cầu.
  - `Send Values` – đẩy các chỉ số min/max và biểu đồ lên broker MQTT/Firebase Storage.

### Xử Lý Dữ Liệu

- Tất cả các phiên đã lưu nằm trong thư mục `data/` có thể cấu hình, được tổ chức theo loại dung dịch, nồng độ, ngày và chỉ số đo lường.
- Các hình ảnh tạm thời để tải lên được lưu trong thư mục `temp/` tạm thời, được dọn dẹp sau khi đồng bộ Firebase.

## Ghi Chú Firmware (ControlCircuit)

- `esp_cv/esp_cv.ino` – Firmware ESP32 điều khiển potentiostat và xuất bản mẫu CV qua MQTT. Cập nhật `WIFI_SSID`, `WIFI_PASSWORD` và `mqtt_server` trước khi nạp.
- `cv_arduino/cv_arduino.ino` & `sketch_feb10a/` – Các biến thể điều khiển CV dựa trên serial.
- `LMP91000/`, `scani2c/` – Tiện ích để cấu hình và chẩn đoán front-end LMP91000.
- Các thư viện cần thiết được đóng gói trong `ControlCircuit/libraries.zip` (driver LMP91000, ADC ADS1X15). Sao chép chúng vào thư mục `libraries` của Arduino hoặc cài đặt qua môi trường của bạn.

## Khắc Phục Sự Cố

- **Lỗi Matplotlib/Tkinter trên Windows:** Đảm bảo bạn đang chạy ứng dụng từ venv đã kích hoạt và đã thực thi `python -m pip install --upgrade pip` một lần.
- **Cổng serial không hiển thị:** Sử dụng `Reload list PORT` sau khi cắm thiết bị. Đảm bảo không có phần mềm nào khác đang giữ cổng COM.
- **MQTT không nhận được dữ liệu:** Xác nhận khả năng truy cập broker và ESP32 đang xuất bản đến các topic `CV/*` mong đợi. Sử dụng các công cụ như `mosquitto_sub` để gỡ lỗi.
- **Tải lên Firebase thất bại:** Kiểm tra lại thông tin xác thực trong `authfirebase.py`. Khi bị vô hiệu hóa, ứng dụng vẫn tiếp tục hoạt động cục bộ.

## Lộ Trình / Các Cải Tiến Có Thể

- Đóng gói GUI thành trình cài đặt độc lập với PyInstaller.
- Thêm unit test cho các pipeline xử lý dữ liệu (lọc, tính toán nồng độ).
- Mở rộng tài liệu cho các hướng dẫn PDF hoặc chuyển đổi chúng sang Markdown.

---

Bạn có thể tùy chỉnh README theo môi trường triển khai của mình (ví dụ: topic MQTT tùy chỉnh, backend lưu trữ dữ liệu thay thế).
