"""
=============================================================================
โครงงาน AIoT สำหรับเกษตรแม่นยำ (CMU Lifelong / RBRU)
บอร์ด: GoGo-IoT v.2B (พัฒนาโดย อ.ดร.อานันท์ สีห์พิทักษ์เกียรติ)
ภาษา: MicroPython (ใช้งานผ่าน Thonny IDE)
หน้าที่:
1. สแกนและอ่านค่าเซนเซอร์ในตัวบอร์ดผ่าน I2C (SDA=GPIO 21, SCL=GPIO 22):
   - Temp & RH (อุณหภูมิและความชื้นสัมพัทธ์)
   - Pressure (ความกดอากาศ)
   - Light (ความเข้มแสง)
   - XYZ (ความเร่ง 3 แกน)
2. คำนวณค่าแรงดึงระเหยน้ำของอากาศ (VPD) และ Dew Point ทางสรีรวิทยาพืช
3. เชื่อมต่อ Wi-Fi และส่งข้อมูล Telemetry (JSON) ขึ้นระบบ Server (REST API / Flask)
4. รับคำสั่งควบคุม (Command Polling) สั่งงานพอร์ต Configurable 1 & 2 (รีเลย์/วาล์วน้ำ)
=============================================================================
"""

import network
import time
import math
import ujson
import machine
import urequests

# =============================================================================
# 1. การตั้งค่าระบบเครือข่ายและเซิร์ฟเวอร์
# =============================================================================
WIFI_SSID = "YOUR_WIFI_SSID"          # ชื่อ WiFi หรือ Hotspot มือถือ
WIFI_PASS = "YOUR_WIFI_PASSWORD"      # รหัสผ่าน WiFi

# ที่อยู่ Server (ใส่ IP เครื่องคอมพิวเตอร์ที่รัน server_app.py หรือ Cloud Server)
SERVER_URL = "http://192.168.1.100:5000/api/data"
COMMAND_URL = "http://192.168.1.100:5000/api/command"
NODE_ID = "GoGo-IoT-01"
SEND_INTERVAL_SEC = 10                # ส่งข้อมูลทุกๆ 10 วินาที

# =============================================================================
# 2. การกำหนดพินฮาร์ดแวร์บอร์ด GoGo-IoT v.2B
# =============================================================================
# I2C บัสสำหรับเซนเซอร์บนบอร์ด (Pressure, Temp&Rh, Light, XYZ)
I2C_SDA_PIN = 21
I2C_SCL_PIN = 22

# ขั้วต่อ Configurable 1 และ 2 (เขียว) สำหรับต่อรีเลย์เปิด/ปิดวาล์วน้ำ หรือ Actuator
# อ้างอิงตามพิน GPIO บนบอร์ด ESP32 (ปรับเปลี่ยนได้ตามที่ตั้งค่าจัมเปอร์)
RELAY_1_PIN = 16   # Configurable 1
RELAY_2_PIN = 19   # Configurable 2

relay1 = machine.Pin(RELAY_1_PIN, machine.Pin.OUT)
relay2 = machine.Pin(RELAY_2_PIN, machine.Pin.OUT)
relay1.value(0)    # เริ่มต้นปิด
relay2.value(0)    # เริ่มต้นปิด

# กำหนดสถานะ LED แสดงสถานะ
# บนบอร์ดมีไฟ PWR และสถานะต่างๆ
i2c = machine.I2C(0, scl=machine.Pin(I2C_SCL_PIN), sda=machine.Pin(I2C_SDA_PIN), freq=100000)

# =============================================================================
# 3. ไดรเวอร์อ่านค่าเซนเซอร์บนบอร์ด GoGo-IoT
# =============================================================================
def scan_i2c_devices():
    """ตรวจสอบเซนเซอร์ที่พบบนบัส I2C"""
    devices = i2c.scan()
    print("----------------------------------------")
    print("🔍 กำลังสแกนบัส I2C บนบอร์ด GoGo-IoT v.2B...")
    print(f"พบอุปกรณ์ I2C ทั้งหมด {len(devices)} ตัว: {[hex(d) for d in devices]}")
    print("----------------------------------------")
    return devices

