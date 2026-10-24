# DuckDuckGo tiếng Việt — iOS Community Localization

> **Trạng thái: bản khởi đầu có kiểm thử, CHƯA phải ứng dụng Việt hóa hoàn chỉnh, CHƯA build/kiểm thử trên iPhone.**

Dự án độc lập (không phải phiên bản chính thức của DuckDuckGo) để thêm tiếng Việt cho trình duyệt iOS mã nguồn mở [duckduckgo/apple-browsers](https://github.com/duckduckgo/apple-browsers).

## Đã có

- **2.088 chuỗi tiếng Việt đã được biên soạn trong sáu nguồn chính** gồm giao diện chính, quyền truy cập ứng dụng và một phần Đồng bộ & Sao lưu.
- Công cụ tạo `.lproj/Localizable.strings`, `.lproj/InfoPlist.strings` từ tệp nguồn tiếng Anh chính thức.
- Các chuỗi chưa dịch giữ tiếng Anh, không tuyên bố đạt 100%. Phần lớn 65 khóa còn lại là tên sản phẩm không nên dịch (Duck.ai, VPN, iPhone), nút OK, ví dụ dữ liệu hoặc chuỗi nguồn chỉ chứa tên khóa; chúng vẫn cần rà soát khi chạy thực tế. Phần trăm bao phủ thực tế xuất ở `coverage.json` khi tải được nguồn.
- Trình kiểm tra khóa, trùng khóa, biến định dạng `%@`, `%d`, `%%` và chuỗi rỗng.
- CI chạy kiểm thử, tải **6 tệp nguồn cụ thể** từ commit cố định để tránh thay đổi không báo trước; xuất gói dịch từ GitHub Actions.
- Workflow **thử build không ký** chạy trên Xcode 27; chỉ kích hoạt thủ công hoặc khi sửa chính workflow. Các thử nghiệm thực tế đã giúp sửa phụ thuộc font Duck Sans riêng tư và script ký GRDB.framework. Chưa xác nhận build thành công.

## Mã nguồn gốc

- Repository: https://github.com/duckduckgo/apple-browsers
- Commit cố định: `54be22874ad58d907e88a8a7b0d2065ae19e99d4` (24/10/2026)
- Giấy phép mã nguồn DuckDuckGo: Apache 2.0; font Duck Sans là tài sản cấp phép riêng **không được phân phối**.
- `duckduckgo-locales` dành cho duckduckgo.com, **không phải** bộ mã nguồn trình duyệt iOS.

## Sử dụng đơn giản

Dự án đang được quản lý tại [quocbeck198-hue/duckduckgo-vietnamese](https://github.com/quocbeck198-hue/duckduckgo-vietnamese). Để lấy tài nguyên dịch:

1. Mở **Actions → Validate Vietnamese localization → Run workflow**.
2. Khi job PASS, mở **Artifacts → duckduckgo-vi-lproj** để tải các thư mục bản dịch và `coverage.json`.
3. Không cài trực tiếp Artifact này lên iPhone: đây là **tài nguyên để build**, không phải ứng dụng.

### Tự chạy trên máy tính (có Python 3.10+)

```bash
python3 -m unittest discover -s tests -v
python3 scripts/fetch_upstream.py --source upstream
python3 scripts/localize.py --source upstream --output output
```

> Chỉ tạo tệp ở `output/`, không sửa repository gốc.

### Kiểm thử build iOS bằng GitHub Actions (tùy chọn)

1. Mở **Actions → Experimental iOS unsigned build (manual) → Run workflow**.
2. Workflow sẽ checkout nguyên mã nguồn và submodule, thêm tệp `vi.lproj`, bỏ tham chiếu đến gói font Duck Sans độc quyền theo hướng dẫn chính thức, rồi thử biên dịch bằng Xcode.
3. Nếu build PASS, sản phẩm là **IPA chưa được ký** (UNSIGNED): chưa cài được trên iPhone cho đến khi ký bằng chứng chỉ / provisioning profile hợp lệ.
4. Nếu build FAIL, xem lỗi trong Actions, khắc phục phụ thuộc, resource membership và các vấn đề mới của dự án upstream; kết quả phụ thuộc Apple và môi trường build thực tế.

**Lưu ý:** Standard macOS runner miễn phí đối với repository công khai theo tài liệu GitHub. Workflow macOS không tự chạy khi chỉ cập nhật bản dịch; nó chạy khi sửa tệp workflow hoặc khi bấm Run workflow. Không nhập Apple ID/mật khẩu/2FA vào biến môi trường hoặc workflow.

## Cấu trúc

```text
.github/workflows/validate.yml            # unit tests, xuất vi.lproj + coverage
.github/workflows/build-ios-unsigned.yml   # thử build Xcode, chỉ chạy thủ công
translations/vi.json                       # 2088 chuỗi trong 6 mô-đun đã kiểm kê
scripts/fetch_upstream.py                  # tải 6 tệp đã cố định SHA
scripts/localize.py                        # sinh vi.lproj + kiểm tra format
scripts/patch_project.py                   # thêm vi vào Xcode knownRegions, bỏ font private
scripts/patch_spm_lock.py                  # bỏ khóa gói font riêng tư
scripts/patch_unsigned_grdb.py             # bỏ ký GRDB khi CODE_SIGNING_ALLOWED=NO
upstream.json                              # commit gốc
```

## Cách tiếp tục để đạt bản hoàn thiện

1. CI ban đầu đã PASS với 6 nguồn thật (2.153 chuỗi, 2.088 mục Việt hóa ≈ 96,98%); tiếp tục kiểm tra các bản cập nhật.
2. Dịch tiếp mọi chuỗi tiếng Anh bằng cách sửa `translations/vi.json` (đúng từng key, kiểm tra placeholders).
3. Bổ sung những `.stringsdict`, package hay web resources còn thiếu sau khi đối chiếu toàn bộ mã nguồn. Tránh cho rằng `6` tệp này bao phủ toàn bộ ứng dụng.
4. Build thật, thử các màn hình trên iPhone, sửa lỗi tràn chữ/vấn đề dịch và ký ứng dụng riêng nếu cần.
5. Có thể gửi Pull Request ngược upstream để xin hỗ trợ tiếng Việt chính thức.

## Giới hạn đã xác minh

- Không jailbreak nhưng iOS vẫn yêu cầu **ký mã ứng dụng** mới có thể cài. Bản unsigned IPA không phải ứng dụng đã cài được.
- Repo gốc có gói Swift font DuckSansFont riêng tư; không sao chép font độc quyền.
- Việc dịch **không** làm cho trình duyệt bản App Store được tự động Việt hóa.
- Bản dịch đã qua CI nhưng build iOS chưa được xác nhận PASS; ứng dụng iPhone cần ký mã hợp lệ.

Không liên kết hay tuyên bố được DuckDuckGo tài trợ hoặc chứng nhận.

## Kiểm thử và giới hạn hiện tại (24/10/2026)

- 6 tệp nguồn tiếng Anh có tổng cộng 2.153 khóa theo kiểm đếm cố định; bản dịch cung cấp 2.088 khóa. **Tỷ lệ này chỉ áp dụng cho sáu tệp nguồn, không phải toàn ứng dụng.**
- GitHub Actions chạy kiểm thử Python tự động, phát hiện sai khác placeholder, liên kết Markdown và các biểu thức nhúng; xem [lịch sử CI](https://github.com/quocbeck198-hue/duckduckgo-vietnamese/actions/workflows/validate.yml).
- Build thử không ký trên runner Xcode 27: [xem trạng thái](https://github.com/quocbeck198-hue/duckduckgo-vietnamese/actions/workflows/build-ios-unsigned.yml). Không tuyên bố có IPA cài được khi chưa thấy job PASS.
- Các mẫu ví dụ lệnh Siri tiếng Anh được cố ý giữ nguyên để phù hợp cách kích hoạt khẩu lệnh. Tên thương hiệu/định dạng dữ liệu không dịch tùy tiện.
- Cần kiểm tra .stringsdict, các gói SwiftPM dùng tài nguyên riêng, tài nguyên web và thiết kế giao diện trên thiết bị thực trước khi phát hành.
- Cài trên iPhone không jailbreak vẫn yêu cầu ký mã Apple và cấu hình provisioning hợp lệ; tuyệt đối không gửi mật khẩu hoặc mã 2FA vào chat.
