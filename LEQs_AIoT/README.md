# CMU AIoT Smart Farm Mobile Application (Flutter)

แอปพลิเคชันสมาร์ทโฟนสำหรับการบริหารจัดการฟาร์มอัจฉริยะ (Smart Farming AIoT Mobile Dashboard & Control Center) พัฒนาขึ้นด้วย **Flutter (Dart)** ตามหัวข้อหลักสูตรการอบรมเชิงปฏิบัติการ **CMU AIoT Smart Farm Workshop** โดย ผศ.ดร.ชีวะ ทัศนา

---

## 🌾 สถาปัตยกรรมและโครงสร้างระบบที่รองรับ (Workshop Coverage)

แอปพลิเคชันครอบคลุมเนื้อหาและฟังก์ชันการทำงานครบทั้ง 4 ช่วงการอบรม (Activities 1 – 11):

### 1. ช่วงที่ 1: Sense, Act, Logic (กิจกรรม 1, 2, 3)
* **อ่านค่าเซนเซอร์แบบ Real-Time (Sense):**
  * **SHT30:** อุณหภูมิอากาศ (°C) และความชื้นสัมพัทธ์ในอากาศ (%RH)
  * **Analog Soil Moisture Sensor:** ระดับความชื้นในดิน (% Soil Moisture) พร้อมแถบแสดงสถานะ
  * **BH1750:** ความเข้มแสงแดด (Lux)
  * **Digital Float Switch:** สวิตช์ลูกลอยตรวจวัดระดับน้ำในถังพักน้ำ
* **สั่งงานรีเลย์และอุปกรณ์ภาคสนาม (Act):**
  * รีเลย์ที่ 1: ปั๊มน้ำรดน้ำอัตโนมัติ / โซลินอยด์วาล์ว (Irrigation Pump) พร้อมตัวนับเวลานับถอยหลัง (Timer Countdown)
  * รีเลย์ที่ 2: หลอดไฟปลูกพืช / พัดลมระบายอากาศ (Grow Light / Exhaust Fan)
* **ระบบตัดการทำงานฉุกเฉิน (Emergency Stop - E-Stop):** ปุ่มตัดกระแสไฟรีเลย์ทั้งหมดทันทีเมื่อเกิดเหตุขัดข้อง

---

### 2. ช่วงที่ 2: Think & Failure Lab (กิจกรรม 4, 5)
* **ระบบตั้งกฎรดน้ำอัตโนมัติ (Autonomous Irrigation Rules):**
  * ปรับแต่งเกณฑ์ความชื้นดินเริ่มรดน้ำ (Start Threshold e.g. < 40%)
  * ปรับแต่งเกณฑ์ความชื้นดินหยุดรดน้ำ (Stop Threshold e.g. ≥ 75%)
* **ระบบป้องกันความเสียหายและกลไกนิรภัย (Fail-Safe Watchdogs):**
  * **ระบบป้องกันปั๊มทำงานแห้ง (Dry-Run Protection):** อินเทอร์ล็อกกับสวิตช์ลูกลอย ตัดปั๊มทันทีเมื่อน้ำแห้ง ป้องกันขดลวดปั๊มไหม้
  * **ตัวจำกัดเวลาทำงานสูงสุด (Max Runtime Watchdog):** ตัดการทำงานเมื่อปั๊มทำงานต่อเนื่องเกินกำหนด (เช่น 180 วินาที) ป้องกันน้ำล้นแปลงกรณีเซนเซอร์ชำรุด
  * **ห้องจำลองปัญหา (Failure Lab Simulator):** ปุ่มทดสอบจำลองน้ำแห้งเพื่อสาธิตการทำงานของระบบความปลอดภัย

---

### 3. ช่วงที่ 3: History, Dashboard & Analytics (กิจกรรม 6, 7, 8)
* **กราฟแสดงแนวโน้มย้อนหลัง (Historical Sparkline Trends):**
  * กราฟความชื้นดิน, อุณหภูมิ, ความชื้นอากาศ, และความเข้มแสง ย้อนหลังแบบละเอียด 60 จุดตรวจวัด
  * คำนวณค่าเฉลี่ย (Average), ต่ำสุด (Min), สูงสุด (Max)
* **ส่งออกข้อมูลการทำกิจกรรม (Export JSON):**
  * รองรับการดาวน์โหลดคำตอบและผลการตรวจวัดประจำกลุ่ม (Team JSON Export) ตามมาตรฐานใบงาน

---

