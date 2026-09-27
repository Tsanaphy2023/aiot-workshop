/*
  =============================================================================
  โครงการ: LEQs-AIoT & GoGo-IoT xAI Smart Farm System
  ไฟล์: leqs_iot_wifi_direct_firmware.ino
  บอร์ดที่รองรับ:
    - LEQs-IoT xAI v.1 (ESP32-C3 RISC-V Architecture)
    - GoGo-IoT v.2B (ESP32 Dual-Core Architecture)
  =============================================================================
  คุณสมบัติระบบเครือข่ายและการค้นหาอัตโนมัติ (Wi-Fi Zero-Config & Auto-Discovery):
    1. 📡 UDP Auto-Discovery (Port 8266):
       - ตอบสนองต่อสัญญาณสแกน "DISCOVER_LEQS_DEVICE" จากแอปพลิเคชัน LEQs_AIoT ทันที
       - ส่งข้อมูล Device ID, IP, MAC, ระดับสัญญาณ RSSI, และค่าเซนเซอร์แบบเรียลไทม์
    2. 🌐 mDNS Service:
       - ประกาศชื่อโดเมน leqs-farm-team<N>.local และบริการ _leqsiot._tcp
    3. ⚡ Embedded HTTP REST API Server (Port 80):
       - GET /api/info    -> ข้อมูลบอร์ดและเวอร์ชันเฟิร์มแวร์
       - GET /api/sensors -> ค่าเซนเซอร์ I2C (SHT30, BH1750), ความชื้นดิน และระดับน้ำ
       - GET /api/relay   -> สั่งเปิด/ปิดรีเลย์ (ch=1..5, state=0/1) พร้อมระบบป้องกันน้ำแห้ง
       - GET /api/estop   -> ตัดการทำงานรีเลย์ทุกช่องทันที (Emergency Stop)
    4. 🛡️ Fail-Safe Watchdog:
       - ตัดการทำงานปั๊มน้ำอัตโนมัติหากลูกลอยตรวจพบน้ำแห้ง หรือทำงานเกินเวลาที่กำหนด
  =============================================================================
*/

#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Wire.h>
#include <ArduinoJson.h>

// =============================================================================
// 1. การกำหนดหมายเลขกลุ่มและพินฮาร์ดแวร์
// =============================================================================
#define TEAM_NUMBER       3                   // หมายเลขกลุ่มประจำบอร์ด (ปรับตามกลุ่ม)
#define DEVICE_MODEL      "LEQs-IoT xAI"      // รุ่นบอร์ดฮาร์ดแวร์
#define FIRMWARE_VERSION  "2.2.0-direct-wifi"
#define UDP_DISCOVERY_PORT 8266               // พอร์ตรับการสแกนหาบอร์ด

#if defined(CONFIG_IDF_TARGET_ESP32C3)
  // พินสำหรับบอร์ด LEQs-IoT v.1 (ESP32-C3)
  #define PIN_SDA         8
  #define PIN_SCL         9
  #define PIN_SOIL_ADC    2                   // ADC1_CH2 สำหรับ Capacitive Soil Moisture
  #define PIN_FLOAT_SW    3                   // สวิตช์ลูกลอยตัดวงจรน้ำแห้ง (Active LOW)
  #define PIN_RELAY_PUMP  4                   // รีเลย์ 1: ปั๊มรดน้ำ
  #define PIN_RELAY_LIGHT 5                   // รีเลย์ 2: หลอดไฟปลูกพืช
  #define PIN_RELAY_3     6                   // รีเลย์ 3: พัดลมระบายอากาศ
  #define PIN_RELAY_4     7                   // รีเลย์ 4: วาล์วพ่นหมอก
  #define PIN_STATUS_LED  10                  // ไฟ LED แสดงสถานะบนบอร์ด
#else
  // พินสำหรับบอร์ด GoGo-IoT v.2B (ESP32 WROOM)
  #define PIN_SDA         21
  #define PIN_SCL         22
  #define PIN_SOIL_ADC    34
  #define PIN_FLOAT_SW    35
  #define PIN_RELAY_PUMP  25
  #define PIN_RELAY_LIGHT 26
  #define PIN_RELAY_3     27
  #define PIN_RELAY_4     14
  #define PIN_STATUS_LED  2
#endif

