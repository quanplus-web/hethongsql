import subprocess
import os

html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>KẾ HOẠCH MIGRATION DỮ LIỆU & ĐỐI SOÁT CHẤT LƯỢNG</title>
<style>
  @page {
    size: A4;
    margin: 15mm 15mm 15mm 15mm;
  }
  body {
    font-family: 'Times New Roman', Times, serif, 'Segoe UI', Arial;
    color: #000;
    line-height: 1.4;
    font-size: 12px;
    background: #fff;
    margin: 0;
    padding: 0;
  }
  .header {
    border-bottom: 2px solid #000;
    padding-bottom: 8px;
    margin-bottom: 12px;
    text-align: center;
  }
  .company-tag {
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
  }
  .title {
    font-size: 16px;
    font-weight: bold;
    color: #000;
    margin: 0 0 4px 0;
    text-transform: uppercase;
  }
  .subtitle {
    font-size: 11.5px;
    color: #333;
    margin: 0;
    font-style: italic;
  }
  .info-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 12px;
    font-size: 11px;
  }
  .info-table td {
    border: 1px solid #000;
    padding: 4px 8px;
  }
  .info-table td.label {
    font-weight: bold;
    background: #f0f0f0;
    width: 22%;
  }
  h2 {
    font-size: 13px;
    font-weight: bold;
    color: #000;
    border-bottom: 1px solid #000;
    padding-bottom: 3px;
    margin-top: 12px;
    margin-bottom: 6px;
    text-transform: uppercase;
  }
  h3 {
    font-size: 12px;
    font-weight: bold;
    color: #000;
    margin-top: 8px;
    margin-bottom: 4px;
  }
  p, li {
    font-size: 11.5px;
    color: #000;
    margin: 3px 0;
  }
  ul, ol {
    margin-top: 2px;
    margin-bottom: 6px;
    padding-left: 20px;
  }
  li {
    margin-bottom: 2px;
  }
  .box-note {
    border: 1px solid #000;
    padding: 6px 10px;
    margin: 8px 0;
    background: #fafafa;
    font-size: 11px;
  }
  .box-note strong {
    text-transform: uppercase;
  }
  
  table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0 10px 0;
    font-size: 11px;
  }
  table.data-table th, table.data-table td {
    border: 1px solid #000;
    padding: 4px 6px;
    text-align: left;
    vertical-align: middle;
  }
  table.data-table th {
    background: #e5e5e5;
    color: #000;
    font-weight: bold;
    text-align: center;
  }
  table.data-table td.center {
    text-align: center;
  }
  code {
    font-family: Consolas, 'Courier New', monospace;
    font-size: 10px;
    color: #000;
  }
  .page-break {
    page-break-before: always;
  }
  .footer {
    margin-top: 15px;
    border-top: 1px solid #000;
    padding-top: 4px;
    font-size: 9.5px;
    display: flex;
    justify-content: space-between;
  }
</style>
</head>
<body>

<div class="header">
  <div class="company-tag">TÀI LIỆU KỸ THUẬT & QUY TRÌNH NGIỆM THU DỮ LIỆU</div>
  <h1 class="title">KẾ HOẠCH MIGRATION DỮ LIỆU & ĐỐI SOÁT CHẤT LƯỢNG</h1>
  <p class="subtitle">Dự án: Chuyển đổi dữ liệu 30 Bảng (Sheets/Excel) & Tệp đính kèm (Google Drive) sang Database</p>
</div>

<table class="info-table">
  <tr>
    <td class="label">Nguồn dữ liệu:</td>
    <td>30 Bảng/Sheets (RQC-CP-Database.xlsx) & Tệp đính kèm trên Google Drive</td>
    <td class="label">Hệ quản trị CSDL:</td>
    <td>PostgreSQL / MySQL</td>
  </tr>
  <tr>
    <td class="label">Nguyên tắc an toàn:</td>
    <td>Zero Direct Mutation (Chỉ xuất file .sql để Review trước khi nạp DB)</td>
    <td class="label">Cơ chế đối soát:</td>
    <td>Matrix Validation (Kiểm tra khớp 100% dòng, nhóm & link file)</td>
  </tr>
