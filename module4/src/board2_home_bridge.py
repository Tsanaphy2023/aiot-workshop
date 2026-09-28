"""
Module 4: การเชื่อมต่อระบบฟาร์มสู่คลาวด์และแดชบอร์ด
ไฟล์: board2_home_bridge.py (MicroPython สำหรับบอร์ด 2 - ประจำในบ้าน / เรือน)
หน้าที่:
- ต่อ WiFi เพื่อคุยกับ Cloud (เช่น AWS EC2 / Server)
- รับข้อมูลเซนเซอร์จากบอร์ด 1 ผ่าน ESP-NOW แล้ว HTTP POST ขึ้น Cloud API
- คอย Poll (สอบถาม) คำสั่งรดน้ำจาก Cloud ทุกๆ 15 วินาที
- หาก Cloud สั่งเปิด/ปิดน้ำ จะส่งคำสั่งต่อไปให้บอร์ด 1 ผ่าน ESP-NOW
"""

import network
import espnow
import urequests
import ujson
import time

# --- ตั้งค่า WiFi ---
WIFI_SSID = "YOUR_WIFI_NAME"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

# *** ใส่ Public IP หรือ Domain ของ EC2 ***
EC2_URL = "http://YOUR_EC2_PUBLIC_IP:5000"

# *** ใส่ MAC Address ของบอร์ด 1 (ในสวน) ***
BOARD_1_MAC = b'\xff\xff\xff\xff\xff\xff'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("WiFi connected! IP:", wlan.ifconfig()[0])

connect_wifi()

# --- ตั้งค่า ESP-NOW ---
e = espnow.ESPNow()
e.active(True)
try:
    e.add_peer(BOARD_1_MAC)
except Exception:
    pass

last_poll_time = 0
POLL_INTERVAL = 15  # ดึงคำสั่งจาก Cloud ทุก 15 วินาที
print("Board 2 (Home Bridge) ready...")

while True:
    # 1. รับค่าจากบอร์ด 1 ผ่าน ESP-NOW แล้วยิงส่งไปที่ EC2
    host, msg = e.irecv(0)
    if msg:
        try:
            payload_str = msg.decode('utf-8')
            sensor_data = ujson.loads(payload_str)
            print("Received from Board 1:", sensor_data)
            # ส่งไปเก็บที่ EC2
            res = urequests.post(
                f"{EC2_URL}/api/data",
                json=sensor_data,
                headers={'Content-Type': 'application/json'}
            )
            res.close()
            print("Uploaded data to EC2 successfully")
        except Exception as err:
            print("Error uploading data to EC2:", err)

    # 2. คอยเช็กคำสั่งจาก EC2 (Polling)
    if time.time() - last_poll_time >= POLL_INTERVAL:
        try:
            res = urequests.get(f"{EC2_URL}/api/command")
            if res.status_code == 200:
                cmd_data = res.json()
                cmd = cmd_data.get("cmd")
                # หากมีคำสั่งค้างอยู่ (เช่น WATER_ON หรือ WATER_OFF)
                if cmd in ["WATER_ON", "WATER_OFF"]:
                    print("Sending command to Board 1:", cmd)
                    e.send(BOARD_1_MAC, ujson.dumps({"cmd": cmd}))
            res.close()
        except Exception as err:
            print("Error polling command from EC2:", err)
        last_poll_time = time.time()

    time.sleep_ms(100)