### 4. ช่วงที่ 4: Send, Receive, Bridge (กิจกรรม 9, 10, 11)
* **โครงข่ายไร้สายระยะไกล ESP-NOW (Peer-to-Peer Long-Range Network):**
  * บอร์ดแปลงต้นทาง: `gogo-iot-red-242dcc`
  * บอร์ดตัวรับที่บ้าน: `farm-receiver-red-d4e5f6`
  * ช่องสัญญาณวิทยุ: Wi-Fi Channel 6 (2.437 GHz)
  * มาตรวัดความแรงสัญญาณวิทยุ (RSSI dBm) และอัตราส่งผ่านสำเร็จ (Packet Delivery Rate %)
* **ตารางเปรียบเทียบข้อมูลสองทาง (Activity 11.2 Dual-Path Telemetry):**
  * แสดงค่าเซนเซอร์ที่มาทาง Wi-Fi โดยตรง เปรียบเทียบกับค่าที่ส่งผ่านโครงข่าย ESP-NOW
* **ระบบเตือนเมื่อแปลงเงียบ (Activity 11.4 Deadman Watchdog Alert):**
  * ตรวจจับสัญญาณ Heartbeat ขาดหายเกิน 15-30 วินาที พร้อมส่ง Notification แจ้งเตือนผู้ดูแลฟาร์มทันที

---

## 📁 โครงสร้างโปรเจกต์ (Clean MVVM Architecture)

```text
Flutter AIoT/
├── lib/
│   ├── data/
│   │   ├── models/
│   │   │   └── farm_models.dart         # Data Models (Telemetry, Actuators, Rules, ESP-NOW)
│   │   ├── repositories/
│   │   │   └── farm_repository.dart     # Single Source of Truth Repository
│   │   └── services/
│   │       ├── farm_simulator_service.dart # Real-time Physical Dynamics & Failure Simulator
│   │       └── home_assistant_service.dart # Home Assistant REST API Integration
│   ├── ui/
│   │   ├── core/
│   │   │   ├── app_theme.dart           # Emerald & Mint Material 3 Dark/Light Design System
│   │   │   └── widgets/
│   │   │       ├── actuator_card.dart   # Interactive Actuator & Safety Lock Widget
│   │   │       ├── sensor_gauge_card.dart # Responsive Sensor Gauge & Progress Card
│   │   │       └── sparkline_chart.dart # Zero-GC 60fps Vector Historical Chart Painter
│   │   ├── view_models/
│   │   │   └── farm_view_model.dart     # Business Logic, Interlocks & Watchdogs
│   │   └── views/
│   │       ├── main_screen.dart         # Root Navigation, Team Picker & Alert Banner
│   │       └── tabs/
│   │           ├── dashboard_tab.dart   # Live Environmental & Soil Gauges
│   │           ├── control_tab.dart     # Actuators, Pump Countdown & E-Stop
│   │           ├── automation_tab.dart  # Threshold Sliders & Fail-Safe Watchdogs
│   │           ├── espnow_tab.dart      # ESP-NOW Dual-Path & RSSI Diagnostics
│   │           └── history_tab.dart     # 24h Sensor History & JSON Export
│   └── main.dart                        # Application Entry Point & Provider Injection
├── test/
│   ├── farm_view_model_test.dart        # Business Logic & Fail-Safe Unit Tests (Passed ✓)
│   └── widget_test.dart                 # Dashboard Smoke Tests (Passed ✓)
└── pubspec.yaml
```

---

## 🚀 วิธีการติดตั้งและรันแอปพลิเคชัน (How to Run)

### 1. รันบน Web Browser (Chrome) เพื่อทดสอบทันที
```bash
cd "Flutter AIoT"
/Users/chewathassana/flutter/bin/flutter run -d chrome
```

### 2. รันบนโทรศัพท์สมาร์ทโฟน Android
1. เสียบสาย USB ระหว่างสมาร์ทโฟนกับคอมพิวเตอร์ และเปิดโหมด **USB Debugging**
2. ตรวจสอบอุปกรณ์:
   ```bash
   /Users/chewathassana/flutter/bin/flutter devices
   ```
3. สั่งรันลงสมาร์ทโฟน:
   ```bash
   /Users/chewathassana/flutter/bin/flutter run
   ```

### 3. รัน Unit & Widget Tests
```bash
/Users/chewathassana/flutter/bin/flutter test
```
*(ผ่านการทดสอบ 100% ครบทุกโมดูล)*
