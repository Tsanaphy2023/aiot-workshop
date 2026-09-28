import json
import os

with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/cmu_pretest_40.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

questions = raw_data["data"]["questions"]

# Module mapping helper
module_map = {
    range(1, 6): "โมดูล 1: วิทยาการเกษตรดิจิทัลและการตรวจวัดสภาพแวดล้อม",
    range(6, 16): "โมดูล 3: ชลศาสตร์และการจัดการน้ำอัตโนมัติในฟาร์ม",
    range(16, 26): "โมดูล 4: เครือข่ายการสื่อสาร LoRa และ ESP-NOW",
    range(26, 31): "โมดูล 6: ปัญญาประดิษฐ์ตรวจจับวัตถุและจำแนกพืชผล",
    range(31, 41): "โมดูล 5 & 7: การประมวลผลภาพดิจิทัลและ TinyML สมองกลฝังตัว"
}

def get_module_title(q_num):
    for r, title in module_map.items():
        if q_num in r:
            return title
    return "แบบทดสอบวัดผลการเรียนรู้"

html_content = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <title>แบบทดสอบก่อนเรียน (Master Pre-test 40 ข้อ) - หลักสูตร AIoT & เกษตรดิจิทัล</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Prompt:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    @page {
      size: A4 portrait;
      margin: 12mm 14mm 12mm 14mm;
    }
    * {
      box-sizing: border-box;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }
    body {
      font-family: 'Sarabun', sans-serif;
      font-size: 11pt;
      line-height: 1.45;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }
    .no-print-bar {
      background: #0f172a;
      color: #ffffff;
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 1000;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .btn-print {
      background: #10b981;
      color: white;
      border: none;
      padding: 8px 18px;
      border-radius: 6px;
      font-family: 'Prompt', sans-serif;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
    }
    .btn-print:hover {
      background: #059669;
    }
    @media print {
      .no-print-bar {
        display: none !important;
      }
      body {
        font-size: 10pt;
        line-height: 1.35;
      }
      .page-break {
        page-break-before: always;
      }
    }
    .header-sheet {
      border-bottom: 2px solid #0284c7;
      padding-bottom: 8px;
      margin-bottom: 12px;
    }
    .org-title {
      font-family: 'Prompt', sans-serif;
      font-size: 14pt;
      font-weight: 700;
      color: #0369a1;
      text-align: center;
      margin: 0;
    }
    .sub-org {
      font-size: 10.5pt;
      color: #475569;
      text-align: center;
      margin: 2px 0 6px 0;
    }
    .exam-badge {
      display: inline-block;
      background: #e0f2fe;
      color: #0369a1;
      padding: 2px 10px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 10pt;
    }
    .student-info-box {
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 8px 12px;
      background: #f8fafc;
      margin-bottom: 12px;
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 8px;
      font-size: 10pt;
    }
    .info-line {
      border-bottom: 1px dotted #94a3b8;
      display: inline-block;
      min-width: 100px;
    }
    .instructions {
      font-size: 9.5pt;
      color: #475569;
      margin-bottom: 12px;
      background: #fffbeb;
      border-left: 3px solid #f59e0b;
      padding: 6px 10px;
    }
    .module-banner {
      background: #f1f5f9;
      border-left: 3px solid #0284c7;
      padding: 3px 8px;
      font-family: 'Prompt', sans-serif;
      font-size: 10.5pt;
      font-weight: 600;
      color: #0f172a;
      margin: 12px 0 8px 0;
    }
    .question-block {
      margin-bottom: 10px;
      break-inside: avoid;
    }
    .q-text {
      font-weight: 600;
      color: #0f172a;
      margin-bottom: 3px;
    }
    .choices-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 3px 14px;
      padding-left: 14px;
    }
    .choice-item {
      display: flex;
      align-items: baseline;
      gap: 6px;
      font-size: 10pt;
    }
    .choice-bullet {
      display: inline-block;
      width: 14px;
      height: 14px;
      border: 1px solid #64748b;
      border-radius: 50%;
      text-align: center;
      line-height: 12px;
      font-size: 7.5pt;
      color: #475569;
      flex-shrink: 0;
    }
    .answer-key-section {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 12px;
      margin-top: 18px;
    }
    .key-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 9pt;
    }
    .key-table th, .key-table td {
      border: 1px solid #cbd5e1;
      padding: 4px 6px;
      text-align: left;
    }
    .key-table th {
      background: #0284c7;
      color: white;
      text-align: center;
    }
    .key-badge {
      font-weight: 600;
      color: #047857;
    }
  </style>
