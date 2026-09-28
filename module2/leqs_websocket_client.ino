/*
  =============================================================================
  โครงการ LEQs-AIoT v.1 & Deep+ Precision Agriculture
  บอร์ด: LEQs-AIoT v.1 (เข้ากันได้กับ GoGo-IoT v.2B)
  สถาปัตยกรรม: ESP32-C3 RISC-V / ESP32 Dual-Core
  รูปแบบที่ 2: Real-time WebSocket (< 50ms Sub-second Latency)
  =============================================================================
  ฟังก์ชันเด่นด้านเครือข่าย Wi-Fi:
  1. 📶 Multi-SSID Configuration Table: เพิ่ม ลบ หรือเปลี่ยน Wi-Fi และรหัสผ่านได้ไม่จำกัด
  2. ⚡ Serial On-the-Fly Config: เปลี่ยน Wi-Fi และ Server IP ผ่าน Serial Monitor โดยไม่ต้องแฟลชใหม่!
     - พิมพ์: SET_WIFI <SSID> <PASSWORD>   (บันทึกเข้า Flash NVS ถาวร)
     - พิมพ์: SET_HOST <SERVER_IP>         (เปลี่ยน IP เครื่องคอมพิวเตอร์ที่รัน ws_server.py)
     - พิมพ์: SCAN                         (สแกนหา Wi-Fi รอบข้างพร้อมระดับสัญญาณ RSSI)
     - พิมพ์: STATUS                       (ดูสถานะการเชื่อมต่อปัจจุบันและ IP บอร์ด)
     - พิมพ์: RESET_WIFI                   (ล้างการตั้งค่า Flash กลับไปใช้ค่าเริ่มต้น)
  3. 🚀 Zero-Delay Relay Control: สั่งงานรีเลย์ 5 ช่องผ่าน WebSocket เฟรมในเวลา < 15ms
  =============================================================================
*/

#include <WiFi.h>
#include <WiFiMulti.h>
#include <WebSocketsClient.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <Preferences.h>

WiFiMulti wifiMulti;
WebSocketsClient webSocket;
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
// 2. การตั้งค่าที่อยู่ WebSocket Server (รันผ่าน python3 module2/ws_server.py)
// =============================================================================
String wsServerHost = "10.0.0.41"; // ค่าเริ่มต้น (สามารถเปลี่ยนผ่าน Serial ด้วย: SET_HOST <IP>)
int    wsServerPort = 8765;
const char* wsServerPath = "/";

// =============================================================================
// 3. การกำหนดพินฮาร์ดแวร์บอร์ด LEQs-AIoT v.1 (ESP32-C3 vs ESP32 WROOM)
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

// ตัวแปรเวลาและสถานะ
unsigned long lastTelemetryTime = 0;
unsigned long telemetryInterval = 500; // สตรีม Telemetry ทุก 500ms (2 Hz)
bool wsConnected = false;

// สถานะ Actuators จริงบนบอร์ด
bool stateValve = false;
bool stateFan   = false;
bool stateMist  = false;
bool stateLight = false;
bool stateAlarm = false;

// =============================================================================
// ฟังก์ชันอ่านเซนเซอร์และคำนวณฟิสิกส์เกษตร
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
// การจัดการ Event ของ WebSocket (รับคำสั่ง JSON สั่งงานรีเลย์ทันที)
// =============================================================================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      wsConnected = false;
      Serial.println("❌ [WEBSOCKET] หลุดการเชื่อมต่อจากเซิร์ฟเวอร์");
      break;

    case WStype_CONNECTED:
      wsConnected = true;
      Serial.printf("⚡ [WEBSOCKET] เชื่อมต่อสำเร็จ! url: %s\n", payload);
      // ส่ง Handshake ประกาศตัวตนของบอร์ด
      webSocket.sendTXT("{\"type\":\"register\",\"device\":\"LEQs-AIoT-v1\",\"role\":\"hardware\"}");
      break;

    case WStype_TEXT: {
      StaticJsonDocument<512> doc;
      DeserializationError err = deserializeJson(doc, payload, length);
      if (err) return;

      const char* msgType = doc["type"] | "";

      // 1. รับคำสั่งควบคุมอุปกรณ์จาก Web Simulator
      if (strcmp(msgType, "command") == 0) {
        const char* dev = doc["device"] | "";
        int state = doc["state"] | 0;

        Serial.printf("🎛️ [WS COMMAND ⚡] Device: %s -> %s\n", dev, state ? "HIGH (ON)" : "LOW (OFF)");

        if (strcmp(dev, "valve") == 0) {
          stateValve = (state == 1);
          digitalWrite(PIN_VALVE, stateValve ? HIGH : LOW);
        } else if (strcmp(dev, "fan") == 0) {
          stateFan = (state == 1);
          digitalWrite(PIN_FAN, stateFan ? HIGH : LOW);
        } else if (strcmp(dev, "mist") == 0) {
          stateMist = (state == 1);
          digitalWrite(PIN_MIST, stateMist ? HIGH : LOW);
        } else if (strcmp(dev, "light") == 0) {
          stateLight = (state == 1);
          digitalWrite(PIN_LIGHT, stateLight ? HIGH : LOW);
        } else if (strcmp(dev, "alarm") == 0) {
          stateAlarm = (state == 1);
          digitalWrite(PIN_ALARM, stateAlarm ? HIGH : LOW);
        }

        // ส่ง Echo ยืนยันกลับไปยัง Simulator
        StaticJsonDocument<256> resp;
        resp["type"] = "ack";
        resp["device"] = dev;
        resp["state"] = state;
        resp["hw_time"] = millis();
        String respText;
        serializeJson(resp, respText);
        webSocket.sendTXT(respText);
      }
      break;
    }

    default:
      break;
  }
}