</table>

<h2>I. NGUYÊN TẮC VÀ CAM KẾT TRIỂN KHAI</h2>
<ul>
  <li><strong>1. Kiểm soát an toàn (Zero Direct Mutation):</strong> Tool hoạt động hoàn toàn ở chế độ Đọc (Read-Only) đối với dữ liệu nguồn. Toàn bộ dữ liệu được chuyển đổi thành các file kịch bản SQL (<code>.sql</code>) riêng biệt. <strong>Tuyệt đối không tự ý thực thi bất kỳ lệnh INSERT/UPDATE trực tiếp vào Database</strong> trước khi Sếp kiểm tra và duyệt file SQL.</li>
  <li><strong>2. Độc lập cấu hình (Config-Driven):</strong> Toàn bộ đường dẫn Google Sheet và Google Drive được quản lý qua file cấu hình môi trường (<code>.env</code>). Hiện tại đã dựng khung và kiểm thử hoàn chỉnh trên Drive/Sheet nội bộ; khi có liên kết nguồn chính thức, chỉ cần thay đổi 2 dòng cấu hình là hệ thống chạy ngay.</li>
  <li><strong>3. Xử lý toàn diện tệp tin Google Drive:</strong> Tự động quét cây thư mục Google Drive qua API, bóc tách mã định danh để khớp chính xác từng tệp đính kèm vào đúng bản ghi dữ liệu tương ứng ở tất cả các bảng.</li>
</ul>

<h2>II. QUY TRÌNH 5 BƯỚC THỰC HIỆN (PIPELINE)</h2>
<ol>
  <li><strong>Bước 1 - Extract (Trích xuất):</strong> Đọc dữ liệu từ 30 sheets nguồn và quét danh mục file trên Google Drive qua API (lấy File ID, tên file, kích thước, link tải).</li>
  <li><strong>Bước 2 - Transform (Chuẩn hóa):</strong> Chuẩn hóa định dạng ngày tháng, số tiền, text UTF-8 và xây dựng quan hệ khóa ngoại (Foreign Keys) giữa các bảng cha - con.</li>
  <li><strong>Bước 3 - File Mapping (Ánh xạ tệp tin):</strong> Bóc tách mã ID từ tên file Drive để gắn đúng File ID/URL vào từng dòng dữ liệu ở tất cả các bảng có file.</li>
  <li><strong>Bước 4 - SQL Generation (Sinh tập lệnh SQL):</strong> Kết xuất dữ liệu thành các file <code>.sql</code> theo thứ tự phụ thuộc bảng để không bị lỗi khóa ngoại.</li>
  <li><strong>Bước 5 - Validation (Đối soát dữ liệu):</strong> Chạy kiểm tra chéo 100% giữa Sheet nguồn và file SQL/Database, xuất báo cáo đối soát chi tiết.</li>
</ol>

<div class="box-note">
  <strong>QUY TRÌNH PHÊ DUYỆT:</strong> Sau Bước 4 và Bước 5, toàn bộ tập tin SQL (<code>01_master_data.sql</code>, <code>02_transaction_data.sql</code>, <code>03_files_data.sql</code>) kèm theo <strong>Báo Cáo Đối Soát Dữ Liệu</strong> sẽ được gửi Sếp kiểm duyệt trước khi nạp vào Database.
</div>

<h2>III. CHIẾN LƯỢC XỬ LÝ TỆP TIN GOOGLE DRIVE</h2>

<h3>1. Phạm vi các bảng chứa tệp đính kèm</h3>
<ul>
  <li><strong>Bảng PROCESS:</strong> Ánh xạ file quy trình tại cột <code>PROCEDURE FILE</code> (ví dụ: <code>00d30875.PROCEDURE FILE.094814.xlsm - Procurement.pdf</code>) và link <code>PROCEDURE LINK</code>.</li>
  <li><strong>Bảng REQUEST DETAIL:</strong> Các file hóa đơn, báo giá, tài liệu đính kèm theo từng hạng mục chi tiết.</li>
  <li><strong>Bảng INVOICE / PAYMENT / EXPENSE:</strong> File scan hóa đơn VAT, ủy nhiệm chi, chứng từ ngân hàng.</li>
  <li><strong>Bảng ASSET / SERVICE ORDER:</strong> Biên bản bàn giao tài sản, hợp đồng dịch vụ kỹ thuật.</li>
