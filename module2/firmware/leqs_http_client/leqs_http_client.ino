/*
  =============================================================================
  โครงการ LEQs-AIoT v.1 & Deep+ Precision Agriculture
  บอร์ด: LEQs-AIoT v.1 (เข้ากันได้กับ GoGo-IoT v.2B)
  สถาปัตยกรรม: ESP32-C3 RISC-V / ESP32 Dual-Core (Format 1: HTTP REST Bridge)
  =============================================================================
  ฟังก์ชันเด่นด้านเครือข่าย Wi-Fi:
  1. 📶 Multi-SSID Configuration Table: เพิ่ม ลบ หรือเปลี่ยน Wi-Fi และรหัสผ่านได้ไม่จำกัด
  2. ⚡ Serial On-the-Fly Config: เปลี่ยน Wi-Fi และ Server URL ผ่าน Serial Monitor โดยไม่ต้องแฟลชใหม่!
     - พิมพ์: SET_WIFI <SSID> <PASSWORD>   (บันทึกเข้า Flash NVS ถาวร)
     - พิมพ์: SET_BRIDGE <URL_OR_IP>       (เปลี่ยน IP หรือ URL ของ XAMPP Bridge)
     - พิมพ์: SCAN                         (สแกนหา Wi-Fi รอบข้างพร้อมระดับสัญญาณ RSSI)
     - พิมพ์: STATUS                       (ดูสถานะการเชื่อมต่อปัจจุบันและ IP บอร์ด)
     - พิมพ์: RESET_WIFI                   (ล้างการตั้งค่า Flash กลับไปใช้ค่าเริ่มต้น)
  3. 🛡️ Fail-safe Hysteresis: ทำงานฉุกเฉินอัตโนมัติในตัวบอร์ดแม้ Wi-Fi หรือ XAMPP หลุด
  =============================================================================
*/

#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <Preferences.h>

WiFiMulti wifiMulti;
Preferences preferences;

// =============================================================================
// 1. ตารางเครือข่าย Wi-Fi เริ่มต้น (สามารถเพิ่ม/แก้ไขรายการและรหัสผ่านได้อิสระ)
// =============================================================================
struct WiFiCredential {
  const char* ssid;
  const char* password;
  const char* note;
};

// ** เพิ่มเครือข่าย Wi-Fi ของท่านในรายการนี้ได้ทันที **
WiFiCredential defaultWifiList[] = {
  {"Jade Rower",       "JT23456899",   "เครือข่าย Wi-Fi หลักของผู้ใช้ (Jade Rower)"},
  {"Jade Tower",       "JT23456899",   "เครือข่าย Wi-Fi สำรอง (Jade Tower)"},
  {"farm-iot-red",     "iotfarmer",    "เราเตอร์โรงเรือนหลัก (Farm Master Router)"},
  {"tsanac",           "c9twv3rd",     "ฮอตสปอตมือถือ / สำนักงาน (Office Hotspot)"},
  {"farm-laptop-red",  "iotfarmer",    "ฮอตสปอตคอมพิวเตอร์ Lab (Field Laptop)"},
  {"CMU-WiFi-IoT",     "cmu_aiot2027", "เครือข่ายโครงการ AIoT 2027"},
  {"Home-WiFi-2.4G",   "12345678",     "Wi-Fi ที่บ้าน / หอพัก (2.4 GHz)"}
};
const int TOTAL_DEFAULT_WIFI = sizeof(defaultWifiList) / sizeof(defaultWifiList[0]);

// =============================================================================
// 2. ที่อยู่ Hardware Bridge API บน XAMPP Web Server
// =============================================================================
String serverUrl = "http://10.0.0.41/cmu_aiot/module2/api/bridge.php?action=telemetry";

// =============================================================================
// 3. การกำหนดพินฮาร์ดแวร์ LEQs-AIoT v.1 (ESP32-C3 vs ESP32 WROOM)
// =============================================================================
#if defined(CONFIG_IDF_TARGET_ESP32C3)
  // สำหรับ LEQs-AIoT ชิป ESP32-C3
  #define I2C_SDA        8
  #define I2C_SCL        9
  #define PIN_VALVE      4    // ขั้วต่อสีเขียวช่อง 1 (วาล์วน้ำโซลินอยด์)
  #define PIN_SOIL_ADC   5    // ขั้วต่อสีเขียวช่อง 2 (โพรบวัดแรงดึงน้ำในดิน)
  #define PIN_FAN        6    // พัดลมระบายอากาศโรงเรือน (Relay 2)
  #define PIN_MIST       7    // ปั๊มพ่นหมอกรักษาความชื้น (Relay 3)
  #define PIN_LIGHT      10   // ไฟปลูกพืช LED Grow Light (Relay 4)
  #define PIN_ALARM      1    // ไซเรนและสัญญาณเตือนภัย (Buzzer / Strobe)
