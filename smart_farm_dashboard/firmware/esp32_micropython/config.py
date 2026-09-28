# ==============================================================================
# Smart Farm AIoT - ESP32 MicroPython Configuration
# ==============================================================================

# Wi-Fi Credentials
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

# Smart Farm Dashboard Server URL
# ตัวอย่าง: "http://192.168.1.50/cmu_aiot/smart_farm_dashboard/api/api.php"
# หรือถ้าใช้ Python Server: "http://192.168.1.50:5000/api/telemetry"
SERVER_URL = "http://192.168.1.50/cmu_aiot/smart_farm_dashboard/api/api.php?action=telemetry"

# กำหนดแปลงประจำบอร์ดนี้ ('flower', 'corn', 'grass')
FARM_AREA = "flower"

# กำหนดขา GPIO เชื่อมต่อเซนเซอร์และรีเลย์
PIN_DHT = 4          # ขาสัญญาณ DHT22 (อุณหภูมิ & ความชื้นสัมพัทธ์)
PIN_SOIL = 34        # ขา ADC สำหรับเซนเซอร์ความชื้นในดิน (Analog)
PIN_VALVE = 18       # รีเลย์สั่งเปิด-ปิดวาล์วน้ำ (Relay CH1)
PIN_PUMP = 19        # รีเลย์สั่งเปิด-ปิดปั๊มน้ำ (Relay CH2)
PIN_MIST = 21        # รีเลย์สั่งหัวพ่นหมอก (Relay CH3)
PIN_FAN = 22         # รีเลย์สั่งพัดลมระบายอากาศ (Relay CH4)

# ความถี่ในการส่งข้อมูล (วินาที)
POLL_INTERVAL = 5
