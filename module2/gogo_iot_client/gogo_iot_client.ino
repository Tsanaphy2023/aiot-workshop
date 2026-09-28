/*
  =============================================================================
  โครงงาน AIoT สำหรับเกษตรแม่นยำ (CMU Lifelong / RBRU)
  บอร์ด: GoGo-IoT v.2B (พัฒนาโดย อ.ดร.อานันท์ สีห์พิทักษ์เกียรติ)
  สถาปัตยกรรม: ESP32-C3 / ESP32 Dual-Core
  เวอร์ชัน: 2.1 (Anti-Congestion, Non-Blocking, Multi-WiFi & Jitter Telemetry)
  =============================================================================
*/

#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <ArduinoJson.h>

WiFiMulti wifiMulti;

// --- 1. ตั้งค่าเครือข่าย WiFi หลายชุด (Multi-SSID Auto Fallback) ---
// บอร์ดจะค้นหาและเชื่อมต่อกับตัวที่สัญญาณแรงที่สุดโดยอัตโนมัติ
const char* AP_SSID_1 = "farm-iot-red";
const char* AP_PASS_1 = "iotfarmer";

const char* AP_SSID_2 = "tsanac";
const char* AP_PASS_2 = "c9twv3rd";

const char* AP_SSID_3 = "farm-laptop-red";
const char* AP_PASS_3 = "iotfarmer";

// --- 2. ที่อยู่ API Server (รองรับ XAMPP และ Home Assistant) ---
// ปรับเปลี่ยน IP ตามเครื่องโฮสต์ที่รัน XAMPP Dashboard
const String serverUrl = "http://10.243.96.9/cmu_aiot/smart_farm_dashboard/api/api.php?action=telemetry";

// --- 3. การกำหนดพินฮาร์ดแวร์บอร์ด GoGo-IoT (รองรับทั้ง ESP32 ทั่วไป และ ESP32-C3) ---
#if defined(CONFIG_IDF_TARGET_ESP32C3)
  // สำหรับ GoGo-IoT ชิป ESP32-C3 (ป้องกันชนพิน USB CDC 18, 19)
  #define I2C_SDA 8
  #define I2C_SCL 9
  #define PIN_CONFIGURABLE_1 4   // ขั้วต่อสีเขียวช่อง 1 (สั่งเปิด/ปิด รีเลย์/วาล์ว)
  #define PIN_CONFIGURABLE_2 5   // ขั้วต่อสีเขียวช่อง 2 (โพรบวัดดิน)
#else
  // สำหรับ ESP32 WROOM รุ่นดั้งเดิม
  #define I2C_SDA 21
  #define I2C_SCL 22
  #define PIN_CONFIGURABLE_1 16
  #define PIN_CONFIGURABLE_2 19
#endif

// ตัวแปรจับเวลาแบบ Non-blocking พร้อม Random Jitter (กระจายทราฟฟิกไม่ให้ชนกัน)
unsigned long lastSendTime = 0;
unsigned long currentInterval = 10000; // เริ่มต้น 10 วินาที
unsigned long lastWifiCheck = 0;

// ฟังก์ชันคำนวณ Vapor Pressure Deficit (VPD) หน่วย kPa ตามสมการ Tetens
float calculateVPD(float tempC, float humRH) {
  float es = 0.61078 * exp((17.27 * tempC) / (tempC + 237.3));
  float vpd = es * (1.0 - (humRH / 100.0));
  return vpd;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n==================================================");
  Serial.println("🚀 GoGo-IoT v.2B Resilient Firmware v2.1 Starting");
  Serial.println("   [Anti-Congestion & Zero-Hang Architecture]");
  Serial.println("==================================================");

  // 1. ตั้งค่าขาพินควบคุมอย่างปลอดภัย
  pinMode(PIN_CONFIGURABLE_1, OUTPUT);
  pinMode(PIN_CONFIGURABLE_2, OUTPUT);
  digitalWrite(PIN_CONFIGURABLE_1, LOW);
  digitalWrite(PIN_CONFIGURABLE_2, LOW);

  // 2. เริ่มต้นบัส I2C
  Wire.begin(I2C_SDA, I2C_SCL);
  Serial.printf("🔍 Scanning I2C Bus (SDA=%d, SCL=%d)...\n", I2C_SDA, I2C_SCL);
  byte count = 0;
  for (byte i = 1; i < 127; i++) {
    Wire.beginTransmission(i);
    if (Wire.endTransmission() == 0) {
      Serial.printf("   - พบอุปกรณ์ I2C ที่ Address: 0x%02X\n", i);
      count++;
    }
  }
  Serial.printf("   สรุป: พบเซนเซอร์ I2C รวม %d ตัว\n", count);

  // 3. ปรับแต่ง WiFi แบบประสิทธิภาพสูงสำหรับพื้นที่คนหนาแน่น
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false); // ปิดโหมดหลับ เพิ่มความเสถียรในการรับส่งข้อมูลในห้องอบรม
  WiFi.setTxPower(WIFI_POWER_19_5dBm); // กำลังส่งสูงสุดทะลุคลื่นรบกวน

  // ลงทะเบียนเครือข่าย WiFi ที่สามารถเชื่อมต่อได้
  wifiMulti.addAP(AP_SSID_1, AP_PASS_1);
  wifiMulti.addAP(AP_SSID_2, AP_PASS_2);
  wifiMulti.addAP(AP_SSID_3, AP_PASS_3);

  Serial.println("🌐 กำลังเชื่อมต่อเครือข่าย (Multi-WiFi Scanning)...");
  
  // พยายามเชื่อมต่อแบบ Non-blocking สูงสุด 6 วินาทีตอนบูต
  int attempts = 0;
  while (wifiMulti.run() != WL_CONNECTED && attempts < 12) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.printf("   SSID: %s | IP: %s | RSSI: %d dBm\n", WiFi.SSID().c_str(), WiFi.localIP().toString().c_str(), WiFi.RSSI());
  } else {
    Serial.println("\n⚠️ WiFi Connection Timeout! เข้าสู่โหมดออฟไลน์อัตโนมัติ (จะลองใหม่ใน Background)");
  }
}

