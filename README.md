# DuckDuckGo tiếng Việt — iOS Community Localization

> **Trạng thái: bản khởi đầu có kiểm thử, CHƯA phải ứng dụng Việt hóa hoàn chỉnh, CHƯA build/kiểm thử trên iPhone.**

Dự án độc lập (không phải phiên bản chính thức của DuckDuckGo) để thêm tiếng Việt cho trình duyệt iOS mã nguồn mở [duckduckgo/apple-browsers](https://github.com/duckduckgo/apple-browsers).

## Đã có

- **208 bản dịch được biên soạn** gồm giao diện chính, quyền truy cập ứng dụng và một phần Đồng bộ & Sao lưu.
- Công cụ tạo `.lproj/Localizable.strings`, `.lproj/InfoPlist.strings` từ tệp nguồn tiếng Anh chính thức.
- Các chuỗi chưa dịch giữ tiếng Anh, không tuyên bố đạt 100%. Phần trăm bao phủ thực tế xuất ở `coverage.json` khi tải được nguồn.
- Trình kiểm tra khóa, trùng khóa, biến định dạng `%@`, `%d`, `%%` và chuỗi rỗng.
- CI chạy kiểm thử, tải **6 tệp nguồn cụ thể** từ commit cố định để tránh thay đổi không báo trước; xuất gói dịch từ GitHub Actions.
- Workflow **thử build không ký (manual)** trên macOS Runner với Xcode. Quy trình thử nghiệm, có thể thất bại vì phụ thuộc dự án và chưa được chạy thực tế. Không tự chạy khi push.

## Mã nguồn gốc

- Repository: https://github.com/duckduckgo/apple-browsers
- Commit cố định: `54be22874ad58d907e88a8a7b0d2065ae19e99d4` (24/10/2026)
- Giấy phép mã nguồn DuckDuckGo: Apache 2.0; font Duck Sans là tài sản cấp phép riêng **không được phân phối**.
- `duckduckgo-locales` dành cho duckduckgo.com, **không phải** bộ mã nguồn trình duyệt iOS.

## Sử dụng đơn giản

Sau khi đưa các tệp của dự án này lên **một repository GitHub mới, riêng biệt**:

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

### Kiểm thử build iOS tự động bằng GitHub Actions (tùy chọn)

1. Mở **Actions → Experimental iOS unsigned build (manual) → Run workflow**.
2. Workflow sẽ checkout nguyên mã nguồn và submodule, thêm tệp `vi.lproj`, bỏ tham chiếu đến gói font Duck Sans độc quyền theo hướng dẫn chính thức, rồi thử biên dịch bằng Xcode.
3. Nếu build PASS, sản phẩm là **IPA chưa được ký** (UNSIGNED): chưa cài được trên iPhone cho đến khi ký bằng chứng chỉ / provisioning profile hợp lệ.
4. Nếu build FAIL, xem lỗi trong Actions, khắc phục phụ thuộc, resource membership và các vấn đề mới của dự án upstream; kết quả phụ thuộc Apple và môi trường build thực tế.

**Lưu ý:** GitHub Actions có thể tính phút chạy theo gói và loại repository; workflow macOS chỉ chạy thủ công để không tiêu phí ngoài ý muốn. Không nhập Apple ID/mật khẩu/2FA vào biến môi trường hoặc workflow.

## Cấu trúc

```text
.github/workflows/validate.yml            # unit tests, xuất vi.lproj + coverage
.github/workflows/build-ios-unsigned.yml   # thử build Xcode, chỉ chạy thủ công
translations/vi.json                       # 208 bản dịch thật
scripts/fetch_upstream.py                  # tải 6 tệp đã cố định SHA
scripts/localize.py                        # sinh vi.lproj + kiểm tra format
scripts/patch_project.py                   # thêm vi vào Xcode knownRegions, bỏ font private
upstream.json                              # commit gốc
```

## Cách tiếp tục để đạt bản hoàn thiện

1. Đưa dự án vào repo mới, chạy CI đầu tiên; sửa lỗi xảy ra trên chuỗi thực và báo cáo coverage.
2. Dịch tiếp mọi chuỗi tiếng Anh bằng cách sửa `translations/vi.json` (đúng từng key, kiểm tra placeholders).
3. Bổ sung những `.stringsdict`, package hay web resources còn thiếu sau khi đối chiếu toàn bộ mã nguồn. Tránh cho rằng `6` tệp này bao phủ toàn bộ ứng dụng.
4. Build thật, thử các màn hình trên iPhone, sửa lỗi tràn chữ/vấn đề dịch và ký ứng dụng riêng nếu cần.
5. Có thể gửi Pull Request ngược upstream để xin hỗ trợ tiếng Việt chính thức.

## Giới hạn đã xác minh

- Không jailbreak nhưng iOS vẫn yêu cầu **ký mã ứng dụng** mới có thể cài. Bản unsigned IPA không phải ứng dụng đã cài được.
- Repo gốc có gói Swift font DuckSansFont riêng tư; không sao chép font độc quyền.
- Việc dịch **không** làm cho trình duyệt bản App Store được tự động Việt hóa.
- Hiện project không chứa bản build iOS đã kiểm chứng.

Không liên kết hay tuyên bố được DuckDuckGo tài trợ hoặc chứng nhận.
