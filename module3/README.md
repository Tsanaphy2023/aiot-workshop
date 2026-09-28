# Module 3: การจัดการข้อมูลและการสื่อสารในฟาร์มยุคดิจิทัล
**(Farm Data Logging & Communication)**

หลักสูตร: นวัตกรเกษตรอัจฉริยะ AIoT สำหรับเกษตรแม่นยำ รุ่นที่ 1 (วิทยาลัยการศึกษาตลอดชีวิต มหาวิทยาลัยเชียงใหม่)

---

## 📌 สารบัญเนื้อหาในโมดูล
* 📄 **ไฟล์สไลด์ประกอบการสอนฉบับล่าสุด (อ.กำพล):** [Module 3_การจัดการข้อมูลและการสื่อสารในฟาร์ม.pdf](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/Module%203_%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%88%E0%B8%B1%E0%B8%94%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%A1%E0%B8%B9%E0%B8%A5%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%AA%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%99%E0%B8%9F%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%A1.pdf) *(37 สไลด์ความละเอียดสูง 54.5 MB จาก Google Drive)*
* 📦 **คู่มือวิศวกรรมอุปกรณ์และงบประมาณระบบ Smart Farm:** [EQUIPMENT_AND_PRICING_GUIDE.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/EQUIPMENT_AND_PRICING_GUIDE.md) *(บัญชีราคา 22 รายการ, เปรียบเทียบโซลินอยด์ vs มอเตอร์บอลวาล์ว, Zigbee vs WiFi, การตั้งค่า Median ใน Home Assistant)*
* 📑 **เอกสารสรุปถาม-ตอบและต้นทุน:** [q-a.pdf](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/q-a.pdf) / [q-a.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/q-a.txt)
* 📊 **ไฟล์บัญชีราคาชุดกล่องทดลอง (CSV):** [box_equipment_pricing.csv](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/box_equipment_pricing.csv)
* 📐 **คู่มือสรุปสูตรคำนวณและตารางวิศวกรรมฉบับสมบูรณ์:** [FORMULAS_AND_CALCULATIONS.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/FORMULAS_AND_CALCULATIONS.md) *(สรุปสูตรแบบข้อๆ, ตารางวิศวกรรม, ค่าสัมประสิทธิ์, ตัวอย่างคำนวณจริง 5 ไร่, และระบบโซลาร์)*
* 🎬 **ไฟล์วิดีโอบรรยาย (1080p Full HD, 37:17 นาที):** [Module3_video.mp4](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/Module3_video.mp4) *(376.16 MB)*
* 📝 **สคริปต์ถอดคำบรรยายเสียงภาษาไทย:** [Module_3_lecture_transcript.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/extracted_text/Module_3_lecture_transcript.txt) *(574 บรรทัด)*
* 🖼️ **แกลเลอรีภาพสไลด์ความละเอียดสูง (PNG):** [slides_png/](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/slides_png) *(37 สไลด์)*
* 💻 **ซอร์สโค้ด MicroPython:** [water_logger.py](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/src/water_logger.py)