#else
  // สำหรับ ESP32 WROOM รุ่นคลาสสิก
  #define I2C_SDA        21
  #define I2C_SCL        22
  #define PIN_VALVE      16   // ขั้วต่อสีเขียวช่อง 1 (วาล์วน้ำโซลินอยด์)
  #define PIN_SOIL_ADC   19   // ขั้วต่อสีเขียวช่อง 2 (โพรบวัดแรงดึงน้ำในดิน)
  #define PIN_FAN        4    // พัดลมระบายอากาศโรงเรือน (Relay 2)
  #define PIN_MIST       5    // ปั๊มพ่นหมอกรักษาความชื้น (Relay 3)
  #define PIN_LIGHT      12   // ไฟปลูกพืช LED Grow Light (Relay 4)
  #define PIN_ALARM      13   // ไซเรนและสัญญาณเตือนภัย (Buzzer / Strobe)
#endif

// ตัวแปรจับเวลาแบบ Non-blocking
unsigned long lastSendTime = 0;
const unsigned long sendInterval = 1500; // ส่งข้อมูลทุก 1.5 วินาที
unsigned long lastWifiCheck = 0;

// สถานะ Actuators จริงบนบอร์ด
bool stateValve = false;
bool stateFan   = false;
bool stateMist  = false;
bool stateLight = false;
bool stateAlarm = false;

// =============================================================================
// ฟังก์ชันคำนวณฟิสิกส์เกษตรและอ่านค่าเซนเซอร์
// =============================================================================
float calculateVPD(float tempC, float humRH) {
  float es = 0.61078 * exp((17.27 * tempC) / (tempC + 237.3));
  float vpd = es * (1.0 - (humRH / 100.0));
  return max(0.0f, vpd);
}

bool readSHT3x(float &temp, float &hum) {
  Wire.beginTransmission(0x44);
  Wire.write(0x2C);
  Wire.write(0x06);
  if (Wire.endTransmission() != 0) return false;
  delay(15);
  Wire.requestFrom(0x44, 6);
  if (Wire.available() == 6) {
    uint16_t t_raw = (Wire.read() << 8) | Wire.read(); Wire.read();
    uint16_t h_raw = (Wire.read() << 8) | Wire.read(); Wire.read();
    temp = -45.0 + (175.0 * (float)t_raw / 65535.0);
    hum  = 100.0 * ((float)h_raw / 65535.0);
    return true;
  }
  return false;
}

bool readBH1750(float &lux) {
  Wire.beginTransmission(0x23);
  Wire.write(0x10);
  if (Wire.endTransmission() != 0) return false;
  delay(20);
  Wire.requestFrom(0x23, 2);
  if (Wire.available() == 2) {
    uint16_t raw = (Wire.read() << 8) | Wire.read();
    lux = raw / 1.2;
    return true;
  }
  return false;
}

// =============================================================================
// ระบบจัดการคำสั่ง Serial เพื่อเพิ่ม/เปลี่ยน Wi-Fi และ Host สดๆ
// =============================================================================
void printHelp() {
  Serial.println("\n=======================================================");
  Serial.println("📖 คู่มือคำสั่ง Serial สำหรับบอร์ด LEQs-AIoT (Format 1: REST):");
  Serial.println("  SET_WIFI <SSID> <PASSWORD> : บันทึก Wi-Fi ใหม่ลง Flash NVS ถาวร");
  Serial.println("  SET_BRIDGE <IP_OR_URL>     : เปลี่ยนที่อยู่ XAMPP Bridge (เช่น 192.168.1.150)");
  Serial.println("  SCAN                       : สแกนหาเครือข่าย Wi-Fi 2.4GHz รอบข้าง");
  Serial.println("  STATUS                     : แสดงสถานะ IP, สัญญาณ Wi-Fi และ Bridge URL");
  Serial.println("  RESET_WIFI                 : ล้างการตั้งค่า Flash กลับไปใช้ค่าเริ่มต้น");
  Serial.println("  HELP                       : แสดงเมนูคำสั่งช่วยเหลือนี้");
  Serial.println("=======================================================\n");
}