void loop() {
  unsigned long now = millis();

  // ตรวจสอบและเชื่อมต่อ WiFi ซ้ำทุก 15 วินาทีแบบ Background (ไม่บล็อกการทำงาน)
  if (now - lastWifiCheck >= 15000) {
    lastWifiCheck = now;
    if (WiFi.status() != WL_CONNECTED) {
      wifiMulti.run();
    }
  }

  // รอบการอ่านค่าและส่งข้อมูลตาม Interval + Random Jitter
  if (now - lastSendTime >= currentInterval) {
    lastSendTime = now;
    
    // สุ่ม Jitter 0 - 3000ms เพื่อกระจายเวลาส่ง ไม่ให้บอร์ด 100+ ตัวส่งพร้อมกันจนเครือข่ายล่ม
    currentInterval = 10000 + random(0, 3000);

    // 1. อ่านค่าเซนเซอร์จำลองหรือเซนเซอร์จริง
    float temp = 28.5 + (random(-10, 10) / 10.0);       // °C
    float hum = 65.0 + (random(-20, 20) / 10.0);        // %RH
    float pressure = 1012.8;                            // hPa
    float light = 520.0 + random(-50, 50);              // Lux
    float soilTension = 32.0;                           // kPa
    float vpd = calculateVPD(temp, hum);

    Serial.printf("\n📊 [GoGo-IoT] T: %.1f°C | RH: %.1f%% | Lux: %.0f | VPD: %.3fkPa | Status: %s\n",
                  temp, hum, light, vpd, (WiFi.status() == WL_CONNECTED ? "ONLINE" : "OFFLINE"));

    // 2. ลอจิกควบคุมอัตโนมัติในตัว (Fail-safe แม้เน็ตหลุด)
    if (soilTension > 45.0) {
      digitalWrite(PIN_CONFIGURABLE_1, HIGH);
      Serial.println("   🌱 [Fail-safe Engine] ดินแห้ง > 45 kPa -> เปิดวาล์วรดน้ำอัตโนมัติ");
    } else {
      digitalWrite(PIN_CONFIGURABLE_1, LOW);
    }

    // 3. ส่งข้อมูล HTTP POST เมื่อมีเครือข่าย WiFi
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.setTimeout(3500); // Timeout 3.5 วินาที ป้องกันโปรแกรมค้างหากเซิร์ฟเวอร์ตอบช้า
      
      if (http.begin(serverUrl)) {
        http.addHeader("Content-Type", "application/json");

        // จัดรูปแบบ JSON
        StaticJsonDocument<256> doc;
        doc["area"] = "flower";
        doc["node_id"] = "GoGo-IoT-Red";
        doc["temp"] = temp;
        doc["humidity"] = hum;
        doc["light"] = (int)light;
        doc["soil"] = soilTension;
        doc["vpd"] = vpd;

        String jsonPayload;
        serializeJson(doc, jsonPayload);

        int httpCode = http.POST(jsonPayload);
        if (httpCode > 0) {
          Serial.printf("   ➡️ Telemetry Sent -> Server Status: %d\n", httpCode);
          if (httpCode == 200) {
            String resp = http.getString();
            StaticJsonDocument<256> respDoc;
            if (deserializeJson(respDoc, resp) == DeserializationError::Ok) {
              if (respDoc.containsKey("commands")) {
                bool valveCmd = respDoc["commands"]["valve"];
                if (valveCmd) {
                  digitalWrite(PIN_CONFIGURABLE_1, HIGH);
                  Serial.println("   🚰 เซิร์ฟเวอร์สั่ง: เปิดวาล์วน้ำ (VALVE = ON)");
                }
              }
            }
          }
        } else {
          Serial.printf("   ⚠️ POST ล้มเหลว: %s\n", http.errorToString(httpCode).c_str());
        }
        http.end();
      }
    }
  }
}