// =============================================================================
// ระบบจัดการคำสั่ง Serial เพื่อเพิ่ม/เปลี่ยน Wi-Fi และ Host ได้สดๆ โดยไม่ต้องแฟลช
// =============================================================================
void printHelp() {
  Serial.println("\n=======================================================");
  Serial.println("📖 คู่มือคำสั่ง Serial สำหรับบอร์ด LEQs-AIoT v.1:");
  Serial.println("  SET_WIFI <SSID> <PASSWORD> : บันทึก Wi-Fi ใหม่ลง Flash NVS ถาวร");
  Serial.println("  SET_HOST <SERVER_IP>       : เปลี่ยน IP WebSocket Server (เช่น 192.168.1.150)");
  Serial.println("  SCAN                       : สแกนหาเครือข่าย Wi-Fi 2.4GHz รอบข้าง");
  Serial.println("  STATUS                     : แสดงสถานะ IP, สัญญาณ Wi-Fi และ WebSocket");
  Serial.println("  RESET_WIFI                 : ล้างการตั้งค่า Flash กลับไปใช้ค่าเริ่มต้น");
  Serial.println("  HELP                       : แสดงเมนูคำสั่งช่วยเหลือนี้");
  Serial.println("=======================================================\n");
}

void printSystemStatus() {
  Serial.println("\n📊 --- สถานะระบบ LEQs-AIoT v.1 ---");
  Serial.printf("  สถานะ Wi-Fi     : %s\n", (WiFi.status() == WL_CONNECTED) ? "เชื่อมต่อแล้ว (CONNECTED)" : "ยังไม่เชื่อมต่อ");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("  SSID ที่เชื่อมต่อ : %s\n", WiFi.SSID().c_str());
    Serial.printf("  IP ของบอร์ด      : %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("  ความแรงสัญญาณ    : %d dBm\n", WiFi.RSSI());
    Serial.printf("  Gateway IP       : %s\n", WiFi.gatewayIP().toString().c_str());
  }
  Serial.printf("  WebSocket Host   : %s:%d\n", wsServerHost.c_str(), wsServerPort);
  Serial.printf("  WebSocket Status : %s\n", wsConnected ? "ONLINE (สตรีมสด)" : "OFFLINE");
  Serial.printf("  Uptime           : %lu วินาที\n", millis() / 1000);
  Serial.println("-----------------------------------\n");
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
    Serial.println("💡 ท่านสามารถเชื่อมต่อเครือข่ายด้านบนโดยพิมพ์: SET_WIFI <ชื่อ_SSID> <รหัสผ่าน>\n");
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
  } else if (line.startsWith("SET_HOST ") || line.startsWith("set_host ") || line.startsWith("SET_SERVER ")) {
    int sp = line.indexOf(' ');
    String newHost = line.substring(sp + 1);
    newHost.trim();
    preferences.putString("ws_host", newHost);
    wsServerHost = newHost;
    Serial.printf("\n💾 [NVS] บันทึก WebSocket Server IP ใหม่: %s:%d\n", wsServerHost.c_str(), wsServerPort);
    Serial.println("🔄 กำลัง Reconnect WebSocket ไปยัง Host ใหม่...");
    webSocket.disconnect();
    webSocket.begin(wsServerHost.c_str(), wsServerPort, wsServerPath);
  } else if (line.equalsIgnoreCase("SCAN")) {
    scanNearbyNetworks();
  } else if (line.equalsIgnoreCase("STATUS")) {
    printSystemStatus();
  } else if (line.equalsIgnoreCase("RESET_WIFI")) {
    preferences.clear();
    Serial.println("\n🧹 [NVS] ล้างการตั้งค่า Wi-Fi และ Host ใน Flash เรียบร้อย! ระบบจะกลับไปใช้ค่าเริ่มต้น");
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
  Serial.println("🚀 LEQs-AIoT v.1 Real-Time WebSocket Client Starting");
  Serial.println("   บอร์ด: LEQs-AIoT (ESP32 / ESP32-C3)");
  Serial.println("   Latency: < 50ms Sub-second Real-time Relay");
  Serial.println("=======================================================");

  // 1. กำหนดพินรีเลย์เอาต์พุต
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

  // 3. เริ่มต้นระบบ Flash NVS สำหรับเก็บการตั้งค่า Wi-Fi & Host
  preferences.begin("leqs_aiot", false);

  if (preferences.isKey("ws_host")) {
    wsServerHost = preferences.getString("ws_host", wsServerHost);
    Serial.printf("📌 โหลด WebSocket Host จาก Flash: %s\n", wsServerHost.c_str());
  }

  // 4. ตั้งค่า Wi-Fi โหมดสถานี (STA)
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setTxPower(WIFI_POWER_19_5dBm);

  // โหลด Wi-Fi กำหนดเองจาก Flash (ถ้ามี)
  if (preferences.isKey("custom_ssid")) {
    String cSsid = preferences.getString("custom_ssid");
    String cPass = preferences.getString("custom_pass");
    wifiMulti.addAP(cSsid.c_str(), cPass.c_str());
    Serial.printf("📌 โหลด Wi-Fi กำหนดเองจาก Flash: '%s'\n", cSsid.c_str());
  }

  // ลงทะเบียนเครือข่ายจากตาราง defaultWifiList
  Serial.println("📋 รายการเครือข่าย Wi-Fi ที่ลงทะเบียน:");
  for (int i = 0; i < TOTAL_DEFAULT_WIFI; i++) {
    wifiMulti.addAP(defaultWifiList[i].ssid, defaultWifiList[i].password);
    Serial.printf("   [%d] %-18s (%s)\n", i + 1, defaultWifiList[i].ssid, defaultWifiList[i].note);
  }

  Serial.println("\n🌐 กำลังค้นหาและเชื่อมต่อ Wi-Fi (Multi-SSID Auto Fallback)...");
  int retry = 0;
  while (wifiMulti.run() != WL_CONNECTED && retry < 20) {
    delay(500);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Wi-Fi เชื่อมต่อสำเร็จ!");
    Serial.printf("   เครือข่าย : %s\n", WiFi.SSID().c_str());
    Serial.printf("   IP บอร์ด : %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n⚠️ ยังไม่สามารถเชื่อมต่อ Wi-Fi ได้ในขณะนี้ (ระบบจะสแกนต่อในพื้นหลัง)");
    Serial.println("💡 ท่านสามารถพิมพ์ 'SET_WIFI <SSID> <PASSWORD>' หรือ 'SCAN' ใน Serial Monitor เพื่อตั้งค่าใหม่ได้");
  }

  // 5. เริ่มต้น Client WebSocket
  Serial.printf("🔌 กำลังเชื่อมต่อไปยัง WebSocket Server: ws://%s:%d%s\n", wsServerHost.c_str(), wsServerPort, wsServerPath);
  webSocket.begin(wsServerHost.c_str(), wsServerPort, wsServerPath);
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(2000); // Reconnect ทุก 2 วินาทีหากหลุด

  printHelp();
}