</ul>

<h3>2. Cơ chế bóc tách và khớp file (Pattern Matching)</h3>
<ul>
  <li><strong>Trích xuất mã bản ghi:</strong> Dùng Regex bóc tách mã ID ở đầu tên file trên Drive: <code>[RECORD_ID].[TÊN_CỘT].[TIMESTAMP].[TÊN_FILE]</code> (Ví dụ trích xuất được <code>RECORD_ID = 00d30875</code> để gán đúng vào bản ghi tương ứng).</li>
  <li><strong>Lưu trữ Metadata trong DB:</strong> Lưu các trường: <code>drive_file_id</code>, <code>file_name</code>, <code>file_size_bytes</code>, <code>mime_type</code>, <code>drive_view_link</code>, <code>download_link</code>.</li>
</ul>

<h3>3. Xử lý các tình huống ngoại lệ</h3>
<table class="data-table">
  <thead>
    <tr>
      <th style="width: 25%;">Tình Huống Ngoại Lệ</th>
      <th style="width: 45%;">Giải Pháp Xử Lý Kỹ Thuật</th>
      <th style="width: 30%;">Phương Án Báo Cáo</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. File bị thiếu trên Drive</strong><br>(Sheet có tên nhưng Drive không có)</td>
      <td>Giữ nguyên tên file text trên Sheet, đánh dấu cờ <code>has_missing_file = true</code> để không làm ngắt quãng quá trình sinh SQL.</td>
      <td>Xuất riêng danh sách <code>missing_files_audit.xlsx</code> để Sếp kiểm tra.</td>
    </tr>
    <tr>
      <td><strong>2. Trùng mã ID / Nhiều phiên bản</strong></td>
      <td>Lưu trữ theo quan hệ 1-N hoặc chọn file có thời gian cập nhật mới nhất (<code>modifiedTime</code>).</td>
      <td>Ghi log danh sách file trùng lặp.</td>
    </tr>
    <tr>
      <td><strong>3. File lỗi / 0 bytes</strong></td>
      <td>Kiểm tra dung lượng <code>size > 0</code> trước khi sinh lệnh SQL gán file.</td>
      <td>Cảnh báo trong Báo cáo đối soát.</td>
    </tr>
    <tr>
      <td><strong>4. Quyền truy cập tệp</strong></td>
      <td>Đảm bảo link xem trực tiếp (View Link) theo chuẩn định dạng Google Workspace.</td>
      <td>Kiểm tra 100% link mở được bởi nhân sự có thẩm quyền.</td>
    </tr>
  </tbody>
</table>

<div class="page-break"></div>

<h2>IV. MA TRẬN TIÊU CHÍ ĐỐI SOÁT DỮ LIỆU (VALIDATION MATRIX)</h2>