1. [วิศวกรรมการวางระบบให้น้ำอัจฉริยะ (Hydraulic Engineering)](#1-วิศวกรรมการวางระบบให้น้ำอัจฉริยะ)
2. [ขั้นตอนการออกแบบระบบให้น้ำ 5 ขั้นตอน](#2-ขั้นตอนการออกแบบระบบให้น้ำ-5-ขั้นตอน)
3. [ตารางสรุปสูตรและแนวทางออกแบบ](#3-ตารางสรุปสูตรและแนวทางออกแบบ)
4. [อุปกรณ์ฮาร์ดแวร์และระบบพลังงาน (Hardware & Power System)](#4-อุปกรณ์ฮาร์ดแวร์และระบบพลังงาน)
5. [ทางเลือกการควบคุม: อุปกรณ์สำเร็จรูป vs Custom IoT](#5-ทางเลือกการควบคุม-sonoff-vs-custom-pcb)
6. [ซอฟต์แวร์ MicroPython Data Logging บน ESP32-C3](#6-ซอฟต์แวร์-micropython-data-logging)
7. [คู่มือจัดซื้อและคำถามสำคัญ (BOM & Sourcing)](#7-คู่มือจัดซื้อและรายการอุปกรณ์ในชุดกล่องทดลอง)

---

## 1. วิศวกรรมการวางระบบให้น้ำอัจฉริยะ

### 1.1 การคำนวณปริมาณน้ำและอัตราการไหล ($Q$)
เริ่มต้นจากการหาความต้องการน้ำของพืช (*Crop Water Requirement*) เพื่อกำหนดอัตราการไหลรวม (*Flow Rate*) ของระบบจากความต้องการน้ำสูงสุด (*Peak Water Demand*):

$$Q = \frac{A \times ET_c}{T \times Eff}$$

* **$Q$**: อัตราการไหลที่ต้องการ ($m^3/hr$ หรือ $L/min$)
* **$A$**: พื้นที่เพาะปลูก (ตารางเมตร - $m^2$)
* **$ET_c$**: อัตราการคายน้ำของพืช ($mm/day$)
* **$Eff$**: ประสิทธิภาพระบบให้น้ำ (ระบบน้ำหยด $\approx 90\%$, ระบบสปริงเกลอร์ $\approx 75\%$)
* **$T$**: ระยะเวลาการให้น้ำในแต่ละวัน ($hr/day$)

---

### 1.2 ไฮดรอลิกส์และการเลือกขนาดท่อ
* **ความเร็วของน้ำในท่อ (Velocity - $v$):**
  * ค่าความเร็วที่เหมาะสมในท่อเมนและท่อย่อยควรอยู่ที่ **$1.0 - 2.0\text{ m/s}$**
  * *ถ้าน้ำไหลช้าเกินไป ($< 0.5\text{ m/s}$):* สิ้นเปลืองค่าท่อที่มีขนาดใหญ่เกินจำเป็น
  * *ถ้าน้ำไหลเร็วเกินไป ($> 2.5\text{ m/s}$):* เกิดปรากฏการณ์แรงดันค้อน (**Water Hammer**) และมีความต้านทานการไหลสูง
* **การคำนวณพื้นที่หน้าตัดท่อ ($A = Q / v$):**

$$Q = A \times v = \frac{\pi \times d^2}{4} \times v$$

---

### 1.3 การสูญเสียแรงดันในท่อ (Head Loss - $h_f$)
เมื่อน้ำไหลผ่านท่อจะเกิดแรงเสียดทาน ทำให้แรงดันปลายทางลดลง คำนวณได้จาก **Hazen-Williams Equation**:

$$h_f = \frac{10.67 \times L \times Q^{1.852}}{C^{1.852} \times D^{4.87}}$$

* **$h_f$**: การสูญเสียความดัน (Head Loss) ในหน่วยเมตร ($m$)
* **$L$**: ความยาวของท่อ ($m$)
* **$Q$**: อัตราการไหลของน้ำ ($m^3/s$)
* **$D$**: เส้นผ่านศูนย์กลางภายในของท่อ ($m$)
* **$C$**: ค่าสัมประสิทธิ์ความเรียบของผิวท่อ (*Hazen-Williams Coefficient*)
  * ท่อพีวีซี (PVC) / ท่อทองแดง: $C = 130 - 150$
  * ท่อเหล็กชุบสังกะสี (Galvanized Steel): $C = 120$
  * ท่อเหล็กหล่อ (Cast Iron): $C = 100 - 130$
  * ท่อคอนกรีต: $C = 100 - 140$
* **ข้อควรระวัง:** ต้องเผื่อแรงดันตกจากข้อต่อและวาล์ว (*Minor Loss*) อีกประมาณ **10 - 20%**

---

### 1.4 การคำนวณเฮดรวม (Total Dynamic Head - $TDH$)
เฮดรวมคือพลังงานแรงดันทั้งหมดที่ปั๊มต้องสร้างขึ้น เพื่อส่งน้ำไปยังจุดใช้งานปลายทางได้อย่างสมบูรณ์:

$$TDH = H_s + H_d + H_f + H_{op}$$

* **$H_s$** (*Static Suction*): ระยะความสูงฝั่งสูบน้ำ ($m$)
* **$H_d$** (*Static Discharge*): ระยะความสูงจากปั๊มถึงจุดสูงสุดของแปลง ($m$)
* **$H_f$** (*Friction Loss*): แรงดันสูญเสียรวมในท่อ ข้อต่อ และวาล์ว ($m$)
* **$H_{op}$** (*Operating Pressure*): แรงดันใช้งานของหัวมินิสปริงเกลอร์หรือหัวน้ำหยด ($m$)

---

### 1.5 การคำนวณกำลังมอเตอร์ปั๊มน้ำ ($P$)

$$P\text{ (kW)} = \frac{\rho \times g \times Q \times TDH}{3600 \times \eta}$$

* **$\rho$**: ความหนาแน่นของน้ำ ($1000\text{ kg/m}^3$)
* **$g$**: ความเร่งโน้มถ่วง ($9.81\text{ m/s}^2$)
* **$Q$**: อัตราการไหล ($\text{m}^3\text{/hr}$)
* **$\eta$**: ประสิทธิภาพปั๊มรวม (ประมาณ $0.60 - 0.75$)
* *ข้อแนะนำ:* ควรเผื่อกำลังมอเตอร์อีก **15 - 20%** สำหรับ Service Factor

---

## 2. ขั้นตอนการออกแบบระบบให้น้ำ 5 ขั้นตอน

1. **สังเกตพื้นที่ (Survey):** สำรวจแปลง คำนวณความต้องการน้ำของพืช และแบ่งโซนการจ่ายน้ำเพื่อลดขนาดปั๊ม
2. **เลือกหัวจ่าย (Emitters):** กำหนดประเภทหัวหยด/สปริงเกลอร์ แรงดันใช้งาน และอัตราจ่ายน้ำ
3. **ขนาดท่อน้ำ (Pipe Sizing):** คำนวณท่อเมน/ท่อย่อยตามอัตราไหลและความเร็วไม่เกิน $2\text{ m/s}$
4. **คำนวณ TDH (Head Calculation):** รวมความสูง แรงดันใช้งาน และ Head Loss ในท่อทั้งหมด
5. **เลือกปั๊มและตู้ควบคุม (Pump & IoT Control):** เลือกปั๊มน้ำ ติดตั้งโซลินอยด์วาล์ว และระบบบอร์ดสั่งการ IoT

---

## 3. ตารางสรุปสูตรและแนวทางออกแบบ

| หัวข้อการคำนวณ | สูตร / ค่ามาตรฐาน | หน่วย | ข้อแนะนำการใช้งาน |
| :--- | :--- | :---: | :--- |
| **อัตราการไหล ($Q$)** | $Q = \frac{A \times ET_c}{T \times Eff}$ | $\text{m}^3\text{/hr}$ (ลบ.ม./ชม.) | คำนวณจากความต้องการน้ำสูงสุดใน 1 วัน |
| **ความเร็วในท่อ ($v$)** | $v = \frac{4Q}{\pi \times d^2}$ | $\text{m/s}$ (เมตร/วินาที) | ควบคุมให้อยู่ในช่วง $1.0 - 2.0\text{ m/s}$ เพื่อลด friction loss |
| **แรงดันสูญเสีย ($H_f$)** | Hazen-Williams Equation | $m$ (เมตรน้ำ) | เพิ่ม Minor loss (ข้อต่อ/วาล์ว) อีก $10 - 20\%$ |
| **เฮดรวม ($TDH$)** | $TDH = H_s + H_d + H_f + H_{op}$ | $m$ (เมตรน้ำ) | นำคู่ค่า $Q$ และ $TDH$ ไปเปิดกราฟ Pump Performance Curve |
| **กำลังมอเตอร์ ($P$)** | $P = \frac{\rho \times g \times Q \times TDH}{3600 \times \eta}$ | $\text{kW / HP}$ (แรงม้า) | เผื่อกำลังมอเตอร์อีก $15 - 20\%$ สำหรับ Service Factor |

---

## 4. อุปกรณ์ฮาร์ดแวร์และระบบพลังงาน

### รายการอุปกรณ์ (Bill of Materials):
* **ตัวประมวลผล:** บอร์ดคอมพิวเตอร์บอร์ดเดี่ยว ESP32-C3 Super Mini
* **เซนเซอร์:** DHT22 (วัดอุณหภูมิและความชื้น), เซนเซอร์ปริมาณน้ำฝน (Tipping Bucket)
* **ตัวขับกำลัง:** บอร์ดรีเลย์ (Relay) ควบคุม Solenoid Valve ($12\text{VDC}$ หรือ $24\text{VAC}$)
* **ระบบพลังงานแสงอาทิตย์:**
  * แผงโซลาร์เซลล์ขนาดเล็ก $12\text{V } 15 - 30\text{W}$
  * แบตเตอรี่ LiFePO4 32650 $3.2\text{V } 6 - 6.5\text{Ah}$
  * วงจร 1S BMS LiFePO4 $3.2\text{V } 12\text{A}$
  * โมดูลชาร์จ XL4015 5A MPPT Buck Converter
  * โมดูลแปลงแรงดันจ่ายบอร์ด Buck-Boost: TPS63020

---

## 5. ทางเลือกการควบคุม: Sonoff vs Custom PCB

| คุณสมบัติ | กล่องสำเร็จรูป Sonoff TH Elite (THR316D / THR320D) | Custom Board (ESP32-C3 Super Mini) |
| :--- | :--- | :--- |
| **ความสะดวกในการติดตั้ง** | เสียบปลั๊ก AC 100-240V, ต่อเซนเซอร์ RJ11 (4P4C) พร้อมใช้ | ต้องบัดกรีหรือสั่งทำ PCB จาก EasyEDA/JLCPCB |
| **การเชื่อมต่อ** | Wi-Fi 2.4 GHz + Bluetooth Pairing | Wi-Fi / Bluetooth / ESP-NOW / LoRa |
| **การทำงานออฟไลน์** | **LAN Control** สั่งงานในวงแลนได้แม้เน็ตหลุด | เขียนเงื่อนไขควบคุมอิสระบนตัวบอร์ด |
| **การเก็บข้อมูล** | ประวัติ 6 เดือนบน eWeLink (Export .xlsx ได้) | บันทึกแบบ Daily Rolling CSV บนบอร์ด/SD Card |

---

## 6. ซอฟต์แวร์ MicroPython Data Logging
ซอร์สโค้ดสมบูรณ์จัดเก็บไว้ที่: [`src/water_logger.py`](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/src/water_logger.py)

### คุณสมบัติของโค้ด:
1. **Network Time Protocol (NTP):** ดึงเวลาสากลและแปลงเป็น Local Time ประเทศไทย (UTC+7)
2. **Monthly Rolling CSV Logging:** บันทึกข้อมูลแยกรายวัน `01.csv` ถึง `31.csv` โดยตรวจสอบ `mtime` หากเป็นข้อมูลของเดือนเก่าจะเขียนทับให้อัตโนมัติ ป้องกัน Flash Memory เต็ม
3. **Sampling Rate:** อ่านค่าเซนเซอร์ทุกๆ 15 วินาที
4. **Conditional Actuation:** ตรวจสอบความชื้นทุกๆ 20 วินาที หากความชื้น $> 30\%$ ให้กระพริบ LED / ควบคุมวาล์วน้ำ 5 วินาที

---

## 7. คู่มือจัดซื้อและรายการอุปกรณ์ในชุดกล่องทดลอง (Hardware Box BOM & Sourcing)

ดูรายละเอียดฉบับเต็มได้ที่: [EQUIPMENT_AND_PRICING_GUIDE.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module3/EQUIPMENT_AND_PRICING_GUIDE.md)

### 7.1 ข้อมูลสรุปชุดกล่องทดลอง (120 ชุด)
* **งบประมาณรวมทั้งโครงการ:** **319,900 บาท** (เฉลี่ย **~2,665 บาท/ชุด**)
* **อุปกรณ์ประมวลผลหลัก:** บอร์ด GoGo-IoT (ESP32-C3) พร้อมเซนเซอร์อุณหภูมิ, ความชื้น, แสง, บารอมิเตอร์, IMU ออนบอร์ด (สั่งผลิต JLCPCB SMT)
* **ระบบควบคุมกำลัง:** บอร์ดรีเลย์ ESP32-C6-Relay-X1 v1.1 รองรับการเชื่อมต่อ Zigbee 3.0 / Wi-Fi
* **ระบบจ่ายพลังงานภาคสนาม:** แผงโซลาร์เซลล์ 12V 15W + Solar Charge Controller PWM 12V 10A + ถ่านชาร์จ 18650
* **ตัวกระทำ (Actuators):** ปั๊มน้ำจุ่ม 12V (HJ-531), Float Switch ลูกลอย, อะแดปเตอร์แปลงสาย Grove

### 7.2 คำแนะนำทางวิศวกรรมการเลือกวาล์วน้ำ (จาก q-a.pdf)
* **มอเตอร์บอลวาล์ว (Electric Motorized Ball Valve 12V):** *ดีที่สุดสำหรับระบบโซลาร์เซลล์และแท็งก์น้ำปล่อยลอย* เพราะไม่ต้องการแรงดันน้ำหนุน (Zero Pressure) และกินไฟเฉพาะจังหวะหมุนเปิด/ปิด
* **โซลินอยด์วาล์ว (Solenoid Valve 12V):** เหมาะกับระบบที่มีแรงดันน้ำจากปั๊ม (> 0.5 bar) กินไฟเฉพาะขณะสั่งเปิดน้ำ

### 7.3 การกรองสัญญาณและระบบอัตโนมัติใน Home Assistant
* **แก้ปัญหาสัญญาณแกว่งด้วย Median Helper:** ไปที่ `Settings` > `Devices & Services` > `Helpers` > `+ Create Helper` > `Statistic` > เลือกเซนเซอร์และฟังก์ชัน `Median` ย้อนหลัง 15-30 นาที
* **Automation:** กำหนดเงื่อนไขสั่งเปิดวาล์ว Zigbee เมื่อ Median ความชื้นดินต่ำกว่าเกณฑ์ ในช่วงเวลาเช้า/เย็น
