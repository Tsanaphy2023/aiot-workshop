# 🌐 ระบบสื่อสารไร้สาย Zigbee 3.0 และระบบนิเวศ Zigbee เซนเซอร์สำหรับเกษตรอัจฉริยะ (AIoT Smart Agriculture)
**สถาปัตยกรรมระบบ, การออกแบบเครือข่าย Mesh, ฮาร์ดแวร์เซนเซอร์, เกตเวย์ และแนวทางการพัฒนาเฟิร์มแวร์**

---

## 📌 บทนำและภาพรวม (Executive Summary)

ระบบเครือข่ายไร้สาย **Zigbee 3.0** บนมาตรฐานสากล **IEEE 802.15.4** ได้รับการยอมรับอย่างกว้างขวางในระบบอัตโนมัติ (Home & Industrial Automation) และกำลังมีบทบาทสำคัญอย่างยิ่งในการปฏิวัติงาน **เกษตรแม่นยำ (Precision Agriculture)** และ **โรงเรือนอัจฉริยะ (Smart Greenhouse)**

จุดเด่นสำคัญของ Zigbee คือการเป็น **เครือข่ายร่างแหอัตโนมัติ (Self-Healing Mesh Network)** ที่กินพลังงานต่ำมาก (Ultra-Low Power) โหนดเซนเซอร์ปลายทางสามารถทำงานด้วยแบตเตอรี่ก้อนเดียวได้นาน 1–3 ปี พร้อมความสามารถในการถ่ายทอดสัญญาณผ่านโหนดเราเตอร์ (Multi-Hop Routing) ทำให้ครอบคลุมพื้นที่แปลงปลูกและโรงเรือนได้อย่างทั่วถึงโดยไร้จุดอับสัญญาณ

ชุดเอกสารนี้ถูกจัดทำขึ้นแบบแยกโฟลเดอร์และแยกโมดูลอย่างเป็นระบบ เพื่อรองรับทีมวิศวกร นักวิจัย และนักพัฒนาระบบ AIoT ในการศึกษา ออกแบบ จัดซื้ออุปกรณ์ และลงมือพัฒนาฮาร์ดแวร์/เฟิร์มแวร์จริง

---

## 📂 โครงสร้างชุดเอกสาร (Documentation Directory Structure)

```
zigbee_system/
├── README.md                             # [หน้านี้] แผนผังภาพรวมและสารบัญหลัก
│
├── 01_architecture_protocols/            # 📡 โฟลเดอร์ที่ 1: สถาปัตยกรรมและโปรโตคอล
│   ├── README.md                         # ภาพรวมโปรโตคอลสแต็ก Zigbee 3.0 & IEEE 802.15.4
│   ├── mesh_networking_routing.md        # การทำงานของ Mesh Topology, AODV Routing, ZC/ZR/ZED
│   └── zigbee_vs_lora_wifi.md            # ตารางเปรียบเทียบเชิงวิศวกรรม: Zigbee vs LoRa vs Wi-Fi vs BLE
│
├── 02_sensor_ecosystem/                  # 🌾 โฟลเดอร์ที่ 2: ระบบนิเวศเซนเซอร์ (Sensors Ecosystem)
│   ├── README.md                         # ภาพรวมเซนเซอร์ Zigbee เชิงพาณิชย์และงานอุตสาหกรรม
│   ├── soil_environment_sensors.md      # เซนเซอร์ดิน (Soil Moisture/EC/Temp), อากาศ, แสง, ระดับน้ำ
│   ├── commercial_vs_custom.md           # เปรียบเทียบเซนเซอร์สำเร็จรูป (Tuya/Sonoff) vs พัฒนาเอง
│   └── industrial_modbus_bridge.md       # สถาปัตยกรรมสะพานเชื่อม RS485 Modbus NPK สู่ Zigbee 3.0
│
├── 03_gateway_integration/               # 🛰️ โฟลเดอร์ที่ 3: เกตเวย์และการเชื่อมต่อระบบคลาวด์
│   ├── README.md                         # ภาพรวมเกตเวย์ Zigbee2MQTT (Z2M) และ Home Assistant (ZHA)
│   ├── coordinator_hardware.md           # การเลือก USB Coordinator (CC2652P, EFR32MG21, ZBDongle)
│   └── mqtt_topic_payload_spec.md        # ข้อกำหนด JSON Payload, MQTT Topics, Cluster Attributes
│
└── 04_firmware_hardware_dev/             # 💻 โฟลเดอร์ที่ 4: การพัฒนาฮาร์ดแวร์และเฟิร์มแวร์
    ├── README.md                         # แนวทางการพัฒนาโหนด Zigbee (ESP32-C6 / ESP32-H2 / TI CC2652)
    ├── esp32c6_zigbee_guide.md           # โค้ดตัวอย่างและการพัฒนา ESP32-C6 Zigbee 3.0 (ESP-IDF / Arduino)
    ├── esphome_zigbee_yaml.md            # การสร้างเซนเซอร์ Zigbee แบบ Low-Code ด้วย ESPHome YAML
    └── power_management_battery.md       # การจัดการพลังงาน Deep Sleep, แบตเตอรี่ LiFePO4, Solar Harvesting
```