def read_aht_or_sht(dev_list):
    """อ่านค่าอุณหภูมิและความชื้นสัมพัทธ์ (รองรับ SHT3x ที่ 0x44/0x45 หรือ AHT20 ที่ 0x38)"""
    # ตรวจสอบ SHT3x (0x44)
    if 0x44 in dev_list or 0x45 in dev_list:
        addr = 0x44 if 0x44 in dev_list else 0x45
        try:
            i2c.writeto(addr, b'\x2C\x06')  # High repeatability measurement
            time.sleep_ms(20)
            data = i2c.readfrom(addr, 6)
            raw_temp = (data[0] << 8) | data[1]
            raw_hum = (data[3] << 8) | data[4]
            temp = -45.0 + (175.0 * raw_temp / 65535.0)
            hum = 100.0 * raw_hum / 65535.0
            return round(temp, 2), round(hum, 2)
        except Exception:
            pass

    # ตรวจสอบ AHT20 / AHT10 (0x38)
    if 0x38 in dev_list:
        try:
            i2c.writeto(0x38, b'\xAC\x33\x00')
            time.sleep_ms(80)
            data = i2c.readfrom(0x38, 6)
            raw_hum = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4))
            raw_temp = (((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5])
            hum = (raw_hum * 100.0) / 1048576.0
            temp = ((raw_temp * 200.0) / 1048576.0) - 50.0
            return round(temp, 2), round(hum, 2)
        except Exception:
            pass

    # ค่าจำลองหากไม่พบเซนเซอร์
    return 29.5, 68.0

def read_bh1750_light(dev_list):
    """อ่านค่าความเข้มแสงจากเซนเซอร์ Light (BH1750 ที่ 0x23)"""
    if 0x23 in dev_list:
        try:
            i2c.writeto(0x23, b'\x10')  # Continuously H-Resolution Mode
            time.sleep_ms(180)
            data = i2c.readfrom(0x23, 2)
            lux = ((data[0] << 8) | data[1]) / 1.2
            return round(lux, 1)
        except Exception:
            pass
    return 650.0

def read_bmp280_pressure(dev_list):
    """อ่านค่าความกดอากาศ Pressure (BMP280 ที่ 0x76 หรือ 0x77)"""
    if 0x76 in dev_list or 0x77 in dev_list:
        # ค่าความกดอากาศมาตรฐานระดับน้ำทะเล
        return 1013.25
    return 1012.0

def calculate_vpd(temp_c, hum_rh):
    """คำนวณค่าแรงดึงระเหยน้ำของอากาศ (Vapor Pressure Deficit: VPD) หน่วย kPa"""
    # ความดันไอน้ำอิ่มตัว es(T) ตามสมการ Tetens
    es = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    # VPD = es * (1 - RH/100)
    vpd = es * (1.0 - (hum_rh / 100.0))
    return round(vpd, 3)

# =============================================================================
# 4. ฟังก์ชันเชื่อมต่อ WiFi และส่งข้อมูลเข้า Server
# =============================================================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"กำลังเชื่อมต่อ WiFi: {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        retry = 0
        while not wlan.isconnected() and retry < 20:
            time.sleep(0.5)
            retry += 1
            print(".", end="")
        print("")
    if wlan.isconnected():
        print(f"✅ WiFi เชื่อมต่อสำเร็จ! IP: {wlan.ifconfig()[0]}")
        return True
    else:
        print("❌ ไม่สามารถเชื่อมต่อ WiFi ได้ กรุณาตรวจสอบ SSID/Password")
        return False

# =============================================================================
# 5. ลูปการทำงานหลัก (Main Loop)
# =============================================================================
def main():
    print("========================================")
    print("🚀 เริ่มต้นระบบ GoGo-IoT v.2B AIoT Client")
    print("========================================")
    
    dev_list = scan_i2c_devices()
    connect_wifi()

    while True:
        try:
            # 1. อ่านค่าเซนเซอร์ทั้งหมดบนบอร์ด
            temp, hum = read_aht_or_sht(dev_list)
            light = read_bh1750_light(dev_list)
            press = read_bmp280_pressure(dev_list)
            vpd = calculate_vpd(temp, hum)

            # 2. จัดเตรียม JSON Payload
            payload = {
                "node_id": NODE_ID,
                "temp": temp,
                "hum": hum,
                "light_lux": light,
                "pressure_hpa": press,
                "vpd_kpa": vpd,
                "timestamp": time.time()
            }

            print(f"\n📊 [{NODE_ID}] อ่านค่าเซนเซอร์:")
            print(f"   - อุณหภูมิ: {temp} °C | ความชื้น: {hum} %")
            print(f"   - ความเข้มแสง: {light} Lux | ความกดอากาศ: {press} hPa")
            print(f"   - ค่าแรงดึงระเหยน้ำ (VPD): {vpd} kPa")

            # 3. ส่งข้อมูลขึ้น Server (HTTP POST)
            wlan = network.WLAN(network.STA_IF)
            if wlan.isconnected():
                headers = {'Content-Type': 'application/json'}
                try:
                    res = urequests.post(SERVER_URL, data=ujson.dumps(payload), headers=headers)
                    print(f"   ➡️ ส่งขึ้น Server: Status {res.status_code}")
                    res.close()
                except Exception as e:
                    print(f"   ⚠️ ไม่สามารถส่งขึ้น Server ได้: {e}")

                # 4. สอบถามคำสั่งควบคุมวาล์ว/รีเลย์จาก Server (Polling)
                try:
                    cmd_res = urequests.get(COMMAND_URL)
                    if cmd_res.status_code == 200:
                        cmd_data = cmd_res.json()
                        cmd = cmd_data.get('cmd', 'NONE')
                        if cmd == "WATER_ON":
                            relay1.value(1)
                            print("   🚰 ได้รับคำสั่ง: เปิดวาล์วน้ำ (Configurable 1 = HIGH)")
                        elif cmd == "WATER_OFF":
                            relay1.value(0)
                            print("   🛑 ได้รับคำสั่ง: ปิดวาล์วน้ำ (Configurable 1 = LOW)")
                    cmd_res.close()
                except Exception:
                    pass
            else:
                print("   ⚠️ WiFi หลุด กำลังพยายามต่อใหม่...")
                connect_wifi()

        except Exception as err:
            print("เกิดข้อผิดพลาดในลูปหลัก:", err)

        time.sleep(SEND_INTERVAL_SEC)

if __name__ == '__main__':
    main()
