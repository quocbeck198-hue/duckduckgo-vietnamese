# Sử dụng dự án DuckDuckGo tiếng Việt trên iPhone

## Bản dịch đã triển khai

Repository riêng đã được tạo: https://github.com/quocbeck198-hue/duckduckgo-vietnamese

1. Mở GitHub trên iPhone, vào repository nói trên.
2. Chọn **Actions** > **Validate Vietnamese localization**.
3. Chọn lượt chạy PASS mới nhất rồi chọn **Artifacts** > **duckduckgo-vi-lproj**.
4. Gói tải xuống chứa các tệp dịch `vi.lproj` và báo cáo `coverage.json`. **Đó không phải tệp cài đặt iOS**.

## Trạng thái ứng dụng thực tế

- Trình duyệt DuckDuckGo cài từ App Store không tự đổi sang tiếng Việt bằng bộ dịch này.
- Build không ký được thử trên Xcode 27 bằng GitHub Actions; xem https://github.com/quocbeck198-hue/duckduckgo-vietnamese/actions/workflows/build-ios-unsigned.yml
- Chỉ sau khi build PASS và thiết lập đúng chữ ký Apple, mới có thể xem xét cài bản ứng dụng riêng trên iPhone không jailbreak.
- Việc ký và cấp phát cấu hình có thể cần máy Mac/Xcode hoặc hệ thống ký hợp pháp có Apple Developer account và thông tin thiết bị.
- Không gửi Apple ID, mật khẩu, mã xác thực hai bước hay chứng chỉ riêng qua tin nhắn; chỉ dùng công cụ bảo mật hoặc GitHub Secrets khi phù hợp.

## Giới hạn kiểm thử

Báo cáo phần trăm hiện chỉ tính 6 tệp nguồn iOS đã chọn, không bao trọn mọi chuỗi của trình duyệt. Những tên thương hiệu, mẫu URL hay lời gọi Siri tiếng Anh có thể được giữ nguyên có chủ đích. Phải kiểm thử trực tiếp các màn hình và chức năng trước khi dùng làm trình duyệt chính.

Bản dịch là dự án cộng đồng, không phải bản phát hành chính thức.