</head>
<body>

  <div class="no-print-bar">
    <div style="font-family:'Prompt',sans-serif; font-size:14px; font-weight:600;">
      📘 ใบงานแบบทดสอบก่อนเรียน (Master Pre-test 40 ข้อ) - LEQs AIoT
    </div>
    <div style="display:flex; gap:10px;">
      <a href="./worksheet_pretest_40.pdf" download class="btn-print" style="background:#0284c7;">
        📥 ดาวน์โหลด PDF
      </a>
      <button class="btn-print" onclick="window.print()">
        🖨️ สั่งพิมพ์เอกสาร (Print / Save as PDF)
      </button>
    </div>
  </div>

  <div style="max-width: 210mm; margin: 0 auto; padding: 15px 20px;">
    
    <!-- HEADER -->
    <div class="header-sheet">
      <div style="text-align:center; margin-bottom:2px;">
        <span class="exam-badge">แบบทดสอบวัดความรู้พื้นฐานก่อนเรียน (Pre-test Assessment)</span>
      </div>
      <h1 class="org-title">หลักสูตรเกษตรดิจิทัลและปัญญาประดิษฐ์ฝังตัว (AIoT & Digital Agriculture)</h1>
      <p class="sub-org">คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี ร่วมกับ มหาวิทยาลัยเชียงใหม่ (CMU Lifelong)</p>
    </div>

    <!-- STUDENT INFO BOX -->
    <div class="student-info-box">
      <div><b>ชื่อ-นามสกุล:</b> <span class="info-line" style="min-width:180px;"></span></div>
      <div><b>เลขที่ / กลุ่ม:</b> <span class="info-line" style="min-width:60px;"></span></div>
      <div><b>คะแนนที่ได้:</b> <span class="info-line" style="min-width:60px;"></span> / 40</div>
      <div><b>สถานศึกษา / หน่วยงาน:</b> <span class="info-line" style="min-width:180px;"></span></div>
      <div><b>วันที่สอบ:</b> <span class="info-line" style="min-width:90px;"></span></div>
      <div><b>ผลการประเมิน:</b> [ &nbsp; ] ผ่าน [ &nbsp; ] ปรับปรุง</div>
    </div>

    <!-- INSTRUCTIONS -->
    <div class="instructions">
      <b>📌 คำชี้แจง:</b> แบบทดสอบมีทั้งหมด 40 ข้อ (ข้อละ 1 คะแนน รวม 40 คะแนน) ให้ผู้เรียนอ่านโจทย์และเลือกกากบาท (X) หรือระบายคำตอบที่ถูกต้องที่สุดเพียงข้อเดียวลงในช่องตัวเลือก
    </div>
"""

current_mod = ""
choice_letters = ["ก", "ข", "ค", "ง"]

for i, q in enumerate(questions, 1):
    mod_title = get_module_title(i)
    if mod_title != current_mod:
        current_mod = mod_title
        html_content += f"""
    <div class="module-banner">📖 {current_mod}</div>
"""
    q_name = q.get("exam_name_th", "").strip()
    choices = q.get("exam_choice", [])
    
    html_content += f"""
    <div class="question-block">
      <div class="q-text">ข้อ {i}. {q_name}</div>
      <div class="choices-grid">
"""
    for ch_idx, ch in enumerate(choices):
        letter = choice_letters[ch_idx] if ch_idx < len(choice_letters) else str(ch_idx+1)
        ch_text = ch.get("choice_name_th", "").strip()
        html_content += f"""        <div class="choice-item">
          <span class="choice-bullet">{letter}</span>
          <span>{ch_text}</span>
        </div>
"""
    html_content += """      </div>
    </div>
"""

# Append Answer Key Sheet
html_content += """
    <div class="page-break"></div>

    <div class="header-sheet" style="margin-top:16px;">
      <h2 class="org-title" style="font-size:13pt;">📋 กระดาษคำตอบและตารางสรุปเฉลยแบบทดสอบ (Master Key 40 ข้อ)</h2>
      <p class="sub-org">สำหรับคณะกรรมการผู้ตรวจข้อสอบและวิทยากรประจำกลุ่ม</p>
    </div>

    <div class="answer-key-section">
      <table class="key-table">
        <thead>
          <tr>
            <th style="width:6%;">ข้อ</th>
            <th style="width:28%;">หัวข้อข้อสอบ</th>
            <th style="width:48%;">คำตอบที่ถูกต้อง</th>
            <th style="width:18%;">โมดูล</th>
          </tr>
        </thead>
        <tbody>