---

## ⚡ สรุปจุดเด่นทางเทคนิคของ Zigbee 3.0 สำหรับงานเกษตร AIoT

| คุณลักษณะ (Specifications) | รายละเอียดทางเทคนิค | ประโยชน์ในงาน Smart Farm |
| :--- | :--- | :--- |
| **ย่านความถี่ (Frequency Band)** | 2.4 GHz ISM Band (Channels 11–26) | ใช้งานได้ทั่วโลกโดยไม่ต้องขอใบอนุญาตวิทยุ |
| **อัตราการส่งข้อมูล (Data Rate)** | 250 kbps (O-QPSK Modulation) | สูงกว่า LoRa (~5-50 kbps) ส่งค่าหลายเซนเซอร์ได้พร้อมกัน |
| **สถาปัตยกรรมเครือข่าย** | Mesh Network (Self-Healing, Self-Forming) | มีเส้นทางสำรองอัตโนมัติ หากโหนดใดเสีย ระบบไม่ล่ม |
| **จำนวนโหนดสูงสุด** | รองรับได้สูงสุดถึง 65,000 โหนดต่อเครือข่าย | ติดตั้งเซนเซอร์ได้หนาแน่นทุกจุดในแปลง/โรงเรือน |
| **การกินกระแสไฟ (Power)** | Deep Sleep: **10 – 20 µA**, TX/RX: **20 – 35 mA** | ใช้แบตเตอรี่ 18650 หรือถ่านกระดุมได้นานหลายปี |
| **ความเข้ากันได้ (Interoperability)** | Zigbee 3.0 รวมทุก Profile (ZCL) เป็นมาตรฐานเดียว | เซนเซอร์ต่างยี่ห้อ (Tuya, Sonoff, DIY) เชื่อมต่อกันได้ |

---

## 🎯 คำแนะนำในการเริ่มต้นศึกษาและพัฒนา (Quick Navigation)

1. **สำหรับผู้เริ่มต้น/ผู้วางระบบ:**
   * เริ่มต้นอ่านที่ [01_architecture_protocols/README.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/01_architecture_protocols/README.md) เพื่อเข้าใจบทบาทของ Coordinator (ZC), Router (ZR) และ End Device (ZED)
   * เปรียบเทียบจุดเด่นจุดด้อยกับ LoRa ที่ [01_architecture_protocols/zigbee_vs_lora_wifi.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/01_architecture_protocols/zigbee_vs_lora_wifi.md)
2. **สำหรับการเลือกซื้ออุปกรณ์และเซนเซอร์:**
   * ศึกษาประเภทเซนเซอร์วัดดินและสภาพอากาศที่ [02_sensor_ecosystem/soil_environment_sensors.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/02_sensor_ecosystem/soil_environment_sensors.md)
   * หากต้องการเชื่อมต่อหัววัดปุ๋ย NPK อุตสาหกรรม อ่านต่อที่ [02_sensor_ecosystem/industrial_modbus_bridge.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/02_sensor_ecosystem/industrial_modbus_bridge.md)
3. **สำหรับการตั้งค่า Gateway และระบบจัดการข้อมูล:**
   * ติดตั้ง Zigbee2MQTT ร่วมกับ Home Assistant ที่ [03_gateway_integration/README.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/03_gateway_integration/README.md)
4. **สำหรับนักพัฒนาเฟิร์มแวร์ (Embedded Developers):**
   * เขียนโค้ด ESP32-C6 Native Zigbee 3.0 ที่ [04_firmware_hardware_dev/esp32c6_zigbee_guide.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/04_firmware_hardware_dev/esp32c6_zigbee_guide.md)
   * ออกแบบระบบชาร์จโซลาร์เซลล์และคำนวณแบตเตอรี่ที่ [04_firmware_hardware_dev/power_management_battery.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/04_firmware_hardware_dev/power_management_battery.md)
