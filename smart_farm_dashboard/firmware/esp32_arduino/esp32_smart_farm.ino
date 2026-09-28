/*
 * Smart Farm AIoT - ESP32 Arduino C++ Firmware
 * Board: ESP32 Dev Module / ESP32-C3 / NodeMCU-32S
 * Required Libraries:
 *  - WiFi (Built-in)
 *  - HTTPClient (Built-in)
 *  - ArduinoJson (Library Manager)
 *  - DHT sensor library by Adafruit
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "DHT.h"

// 1. ตั้งค่า Wi-Fi
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// 2. URL ของ Smart Farm Server
// เช่น: "http://192.168.1.50/cmu_aiot/smart_farm_dashboard/api/api.php?action=telemetry"
// หรือ: "http://192.168.1.50:5000/api/telemetry"
const char* serverUrl = "http://192.168.1.50/cmu_aiot/smart_farm_dashboard/api/api.php?action=telemetry";
const char* farmArea = "flower"; // 'flower', 'corn', 'grass'

// 3. กำหนดขา GPIO
#define DHTPIN 4
#define DHTTYPE DHT22
#define SOIL_PIN 34
#define PIN_VALVE 18
#define PIN_PUMP 19
#define PIN_MIST 21
#define PIN_FAN 22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n🚀 เริ่มต้นระบบ ESP32 Smart Farm Node...");

  // กำหนดโหมดขาเอาต์พุตรีเลย์
  pinMode(PIN_VALVE, OUTPUT);
  pinMode(PIN_PUMP, OUTPUT);
  pinMode(PIN_MIST, OUTPUT);
  pinMode(PIN_FAN, OUTPUT);

  digitalWrite(PIN_VALVE, LOW);
  digitalWrite(PIN_PUMP, LOW);
  digitalWrite(PIN_MIST, LOW);
  digitalWrite(PIN_FAN, LOW);

  dht.begin();

  // เชื่อมต่อ WiFi
  WiFi.begin(ssid, password);
  Serial.print("กำลังเชื่อมต่อ WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi เชื่อมต่อสำเร็จ! IP: " + WiFi.localIP().toString());
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    // 1. อ่านค่าเซนเซอร์
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (isnan(t)) t = 29.0;
    if (isnan(h)) h = 65.0;

    int rawSoil = analogRead(SOIL_PIN);
    // แปลง 0-4095 เป็น % (ปรับแต่งตามหัวโพรบจริง)
    float soilPct = 100.0 - ((float)(rawSoil - 1400) / (3200 - 1400) * 100.0);
    if (soilPct < 0.0) soilPct = 0.0;
    if (soilPct > 100.0) soilPct = 100.0;

    // 2. สร้าง JSON Payload
    StaticJsonDocument<256> doc;
    doc["area"] = farmArea;
    doc["soil"] = round(soilPct * 10.0) / 10.0;
    doc["temp"] = round(t * 10.0) / 10.0;
    doc["humidity"] = round(h * 10.0) / 10.0;
    doc["light"] = 42500;

    String jsonString;
    serializeJson(doc, jsonString);

    Serial.println("\n[Sending Telemetry] " + jsonString);

    // 3. ส่ง HTTP POST
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(jsonString);

    if (httpCode > 0) {
      String response = http.getString();
      Serial.println("[Server Response] " + response);

      // 4. ถอดรหัสคำสั่งควบคุม
      StaticJsonDocument<512> respDoc;
      DeserializationError err = deserializeJson(respDoc, response);
      if (!err && respDoc.containsKey("commands")) {
        JsonObject cmds = respDoc["commands"];
        bool valve = cmds["valve"] | false;
        bool pump  = cmds["pump"]  | false;
        bool mist  = cmds["mist"]  | false;
        bool fan   = cmds["fan"]   | false;

        digitalWrite(PIN_VALVE, valve ? HIGH : LOW);
        digitalWrite(PIN_PUMP,  pump  ? HIGH : LOW);
        digitalWrite(PIN_MIST,  mist  ? HIGH : LOW);
        digitalWrite(PIN_FAN,   fan   ? HIGH : LOW);

        Serial.printf("[Relay State] Valve:%d, Pump:%d, Mist:%d, Fan:%d\n", valve, pump, mist, fan);
      }
    } else {
      Serial.printf("[Error] HTTP Request Failed: %s\n", http.errorToString(httpCode).c_str());
    }
    http.end();
  } else {
    Serial.println("❌ WiFi หลุดการเชื่อมต่อ กำลังเชื่อมต่อใหม่...");
    WiFi.reconnect();
  }

  // ส่งทุกๆ 5 วินาที
  delay(5000);
}