<h3>1. Tiêu chí kiểm tra Tổng thể Hệ thống & Tệp tin</h3>
<table class="data-table">
  <thead>
    <tr>
      <th style="width: 20%;">Nhóm Tiêu Chí</th>
      <th style="width: 40%;">Mục Tiêu & Phương Pháp Đối Soát</th>
      <th style="width: 25%;">Điều Kiện Đạt (Pass)</th>
      <th style="width: 15%;">Kết Quả Yêu Cầu</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. Tổng số dòng</strong></td>
      <td>So khớp tổng số bản ghi giữa từng Sheet nguồn và bảng trong Database.</td>
      <td><code>COUNT(*)</code> DB = Số dòng trên Sheet</td>
      <td class="center">Khớp 100%</td>
    </tr>
    <tr>
      <td><strong>2. Tính duy nhất</strong></td>
      <td>Kiểm tra các trường khóa chính (ID, Code) không bị trùng lặp.</td>
      <td><code>COUNT(id) = COUNT(DISTINCT id)</code></td>
      <td class="center">Khớp 100%</td>
    </tr>
    <tr>
      <td><strong>3. Khóa ngoại</strong></td>
      <td>Đảm bảo không phát sinh bản ghi mồ côi (Orphan records).</td>
      <td>100% ID tham chiếu tồn tại ở bảng cha</td>
      <td class="center">Khớp 100%</td>
    </tr>
    <tr>
      <td><strong>4. Tệp đính kèm Drive</strong></td>
      <td>Toàn bộ dòng có file trên Sheet đều được gán đúng ID và Link tải.</td>
      <td>Số dòng có file = Số file map thành công</td>
      <td class="center">Khớp 100%</td>
    </tr>
    <tr>
      <td><strong>5. Toàn vẹn Link File</strong></td>
      <td>Gửi HTTP HEAD request kiểm tra tình trạng sống/chết của link đính kèm.</td>
      <td>HTTP Status Code = 200</td>
      <td class="center">100% Link sống</td>
    </tr>
    <tr>
      <td><strong>6. Toàn vẹn số tiền</strong></td>
      <td>Đối chiếu tổng số tiền phát sinh theo từng loại tiền tệ (VND, USD).</td>
      <td><code>SUM(amount)</code> DB = <code>SUM(amount)</code> Sheet</td>
      <td class="center">Sai số = 0</td>
    </tr>
  </tbody>
</table>

<h3>2. Bảng Đối Soát Mẫu Cho Các Bảng Điển Hình</h3>

<h4>A. Bảng Master Data: COMPANY</h4>
<table class="data-table">
  <thead>
    <tr>
      <th style="width: 6%;">STT</th>
      <th style="width: 30%;">Tiêu Chí Kiểm Tra</th>
      <th style="width: 40%;">Câu Lệnh SQL / Phương Pháp Kiểm Tra</th>
      <th style="width: 24%;">Mục Tiêu Kết Quả</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="center">1</td>
      <td>Tổng số lượng Công ty</td>
      <td><code>SELECT COUNT(*) FROM company;</code></td>
      <td>Khớp chính xác số dòng trên Sheet</td>
    </tr>
    <tr>
      <td class="center">2</td>
      <td>Phân bổ theo Loại (Type)</td>
      <td><code>SELECT type, COUNT(*) FROM company GROUP BY type;</code></td>
      <td>Khớp từng nhóm (Khách hàng, NCC, Đối tác)</td>
    </tr>
    <tr>
      <td class="center">3</td>
      <td>Phân bổ Quốc gia & Thành phố</td>
      <td><code>SELECT country, city, COUNT(*) FROM company GROUP BY country, city;</code></td>
      <td>Chuẩn hóa tên địa danh, khớp 100% số lượng</td>
    </tr>
    <tr>
      <td class="center">4</td>
      <td>Trường bắt buộc không NULL</td>
      <td><code>SELECT COUNT(*) FROM company WHERE name IS NULL OR code IS NULL;</code></td>
      <td>Kết quả = 0 bản ghi lỗi</td>
    </tr>
  </tbody>
</table>

<h4>B. Bảng Quy Trình có File: PROCESS</h4>
<table class="data-table">
  <thead>
    <tr>
      <th style="width: 6%;">STT</th>
      <th style="width: 30%;">Tiêu Chí Kiểm Tra</th>
      <th style="width: 40%;">Câu Lệnh SQL / Phương Pháp Kiểm Tra</th>
      <th style="width: 24%;">Mục Tiêu Kết Quả</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="center">1</td>
      <td>Tổng số lượng quy trình</td>
      <td><code>SELECT COUNT(*) FROM process;</code></td>
      <td>Khớp 100% số quy trình trên Sheet</td>
    </tr>
    <tr>
      <td class="center">2</td>
      <td>Khớp File quy trình (Procedure File)</td>
      <td><code>SELECT COUNT(*) FROM process WHERE procedure_file_id IS NOT NULL;</code></td>
      <td>Khớp chính xác số lượng file PDF/Docx trên Drive</td>
    </tr>
    <tr>
      <td class="center">3</td>
      <td>Độ hợp lệ của Procedure Link</td>
      <td><code>SELECT COUNT(*) FROM process WHERE procedure_link IS NOT NULL AND procedure_link NOT LIKE 'http%';</code></td>
      <td>Kết quả = 0 (100% link đúng định dạng URL)</td>
    </tr>
  </tbody>
