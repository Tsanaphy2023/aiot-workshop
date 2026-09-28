# 📄 การพัฒนาเซนเซอร์ Zigbee ด้วย ESPHome YAML แบบ Low-Code (ESPHome Zigbee Framework)

---

## 1. จุดเด่นของการใช้ ESPHome ในงาน Zigbee

สำหรับนักพัฒนาหรือผู้ปฏิบัติการที่ไม่ต้องการเขียนภาษา C++ ทีละบรรทัด **ESPHome (เวอร์ชัน 2024.x ขึ้นไป)** ได้เพิ่มการรองรับโปรโตคอล **Zigbee บนชิป ESP32-C6 และ ESP32-H2** แบบสมบูรณ์:
* **ไม่ต้องเขียนโค้ดภาษา C++:** กำหนดค่าผ่านไฟล์คอนฟิก **YAML** เพียงไฟล์เดียว
* **รองรับเซนเซอร์ยอดนิยมกว่า 1,000 ชนิด:** เช่น BME280, SHT3x, DS18B20, Modbus RS485
* **ผสานรวมกับ Home Assistant & Zigbee2MQTT อัตโนมัติ:** เมื่อ Join เข้าเครือข่าย ค่า Entity ทั้งหมดจะถูกแมปเข้าแดชบอร์ดทันที

---

## 2. ตัวอย่างไฟล์คอนฟิกสมบูรณ์ (`esp32c6_soil_weather.yaml`)

```yaml
esphome:
  name: esp32c6-farm-sensor
  friendly_name: "Greenhouse Soil & Weather Node"

esp32:
  board: esp32-c6-devkitc-1
  framework:
    type: esp-idf

# กำหนดสแต็ก Zigbee 3.0
zigbee:
  # โหมด End Device สำหรับเซนเซอร์ใส่ถ่าน
  device_type: END_DEVICE
  
# บัสสื่อสาร I2C
i2c:
  sda: GPIO21
  scl: GPIO22
  scan: true

# รายการเซนเซอร์
sensor:
  # 1. เซนเซอร์สภาพอากาศ Sensirion SHT30
  - platform: sht3xd
    temperature:
      name: "Greenhouse Air Temperature"
      id: air_temp
      accuracy_decimals: 1
    humidity:
      name: "Greenhouse Air Humidity"
      id: air_hum
      accuracy_decimals: 1
    address: 0x44
    update_interval: 60s

  # 2. เซนเซอร์ความชื้นดินแบบ Capacitive (ADC)
  - platform: adc
    pin: GPIO2
    name: "Soil Moisture Raw Voltage"
    id: soil_raw
    update_interval: 60s
    unit_of_measurement: "%"
    filters:
      # แปลงแรงดัน 2.8V (แห้ง) ถึง 1.2V (เปียก) เป็นเปอร์เซ็นต์ 0-100%
      - calibrate_linear:
          - 2.8 -> 0.0
          - 1.2 -> 100.0

  # 3. ตรวจวัดแรงดันแบตเตอรี่ในตัว
  - platform: adc
    pin: GPIO0
    name: "Node Battery Voltage"
    update_interval: 300s
    filters:
      - multiply: 2.0 # ผ่านวงจร Voltage Divider 1:1

# จัดการพลังงาน Deep Sleep (หลับ 10 นาที ตื่นมาวัดและส่ง 1 รอบ)
deep_sleep:
  run_duration: 15s   # ตื่นมาทำงานและส่งข้อมูล 15 วินาที
  sleep_duration: 10min # เข้าโหมดหลับลึก 10 นาที
```

---

## 3. ขั้นตอนการคอมไพล์และแฟลชลงบอร์ด (Compile & Flash Workflow)

1. เสียบบอร์ด ESP32-C6 เข้ากับคอมพิวเตอร์ผ่านสาย USB Type-C
2. รันคำสั่งคอมไพล์และอัปโหลดผ่าน ESPHome CLI:
   ```bash
   esphome run esp32c6_soil_weather.yaml
   ```
3. บอร์ดจะคอมไพล์ผ่าน ESP-IDF และอัปโหลดเฟิร์มแวร์เข้าบอร์ดผ่าน Serial Port
4. เมื่ออัปโหลดเสร็จสิ้น บอร์ดจะเริ่มค้นหา Zigbee Coordinator และขอ Pair เข้าสู่เครือข่ายโดยอัตโนมัติ