// ที่อยู่ I2C ของเซนเซอร์
#define SHT30_I2C_ADDR   0x44
#define BH1750_I2C_ADDR  0x23

// =============================================================================
// 2. เครือข่าย Wi-Fi ที่รองรับ (เชื่อมต่ออัตโนมัติ)
// =============================================================================
WiFiMulti wifiMulti;
WiFiUDP udpDiscovery;
WebServer server(80);

// =============================================================================
// 3. ตัวแปรเก็บสถานะเซนเซอร์และรีเลย์ (State Management)
// =============================================================================
float currentTemperature = 28.5;
float currentHumidity = 60.0;
float currentSoilMoisture = 50.0;
float currentLightLux = 350.0;
bool  isWaterLow = false;

// Edge Agriphysics & TinyML Metrics
float currentVPD = 1.05;
String currentPlantStress = "OPTIMAL_GROWTH";
bool  isSensorAnomaly = false;
String anomalyReason = "";

bool  relayPumpState = false;
bool  relayLightState = false;
bool  relay3State = false;
bool  relay4State = false;
bool  isEmergencyStopped = false;

unsigned long pumpStartTime = 0;
const unsigned long MAX_PUMP_RUNTIME_MS = 60000; // ตัดการทำงานอัตโนมัติหลัง 60 วินาที

// =============================================================================
// Edge Agriphysics: คำนวณ Vapor Pressure Deficit (VPD) ในหน่วย kPa
// =============================================================================
float calculateVPD(float tempC, float rhPercent) {
  // Tetens equation for saturation vapor pressure (kPa)
  float vpSat = 0.61078f * exp((17.27f * tempC) / (tempC + 237.3f));
  float vpAct = vpSat * (rhPercent / 100.0f);
  float vpd = vpSat - vpAct;
  return (vpd < 0.0f) ? 0.0f : vpd;
}

String evaluatePlantStress(float vpd) {
  if (vpd < 0.4f) return "LOW_TRANSPIRATION_FUNGAL_RISK";
  if (vpd <= 1.2f) return "OPTIMAL_GROWTH";
  if (vpd <= 1.6f) return "MILD_WATER_STRESS";
  return "HIGH_TRANSPIRATION_STRESS";
}

// TinyML & Edge Anomaly Detection for Smart Farm Sensors
void runEdgeAnomalyDetection() {
  isSensorAnomaly = false;
  anomalyReason = "";

  // 1. SHT30 Out-of-bounds check (ชำรุดหรือสายหลุด)
  if (currentTemperature < 2.0 || currentTemperature > 65.0 || currentHumidity <= 1.0 || currentHumidity > 100.0) {
    isSensorAnomaly = true;
    anomalyReason = "SHT30 sensor read error or wire disconnected";
    return;
  }

  // 2. Soil Moisture Float / Sensor disconnected check
  if (currentSoilMoisture <= 0.5) {
    isSensorAnomaly = true;
    anomalyReason = "Soil sensor disconnected or dry-air exposed";
    return;
  }
}