"""

key_summary = [
  (1, "สมการพันธุกรรม P=G+E+(G×E)", "ปฏิสัมพันธ์ระหว่างพันธุกรรมกับสิ่งแวดล้อม", "Module 1"),
  (2, "อุปกรณ์วัดปริมาณรังสีดวงอาทิตย์", "Pyranometer", "Module 1"),
  (3, "ข้อดีเด่นของ Ultrasonic Anemometer", "ไม่มีชิ้นส่วนที่เคลื่อนที่ทำให้ลดปัญหาการสึกหรอ", "Module 1"),
  (4, "ความชื้นสัมพัทธ์สัมพันธ์กับการระเหยน้ำ", "ค่าแรงดึงระเหยน้ำของอากาศ (VPD)", "Module 1"),
  (5, "ก๊าซสำคัญต่อการหายใจของรากพืช", "ก๊าซออกซิเจน (O₂)", "Module 1"),
  (6, "เหตุผลที่ฟาร์มใหญ่ต้องใช้ระบบน้ำอัตโนมัติ", "ช่วยบริหารจัดการแปลงขนาดใหญ่ได้อย่างแม่นยำและลดแรงงานคน", "Module 3"),
  (7, "สูตรคำนวณอัตราการไหล Q = (A × ETc)/(T × Eff)", "ปริมาณการใช้น้ำของพืช (Crop Evapotranspiration)", "Module 3"),
  (8, "ความเร็วของน้ำในท่อเมนและท่อย่อยที่เหมาะสม", "1.5 - 2.0 เมตรต่อวินาที (หรือ 1.0 - 2.0 m/s)", "Module 3"),
  (9, "น้ำไหลในท่อเร็วกว่า 2.5 m/s", "แรงดันสูญเสียสูง และเสี่ยงต่อการเกิด Water Hammer ท่อแตก", "Module 3"),
  (10, "เฮดรวมของระบบ (TDH)", "TDH = Hs + hf + hm + Hop", "Module 3"),
  (11, "สายไฟร้อยท่อฝังดินไปปั๊มน้ำ", "สาย NYY (หรือ NYY-G)", "Module 3"),
  (12, "การติดตั้งแผงโซลาร์เซลล์ในไทย", "หันหน้าทางทิศใต้ ทำมุมเอียงประมาณ 10 - 15 องศา", "Module 3"),
  (13, "ข้อได้เปรียบแผง Polycrystalline", "มีราคาถูกกว่าและคุ้มค่าต่อการลงทุนเริ่มต้น", "Module 3"),
  (14, "ปุ่มปรับ CV บนบอร์ดแปลงไฟ XL4015", "แรงดันไฟฟ้าสูงสุดที่จ่ายออกไปชาร์จแบตเตอรี่ (Output Voltage)", "Module 3"),
  (15, "ปุ่มปรับ CC บนบอร์ดแปลงไฟ XL4015", "จำกัดกระแสชาร์จสูงสุดเพื่อความปลอดภัยของแบตเตอรี่", "Module 3"),
  (16, "LoRa ออกแบบเพื่อรองรับงานประเภทใด", "งานส่งข้อมูลเซนเซอร์ระยะไกลที่ส่งเป็นครั้งคราว (Telemetry)", "Module 4"),
  (17, "ขนาด Payload ของ LoRa ต่อแพ็กเกต", "หลักสิบไบต์ ถึงประมาณไม่เกิน 200 - 250 ไบต์", "Module 4"),
  (18, "Duty Cycle สัญญาณ LoRa ตามกฎหมายไทย", "ไม่เกิน 1% (Time-on-Air ไม่เกิน 36 วินาที/ชั่วโมง)", "Module 4"),
  (19, "LoRaWAN vs Custom LoRa", "LoRaWAN ใช้ Gateway และ Server คลาวด์ ส่วน Custom LoRa คุมคลื่นตรง", "Module 4"),
  (20, "แนวทางเพิ่มระยะสื่อสารของ LoRa", "ต่อหัว u.fl ผ่านสายแปลงเป็น SMA เข้ากับสายอากาศเกนสูง", "Module 4"),
  (21, "บทบาทของ ESP-NOW ในระบบสองบอร์ด", "ส่งข้อมูลและรับคำสั่งระหว่างบอร์ดในสวนกับบอร์ดในบ้านโดยตรง", "Module 4"),
  (22, "หน้าที่ของบอร์ด 1 ที่ติดตั้งในสวน", "อ่านค่าเซนเซอร์แล้วส่งออก และรับคำสั่งมาสั่งเปิด-ปิดรีเลย์วาล์ว", "Module 4"),
  (23, "หน้าที่ของบอร์ด 2 ที่ติดตั้งในบ้าน", "เป็นสะพานเชื่อม รับค่าจากบอร์ดในสวนแล้วส่งขึ้นคลาวด์ผ่าน WiFi", "Module 4"),
  (24, "รูปแบบไฟล์ตั้งค่า ESPHome", "ไฟล์ YAML (.yaml)", "Module 4"),
  (25, "URL หน้าแดชบอร์ด Home Assistant", "http://homeassistant.local:8123", "Module 4"),
  (26, "Classification vs Object Detection", "Classification ทายภาพรวมทั้งภาพ ส่วน Object Detection ชี้พิกัดวัตถุได้", "Module 6"),
  (27, "เครื่องมือออนไลน์จัดการข้อมูลและวาดกรอบ Bounding Box", "Roboflow", "Module 6"),
  (28, "การตั้งชื่อ Class Name ให้ AI", "ใช้คำสั้น สื่อความหมาย และสะกดให้เหมือนกันทุกรูป เช่น healthy", "Module 6"),
  (29, "จำนวนรูปถ่ายขั้นต่ำต่อ 1 Class", "20 รูปถ่ายต่อ 1 Class (ขั้นต่ำ)", "Module 6"),
  (30, "ลักษณะการถ่ายภาพเตรียมสอน AI", "คละมุมมอง (บน/ข้าง/เอียง), คละสภาพแสง และมีฉากหลังสายพานจริง", "Module 6"),
  (31, "คอมพิวเตอร์มองเห็นภาพถ่ายดิจิทัลอย่างไร", "มองเห็นเป็น 'ตารางตัวเลข' (พิกเซล) ที่มีค่ากำกับในแต่ละช่อง", "Module 5"),
  (32, "สมองกลขนาดจิ๋ว Edge AI ไม่พึ่งพาเน็ต", "คอมพิวเตอร์บอร์ดเดี่ยว (Single Board Computer เช่น Raspberry Pi)", "Module 7"),
  (33, "เป้าหมายหลักของ Image Processing (Rule-based)", "สำหรับการวัดขนาด (S-M-L), นับพื้นที่ และคัดกรองรูปทรงพื้นฐานรวดเร็ว", "Module 7"),
  (34, "วิธีการทำงานของ AI ในการตรวจหารอยโรค", "เหมือนสอนงานพนักงานใหม่ โดยป้อนรูปตัวอย่างให้ AI จำแพทเทิร์นเอง", "Module 7"),
  (35, "สาเหตุที่ค่าสี RGB ผิดพลาดเมื่อเจอแสงเงา", "เพราะค่า RGB วัดสีรวมกับความสว่าง โดนเงาจะสับสนคิดว่าเป็นสีดำ", "Module 5"),
  (36, "คอมพิวเตอร์มองเห็นภาพถ่ายดิจิทัลอย่างไร", "มองเห็นเป็น 'ตารางตัวเลข' (พิกเซล) ที่มีค่ากำกับในแต่ละช่อง", "Module 5"),
  (37, "สมองกลขนาดจิ๋ว Edge AI ไม่พึ่งพาเน็ต", "คอมพิวเตอร์บอร์ดเดี่ยว (เช่น Raspberry Pi)", "Module 7"),
  (38, "เป้าหมายหลักของ Image Processing Rule-based", "สำหรับการวัดขนาด (S-M-L), นับพื้นที่ และคัดกรองรูปทรงพื้นฐานรวดเร็ว", "Module 7"),
  (39, "วิธีการทำงานของ AI ในการตรวจหารอยโรค", "เหมือนสอนงานพนักงานใหม่ โดยป้อนรูปตัวอย่างให้ AI จำแพทเทิร์นเอง", "Module 7"),
  (40, "สาเหตุที่ค่าสี RGB ผิดพลาดเมื่อเจอแสงเงา", "เพราะค่า RGB วัดสีรวมกับความสว่าง โดนเงาจะสับสนคิดว่าเป็นสีดำ", "Module 5")
]

for row in key_summary:
    html_content += f"""          <tr>
            <td style="text-align:center; font-weight:700;">{row[0]}</td>
            <td>{row[1]}</td>
            <td class="key-badge">✅ {row[2]}</td>
            <td style="text-align:center; color:#64748b;">{row[3]}</td>
          </tr>
"""

html_content += """        </tbody>
      </table>
    </div>

  </div>
</body>
</html>
"""

output_path = "/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/worksheet_pretest_40.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated {output_path} successfully!")
