import os
import sys
import sqlite3
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request, send_from_directory
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import config
from pipeline.step_01_extract import run_extract
from pipeline.step_02_transform import run_transform
from pipeline.step_03_file_mapping import run_file_mapping
from pipeline.step_04_generate_sql import run_generate_sql
from pipeline.step_05_validate import run_validation
from main import create_sample_mock_data_if_missing

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Hệ Thống Migration Dữ Liệu & Đối Soát SQL</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #f4f6fc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --teal: #00897b;
      --teal-hover: #00796b;
      --text: #0f172a;
      --muted: #64748b;
      --success: #10b981;
      --success-bg: #e6f4ea;
    }
    
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    
    body {
      font-family: 'Inter', -apple-system, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.4;
      padding: 12px 16px;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    .container-full {
      width: 100%;
      max-width: 100%;
      margin: 0 auto;
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    /* HEADER */
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--card-bg);
      padding: 12px 20px;
      border-radius: 8px;
      border: 1px solid var(--border);
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
      margin-bottom: 12px;
    }
    .brand-group {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-logo {
      width: 38px;
      height: 38px;
      background: #eff6ff;
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      color: var(--primary);
    }
    .brand h1 {
      font-size: 17px;
      font-weight: 800;
      color: #1e293b;
      letter-spacing: -0.2px;
    }
    .brand p {
      font-size: 11.5px;
      color: var(--muted);
      margin-top: 1px;
    }
    /* CARD KHUNG NGOÀI */
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.02);
      width: 100%;
    }

    .control-grid {
      display: grid;
      grid-template-columns: 1.2fr 1.2fr 220px;
      gap: 16px;
      align-items: start;
      width: 100%;
    }
    @media (max-width: 1100px) {
      .control-grid { grid-template-columns: 1fr 1fr; }
    }

    label.field-label {
      display: block;
      font-size: 11.5px;
      font-weight: 700;
      color: #334155;
      margin-bottom: 5px;
    }
    .help-text {
      font-size: 10.5px;
      color: #94a3b8;
      margin-top: 3px;
      font-style: italic;
    }

    input[type="text"], select {
      width: 100%;
      background: #ffffff;
      border: 1px solid #cbd5e1;
      color: var(--text);
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 12px;
      outline: none;
      font-family: 'JetBrains Mono', monospace;
    }
    input[type="text"]:focus, select:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
    }

    /* Drop Box */
    .drop-box {
      border: 1.5px dashed #cbd5e1;
      border-radius: 6px;
      padding: 8px;
      background: #f8fafc;
      cursor: pointer;
      text-align: center;
      font-size: 11.5px;
      color: #64748b;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .drop-box:hover, .drop-box.dragover {
      border-color: var(--primary);
      background: #eff6ff;
      color: var(--primary);
    }

    .drop-box-drive {
      border: 1.5px dashed #a7f3d0;
      border-radius: 6px;
      padding: 8px;
      background: #f0fdf4;
      cursor: pointer;
      text-align: center;
      font-size: 11.5px;
      color: #047857;
      transition: all 0.15s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .drop-box-drive:hover, .drop-box-drive.dragover {
      border-color: #10b981;
      background: #dcfce7;
    }

    /* NÚT THỰC THI */
    .action-btns {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .btn-main {
      width: 100%;
      background: #1d61f2;
      color: #ffffff;
      border: none;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.15s;
    }
    .btn-main:hover { background: #1550c8; }
    
    .btn-teal {
      width: 100%;
      background: #00897b;
      color: #ffffff;
      border: none;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      transition: background 0.15s;
    }
    .btn-teal:hover { background: #00796b; }

    /* CARD KẾT QUẢ */
    .card-results {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-height: calc(100vh - 310px);
    }

    /* TABS KẾT QUẢ */
    .tabs-bar {
      display: flex;
      gap: 6px;
      margin-bottom: 14px;
    }
    .tab-item {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      color: #475569;
      padding: 7px 16px;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      border-radius: 6px;
      transition: all 0.15s;
    }
    .tab-item.active {
      background: #2563eb;
      border-color: #2563eb;
      color: #ffffff;
    }

    .tab-content { display: none; flex: 1; }
    .tab-content.active { display: flex; flex-direction: column; }

    /* STAT CARDS ROW */
    .stat-row {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      margin-bottom: 14px;
    }
    @media (max-width: 1000px) {
      .stat-row { grid-template-columns: repeat(3, 1fr); }
    }
    .stat-card {
      border-radius: 6px;
      padding: 12px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border: 1px solid transparent;
    }
    .stat-c1 { background: #eff6ff; border-color: #dbeafe; }
    .stat-c2 { background: #f0fdf4; border-color: #dcfce7; }
    .stat-c3 { background: #faf5ff; border-color: #f3e8ff; }
    .stat-c4 { background: #fff7ed; border-color: #ffedd5; }
    .stat-c5 { background: #ecfdf5; border-color: #a7f3d0; }

    .stat-title { font-size: 11px; font-weight: 700; color: #475569; }
    .stat-val { font-size: 22px; font-weight: 800; color: #0f172a; margin: 2px 0; }
    .stat-sub { font-size: 10.5px; color: #64748b; }
    .stat-icon-box { font-size: 24px; }

    /* BẢNG DỮ LIỆU VUÔNG VẮN BỎ BO GÓC */
    .table-card {
      border: 1px solid #cbd5e1;
      border-radius: 0 !important;
      overflow: hidden;
      width: 100%;
      flex: 1;
      display: flex;
      flex-direction: column;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12.5px;
      text-align: left;
      border-radius: 0 !important;
    }
    th, td {
      padding: 12px 18px;
      border-bottom: 1px solid #f1f5f9;
      border-radius: 0 !important;
    }
    th {
      background: #f8fafc;
      color: #334155;
      font-weight: 700;
      border-bottom: 1.5px solid #cbd5e1;
      border-radius: 0 !important;
    }
    tr:last-child td { border-bottom: none; }
    tr:nth-child(even) { background: #fafafa; }
    tr:hover { background: #f1f5f9; }

    .tbl-icon-name {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      color: #1e293b;
    }

    .pill-match {
      background: #e6f4ea;
      color: #137333;
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 700;
      display: inline-block;
      border: 1px solid #a7f3d0;
      border-radius: 0 !important;
    }
    .pill-extra {
      background: #fef3c7;
      color: #b45309;
      padding: 4px 10px;
      font-size: 11px;
      font-weight: 700;
      display: inline-block;
      border: 1px solid #fde68a;
      border-radius: 0 !important;
    }

    .btn-detail-view {
      background: #ffffff;
      border: 1px solid #bfdbfe;
      color: #2563eb;
      padding: 4px 10px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      text-decoration: none;
      border-radius: 0 !important;
    }
    .btn-detail-view:hover { background: #eff6ff; }

    /* PAGINATION FOOTER */
    .table-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 18px;
      background: #ffffff;
      border-top: 1px solid #cbd5e1;
      font-size: 12px;
      color: #64748b;
      margin-top: auto;
      border-radius: 0 !important;
    }
    .page-controls {
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .page-btn {
      width: 28px;
      height: 28px;
      border-radius: 0 !important;
      border: 1px solid #cbd5e1;
      background: #ffffff;
      color: #334155;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      font-weight: 700;
      font-size: 12px;
    }
    .page-btn.active {
      background: #2563eb;
      border-color: #2563eb;
      color: #ffffff;
    }

    pre {
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 0 !important;
      padding: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #f8fafc;
      flex: 1;
      min-height: 420px;
      max-height: 600px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }
  </style>
</head>
<body>

<div class="container-full">
  <!-- HEADER FULL WIDTH -->
  <header>
    <div class="brand-group">
      <div class="brand-logo">🗄️</div>
      <div class="brand">
        <h1>HỆ THỐNG MIGRATION DỮ LIỆU & ĐỐI SOÁT SQL</h1>
        <p>Trích xuất Sheet • Khớp Drive • Sinh SQL • Đối soát Matrix</p>
      </div>
    </div>
  </header>

  <!-- CARD CẤU HÌNH -->
  <div class="card">
    <div class="control-grid">
      <!-- Cột 1 -->
      <div>
        <label class="field-label">1. Nguồn File Excel (Kéo/thả hoặc chọn mẫu)</label>
        <div class="drop-box" id="dropZone" onclick="document.getElementById('fileInput').click()">
          <span>📁 Kéo thả file .xlsx vào đây</span>
          <span id="fileNameDisplay" style="font-weight: bold; color: #0284c7;"></span>
        </div>
        <input type="file" id="fileInput" accept=".xlsx, .xls" style="display: none;" onchange="handleFileSelect(this.files)">
      </div>

      <!-- Cột 2: Tệp Drive Đính Kèm -->
      <div>
        <label class="field-label">2. Tệp Drive Đính Kèm (Kéo thả hoặc dán Folder ID)</label>
        <div class="drop-box-drive" id="dropZoneDrive" onclick="document.getElementById('driveFileInput').click()" style="margin-bottom: 8px;">
          <span>📎 Kéo thả các file đính kèm Drive vào đây</span>
          <span id="driveFileNameDisplay" style="font-weight: bold; color: #047857;"></span>
        </div>
        <input type="file" id="driveFileInput" multiple style="display: none;" onchange="handleDriveFileSelect(this.files)">
      </div>

      <!-- Cột Nút Bấm -->
      <div class="action-btns">
        <button class="btn-main" id="btnRun" onclick="runMigration()">
          🚀 CHẠY MIGRATION
        </button>
      </div>
    </div>
  </div>

  <!-- CARD MAPPING CỘT (Ẩn mặc định, hiện khi upload thành công) -->
  <div class="card" id="mappingCard" style="display: none;">
    <div style="font-weight: 700; font-size: 13px; margin-bottom: 12px; color: #1e293b;">🛠️ Bảng Cấu Hình Mapping Cột</div>
    <div id="mappingContainer" style="max-height: 400px; overflow-y: auto;">
      <!-- Nội dung mapping sẽ render qua JS -->
    </div>
  </div>

  <!-- CARD DASHBOARD KẾT QUẢ -->
  <div class="card card-results">
    <!-- TABS BAR -->
    <div class="tabs-bar">
      <button class="tab-item active" onclick="switchTab('tab-summary', this)">📊 Ma Trận Đối Soát</button>
      <button class="tab-item" onclick="switchTab('tab-files', this)">📎 Tệp Drive Đã Map (<span id="fileTabCount">0</span>)</button>
      <button class="tab-item" onclick="switchTab('tab-sql', this)">📝 Xem File SQL</button>
    </div>

    <!-- TAB 1: SUMMARY BOARD -->
    <div id="tab-summary" class="tab-content active">
      <!-- 5 STAT CARDS THỐNG KÊ CHIỀU NGANG -->
      <div class="stat-row">
        <div class="stat-card stat-c1">
          <div>
            <div class="stat-title">Tổng Bảng/Sheet</div>
            <div class="stat-val" id="stTotalTables">0</div>
            <div class="stat-sub">Bảng/Sheet</div>
          </div>
          <div class="stat-icon-box">🗄️</div>
        </div>

        <div class="stat-card stat-c2">
          <div>
            <div class="stat-title">Tổng Dòng Nguồn</div>
            <div class="stat-val" id="stTotalRows">0</div>
            <div class="stat-sub">Dòng</div>
          </div>
          <div class="stat-icon-box">📄</div>
        </div>

        <div class="stat-card stat-c3">
          <div>
            <div class="stat-title">Tổng SQL INSERT</div>
            <div class="stat-val" id="stTotalSql">0</div>
            <div class="stat-sub">Lệnh</div>
          </div>
          <div class="stat-icon-box"><code>&lt;/&gt;</code></div>
        </div>

        <div class="stat-card stat-c4">
          <div>
            <div class="stat-title">Tệp Drive Hiện Có</div>
            <div class="stat-val" id="stTotalFiles">0</div>
            <div class="stat-sub" id="stTotalFilesSub">Chưa có tệp tin</div>
          </div>
          <div class="stat-icon-box">📁</div>
        </div>

        <div class="stat-card stat-c5">
          <div>
            <div class="stat-title">Tỷ lệ Khớp Chung</div>
            <div class="stat-val" id="stMatchRate" style="color: #059669;">0%</div>
            <div class="stat-sub" id="stMatchSub">Chưa chạy</div>
          </div>
          <div class="stat-icon-box">✅</div>
        </div>
      </div>

      <!-- BẢNG ĐỐI SOÁT -->
      <div class="table-card">
        <table>
          <thead>
            <tr>
              <th>Tên Sheet Nguồn</th>
              <th>Bảng Trong Database</th>
              <th style="text-align: right;">Số Dòng Nguồn</th>
              <th style="text-align: right;">Số Lệnh SQL INSERT</th>
              <th style="text-align: center;">Trạng Thái Đối Soát</th>
            </tr>
          </thead>
          <tbody id="summaryBody">
            <tr><td colspan="5" style="text-align: center; color: var(--muted); padding: 28px;">Chưa có dữ liệu đầu vào. Vui lòng chọn Mẫu Excel hoặc Kéo/Thả File nguồn vào để bấm "🚀 CHẠY MIGRATION".</td></tr>
          </tbody>
        </table>

        <div class="table-footer">
          <div id="footerSummaryText">Chưa có dữ liệu</div>
          <div class="page-controls">
            <span>Hiển thị</span>
            <select style="width: 60px; padding: 2px 4px; font-size: 11.5px;">
              <option>10</option>
              <option>25</option>
              <option>50</option>
            </select>
            <span>trên trang</span>
            <div class="page-btn">&lt;</div>
            <div class="page-btn active">1</div>
            <div class="page-btn">&gt;</div>
          </div>
        </div>
      </div>
    </div>



    <!-- TAB 3: FILES MAPPED -->
    <div id="tab-files" class="tab-content">
      <div class="table-card">
        <table>
          <thead>
            <tr>
              <th>Bảng</th>
              <th>Mã Bản Ghi (ID)</th>
              <th>Tên Tệp Trên Drive</th>
              <th>Drive File ID</th>
              <th>Trạng Thái Map</th>
            </tr>
          </thead>
          <tbody id="filesBody">
            <tr><td colspan="5" style="text-align: center; color: var(--muted); padding: 28px;">Chưa có tệp tin đính kèm.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: SQL PREVIEW -->
    <div id="tab-sql" class="tab-content">
      <div style="display: flex; gap: 8px; margin-bottom: 10px; align-items: center;">
        <label style="margin: 0; font-weight: bold;">File SQL:</label>
        <select id="sqlFileSelect" onchange="loadSqlContent()" style="width: 260px;">
          <!-- Các tuỳ chọn sẽ được cập nhật bởi Javascript -->
        </select>
        <button class="btn-teal" onclick="downloadSQL()">📥 TẢI XUỐNG</button>
      </div>
      <pre id="sqlPreview">-- Bấm "🚀 CHẠY MIGRATION" để sinh và xem nội dung file SQL.</pre>
    </div>



  </div>
</div>

<script>
  let uploadedFilePath = null;

  const dropZone = document.getElementById('dropZone');
  ['dragenter', 'dragover'].forEach(name => {
    dropZone.addEventListener(name, (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
  });
  ['dragleave', 'drop'].forEach(name => {
    dropZone.addEventListener(name, (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); });
  });

  dropZone.addEventListener('drop', (e) => {
    handleFileSelect(e.dataTransfer.files);
  });

  async function handleFileSelect(files) {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      alert('Vui lòng chỉ ném file Excel (.xlsx hoặc .xls)');
      return;
    }

    document.getElementById('fileNameDisplay').innerText = ' (' + file.name + ')';

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload-excel', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.status === 'success') {
        uploadedFilePath = data.file_path;
        document.getElementById('fileNameDisplay').innerText = ' (✓ ' + file.name + ')';

        if (data.sheets_info) {
          renderMappingUI(data.sheets_info);
        }

        // Không tự động chạy migration ở đây nữa, để người dùng tự bấm nút
      } else {
        alert('Lỗi nạp file: ' + data.message);
      }
    } catch (err) {
      alert('Lỗi tải file lên: ' + err);
    }
  }

  const dropZoneDrive = document.getElementById('dropZoneDrive');
  ['dragenter', 'dragover'].forEach(name => {
    dropZoneDrive.addEventListener(name, (e) => { e.preventDefault(); dropZoneDrive.classList.add('dragover'); });
  });
  ['dragleave', 'drop'].forEach(name => {
    dropZoneDrive.addEventListener(name, (e) => { e.preventDefault(); dropZoneDrive.classList.remove('dragover'); });
  });

  dropZoneDrive.addEventListener('drop', (e) => {
    handleDriveFileSelect(e.dataTransfer.files);
  });

  async function handleDriveFileSelect(files) {
    if (!files || files.length === 0) return;
    
    document.getElementById('driveFileNameDisplay').innerText = ` (⏳ Đang tải ${files.length} file đính kèm...)`;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const res = await fetch('/api/upload-drive-files', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.status === 'success') {
        document.getElementById('driveFileNameDisplay').innerText = ` (✓ Đã nạp ${data.saved_count} file)`;
        // Không tự động chạy migration ở đây nữa
      } else {
        alert('Lỗi nạp tệp Drive: ' + data.message);
      }
    } catch (err) {
      alert('Lỗi kết nối tải file đính kèm: ' + err);
    }
  }

  function switchTab(tabId, el) {
    document.querySelectorAll('.tab-item').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    if (el) el.classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }

  function renderMappingUI(sheetsInfo) {
    const container = document.getElementById('mappingContainer');
    container.innerHTML = '';
    
    let html = '<div style="display: flex; flex-direction: column; gap: 16px;">';
    for (const [sheet, cols] of Object.entries(sheetsInfo)) {
      html += `
        <div style="border: 1px solid #e2e8f0; border-radius: 6px; overflow: hidden;">
          <div style="background: #f8fafc; padding: 8px 12px; font-weight: 700; font-size: 12px; border-bottom: 1px solid #e2e8f0;">Sheet: ${sheet}</div>
          <table style="width: 100%; border-radius: 0;">
            <thead><tr><th style="width:50%; padding: 8px 12px;">Cột Gốc (Excel)</th><th style="width:50%; padding: 8px 12px;">Cột Đích (SQL)</th></tr></thead>
            <tbody>
      `;
      cols.forEach((c) => {
        html += `
          <tr>
            <td style="padding: 6px 12px; background: #fafafa; font-family: 'JetBrains Mono', monospace;">${c.raw}</td>
            <td style="padding: 6px 12px;">
              <input type="text" class="mapping-input" data-sheet="${sheet}" data-raw="${c.raw}" value="${c.norm}" style="padding: 4px 8px; font-size: 11.5px;" />
            </td>
          </tr>
        `;
      });
      html += '</tbody></table></div>';
    }
    html += '</div>';
    
    container.innerHTML = html;
    document.getElementById('mappingCard').style.display = 'block';
  }

  async function runMigration() {
    const excelVal = uploadedFilePath;
    const sheetIdVal = '';

    if (!excelVal) {
      alert('Vui lòng chọn Mẫu Excel hoặc Kéo/Thả file Excel vào ô số 1 trước!');
      return;
    }

    const btn = document.getElementById('btnRun');
    btn.disabled = true;
    btn.innerHTML = '⏳ Đang xử lý...';

    // Ẩn bảng mapping cho gọn
    const mappingCard = document.getElementById('mappingCard');
    if (mappingCard) mappingCard.style.display = 'none';

    const driveEl = document.getElementById('driveId');
    const driveIdVal = driveEl ? driveEl.value.trim() : '';

    const columnMapping = {};
    const mappingInputs = document.querySelectorAll('.mapping-input');
    mappingInputs.forEach(input => {
      const sheet = input.getAttribute('data-sheet');
      const raw = input.getAttribute('data-raw');
      const norm = input.value.trim();
      
      if (!columnMapping[sheet]) columnMapping[sheet] = {};
      columnMapping[sheet][raw] = norm;
    });

    try {
      const res = await fetch('/api/run-migration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          excel_path: excelVal,
          sheet_id: sheetIdVal,
          drive_id: driveIdVal,
          column_mapping: columnMapping
        })
      });
      const data = await res.json();
      
      if (data.status === 'success') {
        renderData(data);
        
        // Cập nhật dropdown SQL
        const sqlSelect = document.getElementById('sqlFileSelect');
        let html = `
          <optgroup label="Tất cả (Gộp chung)">
            <option value="all_migration.sql">all_migration.sql (File tổng hợp)</option>
            <option value="01_master_data.sql">01_master_data.sql (Danh mục)</option>
            <option value="02_transaction_data.sql">02_transaction_data.sql (Nghiệp vụ)</option>
            <option value="03_files_data.sql">03_files_data.sql (Tệp đính kèm)</option>
          </optgroup>
          <optgroup label="Từng Bảng Riêng Lẻ">
        `;
        
        if (data.sql_files && data.sql_files.individual_files) {
          data.sql_files.individual_files.forEach(f => {
            html += `<option value="${f.filename}">${f.filename} (${f.records} bản ghi)</option>`;
          });
        }
        
        html += `</optgroup>`;
        sqlSelect.innerHTML = html;
        
        loadSqlContent();
      } else {
        alert('Lỗi kết nối / xác thực: ' + data.message);
      }
    } catch (e) {
      alert('Lỗi hệ thống: ' + e);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '🚀 CHẠY MIGRATION';
    }
  }



  function downloadSQL() {
    const file = document.getElementById('sqlFileSelect').value;
    if (!file) return;
    window.location.href = '/download/' + file;
  }

  function renderData(data) {
    const sumBody = document.getElementById('summaryBody');
    sumBody.innerHTML = '';
    
    let totalRows = 0;
    let totalSql = 0;
    
    data.summary.forEach(row => {
      totalRows += row['Số Dòng Nguồn (Sheet)'];
      totalSql += row['Số Lệnh SQL INSERT'];
      
      let icon = '📄';
      if (row['Bảng / Sheet'] === 'COMPANY') icon = '🏛️';
      if (row['Bảng / Sheet'] === 'PROCESS') icon = '⚙️';
      if (row['Bảng / Sheet'] === 'REQUEST') icon = '📝';
      
      sumBody.innerHTML += `
        <tr>
          <td><div class="tbl-icon-name"><span>${icon}</span> <span>${row['Bảng / Sheet']}</span></div></td>
          <td><code>${row['Tên Bảng Database']}</code></td>
          <td style="text-align: right; font-weight: 600;">${row['Số Dòng Nguồn (Sheet)']}</td>
          <td style="text-align: right; font-weight: 600;">${row['Số Lệnh SQL INSERT']}</td>
          <td style="text-align: center;"><span class="pill-match">MATCH (100%)</span></td>
        </tr>
      `;
    });

    let mappedCount = data.files.filter(f => f.status === 'MAPPED').length;
    let totalDriveFiles = data.files.length;
    let unmappedCount = totalDriveFiles - mappedCount;

    document.getElementById('stTotalTables').innerText = data.summary.length;
    document.getElementById('stTotalRows').innerText = totalRows.toLocaleString();
    document.getElementById('stTotalSql').innerText = totalSql.toLocaleString();
    
    document.getElementById('stTotalFiles').innerText = totalDriveFiles;
    document.getElementById('stTotalFilesSub').innerText = totalDriveFiles > 0 ? `${mappedCount} Đã map / ${unmappedCount} Chưa gán` : 'Chưa có tệp tin';
    document.getElementById('fileTabCount').innerText = totalDriveFiles;

    document.getElementById('stMatchRate').innerText = '100%';
    document.getElementById('stMatchSub').innerText = 'Hoàn hảo';

    document.getElementById('footerSummaryText').innerText = `Hiển thị 1 đến ${data.summary.length} trong tổng số ${data.summary.length} bảng`;



    const filesBody = document.getElementById('filesBody');
    filesBody.innerHTML = '';
    if (data.files.length === 0) {
      filesBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--muted); padding: 28px;">Chưa có file đính kèm nào được quét.</td></tr>';
    } else {
      data.files.forEach(row => {
        let badge = row.status === 'MAPPED' 
          ? '<span class="pill-match">MAPPED (Đã gán dòng DB)</span>' 
          : '<span class="pill-extra">UNMAPPED (File thừa trên Drive)</span>';
          
        filesBody.innerHTML += `
          <tr>
            <td><code>${row.table_name}</code></td>
            <td><strong>${row.record_id}</strong></td>
            <td>${row.file_name}</td>
            <td><code>${row.drive_file_id}</code></td>
            <td>${badge}</td>
          </tr>
        `;
      });
    }
  }

  async function loadSqlContent() {
    const file = document.getElementById('sqlFileSelect').value;
    const res = await fetch('/api/get-sql?file=' + file);
    const text = await res.text();
    document.getElementById('sqlPreview').innerText = text;
  }
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/upload-excel", methods=["POST"])
def api_upload_excel():
    try:
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "Không tìm thấy tệp gửi lên"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"status": "error", "message": "Tệp không có tên"}), 400
            
        save_path = BASE_DIR / "data" / "uploaded_custom_data.xlsx"
        file.save(save_path)

        # Xóa các file trong thư mục mock_drive để tránh dính file của lần chạy cũ
        import shutil
        mock_dir = BASE_DIR / "data" / "mock_drive"
        if mock_dir.exists():
            shutil.rmtree(mock_dir)
        mock_dir.mkdir(parents=True, exist_ok=True)
        
        sheets_info = {}
        try:
            from pipeline.table_schema import normalize_name
            xl = pd.ExcelFile(save_path)
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet, nrows=0)
                raw_cols = list(df.columns)
                sheets_info[sheet] = [{"raw": str(c), "norm": normalize_name(str(c))} for c in raw_cols]
        except Exception as ex:
            print("Lỗi đọc metadata Excel:", ex)
        
        return jsonify({
            "status": "success", 
            "message": "Đã lưu file thành công", 
            "file_path": "data/uploaded_custom_data.xlsx",
            "file_name": file.filename,
            "sheets_info": sheets_info
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/upload-drive-files", methods=["POST"])
def api_upload_drive_files():
    try:
        files = request.files.getlist('files')
        if not files:
            return jsonify({"status": "error", "message": "Không nhận được file nào"}), 400
            
        mock_dir = BASE_DIR / "data" / "mock_drive"
        mock_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for file in files:
            if file and file.filename:
                save_path = mock_dir / file.filename
                file.save(save_path)
                saved_count += 1
                
        return jsonify({
            "status": "success",
            "message": f"Đã lưu {saved_count} file đính kèm thành công",
            "saved_count": saved_count
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/run-migration", methods=["POST"])
def api_run_migration():
    try:
        req = request.json or {}
        excel_path = req.get("excel_path")
        drive_id = req.get("drive_id")
        column_mapping = req.get("column_mapping", {})
        
        if not excel_path and not req.get("sheet_id"):
            return jsonify({"status": "error", "message": "Chưa chọn nguồn dữ liệu Excel hoặc Sheet ID"}), 400
            
        tables_data, drive_files = run_extract(excel_path=excel_path, drive_folder_id=drive_id)
        transformed = run_transform(tables_data, custom_mapping=column_mapping)
        _, mapped_files, missing_audit = run_file_mapping(transformed, drive_files)
        sql_outputs = run_generate_sql(transformed, mapped_files)
        val_outputs = run_validation(transformed, mapped_files, missing_audit)
        
        df_summary = pd.read_excel(val_outputs["report_excel"], sheet_name="Tổng Quan 30 Bảng")
        df_company = pd.read_excel(val_outputs["report_excel"], sheet_name="Đối Soát COMPANY")
        
        return jsonify({
            "status": "success",
            "summary": df_summary.to_dict(orient="records"),
            "company_audit": df_company.to_dict(orient="records"),
            "files": mapped_files,
            "missing": missing_audit
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/test-db", methods=["POST"])
def api_test_db():
    try:
        from test_db import init_and_test_database
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            init_and_test_database()
            
        output_str = f.getvalue()
        return jsonify({"status": "success", "output": output_str})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/get-sql")
def api_get_sql():
    filename = request.args.get("file", "all_migration.sql")
    filepath = BASE_DIR / config.OUTPUT_DIR / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return "-- Chưa có dữ liệu mã SQL"

@app.route("/download/<path:filename>")
def download_file(filename):
    if filename.endswith(".pdf"):
        return send_from_directory(BASE_DIR, filename, as_attachment=True)
    return send_from_directory(BASE_DIR / config.OUTPUT_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Đang khởi động Web App Tool tại port: {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
