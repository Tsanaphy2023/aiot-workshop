# -*- coding: utf-8 -*-
"""
Generator for Activity Guides (Activities 1, 2, 3, 4, 6, 7, 8, 9, 10, 11)
Matches the quality, styling, and structure of Activity 5 Guide.
"""

import os

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>คู่มือการจัดกิจกรรมเชิงปฏิบัติการ: กิจกรรมที่ {num} — {title_th} ({title_en}) | Smart Farm AIoT</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});</script>
  <style>
    :root {{
      --primary: {primary_color};
      --primary-dark: {primary_dark};
      --primary-light: {primary_light};
      --success: #16a34a;
      --success-light: #dcfce7;
      --warning: #d97706;
      --warning-light: #fef3c7;
      --danger: #dc2626;
      --danger-light: #fee2e2;
      --purple: #7c3aed;
      --purple-light: #f3e8ff;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --bg-page: #f8fafc;
      --bg-card: #ffffff;
      --border: #e2e8f0;
      --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
      --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
      --radius: 12px;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Sarabun', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-page);
      color: var(--text-main);
      line-height: 1.7;
      font-size: 16px;
      -webkit-font-smoothing: antialiased;
    }}
    .container {{
      max-width: 960px;
      margin: 0 auto;
      padding: 30px 20px 80px 20px;
    }}
    header {{
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 40%, var(--primary-dark) 100%);
      color: white;
      padding: 44px 32px;
      border-radius: var(--radius);
      box-shadow: var(--shadow-lg);
      margin-bottom: 28px;
      position: relative;
      overflow: hidden;
    }}
    header::after {{
      content: '{icon}';
      position: absolute;
      right: 24px;
      bottom: -15px;
      font-size: 130px;
      opacity: 0.18;
      pointer-events: none;
    }}
    .badge-header {{
      display: inline-block;
      background: rgba(255, 255, 255, 0.18);
      backdrop-filter: blur(8px);
      padding: 4px 14px;
      border-radius: 9999px;
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 12px;
      border: 1px solid rgba(255, 255, 255, 0.25);
    }}
    header h1 {{
      font-size: 26px;
      font-weight: 700;
      line-height: 1.35;
      margin-bottom: 8px;
    }}
    header p {{
      font-size: 16px;
      opacity: 0.9;
      max-width: 760px;
    }}
    .nav-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 24px;
      padding: 12px 18px;
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
    }}
    .nav-bar a {{
      color: var(--primary);
      text-decoration: none;
      font-size: 14px;
      font-weight: 500;
      padding: 4px 10px;
      border-radius: 6px;
      transition: background 0.15s;
    }}
    .nav-bar a:hover {{
      background: var(--primary-light);
    }}
    .card {{
      background: var(--bg-card);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      padding: 30px;
      margin-bottom: 24px;
      box-shadow: var(--shadow-sm);
    }}
    h2.section-title {{
      font-size: 21px;
      font-weight: 700;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid #f1f5f9;
    }}
    h3.sub-title {{
      font-size: 18px;
      font-weight: 600;
      color: #1e293b;
      margin: 22px 0 12px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .callout {{
      padding: 16px 20px;
      border-radius: 10px;
      margin: 18px 0;
      font-size: 15px;
      display: flex;
      gap: 14px;
      align-items: flex-start;
    }}
    .callout-icon {{ font-size: 22px; line-height: 1.4; flex-shrink: 0; }}
    .callout.important {{ background-color: var(--primary-light); border-left: 4px solid var(--primary); color: var(--primary-dark); }}
    .callout.warning {{ background-color: var(--warning-light); border-left: 4px solid var(--warning); color: #92400e; }}
    .callout.success {{ background-color: var(--success-light); border-left: 4px solid var(--success); color: #166534; }}
    .callout.danger {{ background-color: var(--danger-light); border-left: 4px solid var(--danger); color: #991b1b; }}
    table {{ width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14.5px; }}
    th, td {{ border: 1px solid var(--border); padding: 12px 14px; text-align: left; vertical-align: top; }}
    th {{ background: #f8fafc; font-weight: 600; color: #334155; }}
    tr:nth-child(even) td {{ background-color: #fafbfd; }}
    pre {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 18px;
      border-radius: 10px;
      overflow-x: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13.5px;
      line-height: 1.6;
      margin: 16px 0;
      position: relative;
    }}
    code {{ font-family: 'JetBrains Mono', monospace; font-size: 13.5px; }}
    .code-inline {{ background: #f1f5f9; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-weight: 500; }}
    .copy-btn {{
      position: absolute;
      top: 10px;
      right: 10px;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.25);
      color: white;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
      font-family: 'Sarabun', sans-serif;
    }}
    .copy-btn:hover {{ background: rgba(255, 255, 255, 0.3); }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 14.5px;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      border: none;
      transition: all 0.2s;
    }}
    .btn-primary {{ background: var(--primary); color: white; }}
    .btn-primary:hover {{ background: var(--primary-dark); }}
    .btn-outline {{ background: white; color: var(--primary); border: 1.5px solid var(--primary); }}
    .btn-outline:hover {{ background: var(--primary-light); }}
    .footer-nav {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      margin-top: 30px;
      flex-wrap: wrap;
    }}
    @media print {{
      body {{ background: white; color: black; font-size: 13px; }}
      .container {{ max-width: 100%; padding: 0; }}
      .card {{ border: 1px solid #ccc; box-shadow: none; page-break-inside: avoid; margin-bottom: 16px; padding: 16px; }}
      header {{ background: #1e293b !important; color: white !important; padding: 20px; page-break-after: avoid; }}
      .nav-bar, .copy-btn, .footer-nav {{ display: none !important; }}
      pre {{ background: #f8fafc !important; color: #0f172a !important; border: 1px solid #ccc; }}
    }}
  </style>
</head>
<body>

<div class="container">

  <header>
    <div class="badge-header">คู่มือมาตรฐานสำหรับวิทยากร ผู้ช่วยสอน (TA) และผู้เรียน</div>
    <h1>{icon} กิจกรรมที่ {num} — {title_th} ({title_en})</h1>
    <p>{header_desc}</p>
  </header>

  <div class="nav-bar">
    <a href="index.html">🏠 ศูนย์รวมคู่มือ (Master Hub)</a>
    <a href="#intro">1. บทนำและแนวคิด</a>
    <a href="#time-matrix">2. แผนการจัดเวลา</a>
    <a href="#hardware">3. อุปกรณ์และการเชื่อมต่อ</a>
    <a href="#steps">4. ขั้นตอนการทดลอง</a>
    <a href="#code">5. โค้ด/การตั้งค่า</a>
    <a href="#answers">6. เฉลยใบงาน</a>
    <a href="#troubleshooting">7. การแก้ปัญหา</a>
    <a href="#rubric">8. เกณฑ์การประเมิน</a>
  </div>

{content_html}

  <div class="card footer-nav">
    {prev_btn}
    <a href="index.html" class="btn btn-outline">🏠 กลับสู่ศูนย์รวมคู่มือ</a>
    {next_btn}
  </div>

</div>

<script>
function copyCode(btn) {{
  const pre = btn.parentElement;
  const code = pre.querySelector('code').innerText;
  navigator.clipboard.writeText(code).then(() => {{
    const originalText = btn.innerText;
    btn.innerText = '✓ คัดลอกแล้ว';
    setTimeout(() => {{ btn.innerText = originalText; }}, 2000);
  }});
}}
</script>

</body>
</html>
"""

print("HTML Template prepared.")
