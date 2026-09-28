# 💻 คู่มือการพัฒนาฮาร์ดแวร์และเฟิร์มแวร์ Zigbee สำหรับนักพัฒนา (Hardware & Firmware Development Guide)

---

## 1. ภาพรวมการพัฒนาอุปกรณ์ Zigbee 3.0 (Development Landscape)

ในอดีต การพัฒนาอุปกรณ์ Zigbee ต้องพึ่งพาชุดพัฒนาเฉพาะทางที่มีราคาสูง (เช่น TI Z-Stack บน CC2530 หรือ Silicon Labs Simplicity Studio) แต่ในปัจจุบัน ด้วยการเปิดตัวของชิป **Espressif ESP32-C6 และ ESP32-H2** ทำให้นักพัฒนาสามารถเขียนโค้ด Zigbee 3.0 ได้อย่างง่ายดายผ่าน:
* **Arduino IDE (ESP32 Board Package v3.0+)**
* **ESP-IDF (Espressif IoT Development Framework)**
* **ESPHome YAML (Low-Code / No-Code Framework)**

```
┌────────────────────────────────────────────────────────┐
│          FIRMWARE DEVELOPMENT PATHWAYS                │
└──────────────────────────┬─────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  ESP-IDF SDK  │   │  Arduino IDE  │   │ ESPHome YAML  │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ • ควบคุมลึกสุด │   │ • พัฒนาง่าย    │   │ • ไม่ต้องโค้ด  │
│ • Low-power   │   │ • ไลบรารีเยอะ  │   │ • คอมไพล์ตรง  │
│ • Production  │   │ • เหมาะทำ Demo│   │ • เข้า HA ทันที│
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## 2. การเลือกชิปไมโครคอนโทรลเลอร์ (Silicon Selection)

| ชิปไมโครคอนโทรลเลอร์ | ซีพียู (CPU Core) | การเชื่อมต่อไร้สาย (Radios) | แรม / แฟลช | เหมาะสำหรับงาน |
| :--- | :--- | :--- | :--- | :--- |
| **ESP32-C6 (แนะนำ)** | RISC-V 32-bit Single-core @ 160 MHz | **Wi-Fi 6 (2.4GHz) + Bluetooth 5 (LE) + Zigbee 3.0 / Thread (802.15.4)** | 512 KB SRAM / 4-8 MB Flash | โหนดเซนเซอร์อเนกประสงค์, โหนดสลับ Wi-Fi/Zigbee, และ Zigbee Router |
| **ESP32-H2** | RISC-V 32-bit Single-core @ 96 MHz | **Bluetooth 5 (LE) + Zigbee 3.0 / Thread (802.15.4)** *(ไม่มี Wi-Fi)* | 320 KB SRAM / 2-4 MB Flash | **เซนเซอร์ใส่ถ่าน (ZED) ที่ต้องการกินไฟต่ำที่สุด** ราคาประหยัดสุด |
| **TI CC2652P** | ARM Cortex-M4F @ 48 MHz + Sensor Controller | 802.15.4 Zigbee / Thread + PA (+20 dBm) | 88 KB SRAM / 352 KB Flash | เหมาะสำหรับทำ **Coordinator หลักของระบบ** |

---

## 3. สารบัญเอกสารในโฟลเดอร์นี้

* [esp32c6_zigbee_guide.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/04_firmware_hardware_dev/esp32c6_zigbee_guide.md) - โค้ดตัวอย่าง C++ การพัฒนา Zigbee End Device และ Router บน ESP32-C6
* [esphome_zigbee_yaml.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/04_firmware_hardware_dev/esphome_zigbee_yaml.md) - การสร้างเซนเซอร์ Zigbee ด้วย ESPHome YAML โดยไม่ต้องเขียนโค้ด C++
* [power_management_battery.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/04_firmware_hardware_dev/power_management_battery.md) - การคำนวณการใช้พลังงาน Deep Sleep, แบตเตอรี่ LiFePO4, และระบบ Solar Harvesting
