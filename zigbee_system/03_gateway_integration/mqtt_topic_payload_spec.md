# 📨 ข้อกำหนดโครงสร้างข้อมูล JSON และหัวข้อ MQTT (MQTT Topic & Payload Specification)

---

## 1. การกำหนดค่า Zigbee2MQTT (`configuration.yaml`)

ไฟล์คอนฟิกพื้นฐานสำหรับเชื่อมต่อ USB Coordinator และส่งข้อมูลเข้า MQTT Broker ในระบบ XAMPP / Mosquitto:

```yaml
# /opt/zigbee2mqtt/data/configuration.yaml
homeassistant: true
permit_join: true

mqtt:
  base_topic: zigbee2mqtt
  server: 'mqtt://localhost:1883'
  # user: 'my_mqtt_user'
  # password: 'my_mqtt_password'

serial:
  port: /dev/ttyUSB0          # หรือพอร์ต COM บน Windows
  adapter: zstack             # สำหรับชิป CC2652P (Sonoff ZBDongle-P)
  baudrate: 115200
  rtscts: false

advanced:
  pan_id: 0x1A62
  ext_pan_id: [0xDD, 0xDD, 0xDD, 0xDD, 0xDD, 0xDD, 0xDD, 0xDD]
  channel: 25                 # หลบหลีกสัญญาณ Wi-Fi กวน แนะนำช่อง 25
  network_key: GENERATE
  log_level: info

frontend:
  port: 8080                  # Web GUI สำหรับมอนิเตอร์และจับคู่อุปกรณ์
```

---

## 2. โครงสร้างหัวข้อ MQTT (MQTT Topics Convention)

| ประเภทการสื่อสาร | รูปแบบ MQTT Topic | คำอธิบาย |
| :--- | :--- | :--- |
| **เซนเซอร์ส่งข้อมูลขึ้น (Telemetry)** | `zigbee2mqtt/<device_friendly_name>` | ข้อมูล JSON จากเซนเซอร์ส่งมายัง Gateway |
| **เซิร์ฟเวอร์สั่งการลงไป (Command)** | `zigbee2mqtt/<device_friendly_name>/set` | ส่งคำสั่ง JSON ไปยังรีเลย์หรือวาล์วน้ำ |
| **ดึงสถานะล่าสุด (Get State)** | `zigbee2mqtt/<device_friendly_name>/get` | ร้องขอให้อุปกรณ์ส่งค่าล่าสุดกลับมา |
| **สถานะการเชื่อมต่อ (Bridge State)** | `zigbee2mqtt/bridge/state` | สถานะของ Gateway (`online` หรือ `offline`) |

---

## 3. ตัวอย่างโครงสร้าง JSON Payload มาตรฐาน (JSON Payload Examples)

### 3.1 โหนดวัดสภาพดินและธาตุอาหาร (Soil NPK & Chemistry Sensor)
* **Topic:** `zigbee2mqtt/greenhouse_soil_node_01`
* **Payload (JSON):**
```json
{
  "device_id": "0x00124b002934abcd",
  "friendly_name": "greenhouse_soil_node_01",
  "soil_moisture": 45.8,
  "soil_temperature": 26.4,
  "soil_ec": 780,
  "soil_ph": 6.35,
  "nitrogen": 45,
  "phosphorus": 22,
  "potassium": 68,
  "battery": 92,
  "voltage": 3210,
  "linkquality": 142
}
```
*คำอธิบายคีย์เสริม:*
* `battery`: เปอร์เซ็นต์แบตเตอรี่คงเหลือ ($0 - 100\%$)
* `voltage`: แรงดันแบตเตอรี่ หน่วยมิลลิโวลต์ ($mV$)
* `linkquality`: คุณภาพสัญญาณวิทยุ (Link Quality Indicator - LQI ค่า $0 - 255$, ถ้ามากกว่า 80 ถือว่าสัญญาณดีเยี่ยม)

---

### 3.2 โหนดสถานีตรวจวัดจุลภูมิอากาศ (Micro-climate Weather Node)
* **Topic:** `zigbee2mqtt/greenhouse_weather_01`
* **Payload (JSON):**
```json
{
  "temperature": 32.5,
  "humidity": 68.2,
  "pressure": 1012.4,
  "illuminance": 18450,
  "illuminance_lux": 18450,
  "vpd": 1.54,
  "co2": 520,
  "battery": 88,
  "linkquality": 168
}
```

---

### 3.3 โหนดควบคุมวาล์วน้ำอัจฉริยะ (Zigbee Smart Water Valve)
* **การสั่งเปิดน้ำ (Publish Command):**
  * **Topic:** `zigbee2mqtt/valve_zone_1/set`
  * **Payload:** `{"state": "ON"}` หรือตั้งเวลาเปิดอัตโนมัติ `{"state": "ON", "timer": 600}` (เปิด 10 นาทีแล้วตัด)
* **การสั่งปิดน้ำ:**
  * **Topic:** `zigbee2mqtt/valve_zone_1/set`
  * **Payload:** `{"state": "OFF"}`
* **สถานะตอบกลับจากวาล์ว:**
  * **Topic:** `zigbee2mqtt/valve_zone_1`
  * **Payload:**
```json
{
  "state": "ON",
  "water_consumed": 125.4,
  "battery": 95,
  "linkquality": 128
}
```