// =============================================================================
// 4. ฟังก์ชันอ่านค่าเซนเซอร์ฮาร์ดแวร์
// =============================================================================
void readSensors() {
  // 1. อ่านสวิตช์ลูกลอย (Active LOW: จมน้ำ=LOW/ปกติ, ลอยพ้นน้ำ=HIGH/แห้ง)
  isWaterLow = (digitalRead(PIN_FLOAT_SW) == HIGH);

  // 2. อ่านความชื้นในดินจาก Analog ADC
  int rawSoil = analogRead(PIN_SOIL_ADC);
  // ปรับเทียบช่วงค่า ADC 0-4095 เป็นเปอร์เซ็นต์ 0-100%
  float soilPercent = map(rawSoil, 3200, 1400, 0, 100);
  currentSoilMoisture = constrain(soilPercent, 0.0, 100.0);

  // 3. อ่านค่า SHT30 ผ่าน I2C
  Wire.beginTransmission(SHT30_I2C_ADDR);
  Wire.write(0x2C);
  Wire.write(0x06);
  if (Wire.endTransmission() == 0) {
    delay(20);
    Wire.requestFrom(SHT30_I2C_ADDR, 6);
    if (Wire.available() == 6) {
      uint16_t rawT = (Wire.read() << 8) | Wire.read();
      Wire.read(); // CRC
      uint16_t rawH = (Wire.read() << 8) | Wire.read();
      Wire.read(); // CRC
      currentTemperature = -45.0 + (175.0 * (float)rawT / 65535.0);
      currentHumidity = 100.0 * ((float)rawH / 65535.0);
    }
  }

  // 4. อ่านค่าแสง BH1750 ผ่าน I2C
  Wire.beginTransmission(BH1750_I2C_ADDR);
  Wire.write(0x10); // Continuously H-Resolution Mode
  if (Wire.endTransmission() == 0) {
    Wire.requestFrom(BH1750_I2C_ADDR, 2);
    if (Wire.available() == 2) {
      uint16_t rawL = (Wire.read() << 8) | Wire.read();
      currentLightLux = (float)rawL / 1.2;
    }
  }

  // 5. คำนวณ Edge Agriphysics และตรวจจับ Anomaly
  currentVPD = calculateVPD(currentTemperature, currentHumidity);
  currentPlantStress = evaluatePlantStress(currentVPD);
  runEdgeAnomalyDetection();

  // 6. ระบบความปลอดภัย: หากน้ำแห้ง ให้ตัดปั๊มทันที (Dry-Run Protection)
  if (isWaterLow && relayPumpState) {
    relayPumpState = false;
    digitalWrite(PIN_RELAY_PUMP, LOW);
    Serial.println("[FAIL-SAFE] ตรวจพบน้ำแห้ง! ปั๊มถูกตัดการทำงานอัตโนมัติ");
  }

  // 6. ตัดการทำงานปั๊มหากทำงานติดต่อกันเกินเวลา (Max Runtime Protection)
  if (relayPumpState && (millis() - pumpStartTime > MAX_PUMP_RUNTIME_MS)) {
    relayPumpState = false;
    digitalWrite(PIN_RELAY_PUMP, LOW);
    Serial.println("[FAIL-SAFE] ปั๊มทำงานครบกำหนดเวลา! สั่งหยุดอัตโนมัติ");
  }
}

// =============================================================================
// 5. การจัดการบริการ UDP Discovery (ตอบสนองแอปที่สแกนหาบอร์ด)
// =============================================================================
void handleUdpDiscovery() {
  int packetSize = udpDiscovery.parsePacket();
  if (packetSize > 0) {
    char packetBuffer[255];
    int len = udpDiscovery.read(packetBuffer, 254);
    if (len > 0) packetBuffer[len] = '\0';

    String message = String(packetBuffer);
    message.trim();

    // หากแอปพลิเคชันส่งสัญญาณค้นหา
    if (message.indexOf("DISCOVER_LEQS_DEVICE") >= 0 || message.indexOf("SCAN_BOARDS") >= 0) {
      StaticJsonDocument<512> doc;
      doc["device"] = DEVICE_MODEL;
      doc["model"] = "ESP32";
      doc["team"] = TEAM_NUMBER;
      doc["ip"] = WiFi.localIP().toString();
      doc["mac"] = WiFi.macAddress();
      doc["rssi"] = WiFi.RSSI();
      doc["firmware"] = FIRMWARE_VERSION;
      doc["uptime_sec"] = millis() / 1000;
      doc["water_low"] = isWaterLow;
      doc["e_stop"] = isEmergencyStopped;

      JsonObject sensors = doc.createNestedObject("sensors");
      sensors["soil"] = currentSoilMoisture;
      sensors["temperature"] = currentTemperature;
      sensors["humidity"] = currentHumidity;
      sensors["light_lux"] = currentLightLux;
      sensors["water_low"] = isWaterLow;

      JsonArray relays = doc.createNestedArray("relays");
      relays.add(relayPumpState ? 1 : 0);
      relays.add(relayLightState ? 1 : 0);
      relays.add(relay3State ? 1 : 0);
      relays.add(relay4State ? 1 : 0);

      String reply;
      serializeJson(doc, reply);

      // ส่งกลับไปยัง IP และพอร์ตของสมาร์ทโฟนที่ส่งสแกนมา
      udpDiscovery.beginPacket(udpDiscovery.remoteIP(), udpDiscovery.remotePort());
      udpDiscovery.print(reply);
      udpDiscovery.endPacket();

      Serial.printf("[UDP DISCOVERY] ตอบกลับแอปที่ IP: %s:%d\n", 
                    udpDiscovery.remoteIP().toString().c_str(), udpDiscovery.remotePort());
    }
  }
}

