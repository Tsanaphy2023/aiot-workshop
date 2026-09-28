/*
  =============================================================================
  โครงการ LEQs-AIoT v.1 & Deep+ Precision Agriculture
  บอร์ด: Ai-Thinker ESP32-CAM (เซนเซอร์ OV2640 + หลอดไฟ Flash LED IO4)
  โมดูล: กล้องตรวจการณ์แปลงปลูก & AI Computer Vision Stream
  =============================================================================
  คุณสมบัติ:
  1. 📹 Real-Time MJPEG Video Streaming ผ่านพอร์ต 81: http://<IP>:81/stream
  2. 📸 Snapshot ภาพเดี่ยวความละเอียดสูง: http://<IP>/capture
  3. 💡 ควบคุมหลอดไฟ Flash LED บนบอร์ด (GPIO 4): http://<IP>/flash?state=1 (หรือ 0)
  4. 📶 รองรับ Multi-SSID Wi-Fi Auto Fallback (เชื่อมต่ออัตโนมัติกับเราเตอร์ที่สัญญาณแรงสุด)
  5. ⚡ รองรับคำสั่ง Serial (115200 baud) ปรับเปลี่ยน Wi-Fi หรือหมุนภาพได้สดๆ
  =============================================================================
*/

#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiMulti.h>
#include "esp_timer.h"
#include "img_converters.h"
#include "Arduino.h"
#include "fb_gfx.h"
#include "soc/soc.h"             // ป้องกัน Brownout Detector รีเซ็ตบอร์ด
#include "soc/rtc_cntl_reg.h"
#include "esp_http_server.h"

// =============================================================================
// 1. การกำหนดพินฮาร์ดแวร์สำหรับโมเดล CAMERA_MODEL_AI_THINKER (ตามในรูปภาพ)
// =============================================================================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

#define FLASH_LED_PIN      4   // หลอดไฟ Flash LED สีเหลืองกำลังสูงบนบอร์ด

// =============================================================================
// 2. ตารางเครือข่าย Wi-Fi (Multi-SSID Auto Fallback)
// =============================================================================
struct WiFiCredential {
  const char* ssid;
  const char* password;
  const char* note;
};

WiFiCredential defaultWifiList[] = {
  {"Jade Rower",       "JT23456899",   "เครือข่าย Wi-Fi หลักของผู้ใช้ (Jade Rower)"},
  {"Jade Tower",       "JT23456899",   "เครือข่าย Wi-Fi สำรอง (Jade Tower)"},
  {"farm-iot-red",     "iotfarmer",    "เราเตอร์โรงเรือนหลัก (Farm Master Router)"},
  {"tsanac",           "c9twv3rd",     "ฮอตสปอตมือถือ / สำนักงาน (Office Hotspot)"},
  {"farm-laptop-red",  "iotfarmer",    "ฮอตสปอตคอมพิวเตอร์ Lab (Field Laptop)"},
  {"CMU-WiFi-IoT",     "cmu_aiot2027", "เครือข่ายโครงการ AIoT 2027"},
  {"Home-WiFi-2.4G",   "12345678",     "Wi-Fi ประจำบ้าน/หอพัก (2.4 GHz)"}
};
const int TOTAL_DEFAULT_WIFI = sizeof(defaultWifiList) / sizeof(defaultWifiList[0]);

WiFiMulti wifiMulti;
httpd_handle_t stream_httpd = NULL;
httpd_handle_t camera_httpd = NULL;

// ตัวแปรสถานะ Flash LED
bool flashLedState = false;

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* _STREAM_CONTENT_TYPE = "multipart/x-mixed-replace;boundary=" PART_BOUNDARY;
static const char* _STREAM_BOUNDARY = "\r\n--" PART_BOUNDARY "\r\n";
static const char* _STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

// =============================================================================
// 3. HTTP HANDLERS: สตรีมมิ่งวิดีโอ & สแน็ปช็อตภาพ
// =============================================================================

