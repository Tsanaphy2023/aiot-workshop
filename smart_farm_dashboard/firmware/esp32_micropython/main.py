"""
Smart Farm AIoT - ESP32 MicroPython Main Firmware
Features:
- Wi-Fi auto-reconnect
- DHT22 temperature & humidity readings
- Analog Soil Moisture reading with percentage calibration
- HTTP POST Telemetry to Smart Farm Dashboard
- Two-way command execution (Controls Relays on GPIO 18, 19, 21, 22)
"""

import network
import urequests
import ujson
import time
from machine import Pin, ADC
import dht
import config

# --- 1. ฮาร์ดแวร์เซนเซอร์และรีเลย์ ---
try:
    dht_sensor = dht.DHT22(Pin(config.PIN_DHT))
except Exception as e:
    dht_sensor = None
    print("Warning: DHT sensor init failed:", e)

# กำหนด ADC สำหรับเซนเซอร์ความชื้นในดิน
soil_adc = ADC(Pin(config.PIN_SOIL))
soil_adc.atten(ADC.ATTN_11DB)  # ช่วงแรงดัน 0 - 3.3V

# กำหนดขาเอาต์พุตสำหรับรีเลย์ (Active Low หรือ Active High ขึ้นกับโมดูล)
relay_valve = Pin(config.PIN_VALVE, Pin.OUT, value=0)
relay_pump = Pin(config.PIN_PUMP, Pin.OUT, value=0)
relay_mist = Pin(config.PIN_MIST, Pin.OUT, value=0)
relay_fan = Pin(config.PIN_FAN, Pin.OUT, value=0)

# --- 2. ฟังก์ชันเชื่อมต่อ Wi-Fi ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"กำลังเชื่อมต่อ Wi-Fi: {config.WIFI_SSID}...")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        retry = 0
        while not wlan.isconnected() and retry < 20:
            time.sleep(0.5)
            retry += 1
            print(".", end="")
    if wlan.isconnected():
        print("\n✅ เชื่อมต่อ Wi-Fi สำเร็จ! IP:", wlan.ifconfig()[0])
    else:
        print("\n❌ เชื่อมต่อ Wi-Fi ล้มเหลว โปรดตรวจสอบ SSID/Password")

# --- 3. ฟังก์ชันอ่านค่าเซนเซอร์ ---
def read_sensors():
    temp = 28.0
    humid = 65.0
    if dht_sensor:
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            humid = dht_sensor.humidity()
        except Exception as e:
            print("DHT read error:", e)

    # แปลงค่า ADC (0-4095) เป็น % ความชื้นดิน (ดินแห้งค่าสูง, ดินเปียกค่าต่ำ)
    raw_adc = soil_adc.read()
    # สมมุติค่าดินแห้งสนิท = 3200, ดินแช่น้ำ = 1400
    soil_percent = 100.0 - ((raw_adc - 1400) / (3200 - 1400) * 100.0)
    soil_percent = max(0.0, min(100.0, soil_percent))

    return {
        "area": config.FARM_AREA,
        "soil": round(soil_percent, 1),
        "temp": round(temp, 1),
        "humidity": round(humid, 1),
        "light": 45000
    }

# --- 4. ฟังก์ชันสั่งงานรีเลย์ ---
def apply_commands(commands):
    if not commands:
        return
    
    if "valve" in commands:
        relay_valve.value(1 if commands["valve"] else 0)
    if "pump" in commands:
        relay_pump.value(1 if commands["pump"] else 0)
    if "mist" in commands:
        relay_mist.value(1 if commands["mist"] else 0)
    if "fan" in commands:
        relay_fan.value(1 if commands["fan"] else 0)

# --- 5. ลูปการทำงานหลัก (Main Loop) ---
print("🚀 บอร์ด ESP32 Smart Farm Node เริ่มทำงาน...")
connect_wifi()

while True:
    try:
        payload = read_sensors()
        print("\n[Telemetry] อ่านค่าได้:", payload)

        # ยิง HTTP POST ไปยัง Smart Farm Dashboard
        headers = {'Content-Type': 'application/json'}
        res = urequests.post(config.SERVER_URL, data=ujson.dumps(payload), headers=headers)
        
        if res.status_code == 200:
            resp_data = res.json()
            commands = resp_data.get("commands", {})
            print("[Server Feedback] ได้รับคำสั่งควบคุม:", commands)
            apply_commands(commands)
        else:
            print("[Error] Server returned HTTP:", res.status_code)
        
        res.close()

    except Exception as e:
        print("[Exception]", e)
        # ตรวจสอบว่า WiFi ยังต่ออยู่หรือไม่
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            connect_wifi()

    time.sleep(config.POLL_INTERVAL)