// =============================================================================
// 6. REST API Endpoints สำหรับเชื่อมต่อกับแอป LEQs_AIoT
// =============================================================================
void setupRestApi() {
  // CORS Headers เพื่อให้แอปพลิเคชันทุกแพลตฟอร์ม (รวมถึง Web) เรียกใช้งานได้
  server.enableCORS(true);

  // 1. GET /api/info
  server.on("/api/info", HTTP_GET, []() {
    StaticJsonDocument<300> doc;
    doc["status"] = "online";
    doc["device"] = DEVICE_MODEL;
    doc["team"] = TEAM_NUMBER;
    doc["ip"] = WiFi.localIP().toString();
    doc["mac"] = WiFi.macAddress();
    doc["rssi"] = WiFi.RSSI();
    doc["firmware"] = FIRMWARE_VERSION;
    doc["uptime"] = millis() / 1000;
    
    String res;
    serializeJson(doc, res);
    server.send(200, "application/json", res);
  });

  // 2. GET /api/sensors
  server.on("/api/sensors", HTTP_GET, []() {
    readSensors();
    StaticJsonDocument<512> doc;
    doc["temperature"] = currentTemperature;
    doc["humidity"] = currentHumidity;
    doc["soil_moisture"] = currentSoilMoisture;
    doc["light_lux"] = currentLightLux;
    doc["water_low"] = isWaterLow;
    doc["pump_active"] = relayPumpState;
    doc["light_active"] = relayLightState;
    // Edge Agriphysics & TinyML Telemetry
    doc["vpd"] = round(currentVPD * 100.0) / 100.0;
    doc["plant_stress"] = currentPlantStress;
    doc["anomaly_detected"] = isSensorAnomaly;
    doc["anomaly_message"] = anomalyReason;

    String res;
    serializeJson(doc, res);
    server.send(200, "application/json", res);
  });

  // 3. GET /api/relay?ch=1&state=1
  server.on("/api/relay", HTTP_GET, []() {
    if (isEmergencyStopped) {
      server.send(403, "application/json", "{\"error\":\"E-Stop active. Unlock first.\"}");
      return;
    }

    int ch = server.arg("ch").toInt();
    int st = server.arg("state").toInt();
    bool state = (st == 1);

    if (ch == 1) { // ปั๊มน้ำ
      if (state && isWaterLow) {
        server.send(400, "application/json", "{\"error\":\"Water level low. Dry-run locked!\"}");
        return;
      }
      relayPumpState = state;
      digitalWrite(PIN_RELAY_PUMP, state ? HIGH : LOW);
      if (state) pumpStartTime = millis();
    } else if (ch == 2) { // หลอดไฟปลูกพืช
      relayLightState = state;
      digitalWrite(PIN_RELAY_LIGHT, state ? HIGH : LOW);
    } else if (ch == 3) {
      relay3State = state;
      digitalWrite(PIN_RELAY_3, state ? HIGH : LOW);
    } else if (ch == 4) {
      relay4State = state;
      digitalWrite(PIN_RELAY_4, state ? HIGH : LOW);
    }

    StaticJsonDocument<200> doc;
    doc["success"] = true;
    doc["channel"] = ch;
    doc["state"] = state;
    doc["pump_on"] = relayPumpState;
    doc["light_on"] = relayLightState;

    String res;
    serializeJson(doc, res);
    server.send(200, "application/json", res);
  });

  // 4. GET /api/estop?state=1
  server.on("/api/estop", HTTP_GET, []() {
    int st = server.arg("state").toInt();
    isEmergencyStopped = (st == 1);

    if (isEmergencyStopped) {
      // ตัดวงจรรีเลย์ทุกช่องทันที
      relayPumpState = false;
      relayLightState = false;
      relay3State = false;
      relay4State = false;
      digitalWrite(PIN_RELAY_PUMP, LOW);
      digitalWrite(PIN_RELAY_LIGHT, LOW);
      digitalWrite(PIN_RELAY_3, LOW);
      digitalWrite(PIN_RELAY_4, LOW);
      Serial.println("[EMERGENCY STOP] สั่งตัดรีเลย์ทั้งหมดฉุกเฉิน!");
    }

    StaticJsonDocument<150> doc;
    doc["e_stop"] = isEmergencyStopped;
    doc["message"] = isEmergencyStopped ? "All relays disabled" : "E-Stop reset";

    String res;
    serializeJson(doc, res);
    server.send(200, "application/json", res);
  });

  server.begin();
  Serial.println("[HTTP] REST API Server พร้อมทำงานบนพอร์ต 80");
}