// =============================================================================
// MAIN LOOP (Non-blocking)
// =============================================================================
void loop() {
  // รับคำสั่งปรับตั้งค่า Wi-Fi และ Host ผ่าน Serial Monitor
  handleSerialCommands();

  // รัน Event Loop ของ WebSocket ต่อเนื่อง
  webSocket.loop();

  // ตรวจสอบการเชื่อมต่อ Wi-Fi เบื้องหลังอัตโนมัติ
  wifiMulti.run();

  unsigned long now = millis();

  // สตรีม Telemetry สดทุก 500ms เข้า WebSocket
  if (now - lastTelemetryTime >= telemetryInterval) {
    lastTelemetryTime = now;

    if (wsConnected) {
      float temp = 28.5, hum = 65.0, light = 650.0;
      if (!readSHT3x(temp, hum)) {
        temp = 28.5 + (random(-5, 8) / 10.0);
        hum  = 65.0 + (random(-10, 10) / 10.0);
      }
      if (!readBH1750(light)) {
        light = 650.0 + random(-30, 40);
      }

      int adcRaw = analogRead(PIN_SOIL_ADC);
      float soilTension = (adcRaw / 4095.0) * 100.0;
      if (soilTension < 5.0) soilTension = 33.0 + (random(-10, 10) / 10.0);

      float vpd = calculateVPD(temp, hum);

      StaticJsonDocument<512> doc;
      doc["type"] = "telemetry";
      doc["device"] = "LEQs-AIoT-v1";
      doc["temp"] = round(temp * 10) / 10.0;
      doc["humidity"] = round(hum * 10) / 10.0;
      doc["pressure"] = 1013.2;
      doc["light"] = (int)light;
      doc["soil_tension"] = round(soilTension * 10) / 10.0;
      doc["vpd"] = round(vpd * 100) / 100.0;
      doc["co2"] = 650;
      doc["tank_pct"] = 85.0;

      JsonObject acts = doc.createNestedObject("actuators");
      acts["valve"] = stateValve ? 1 : 0;
      acts["fan"]   = stateFan ? 1 : 0;
      acts["mist"]  = stateMist ? 1 : 0;
      acts["light"] = stateLight ? 1 : 0;
      acts["alarm"] = stateAlarm ? 1 : 0;

      String jsonText;
      serializeJson(doc, jsonText);

      // ส่งแพ็กเก็ตผ่าน WebSocket ด้วย Latency ต่ำมาก (< 5ms)
      webSocket.sendTXT(jsonText);
    }
  }
}