// A. MJPEG Stream Handler (พอร์ต 81)
static esp_err_t stream_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;
  size_t _jpg_buf_len = 0;
  uint8_t * _jpg_buf = NULL;
  char * part_buf[64];

  res = httpd_resp_set_type(req, _STREAM_CONTENT_TYPE);
  if (res != ESP_OK) return res;

  // เพิ่ม CORS Header เพื่อให้ Web Simulator ดึงภาพไปแสดงได้ไม่ติดปัญหา
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  while (true) {
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("❌ Camera capture failed");
      res = ESP_FAIL;
    } else {
      if (fb->format != PIXFORMAT_JPEG) {
        bool jpeg_converted = frame2jpg(fb, 80, &_jpg_buf, &_jpg_buf_len);
        esp_camera_fb_return(fb);
        fb = NULL;
        if (!jpeg_converted) {
          res = ESP_FAIL;
        }
      } else {
        _jpg_buf_len = fb->len;
        _jpg_buf = fb->buf;
      }
    }

    if (res == ESP_OK) {
      size_t hlen = snprintf((char *)part_buf, 64, _STREAM_PART, _jpg_buf_len);
      res = httpd_resp_send_chunk(req, (const char *)part_buf, hlen);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, (const char *)_jpg_buf, _jpg_buf_len);
    }
    if (res == ESP_OK) {
      res = httpd_resp_send_chunk(req, _STREAM_BOUNDARY, strlen(_STREAM_BOUNDARY));
    }

    if (fb) {
      esp_camera_fb_return(fb);
      fb = NULL;
      _jpg_buf = NULL;
    } else if (_jpg_buf) {
      free(_jpg_buf);
      _jpg_buf = NULL;
    }

    if (res != ESP_OK) {
      break;
    }
  }
  return res;
}

// B. Capture Snapshot Handler (พอร์ต 80 /capture)
static esp_err_t capture_handler(httpd_req_t *req) {
  camera_fb_t * fb = NULL;
  esp_err_t res = ESP_OK;

  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("❌ Camera capture failed");
    httpd_resp_send_500(req);
    return ESP_FAIL;
  }

  httpd_resp_set_type(req, "image/jpeg");
  httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=crop_leaf.jpg");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

  res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
  esp_camera_fb_return(fb);
  return res;
}

// C. Flash LED Toggle Handler (พอร์ต 80 /flash?state=1 หรือ 0)
static esp_err_t flash_handler(httpd_req_t *req) {
  char buf[32];
  if (httpd_req_get_url_query_str(req, buf, sizeof(buf)) == ESP_OK) {
    char param[16];
    if (httpd_query_key_value(buf, "state", param, sizeof(param)) == ESP_OK) {
      int state = atoi(param);
      flashLedState = (state == 1);
      digitalWrite(FLASH_LED_PIN, flashLedState ? HIGH : LOW);
      Serial.printf("💡 [FLASH LED] Set to %s\n", flashLedState ? "ON (HIGH)" : "OFF (LOW)");
    }
  }
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  char resp[64];
  snprintf(resp, sizeof(resp), "{\"flash\":%d,\"ip\":\"%s\"}", flashLedState ? 1 : 0, WiFi.localIP().toString().c_str());
  return httpd_resp_send(req, resp, strlen(resp));
}

// D. Status JSON Handler
static esp_err_t status_handler(httpd_req_t *req) {
  httpd_resp_set_type(req, "application/json");
  httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
  char resp[256];
  snprintf(resp, sizeof(resp),
    "{\"device\":\"LEQs-ESP32-CAM\",\"sensor\":\"OV2640\",\"ip\":\"%s\",\"flash\":%d,\"rssi\":%d,\"stream\":\"http://%s:81/stream\"}",
    WiFi.localIP().toString().c_str(), flashLedState ? 1 : 0, WiFi.RSSI(), WiFi.localIP().toString().c_str()
  );
  return httpd_resp_send(req, resp, strlen(resp));
}