// =============================================================================
// 7. ฟังก์ชัน Setup & Loop หลัก
// =============================================================================
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=============================================");
  Serial.println("  LEQs-IoT xAI & GoGo-IoT Wi-Fi Direct Node  ");
  Serial.println("=============================================");

  // กำหนดโหมดพิน
  pinMode(PIN_FLOAT_SW, INPUT_PULLUP);
  pinMode(PIN_SOIL_ADC, INPUT);
  pinMode(PIN_RELAY_PUMP, OUTPUT);
  pinMode(PIN_RELAY_LIGHT, OUTPUT);
  pinMode(PIN_RELAY_3, OUTPUT);
  pinMode(PIN_RELAY_4, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);

  digitalWrite(PIN_RELAY_PUMP, LOW);
  digitalWrite(PIN_RELAY_LIGHT, LOW);
  digitalWrite(PIN_RELAY_3, LOW);
  digitalWrite(PIN_RELAY_4, LOW);
  digitalWrite(PIN_STATUS_LED, LOW);

  // เริ่มต้น I2C
  Wire.begin(PIN_SDA, PIN_SCL);

  // เพิ่มรายการ Wi-Fi เริ่มต้น
  wifiMulti.addAP("Jade Rower", "JT23456899");
  wifiMulti.addAP("Jade Tower", "JT23456899");
  wifiMulti.addAP("farm-iot-red", "iotfarmer");
  wifiMulti.addAP("tsanac", "c9twv3rd");
  wifiMulti.addAP("farm-laptop-red", "iotfarmer");
  wifiMulti.addAP("CMU-WiFi-IoT", "cmu_aiot2027");
  wifiMulti.addAP("Home-WiFi-2.4G", "12345678");

  Serial.println("[Wi-Fi] กำลังเชื่อมต่อเครือข่าย...");
  while (wifiMulti.run() != WL_CONNECTED) {
    delay(500);
    digitalWrite(PIN_STATUS_LED, !digitalRead(PIN_STATUS_LED));
    Serial.print(".");
  }

  digitalWrite(PIN_STATUS_LED, HIGH);
  Serial.println("\n[Wi-Fi] เชื่อมต่อสำเร็จ!");
  Serial.printf("  SSID: %s\n", WiFi.SSID().c_str());
  Serial.printf("  IP Address: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("  MAC Address: %s\n", WiFi.macAddress().c_str());

  // เริ่มต้น mDNS Service (leqs-farm-team3.local)
  String hostname = "leqs-farm-team" + String(TEAM_NUMBER);
  if (MDNS.begin(hostname.c_str())) {
    MDNS.addService("leqsiot", "tcp", 80);
    MDNS.addServiceTxt("leqsiot", "tcp", "team", String(TEAM_NUMBER));
    MDNS.addServiceTxt("leqsiot", "tcp", "model", DEVICE_MODEL);
    Serial.printf("[mDNS] ประกาศโดเมน: http://%s.local\n", hostname.c_str());
  }

  // เริ่มต้น UDP Discovery Listener
  udpDiscovery.begin(UDP_DISCOVERY_PORT);
  Serial.printf("[UDP] เปิดรับการสแกนหาบอร์ดบนพอร์ต: %d\n", UDP_DISCOVERY_PORT);

  // เริ่มต้น HTTP REST Server
  setupRestApi();
}

unsigned long lastSensorRead = 0;

void loop() {
  // รับคำขอ HTTP จากแอป LEQs_AIoT
  server.handleClient();

  // รับแพ็กเกจสแกนหาบอร์ดจากแอปผ่าน UDP Broadcast
  handleUdpDiscovery();

  // อ่านค่าเซนเซอร์ทุก 1 วินาที
  if (millis() - lastSensorRead >= 1000) {
    lastSensorRead = millis();
    readSensors();
  }
}
