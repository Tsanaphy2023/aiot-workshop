import json
import os
import subprocess

# 1. Load raw 45 questions
json_path = "/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/cmu_pretest_45.json"
with open(json_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

questions = raw["data"]["questions"]
print(f"Loaded {len(questions)} questions.")

# Verified Answer Indices (0-indexed)
# Q1: 0, Q2: 0, Q3: 3, Q4: 3, Q5: 3,
# Q6: 0, Q7: 1, Q8: 1, Q9: 2, Q10: 0,
# Q11: 1, Q12: 1, Q13: 2, Q14: 0, Q15: 1,
# Q16: 0, Q17: 0, Q18: 0, Q19: 2, Q20: 1,
# Q21: 1, Q22: 2, Q23: 0, Q24: 0, Q25: 2,
# Q26: 1, Q27: 1, Q28: 0, Q29: 2, Q30: 0,
# Q31: 1, Q32: 0, Q33: 1, Q34: 1, Q35: 1,
# Q36: 1, Q37: 0, Q38: 0, Q39: 1, Q40: 1,
# Q41: 2, Q42: 3, Q43: 1, Q44: 1, Q45: 2
correct_indices = [
    0, 0, 3, 3, 3,  # 1-5
    0, 1, 1, 2, 0,  # 6-10
    1, 1, 2, 0, 1,  # 11-15
    0, 0, 0, 2, 1,  # 16-20
    1, 2, 0, 0, 2,  # 21-25
    1, 1, 0, 2, 0,  # 26-30
    1, 0, 1, 1, 1,  # 31-35
    1, 0, 0, 1, 1,  # 36-40
    2, 3, 1, 1, 2   # 41-45
]

# 2. Build pretest_45_data.json for Web Portal
portal_data = []
for i, q in enumerate(questions):
    q_name = q.get("exam_name_th", "").strip()
    choices = [c.get("choice_name_th", "").strip() for c in q.get("exam_choice", [])]
    ans_idx = correct_indices[i]
    correct_text = choices[ans_idx] if ans_idx < len(choices) else choices[0]
    
    portal_data.append({
        "q": f"{i+1}. {q_name}",
        "options": choices,
        "ans": ans_idx,
        "explain": f"คำตอบที่ถูกต้องคือ: {correct_text}"
    })

portal_json_path = "/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/pretest_45_data.json"
with open(portal_json_path, "w", encoding="utf-8") as f:
    json.dump(portal_data, f, ensure_ascii=False, indent=2)
print(f"Generated {portal_json_path} successfully.")

# 3. Build worksheet_pretest_45.html
module_map = {
    range(1, 6): "โมดูล 1: วิทยาการเกษตรดิจิทัลและการตรวจวัดสภาพแวดล้อม",
    range(6, 16): "โมดูล 3: ชลศาสตร์และการจัดการน้ำอัตโนมัติในฟาร์ม",
    range(16, 26): "โมดูล 4: เครือข่ายการสื่อสาร LoRa และ ESP-NOW",
    range(26, 31): "โมดูล 6: ปัญญาประดิษฐ์ตรวจจับวัตถุและจำแนกพืชผล",
    range(31, 41): "โมดูล 5 & 7: การประมวลผลภาพดิจิทัลและ TinyML สมองกลฝังตัว",
    range(41, 46): "โมดูล 2: ตรรกะระบบควบคุมอัตโนมัติและเซนเซอร์ IoT (State & Rule Engine)"
}

def get_module_title(q_num):
    for r, title in module_map.items():
        if q_num in r:
            return title
    return "แบบทดสอบวัดผลการเรียนรู้"

choice_letters = ["ก", "ข", "ค", "ง"]

html = """<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <title>แบบทดสอบก่อนเรียน (Master Pre-test 45 ข้อ) - หลักสูตร AIoT & เกษตรดิจิทัล</title>
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
      font-size: 10.5pt;
      line-height: 1.4;
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
        font-size: 9.8pt;
        line-height: 1.32;
      }
      .page-break {
        page-break-before: always;
      }
    }
    .header-sheet {
      border-bottom: 2px solid #0284c7;
      padding-bottom: 6px;
      margin-bottom: 10px;
    }
    .org-title {
      font-family: 'Prompt', sans-serif;
      font-size: 13.5pt;
      font-weight: 700;
      color: #0369a1;
      text-align: center;
      margin: 0;
    }
    .sub-org {
      font-size: 10pt;
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
      font-size: 9.5pt;
    }
    .student-info-box {
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 8px 12px;
      background: #f8fafc;
      margin-bottom: 10px;
      display: grid;
      grid-template-columns: 2fr 1fr 1fr;
      gap: 6px 10px;
      font-size: 9.5pt;
    }
    .info-line {
      border-bottom: 1px dotted #94a3b8;
      display: inline-block;
      min-width: 90px;
    }
    .instructions {
      font-size: 9pt;
      color: #475569;
      margin-bottom: 10px;
      background: #fffbeb;
      border-left: 3px solid #f59e0b;
      padding: 5px 8px;
    }
    .module-banner {
      background: #f1f5f9;
      border-left: 3px solid #0284c7;
      padding: 3px 8px;
      font-family: 'Prompt', sans-serif;
      font-size: 10pt;
      font-weight: 600;
      color: #0f172a;
      margin: 10px 0 6px 0;
    }
    .question-block {
      margin-bottom: 8px;
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
      gap: 3px 12px;
      padding-left: 12px;
    }
    .choice-item {
      display: flex;
      align-items: baseline;
      gap: 5px;
      font-size: 9.5pt;
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
      padding: 10px;
      margin-top: 14px;
    }
    .key-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 8.5pt;
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
      📘 ใบงานแบบทดสอบก่อนเรียน (Master Pre-test 45 ข้อ ฉบับอัปเดตล่าสุด) - LEQs AIoT
    </div>
    <div style="display:flex; gap:10px;">
      <a href="./worksheet_pretest_45.pdf" download class="btn-print" style="background:#0284c7;">
        📥 ดาวน์โหลด PDF (45 ข้อ)
      </a>
      <button class="btn-print" onclick="window.print()">
        🖨️ สั่งพิมพ์เอกสาร (Print / Save as PDF)
      </button>
    </div>
  </div>

  <div style="max-width: 210mm; margin: 0 auto; padding: 12px 18px;">
    
    <!-- HEADER -->
    <div class="header-sheet">
      <div style="text-align:center; margin-bottom:2px;">
        <span class="exam-badge">แบบทดสอบวัดความรู้พื้นฐานก่อนเรียน (Pre-test Assessment Master 45 ข้อ)</span>
      </div>
      <h1 class="org-title">หลักสูตรเกษตรดิจิทัลและปัญญาประดิษฐ์ฝังตัว (AIoT & Digital Agriculture)</h1>
      <p class="sub-org">คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏรำไพพรรณี ร่วมกับ มหาวิทยาลัยเชียงใหม่ (CMU Lifelong)</p>
    </div>

    <!-- STUDENT INFO BOX -->
    <div class="student-info-box">
      <div><b>ชื่อ-นามสกุล:</b> <span class="info-line" style="min-width:160px;"></span></div>
      <div><b>เลขที่ / กลุ่ม:</b> <span class="info-line" style="min-width:50px;"></span></div>
      <div><b>คะแนนที่ได้:</b> <span class="info-line" style="min-width:50px;"></span> / 45</div>
      <div><b>สถานศึกษา / หน่วยงาน:</b> <span class="info-line" style="min-width:160px;"></span></div>
      <div><b>วันที่สอบ:</b> <span class="info-line" style="min-width:80px;"></span></div>
      <div><b>ผลการประเมิน:</b> [ &nbsp; ] ผ่าน [ &nbsp; ] ปรับปรุง</div>
    </div>

    <!-- INSTRUCTIONS -->
    <div class="instructions">
      <b>📌 คำชี้แจง:</b> แบบทดสอบมีทั้งหมด 45 ข้อ (ข้อละ 1 คะแนน รวม 45 คะแนน) ให้ผู้เรียนอ่านโจทย์และเลือกกากบาท (X) หรือระบายคำตอบที่ถูกต้องที่สุดเพียงข้อเดียวลงในช่องตัวเลือก
    </div>
"""

current_mod = ""
for i, q in enumerate(questions, 1):
    mod_title = get_module_title(i)
    if mod_title != current_mod:
        current_mod = mod_title
        html += f"""
    <div class="module-banner">📖 {current_mod}</div>
"""
    q_name = q.get("exam_name_th", "").strip()
    choices = q.get("exam_choice", [])
    
    html += f"""
    <div class="question-block">
      <div class="q-text">ข้อ {i}. {q_name}</div>
      <div class="choices-grid">
"""
    for ch_idx, ch in enumerate(choices):
        letter = choice_letters[ch_idx] if ch_idx < len(choice_letters) else str(ch_idx+1)
        ch_text = ch.get("choice_name_th", "").strip()
        html += f"""        <div class="choice-item">
          <span class="choice-bullet">{letter}</span>
          <span>{ch_text}</span>
        </div>
"""
    html += """      </div>
    </div>
"""

# Answer Key Section
html += """
    <div class="page-break"></div>

    <div class="header-sheet" style="margin-top:14px;">
      <h2 class="org-title" style="font-size:12.5pt;">📋 กระดาษคำตอบและตารางสรุปเฉลยแบบทดสอบ (Master Key 45 ข้อ)</h2>
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

key_summary_45 = [
  (1, "สมการพันธุกรรม P=G+E+(G×E)", "ปฏิสัมพันธ์ระหว่างพันธุกรรมกับสิ่งแวดล้อม", "Module 1"),
  (2, "อุปกรณ์วัดปริมาณรังสีดวงอาทิตย์", "Pyranometer", "Module 1"),
  (3, "ข้อดีเด่นของ Ultrasonic Anemometer", "ไม่มีชิ้นส่วนที่เคลื่อนที่ทำให้ลดปัญหาการสึกหรอ", "Module 1"),
  (4, "ความชื้นสัมพัทธ์สัมพันธ์กับการระเหยน้ำ", "ค่าแรงดึงระเหยน้ำของอากาศ (VPD)", "Module 1"),
  (5, "ก๊าซสำคัญต่อการหายใจของรากพืช", "ก๊าซออกซิเจน", "Module 1"),
  (6, "เหตุผลที่ฟาร์มใหญ่ต้องใช้ระบบน้ำอัตโนมัติ", "พื้นที่แปลงกว้าง ต้องดูแลต่อเนื่องตลอด 24 ชั่วโมง และพืชบางชนิดอ่อนไหวต่อการขาดน้ำ", "Module 3"),
  (7, "สูตรคำนวณอัตราการไหล Q = (A × ETc)/(T × Eff)", "อัตราการคายน้ำของพืช หน่วยเป็นมิลลิเมตรต่อวัน", "Module 3"),
  (8, "ความเร็วของน้ำในท่อเมนและท่อย่อยที่เหมาะสม", "1.0 – 2.0 เมตรต่อวินาที", "Module 3"),
  (9, "น้ำไหลในท่อเร็วกว่า 2.5 m/s", "เกิดแรงดันค้อน (Water Hammer) และความต้านทานการไหลสูงขึ้น", "Module 3"),
  (10, "เฮดรวมของระบบ (TDH)", "ความสูงฝั่งดูด + ความสูงฝั่งจ่าย + แรงดันสูญเสียในท่อ + แรงดันใช้งานของหัวจ่าย", "Module 3"),
  (11, "สายไฟร้อยท่อฝังดินไปปั๊มน้ำ", "สาย NYY เพราะมีฉนวนหลายชั้น ทนความชื้นและฝังดินได้", "Module 3"),
  (12, "การติดตั้งแผงโซลาร์เซลล์ในไทย", "หันแผงไปทางทิศใต้ เอียง 15 องศา", "Module 3"),
  (13, "ข้อได้เปรียบแผง Polycrystalline", "มีราคาถูกกว่า", "Module 3"),
  (14, "ปุ่มปรับ CV บนบอร์ด XL4015", "แรงดันไฟฟ้าสูงสุดที่จ่ายออกไปชาร์จแบตเตอรี่", "Module 3"),
  (15, "ปุ่มปรับ CC บนบอร์ด XL4015", "จำกัดกระแสชาร์จสูงสุด เพื่อไม่ให้แบตเตอรี่เสียหายหรือ BMS ตัดการทำงาน", "Module 3"),
  (16, "LoRa ออกแบบเพื่อรองรับงานประเภทใด", "งาน Telemetry คือส่งค่าที่วัดได้จากเซนเซอร์เป็นครั้งคราว", "Module 4"),
  (17, "ขนาด Payload ของ LoRa ต่อแพ็กเกต", "ระดับหลักสิบไบต์", "Module 4"),
  (18, "Duty Cycle สัญญาณ LoRa ตามกฎหมายไทย", "1 เปอร์เซ็นต์", "Module 4"),
  (19, "LoRaWAN vs Custom LoRa", "LoRaWAN ใช้ Gateway และ Network Server บนคลาวด์ ส่วน Custom LoRa ควบคุมคลื่นวิทยุโดยตรงโดยไม่ต้องพึ่งคลาวด์", "Module 4"),
  (20, "แนวทางเพิ่มระยะสื่อสารของ LoRa", "ต่อหัว u.fl ผ่านสายแปลงเป็น SMA เข้ากับสายอากาศเกนสูง", "Module 4"),
  (21, "บทบาทของ ESP-NOW ในระบบสองบอร์ด", "สื่อสารระหว่างบอร์ด ESP32 สองตัวโดยตรง โดยไม่ต้องผ่าน WiFi Route", "Module 4"),
  (22, "หน้าที่ของบอร์ด 1 ที่ติดตั้งในสวน", "อ่านค่าเซนเซอร์แล้วส่งออกไป และรับคำสั่งมาสั่งเปิด-ปิดรีเลย์ควบคุมวาล์วน้ำ", "Module 4"),
  (23, "หน้าที่ของบอร์ด 2 ที่ติดตั้งในบ้าน", "เป็นสะพานเชื่อม รับข้อมูลจากบอร์ดในสวนผ่าน ESP-NOW แล้วส่งต่อขึ้นคลาวด์ผ่าน WiFi", "Module 4"),
  (24, "รูปแบบไฟล์ตั้งค่า ESPHome", "ไฟล์ YAML", "Module 4"),
  (25, "URL หน้าแดชบอร์ด Home Assistant", "http://homeassistant.local:8123", "Module 4"),
  (26, "Classification vs Object Detection", "Classification ทายผลลัพธ์ภาพรวมทั้งภาพ ส่วน Object Detection สามารถตีกรอบชี้พิกัดตำแหน่งของวัตถุแต่ละชิ้นบนสายพานได้", "Module 6"),
  (27, "เครื่องมือออนไลน์จัดการข้อมูลและวาดกรอบ Bounding Box", "Roboflow", "Module 6"),
  (28, "การตั้งชื่อ Class Name ให้ AI", "ใช้คำสั้น สื่อความหมาย และสะกดให้เหมือนกันทุกรูป เช่น healthy หรือ rotten", "Module 6"),
  (29, "จำนวนรูปถ่ายขั้นต่ำต่อ 1 Class", "อย่างน้อย 20 รูปต่อ Class", "Module 6"),
  (30, "ตรวจสอบรูปทรงผลไม้ (Shape Inspection)", "ใช้เกณฑ์วัดสัดส่วนความกว้างต่อความยาว (Aspect Ratio) และความกลม (Roundness)", "Module 6"),
  (31, "คอมพิวเตอร์มองเห็นภาพถ่ายดิจิทัลอย่างไร", "มองเห็นเป็น 'ตารางตัวเลข' (พิกเซล) ที่มีค่าตัวเลขกำกับอยู่ในแต่ละช่อง", "Module 5"),
  (32, "สมองกลขนาดจิ๋ว Edge AI ไม่พึ่งพาเน็ต", "คอมพิวเตอร์บอร์ดเดี่ยว (เช่น Raspberry Pi)", "Module 7"),
  (33, "กฎเหล็กข้อแรกในการติดตั้งกล้อง Vision", "ต้องควบคุมแสงสว่างให้คงที่ (เช่น ใช้ตู้คุมแสงหรือไฟวงแหวน LED) ห้ามใช้แสงธรรมชาติที่เปลี่ยนไปมา", "Module 7"),
  (34, "วิธีการทำงานของ AI ในการตรวจหารอยโรค", "เหมือนการสอนงานพนักงานใหม่ โดยการป้อนรูปตัวอย่างของดีและมีตำหนิให้ AI จดจำแพทเทิร์นได้เอง", "Module 7"),
  (35, "สาเหตุที่ค่าสี RGB ผิดพลาดเมื่อเจอแสงเงา", "เพราะค่า RGB วัดค่าสีรวมกับความสว่าง ทำให้เมื่อโดนเงามาบัง คอมพิวเตอร์จะสับสนคิดว่าเป็นสีดำหรือรอยตำหนิ", "Module 5"),
  (36, "คอมพิวเตอร์มองเห็นภาพถ่ายดิจิทัล", "มองเห็นเป็น 'ตารางตัวเลข' (พิกเซล) ที่มีค่าตัวเลขกำกับอยู่ในแต่ละช่อง", "Module 5"),
  (37, "สมองกลขนาดจิ๋ว Edge Computing", "คอมพิวเตอร์บอร์ดเดี่ยว (เช่น Raspberry Pi)", "Module 7"),
  (38, "เป้าหมายหลักของ Image Processing Rule-based", "สำหรับการวัดขนาด (S-M-L), นับพื้นที่ และคัดกรองรูปทรงพื้นฐานอย่างรวดเร็วโดยไม่ต้องใช้ AI ซับซ้อน", "Module 7"),
  (39, "Edge AI สำหรับโรงงานชุมชน", "เพราะช่วยประหยัดต้นทุนฮาร์ดแวร์ กินไฟต่ำ(~5W), ประมวลผลรวดเร็วที่หน้างานทันที และทำงานได้แม้อินเทอร์เน็ตล่ม", "Module 7"),
  (40, "สาเหตุที่ค่าสี RGB ผิดพลาดเมื่อเจอแสงเงา", "เพราะค่า RGB วัดค่าสีรวมกับความสว่าง ทำให้เมื่อโดนเงามาบัง คอมพิวเตอร์จะสับสนคิดว่าเป็นสีดำหรือรอยตำหนิ", "Module 5"),
  (41, "ระบบคนกดเปิดไฟ vs ระบบโปรแกรมเปิดไฟอัตโนมัติ", "ระบบ A ใช้คนตัดสินใจ ส่วนระบบ B ใช้เงื่อนไขในโปรแกรม", "Module 2"),
  (42, "สวิตช์ลูกลอยสองสถานะวัดระดับน้ำในสองถัง", "ไม่ได้ เพราะลูกลอยส่งสถานะเดียวกัน (บอกได้แค่ถึงหรือไม่ถึงระดับลูกลอย)", "Module 2"),
  (43, "ตรรกะเงื่อนไขปั๊มน้ำเมื่อลูกลอยเปลี่ยนเป็น Dry", "ปั๊มอาจทำงานต่อ เพราะยังไม่มีคำสั่งหยุด (Condition ไม่ตัดจนกว่าจะมี Stop Rule)", "Module 2"),
  (44, "ทริกเกอร์เงื่อนไขข้าม Threshold ความชื้น < 50%", "1 ครั้ง (เกิด Transition ข้ามขอบเขตเพียงรอบเดียวจาก 55% เป็น 45%)", "Module 2"),
  (45, "การตีความสถานะรีเลย์ ON จากหน้าประวัติ History", "รีเลย์มีสถานะ On ต่อเนื่อง 10 นาที (Telemetry ยืนยันเฉพาะสวิตช์สั่งงาน)", "Module 2")
]

for row in key_summary_45:
    html += f"""          <tr>
            <td style="text-align:center; font-weight:700;">{row[0]}</td>
            <td>{row[1]}</td>
            <td class="key-badge">✅ {row[2]}</td>
            <td style="text-align:center; color:#64748b;">{row[3]}</td>
          </tr>
"""

html += """        </tbody>
      </table>
    </div>

  </div>
</body>
</html>
"""

worksheet_html_path = "/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/worksheet_pretest_45.html"
with open(worksheet_html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Generated {worksheet_html_path} successfully!")
