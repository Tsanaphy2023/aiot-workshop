"""
Module 3: การจัดการข้อมูลและการสื่อสารในฟาร์มยุคดิจิทัล
ไฟล์สคริปต์ MicroPython สำหรับบอร์ด ESP32-C3 Super Mini
ฟังก์ชัน:
- เชื่อมต่อ Wi-Fi และซิงก์เวลาจาก NTP Server (UTC+7)
- อ่านค่าเซนเซอร์อุณหภูมิและความชื้น DHT22 (Pin GPIO3)
- บันทึกข้อมูลแบบ Daily Rolling CSV วันทับรายเดือน (01.csv - 31.csv)
- ควบคุมเอาต์พุต LED / Relay ตามเงื่อนไขความชื้น (Pin GPIO8)
"""

import machine
import dht
import network
import ntptime
import time
import os

# ==========================================
# 1. การตั้งค่า Pin และ Hardware
# ==========================================
# DHT22 ต่อที่ GPIO3
sensor = dht.DHT22(machine.Pin(3))

# LED บนบอร์ด ESP32-C3 (หรือ Relay ควบคุมวาล์วน้ำ)
led = machine.Pin(8, machine.Pin.OUT)
led.value(0)

# ==========================================
# 2. เชื่อมต่อ Wi-Fi และซิงก์เวลา NTP
# ==========================================
WIFI_SSID = "JumboPlusIoT"
WIFI_PASS = "ggqvmf29"
TIMEZONE_OFFSET = 7 * 3600  # เวลาประเทศไทย (UTC+7)

def get_mac_address():
    """อ่าน MAC Address ของบอร์ด"""
    import ubinascii
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    return ubinascii.hexlify(wlan.config('mac'), ':').decode()

def connect_wifi():
    """เชื่อมต่อเครือข่าย Wi-Fi และซิงก์เวลามาตรฐาน"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("กำลังเชื่อมต่อ Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("เชื่อมต่อ Wi-Fi สำเร็จ! IP:", wlan.ifconfig()[0])
        try:
            ntptime.settime()  # ซิงก์เวลา UTC จาก pool.ntp.org
            print("ซิงก์เวลา NTP สำเร็จ")
        except Exception as e:
            print("ไม่สามารถซิงก์เวลา NTP ได้:", e)
    else:
        print("การเชื่อมต่อ Wi-Fi ล้มเหลว")

def get_local_time():
    """แปลงเวลา UTC เป็น Local Time (UTC+7)"""
    local_epoch = time.time() + TIMEZONE_OFFSET
    return time.localtime(local_epoch)

# ==========================================
# 3. ฟังก์ชันบันทึกข้อมูลแบบวนทับรายเดือน (สูงสุด 31 ไฟล์)
# ==========================================
def save_to_csv(datetime_str, temp, hum, current_year, current_month, current_day):
    """
    บันทึกข้อมูลลงไฟล์ CSV โดยตั้งชื่อเป็นเลขวันที่ (01.csv - 31.csv)
    หากพบว่าเป็นไฟล์ของเดือนก่อนหน้า จะทำการเคลียร์เขียนทับ (Monthly Rolling Log)
    """
    filename = f"{current_day:02d}.csv"
    mode = "a"  # โหมดเริ่มต้นคือเขียนต่อท้าย
    need_header = False

    try:
        # ดึงสถานะของไฟล์เพื่อเช็กเวลาแก้ไขล่าสุด (mtime)
        stat = os.stat(filename)
        mtime = stat[8]  # เวลา timestamp ของไฟล์
        mtime_local = time.localtime(mtime + TIMEZONE_OFFSET)
        file_year = mtime_local[0]
        file_month = mtime_local[1]

        # ถ้าปีหรือเดือนของไฟล์ไม่ตรงกับปัจจุบัน แปลว่าเป็นข้อมูลของเดือนที่แล้ว
        if (file_year != current_year) or (file_month != current_month):
            print(f"พบไฟล์ {filename} ของเดือนเก่า ({file_year}-{file_month:02d}) -> ทำการเขียนทับใหม่")
            mode = "w"  # เปิดโหมดเขียนทับ (เคลียร์ข้อมูลเก่า)
            need_header = True

    except OSError:
        # ถ้ายังไม่มีไฟล์นี้มาก่อนเลย
        mode = "w"
        need_header = True

    try:
        with open(filename, mode) as f:
            if need_header:
                f.write("datetime,temperature_c,humidity_percent\n")
            f.write(f"{datetime_str},{temp:.1f},{hum:.1f}\n")
        print(f"บันทึกลง {filename} ({mode}): {temp}°C, {hum}%")
    except Exception as e:
        print("เกิดข้อผิดพลาดในการบันทึกไฟล์:", e)

# ==========================================
# 4. ลูปการทำงานหลัก (Main Loop)
# ==========================================
def main():
    connect_wifi()
    last_15s_check = 0
    last_1m_check = 0
    print("เริ่มต้นระบบบันทึกข้อมูล...")

    while True:
        current_time = time.time()

        # --- ทำงานทุกๆ 15 วินาที: อ่านค่า DHT22 และ Save CSV ---
        if current_time - last_15s_check >= 15:
            last_15s_check = current_time

            t = get_local_time()
            c_year, c_month, c_day = t[0], t[1], t[2]
            datetime_str = f"{c_year:04d}-{c_month:02d}-{c_day:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"

            try:
                sensor.measure()
                temp = sensor.temperature()
                hum = sensor.humidity()

                # บันทึกลงไฟล์ .csv (ส่งข้อมูลปี/เดือน/วัน ไปเช็กการเขียนทับ)
                save_to_csv(datetime_str, temp, hum, c_year, c_month, c_day)
            except Exception as e:
                print("อ่านค่าจาก DHT22 ล้มเหลว:", e)

        # --- ทำงานทุกๆ 20 วินาที: เช็กความชื้นเพื่อเปิด/ปิด LED ---
        if current_time - last_1m_check >= 20:
            last_1m_check = current_time

            try:
                sensor.measure()
                current_hum = sensor.humidity()
                print(f"[เช็กความชื้นรอบ 20 วินาที]: {current_hum}%")

                if current_hum > 30:
                    print("ความชื้นสูงกว่า 30% -> ปิด/กระพริบไฟ LED 5 วินาที")
                    led.value(1)
                    time.sleep(5)
                    led.value(0)
            except Exception as e:
                print("อ่านค่า DHT22 สำหรับเงื่อนไข LED ล้มเหลว:", e)

        time.sleep(0.1)

if __name__ == "__main__":
    main()