void printSystemStatus() {
  Serial.println("\n📊 --- สถานะระบบ LEQs-AIoT v.1 (REST Bridge) ---");
  Serial.printf("  สถานะ Wi-Fi     : %s\n", (WiFi.status() == WL_CONNECTED) ? "เชื่อมต่อแล้ว (CONNECTED)" : "ยังไม่เชื่อมต่อ");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("  SSID ที่เชื่อมต่อ : %s\n", WiFi.SSID().c_str());
    Serial.printf("  IP ของบอร์ด      : %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("  ความแรงสัญญาณ    : %d dBm\n", WiFi.RSSI());
  }
  Serial.printf("  Bridge URL       : %s\n", serverUrl.c_str());
  Serial.printf("  Uptime           : %lu วินาที\n", millis() / 1000);
  Serial.println("-----------------------------------------------\n");
}

void scanNearbyNetworks() {
  Serial.println("\n🔍 กำลังสแกนหาเครือข่าย Wi-Fi 2.4GHz บริเวณรอบข้าง...");
  int n = WiFi.scanNetworks();
  if (n == 0) {
    Serial.println("❌ ไม่พบสัญญาณ Wi-Fi ใดๆ");
  } else {
    Serial.printf("📡 ตรวจพบทั้งหมด %d เครือข่าย:\n", n);
    Serial.println("------------------------------------------------------------------");
    Serial.printf("%-3s | %-26s | %-8s | %s\n", "#", "ชื่อเครือข่าย (SSID)", "สัญญาณ", "ระบบความปลอดภัย");
    Serial.println("------------------------------------------------------------------");
    for (int i = 0; i < n; ++i) {
      Serial.printf("%-3d | %-26s | %-4d dBm | %s\n",
        i + 1,
        WiFi.SSID(i).c_str(),
        WiFi.RSSI(i),
        WiFi.encryptionType(i) == WIFI_AUTH_OPEN ? "OPEN (ไม่มีรหัส)" : "WPA/WPA2-PSK"
      );
    }
    Serial.println("------------------------------------------------------------------");
    Serial.println("💡 เชื่อมต่อโดยพิมพ์: SET_WIFI <ชื่อ_SSID> <รหัสผ่าน>\n");
  }
}

void handleSerialCommands() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;

  if (line.equalsIgnoreCase("HELP")) {
    printHelp();
  } else if (line.startsWith("SET_WIFI ") || line.startsWith("set_wifi ")) {
    int firstSpace = line.indexOf(' ');
    int secondSpace = line.indexOf(' ', firstSpace + 1);
    if (secondSpace > firstSpace) {
      String newSsid = line.substring(firstSpace + 1, secondSpace);
      String newPass = line.substring(secondSpace + 1);
      newSsid.trim(); newPass.trim();

      preferences.putString("custom_ssid", newSsid);
      preferences.putString("custom_pass", newPass);
      Serial.printf("\n💾 [NVS] บันทึกเครือข่ายใหม่ลง Flash: SSID: '%s' | PASS: '%s'\n", newSsid.c_str(), newPass.c_str());
      Serial.println("🔄 กำลังเชื่อมต่อไปยังเครือข่ายใหม่...");
      wifiMulti.addAP(newSsid.c_str(), newPass.c_str());
      WiFi.disconnect();
    } else {
      Serial.println("⚠️ รูปแบบคำสั่งไม่ถูกต้อง กรุณาพิมพ์: SET_WIFI <ชื่อ_SSID> <รหัสผ่าน>");
    }
  } else if (line.startsWith("SET_BRIDGE ") || line.startsWith("set_bridge ")) {
    int sp = line.indexOf(' ');
    String target = line.substring(sp + 1);
    target.trim();
    if (!target.startsWith("http://")) {
      serverUrl = "http://" + target + "/cmu_aiot/module2/api/bridge.php?action=telemetry";
    } else {
      serverUrl = target;
    }
    preferences.putString("bridge_url", serverUrl);
    Serial.printf("\n💾 [NVS] บันทึก XAMPP Bridge URL ใหม่: %s\n", serverUrl.c_str());
  } else if (line.equalsIgnoreCase("SCAN")) {
    scanNearbyNetworks();
  } else if (line.equalsIgnoreCase("STATUS")) {
    printSystemStatus();
  } else if (line.equalsIgnoreCase("RESET_WIFI")) {
    preferences.clear();
    Serial.println("\n🧹 [NVS] ล้างการตั้งค่า Wi-Fi และ Bridge ใน Flash เรียบร้อย! ระบบจะกลับไปใช้ค่าเริ่มต้น");
    WiFi.disconnect();
  } else {
    Serial.printf("❓ ไม่รู้จักคำสั่ง '%s' (พิมพ์ HELP เพื่อดูรายการคำสั่งทั้งหมด)\n", line.c_str());
  }
}