</table>

<h4>C. Bảng Transaction & File: REQUEST DETAIL</h4>
<table class="data-table">
  <thead>
    <tr>
      <th style="width: 6%;">STT</th>
      <th style="width: 30%;">Tiêu Chí Kiểm Tra</th>
      <th style="width: 40%;">Câu Lệnh SQL / Phương Pháp Kiểm Tra</th>
      <th style="width: 24%;">Mục Tiêu Kết Quả</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td class="center">1</td>
      <td>Tổng số bản ghi chi tiết</td>
      <td><code>SELECT COUNT(*) FROM request_detail;</code></td>
      <td>Khớp 100% số dòng trên Sheet nguồn</td>
    </tr>
    <tr>
      <td class="center">2</td>
      <td>Khóa ngoại liên kết REQUEST</td>
      <td><code>SELECT COUNT(*) FROM request_detail rd LEFT JOIN request r ON rd.request_id = r.id WHERE r.id IS NULL;</code></td>
      <td>Kết quả = 0 (Tất cả chi tiết đều thuộc Request hợp lệ)</td>
    </tr>
    <tr>
      <td class="center">3</td>
      <td>Tổng giá trị tiền tệ</td>
      <td><code>SELECT currency, SUM(amount) FROM request_detail GROUP BY currency;</code></td>
      <td>Khớp từng đồng/cent so với tổng cột trên Sheet</td>
    </tr>
    <tr>
      <td class="center">4</td>
      <td>Khớp File đính kèm Drive</td>
      <td><code>SELECT COUNT(*) FROM request_detail WHERE has_attachment = true AND drive_file_id IS NULL;</code></td>
      <td>Kết quả = 0 (100% file đính kèm được gắn link)</td>
    </tr>
  </tbody>
</table>

<h2>V. SẢN PHẨM BÀN GIAO SAU KHI HOÀN TẤT</h2>
<ol>
  <li><strong>Bộ kịch bản SQL hoàn chỉnh:</strong> Đầy đủ các file <code>.sql</code> được sắp xếp theo đúng thứ tự nạp dữ liệu tối ưu, không phát sinh lỗi khóa ngoại.</li>
  <li><strong>Báo Cáo Đối Soát Dữ Liệu & Tệp Tin (Validation Report):</strong> File tài liệu tổng hợp bảng kiểm tra chéo từng trường dữ liệu và danh sách kiểm tra link file để Sếp đối chiếu nghiệm thu.</li>
  <li><strong>Mã nguồn Tool Migration & Hướng dẫn vận hành:</strong> Bàn giao kèm hướng dẫn cấu hình <code>.env</code> để phục vụ cho các lần đồng bộ hoặc cập nhật sau này.</li>
</ol>

<div class="footer">
  <span>Tài liệu Kế Hoạch Migration & Đối Soát Dữ Liệu</span>
  <span>Lưu hành nội bộ</span>
</div>

</body>
</html>
"""

html_file = os.path.abspath('plan.html')
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
pdf_out = os.path.abspath(r'd:\toolsql\Ke_Hoach_Migration_Va_Doi_Soat_Du_Lieu.pdf')
file_url = 'file:///' + html_file.replace('\\', '/')

cmd = [
    chrome_path,
    '--headless',
    '--disable-gpu',
    '--no-pdf-header-footer',
    f'--print-to-pdf={pdf_out}',
    file_url
]
res = subprocess.run(cmd, capture_output=True, text=True)
print('Chrome exit code:', res.returncode)
print('PDF file exists:', os.path.exists(pdf_out))
if os.path.exists(pdf_out):
    print('PDF size:', os.path.getsize(pdf_out), 'bytes')