// =============================================================================
// 4. เริ่มต้นเว็บเซิร์ฟเวอร์สำหรับกล้อง (Port 80 สำหรับคำสั่ง & Port 81 สำหรับสตรีมสด)
// =============================================================================
void startCameraServer() {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = 80;

  // Endpoint 1: /capture
  httpd_uri_t capture_uri = {
    .uri       = "/capture",
    .method    = HTTP_GET,
    .handler   = capture_handler,
    .user_ctx  = NULL
  };

  // Endpoint 2: /flash
  httpd_uri_t flash_uri = {
    .uri       = "/flash",
    .method    = HTTP_GET,
    .handler   = flash_handler,
    .user_ctx  = NULL
  };

  // Endpoint 3: /status
  httpd_uri_t status_uri = {
    .uri       = "/status",
    .method    = HTTP_GET,
    .handler   = status_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&camera_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(camera_httpd, &capture_uri);
    httpd_register_uri_handler(camera_httpd, &flash_uri);
    httpd_register_uri_handler(camera_httpd, &status_uri);
    Serial.println("✅ Camera Control Server started on Port 80 (/capture, /flash, /status)");
  }

  // เซิร์ฟเวอร์แยกพอร์ต 81 สำหรับสตรีมมิ่ง MJPEG เพื่อไม่ให้กวนการสั่งงาน
  config.server_port = 81;
  config.ctrl_port = 32769;
  httpd_uri_t stream_uri = {
    .uri       = "/stream",
    .method    = HTTP_GET,
    .handler   = stream_handler,
    .user_ctx  = NULL
  };

  if (httpd_start(&stream_httpd, &config) == ESP_OK) {
    httpd_register_uri_handler(stream_httpd, &stream_uri);
    Serial.println("⚡ Real-time MJPEG Stream Server started on Port 81 (/stream)");
  }
}