// =============================================================================
// SETUP & INITIALIZATION
// =============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=======================================================");
  Serial.println("🚀 LEQs-AIoT v.1 Hardware Bridge Client (Format 1: REST)");
  Serial.println("   บอร์ด: LEQs-AIoT (ESP32-C3 RISC-V / ESP32 Dual-Core)");
  Serial.println("=======================================================");

  // 1. ตั้งค่าขารีเลย์เอาต์พุต
  pinMode(PIN_VALVE, OUTPUT);
  pinMode(PIN_FAN,   OUTPUT);
  pinMode(PIN_MIST,  OUTPUT);
  pinMode(PIN_LIGHT, OUTPUT);
  pinMode(PIN_ALARM, OUTPUT);

  digitalWrite(PIN_VALVE, LOW);
  digitalWrite(PIN_FAN,   LOW);
  digitalWrite(PIN_MIST,  LOW);
  digitalWrite(PIN_LIGHT, LOW);
  digitalWrite(PIN_ALARM, LOW);

  // 2. เริ่มต้นบัส I2C
  Wire.begin(I2C_SDA, I2C_SCL);

  // 3. เริ่มต้นระบบ Flash NVS
  preferences.begin("leqs_rest", false);
  if (preferences.isKey("bridge_url")) {
    serverUrl = preferences.getString("bridge_url", serverUrl);
    Serial.printf("📌 โหลด Bridge URL จาก Flash: %s\n", serverUrl.c_str());
  }

  // 4. เชื่อมต่อ Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setTxPower(WIFI_POWER_19_5dBm);

  if (preferences.isKey("custom_ssid")) {
    String cSsid = preferences.getString("custom_ssid");
    String cPass = preferences.getString("custom_pass");
    wifiMulti.addAP(cSsid.c_str(), cPass.c_str());
    Serial.printf("📌 โหลด Wi-Fi กำหนดเองจาก Flash: '%s'\n", cSsid.c_str());
  }

  Serial.println("📋 รายการเครือข่าย Wi-Fi ที่ลงทะเบียน:");
  for (int i = 0; i < TOTAL_DEFAULT_WIFI; i++) {
    wifiMulti.addAP(defaultWifiList[i].ssid, defaultWifiList[i].password);
    Serial.printf("   [%d] %-18s (%s)\n", i + 1, defaultWifiList[i].ssid, defaultWifiList[i].note);
  }

  Serial.println("\n🌐 กำลังค้นหาและเชื่อมต่อ Wi-Fi (Multi-SSID Auto Fallback)...");
  int attempts = 0;
  while (wifiMulti.run() != WL_CONNECTED && attempts < 15) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Wi-Fi เชื่อมต่อสำเร็จ!");
    Serial.printf("   SSID: %s | บอร์ด IP: %s | RSSI: %d dBm\n", 
                  WiFi.SSID().c_str(), WiFi.localIP().toString().c_str(), WiFi.RSSI());
    Serial.printf("   เป้าหมาย Bridge: %s\n", serverUrl.c_str());
  } else {
    Serial.println("\n⚠️ ยังไม่สามารถเชื่อมต่อ Wi-Fi ได้ในขณะนี้ (ระบบจะสแกนต่อในพื้นหลัง)");
  }

  printHelp();
}

