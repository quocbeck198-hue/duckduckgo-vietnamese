# Ký và cài bản DuckDuckGo Việt hóa trên iPhone (không jailbreak)

## Điều kiện đã biết

- Bộ tài nguyên bản dịch và kiểm thử đang ở repository này. Gói `duckduckgo-vi-lproj` là mã dịch, không thể cài trực tiếp.
- Workflow `build-ios-unsigned.yml` chỉ biên dịch để kiểm tra lỗi. Dù chạy PASS, IPA **chưa ký** sẽ không thể cài như ứng dụng iPhone thông thường.
- Bản dịch cộng đồng có thể được cài như ứng dụng *riêng*, không ghi đè trình duyệt chính thức. Không đổi tên/gói ứng dụng thành định danh của DuckDuckGo gốc nếu không có quyền.

## Phương án miễn phí có máy Mac

1. Dùng máy Mac cài Xcode tương thích với commit nguồn trong `upstream.json`.
2. Mở Xcode, đăng nhập Apple Account của bạn trong **Xcode → Settings → Accounts**, không chia sẻ mật khẩu.
3. Đăng ký `Personal Team` miễn phí trong Xcode và thiết lập một Bundle Identifier riêng.
4. Kết nối iPhone, bật chế độ Developer Mode khi được iOS yêu cầu.
5. Cài và chạy ứng dụng từ Xcode bằng **Automatically manage signing** sau khi build không ký đã PASS.

Apple lưu ý các provisioning profile của Personal Team miễn phí hết hạn sau 7 ngày; thường cần tạo lại và cài lại. Đọc: https://developer.apple.com/help/account/basics/about-your-developer-account/

## Nếu chỉ có iPhone

Không có con đường miễn phí, được xác minh và an toàn để tự ký rồi cài tùy ý một IPA mới bằng GitHub Actions mà không có tài nguyên ký của Apple hoặc một hệ thống Mac/Xcode hỗ trợ. Không sử dụng chứng chỉ doanh nghiệp bị rò rỉ, các trang yêu cầu đăng nhập Apple ID hay IPA DuckDuckGo Việt hóa không rõ nguồn.

## Nếu có tài khoản Apple Developer Program

Bạn có thể đăng ký chứng chỉ phát triển và provisioning profile chứa thiết bị được phép cài, theo hướng dẫn: https://developer.apple.com/help/account/provisioning-profiles/create-a-development-provisioning-profile

Giữ chứng chỉ và khóa riêng trên máy tin cậy hoặc quản lý bí mật có phân quyền. Không gửi private key, mật khẩu, Apple ID hay mã 2FA vào issue, chat hoặc commit GitHub.

## Tiêu chí chấp nhận trước khi dùng chính thức

- Build iOS PASS trên đúng phiên bản Xcode.
- Ứng dụng riêng có chữ ký Apple hợp lệ và cài được lên iPhone thật.
- Kiểm tra ít nhất: tạo/đóng tab, tìm kiếm, dấu trang, lịch sử, xóa dữ liệu, quyền máy ảnh/micrô, đồng bộ, bảo vệ theo dõi và các màn hình Cài đặt.
- Đối chiếu giao diện tiếng Việt trên thiết bị: không tràn chữ, không sai ngữ cảnh, giữ đúng tên thương hiệu và biến số lượng.
- Đánh giá riêng các tính năng đòi hỏi App Groups, VPN/Network Extension và các entitlements có thể không hỗ trợ Personal Team miễn phí.

Đây không phải bản chính thức được DuckDuckGo xác nhận.
