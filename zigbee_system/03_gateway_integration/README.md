# 🛰️ การติดตั้งและกำหนดค่าเกตเวย์ Zigbee (Gateway Integration Architecture)

---

## 1. บทบาทของเกตเวย์ในระบบเกษตร AIoT (Gateway Role)

ในระบบ Zigbee โหนดเซนเซอร์และอุปกรณ์ปลายทางไม่สามารถสื่อสารผ่านโปรโตคอล TCP/IP หรือต่อเข้าอินเทอร์เน็ตได้โดยตรง จึงจำเป็นต้องมี **Zigbee Gateway** ทำหน้าที่เป็นสะพานเชื่อมสัญญาณ (Protocol Translation Bridge):

```
┌──────────────────┐             ┌───────────────────┐             ┌─────────────────────┐
│  Zigbee Sensors  │  Zigbee     │  Zigbee Gateway   │   TCP/IP    │    AIoT Platform    │
│  (Mesh Network)  ├────────────►│  • Zigbee2MQTT    ├────────────►│  • MQTT Broker      │
│  ZED / ZR Nodes  │ (802.15.4)  │  • Home Assistant │  (Ethernet/ │  • Node-RED / XAMPP │
│                  │             │  • Docker on RPi  │   Wi-Fi)    │  • Cloud InfluxDB   │
└──────────────────┘             └───────────────────┘             └─────────────────────┘
```

---

## 2. ทางเลือกสถาปัตยกรรมเกตเวย์ (Gateway Options Comparison)

| สถาปัตยกรรม | ฮาร์ดแวร์หลัก | ซอฟต์แวร์ประมวลผล | ความยืดหยุ่นและการควบคุม | ความเหมาะสม |
| :--- | :--- | :--- | :--- | :--- |
| **Option A: Zigbee2MQTT (แนะนำสูงสุด)** | Raspberry Pi / Mini PC + USB Dongle (CC2652P) | **Zigbee2MQTT (Node.js)** ส่งต่อเข้า Mosquitto MQTT | **สูงสุด (100% Open Source)** ควบคุม Payload, Topics และสร้าง External Converter ได้อิสระ | **เหมาะสำหรับงานวิจัย พัฒนา และระบบ AIoT เชิงพาณิชย์** |
| **Option B: Home Assistant ZHA** | Raspberry Pi / Server + USB Dongle | **ZHA (Zigbee Home Automation)** ในตัว Home Assistant | ใช้งานง่าย ติดตั้งผ่าน Web UI ได้ในคลิกเดียว | เหมาะสำหรับผู้ใช้งาน Home Assistant ที่ไม่ต้องการคอนฟิก MQTT เอง |
| **Option C: Tuya / Sonoff Cloud Gateway** | Tuya Wired/Wireless Gateway | Firmware ปิดของโรงงาน เชื่อมต่อคลาวด์ Tuya | ต่ำ (ติด Vendor Lock-in) ข้อมูลต้องวิ่งออกนอกประเทศ | เหมาะสำหรับงานต้นแบบเร่งด่วนเท่านั้น |

---

## 3. สารบัญเอกสารในโฟลเดอร์นี้

* [coordinator_hardware.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/03_gateway_integration/coordinator_hardware.md) - การเลือกฮาร์ดแวร์ USB Coordinator (Sonoff ZBDongle-P vs ZBDongle-E vs SLZB-06 PoE)
* [mqtt_topic_payload_spec.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/03_gateway_integration/mqtt_topic_payload_spec.md) - มาตรฐานโครงสร้างข้อมูล JSON, MQTT Topics, การ Subscribe/Publish และ Home Assistant Auto-Discovery
