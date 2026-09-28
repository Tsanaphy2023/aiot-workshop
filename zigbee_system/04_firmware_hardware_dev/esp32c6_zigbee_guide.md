# 🛠️ คู่มือการพัฒนาเฟิร์มแวร์ ESP32-C6 Zigbee 3.0 End Device (ESP32-C6 Firmware Development)

---

## 1. การเตรียมสภาพแวดล้อมการพัฒนา (Development Setup)

ตั้งแต่บอร์ดแพ็กเกจ **ESP32 Arduino Core v3.0.0 ขึ้นไป** ได้มีการผนวกไลบรารี **Native Zigbee 3.0** เข้ามาในตัว ทำให้สามารถเขียนโค้ดภาษา C++ บน Arduino IDE หรือ PlatformIO ได้โดยตรง:

1. **ติดตั้งบอร์ดใน Arduino IDE:**
   * เพิ่ม URL ใน Additional Board Manager: `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   * ติดตั้งบอร์ด **esp32 (เวอร์ชัน >= 3.0.2)**
2. **การตั้งค่าบอร์ดใน Tools Menu:**
   * **Board:** `ESP32C6 Dev Module` (หรือ `Seeed Studio XIAO ESP32C6`)
   * **Zigbee Mode:** `Zigbee End Device (ZED)`
   * **Partition Scheme:** `Zigbee 4MB with Spiffs` (ต้องเลือก Partition ที่มีพื้นที่สำหรับ NVS Zigbee Stack)
   * **Upload Speed:** `921600`

---

## 2. ตัวอย่างซอร์สโค้ดสมบูรณ์: โหนดวัดอุณหภูมิ ความชื้น และความชื้นดิน (Production Code)

โค้ดตัวอย่างด้านล่างใช้ไลบรารีมาตรฐาน `Zigbee.h` สร้างอุปกรณ์ Zigbee End Device รายงานค่าอุณหภูมิและความชื้นเข้า Zigbee2MQTT หรือ Home Assistant ตามมาตรฐาน ZCL สากล:

```cpp
/*
 * ESP32-C6 Zigbee 3.0 Smart Agriculture Sensor Node
 * Sensors: Sensirion SHT30 (I2C) & Capacitive Soil Moisture Probe (ADC)
 * Board: Seeed Studio XIAO ESP32C6 / ESP32-C6-WROOM-1
 */

#include "Zigbee.h"
#include <Wire.h>

// กำหนดพอร์ต I2C
#define I2C_SDA 21
#define I2C_SCL 22
#define SHT30_I2C_ADDR 0x44

// กำหนดขาอนาล็อกสำหรับเซนเซอร์ความชื้นดิน
#define SOIL_ADC_PIN 2

// กำหนดพิกัด Endpoint
#define TEMP_HUM_ENDPOINT 1

// ประกาศออบเจกต์เซนเซอร์ Zigbee มาตรฐาน ZCL
ZigbeeTempSensor zbTemp(TEMP_HUM_ENDPOINT);
ZigbeeHumiditySensor zbHum(TEMP_HUM_ENDPOINT);

// ตัวแปรสำหรับอ่านค่า
float airTemp = 0.0;
float airHum = 0.0;
int soilRaw = 0;
float soilPercent = 0.0;

// ฟังก์ชันอ่านค่าเซนเซอร์ SHT30 ผ่าน I2C
bool readSHT30(float &temp, float &hum) {
  Wire.beginTransmission(SHT30_I2C_ADDR);
  Wire.write(0x2C); // High repeatability measurement
  Wire.write(0x06);
  if (Wire.endTransmission() != 0) return false;

  delay(20); // รอการแปลงสัญญาณ

  Wire.requestFrom(SHT30_I2C_ADDR, 6);
  if (Wire.available() == 6) {
    uint8_t data[6];
    for (int i = 0; i < 6; i++) data[i] = Wire.read();

    uint16_t rawT = (data[0] << 8) | data[1];
    uint16_t rawH = (data[3] << 8) | data[4];

    temp = -45.0 + 175.0 * ((float)rawT / 65535.0);
    hum = 100.0 * ((float)rawH / 65535.0);
    return true;
  }
  return false;
}