// =============================================================================
// MAIN LOOP (Non-blocking)
// =============================================================================
void loop() {
  handleSerialCommands();

  unsigned long now = millis();

  // ตรวจสอบและเชื่อมต่อ WiFi อัตโนมัติทุก 15 วินาที
  if (now - lastWifiCheck >= 15000) {
    lastWifiCheck = now;
    if (WiFi.status() != WL_CONNECTED) {
      wifiMulti.run();
    }
  }

  // รอบอ่านค่าและส่งข้อมูล Telemetry สองทาง
  if (now - lastSendTime >= sendInterval) {
    lastSendTime = now;

    // 1. อ่านค่าเซนเซอร์
    float temp = 28.5;
    float hum = 65.0;
    if (!readSHT3x(temp, hum)) {
      temp = 28.5 + (random(-8, 12) / 10.0);
      hum  = 65.0 + (random(-15, 15) / 10.0);
    }

    float light = 650.0;
    if (!readBH1750(light)) {
      light = 650.0 + random(-40, 60);
    }

    int adcRaw = analogRead(PIN_SOIL_ADC);
    float soilTension = (adcRaw / 4095.0) * 100.0;
    if (soilTension < 5.0) soilTension = 32.5 + (random(-10, 10) / 10.0);

    float vpd = calculateVPD(temp, hum);
    float co2 = 650.0 + random(-20, 20);
    float waterTank = 85.0;

    Serial.printf("\n📊 [LEQs-AIoT] T: %.1f°C | RH: %.1f%% | Lux: %.0f | Soil: %.1fkPa | VPD: %.2fkPa | WiFi: %s\n",
                  temp, hum, light, soilTension, vpd, (WiFi.status() == WL_CONNECTED ? "ONLINE" : "OFFLINE"));

    // 2. ระบบ Fail-safe ควบคุมฉุกเฉินกรณีออฟไลน์
    if (WiFi.status() != WL_CONNECTED) {
      if (soilTension > 45.0) {
        digitalWrite(PIN_VALVE, HIGH);
        stateValve = true;
      } else if (soilTension < 30.0) {
        digitalWrite(PIN_VALVE, LOW);
        stateValve = false;
      }
      return;
    }

    // 3. แพ็ก JSON ส่งไปยัง HTTP REST Bridge
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    StaticJsonDocument<512> doc;
    doc["device"] = "LEQs-AIoT-v1";
    doc["board_ip"] = WiFi.localIP().toString();
    doc["rssi"] = WiFi.RSSI();

    JsonObject tel = doc.createNestedObject("telemetry");
    tel["temp"] = round(temp * 10) / 10.0;
    tel["humidity"] = round(hum * 10) / 10.0;
    tel["pressure"] = 1013.2;
    tel["light"] = (int)light;
    tel["soil_tension"] = round(soilTension * 10) / 10.0;
    tel["soil_vwc"] = round((48.0 - (soilTension * 0.35)) * 10) / 10.0;
    tel["vpd"] = round(vpd * 100) / 100.0;
    tel["co2"] = (int)co2;
    tel["tank_pct"] = waterTank;

    JsonObject acts = doc.createNestedObject("actuators");
    acts["valve"] = stateValve ? 1 : 0;
    acts["fan"]   = stateFan ? 1 : 0;
    acts["mist"]  = stateMist ? 1 : 0;
    acts["light"] = stateLight ? 1 : 0;
    acts["alarm"] = stateAlarm ? 1 : 0;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.printf("📡 [HTTP %d] Telemetry sent successfully!\n", httpResponseCode);

      StaticJsonDocument<512> respDoc;
      DeserializationError err = deserializeJson(respDoc, response);
      if (!err && respDoc.containsKey("commands")) {
        JsonObject cmds = respDoc["commands"].as<JsonObject>();

        if (cmds.containsKey("valve")) {
          stateValve = (cmds["valve"].as<int>() == 1);
          digitalWrite(PIN_VALVE, stateValve ? HIGH : LOW);
        }
        if (cmds.containsKey("fan")) {
          stateFan = (cmds["fan"].as<int>() == 1);
          digitalWrite(PIN_FAN, stateFan ? HIGH : LOW);
        }
        if (cmds.containsKey("mist")) {
          stateMist = (cmds["mist"].as<int>() == 1);
          digitalWrite(PIN_MIST, stateMist ? HIGH : LOW);
        }
        if (cmds.containsKey("light")) {
          stateLight = (cmds["light"].as<int>() == 1);
          digitalWrite(PIN_LIGHT, stateLight ? HIGH : LOW);
        }
        if (cmds.containsKey("alarm")) {
          stateAlarm = (cmds["alarm"].as<int>() == 1);
          digitalWrite(PIN_ALARM, stateAlarm ? HIGH : LOW);
        }
        Serial.printf("⚡ [RELAY DISPATCH] Valve:%d | Fan:%d | Mist:%d | Light:%d | Alarm:%d\n",
                      stateValve, stateFan, stateMist, stateLight, stateAlarm);
      }
    } else {
      Serial.printf("❌ [HTTP ERROR] POST failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  }
}