// =============================================================================
// SETUP & INITIALIZATION
// =============================================================================
void setup() {
  // ปิด Brownout Detector เพื่อป้องกันบอร์ดรีเซ็ตเวลา Wi-Fi และกล้องดึงกระแสพร้อมกัน
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=======================================================");
  Serial.println("📷 LEQs-AIoT v.1 - ESP32-CAM AI Vision Node Starting");
  Serial.println("   บอร์ด: Ai-Thinker ESP32-CAM (OV2640 + Flash LED IO4)");
  Serial.println("=======================================================");

  // 1. ตั้งค่าพิน Flash LED
  pinMode(FLASH_LED_PIN, OUTPUT);
  digitalWrite(FLASH_LED_PIN, LOW);

  // 2. กำหนดค่าคอนฟิกกล้อง OV2640
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // ตรวจสอบหน่วยความจำ PSRAM (Ai-Thinker ESP32-CAM มี PSRAM 4MB)
  if (psramFound()) {
    config.frame_size   = FRAMESIZE_SVGA; // 800x600 สวย คมชัด เหมาะกับดูใบพืช
    config.jpeg_quality = 10;            // 10-12 คุณภาพสูง
    config.fb_count     = 2;
    Serial.println("✅ ตรวจพบหน่วยความจำ PSRAM บนบอร์ด! เปิดโหมด SVGA High-Quality");
  } else {
    config.frame_size   = FRAMESIZE_VGA;  // 640x480
    config.jpeg_quality = 14;
    config.fb_count     = 1;
    Serial.println("⚠️ ไม่พบ PSRAM, ใช้งานโหมดประหยัด RAM (VGA 640x480)");
  }

  // 3. เริ่มต้นฮาร์ดแวร์กล้อง
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ esp_camera_init ล้มเหลว! error code: 0x%x\n", err);
    Serial.println("💡 กรุณาตรวจสอบว่าสายแพรกล้อง OV2640 เสียบแน่นสนิทและดึงสลักล็อคแล้ว");
    return;
  }
  Serial.println("✅ เริ่มต้นกล้อง OV2640 สำเร็จ!");

  // ปรับจูนเซนเซอร์ให้สีใบไม้สมจริง
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_brightness(s, 1);     // เพิ่มความสว่างเล็กน้อย (-2 ถึง 2)
    s->set_contrast(s, 1);       // เพิ่มคอนทราสต์ให้เห็นลายเส้นใบชัด
    s->set_saturation(s, 1);     // เพิ่มความสดของสีเขียวคลอโรฟิลล์
    s->set_whitebal(s, 1);       // Auto White Balance
    s->set_awb_gain(s, 1);
    s->set_wb_mode(s, 0);        // Auto mode
  }

  // 4. เชื่อมต่อ Wi-Fi ด้วยระบบ Multi-SSID (STA + SoftAP Dual-Mode Fallback)
  WiFi.mode(WIFI_AP_STA);
  WiFi.setSleep(false);

  // 4. เชื่อมต่อ Wi-Fi เข้ากับ JadeTower โดยตรง (SSID: JadeTower ไม่มีเว้นวรรค Ch 6)
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(true);
  delay(200);

  Serial.println("\n🌐 กำลังเชื่อมต่อ Wi-Fi เราเตอร์: 'JadeTower' (รหัสผ่าน: JT23456899) ...");
  WiFi.begin("JadeTower", "JT23456899");

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 25) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  // 5. เริ่มต้นเว็บเซิร์ฟเวอร์กล้อง
  startCameraServer();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n\n=======================================================");
    Serial.println("🎉🎉🎉 บอร์ด ESP32-CAM เชื่อมต่อเราเตอร์สำเร็จแล้ว! 🎉🎉🎉");
    Serial.printf("   SSID : %s\n", WiFi.SSID().c_str());
    Serial.printf("   IP   : %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("   RSSI : %d dBm\n", WiFi.RSSI());
    Serial.printf("📹 สตรีมสด (MJPEG Live Stream): http://%s:81/stream\n", WiFi.localIP().toString().c_str());
    Serial.printf("📸 สแน็ปช็อตภาพนิ่ง            : http://%s/capture\n", WiFi.localIP().toString().c_str());
    Serial.printf("💡 คำสั่งเปิด Flash LED         : http://%s/flash?state=1\n", WiFi.localIP().toString().c_str());
    Serial.println("=======================================================\n");
  } else {
    Serial.println("\n⚠️ ยังเชื่อมต่อเราเตอร์ไม่ได้ กำลังเปิด Hotspot สำรอง...");
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAP("LEQs-ESP32-CAM", "12345678");
    Serial.printf("   สตรีมสดผ่าน Hotspot: http://%s:81/stream\n", WiFi.softAPIP().toString().c_str());
  }

  Serial.println("\n=======================================================");
  Serial.println("🎉 บอร์ด ESP32-CAM พร้อมใช้งานแล้ว!");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("📹 สตรีมสดผ่านเราเตอร์ : http://%s:81/stream\n", WiFi.localIP().toString().c_str());
    Serial.printf("📸 สแน็ปช็อตภาพนิ่ง      : http://%s/capture\n", WiFi.localIP().toString().c_str());
  }
  Serial.printf("📹 สตรีมสดผ่าน Hotspot : http://%s:81/stream\n", WiFi.softAPIP().toString().c_str());
  Serial.printf("📸 สแน็ปช็อตผ่าน Hotspot: http://%s/capture\n", WiFi.softAPIP().toString().c_str());
  Serial.println("=======================================================\n");
}

// =============================================================================
// MAIN LOOP
// =============================================================================
void loop() {
  // ตรวจสอบการเชื่อมต่อ Wi-Fi อัตโนมัติ
  wifiMulti.run();

  // รับคำสั่ง Serial หากผู้ใช้ต้องการเปิด/ปิด Flash ผ่านสาย USB
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.equalsIgnoreCase("FLASH ON")) {
      digitalWrite(FLASH_LED_PIN, HIGH);
      flashLedState = true;
      Serial.println("💡 Flash LED: ON");
    } else if (cmd.equalsIgnoreCase("FLASH OFF")) {
      digitalWrite(FLASH_LED_PIN, LOW);
      flashLedState = false;
      Serial.println("💡 Flash LED: OFF");
    } else if (cmd.equalsIgnoreCase("STATUS")) {
      Serial.printf("IP: %s | RSSI: %d | Stream: http://%s:81/stream\n",
                    WiFi.localIP().toString().c_str(), WiFi.RSSI(), WiFi.localIP().toString().c_str());
    }
  }

  delay(100);
}