// ฟังก์ชันอ่านค่าความชื้นดิน
float readSoilMoisture() {
  // สุ่มอ่านหลายรอบเพื่อหาค่าเฉลี่ย
  long sum = 0;
  for (int i = 0; i < 16; i++) {
    sum += analogRead(SOIL_ADC_PIN);
    delay(2);
  }
  int raw = sum / 16;
  
  // ปรับเทียบค่าตามชนิดดิน (เช่น 3000 = แห้งสนิท 0%, 1200 = น้ำขัง 100%)
  const int dryVal = 3000;
  const int wetVal = 1200;
  float pct = map(raw, dryVal, wetVal, 0, 100);
  pct = constrain(pct, 0.0, 100.0);
  return pct;
}

void setup() {
  Serial.begin(115200);
  Wire.begin(I2C_SDA, I2C_SCL);
  analogReadResolution(12);

  Serial.println("=========================================");
  Serial.println("Starting ESP32-C6 Zigbee Agriculture Node");
  Serial.println("=========================================");

  // 1. กำหนดข้อมูลประจำอุปกรณ์ (Manufacturer & Model)
  zbTemp.setManufacturerAndModel("DeepAIoT", "SoilClimateSensor-C6");
  
  // 2. ลงทะเบียนเอนด์พอยต์
  Zigbee.addEndpoint(&zbTemp);
  Zigbee.addEndpoint(&zbHum);

  // 3. เริ่มต้นสแต็ก Zigbee ในโหมด End Device
  if (!Zigbee.begin(ZIGBEE_END_DEVICE)) {
    Serial.println("Failed to start Zigbee stack!");
    Serial.println("Rebooting in 3 seconds...");
    delay(3000);
    esp_restart();
  }

  Serial.println("Connecting / Pairing with Zigbee Network...");
  while (!Zigbee.connected()) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\n✅ Zigbee Connected Successfully to Coordinator!");
}

void loop() {
  // อ่านค่าจากเซนเซอร์จริง
  if (readSHT30(airTemp, airHum)) {
    Serial.printf("[SENSOR] Air Temp: %.1f °C, Air Hum: %.1f %%\n", airTemp, airHum);
    // ส่งค่าขึ้นเครือข่าย Zigbee ผ่าน ZCL Clusters
    zbTemp.setTemperature(airTemp);
    zbHum.setHumidity(airHum);
  } else {
    Serial.println("[ERROR] SHT30 sensor read failed!");
  }

  soilPercent = readSoilMoisture();
  Serial.printf("[SENSOR] Soil Moisture: %.1f %%\n", soilPercent);

  // หน่วงเวลาก่อนรอบถัดไป (หรือเข้าสู่ Deep Sleep ในงานประหยัดพลังงาน)
  Serial.println("Sleeping for 60 seconds...");
  delay(60000);
}
```

---

## 3. ขั้นตอนการนำเข้าสู่ Zigbee2MQTT (Pairing & Commissioning)

1. เปิดหน้า Web GUI ของ **Zigbee2MQTT** (พอร์ต `8080`)
2. คลิกปุ่ม **"Permit Join (All)"** ที่มุมบนขวา เพื่อเปิดรับอุปกรณ์ใหม่
3. จ่ายไฟให้บอร์ด ESP32-C6 บอร์ดจะทำการค้นหาช่องสัญญาณและขอ Pair อัตโนมัติ
4. บนหน้าจอ Zigbee2MQTT จะขึ้นแจ้งเตือน:  
   `Device '0x404cca... ' joined the network`
5. เปลี่ยนชื่ออุปกรณ์ (Rename) เป็นชื่อที่เป็นมิตร เช่น `greenhouse_bed_1`
6. ข้อมูลอุณหภูมิและความชื้นจะเริ่มสตรีมเข้าสู่แดชบอร์ดทันที!
