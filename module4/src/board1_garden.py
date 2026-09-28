"""
Module 4: การเชื่อมต่อระบบฟาร์มสู่คลาวด์และแดชบอร์ด
ไฟล์: board1_garden.py (MicroPython สำหรับบอร์ด 1 - ประจำในสวน)
หน้าที่:
- อ่านค่า DHT22 ทุกๆ ช่วงเวลา (เช่น ทุก 5 นาที)
- ส่งค่าอุณหภูมิและความชื้นไปที่บอร์ด 2 ผ่าน ESP-NOW
- คอยฟังคำสั่ง (เปิด/ปิด รีเลย์) จากบอร์ด 2 ผ่าน ESP-NOW แล้วควบคุมวาล์วน้ำ
"""

import network
import espnow
import dht
import machine
import time
import json

# --- กำหนดพิน ---
DHT_PIN = machine.Pin(4, machine.Pin.IN)         # พิน DHT22 (ปรับตามที่ต่อจริง)
RELAY_PIN = machine.Pin(5, machine.Pin.OUT)      # พิน Relay
RELAY_OFF = 0                                    # ปรับเป็น 1 ถ้าเป็น Active LOW
RELAY_ON = 1                                     # ปรับเป็น 0 ถ้าเป็น Active LOW
RELAY_PIN.value(RELAY_OFF)

sensor = dht.DHT22(DHT_PIN)

# --- ตั้งค่า ESP-NOW ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

e = espnow.ESPNow()
e.active(True)

# *** ใส่ MAC Address ของบอร์ด 2 (ในบ้าน) ***
BOARD_2_MAC = b'\xff\xff\xff\xff\xff\xff'  # เช่น b'\x24\xd7\xeb\x12\x34\x56'
try:
    e.add_peer(BOARD_2_MAC)
except Exception:
    pass

last_send_time = 0
SEND_INTERVAL = 300  # ส่งค่าทุก 5 นาที (300 วินาที)
print("Board 1 (Garden Node) ready...")

while True:
    # 1. เช็กว่ามีคำสั่งจากบอร์ด 2 เข้ามาหรือไม่ (Non-blocking)
    host, msg = e.irecv(0)
    if msg:
        try:
            data = json.loads(msg.decode('utf-8'))
            if "cmd" in data:
                command = data["cmd"]
                if command == "WATER_ON":
                    RELAY_PIN.value(RELAY_ON)
                    print("Water Valve: OPEN")
                elif command == "WATER_OFF":
                    RELAY_PIN.value(RELAY_OFF)
                    print("Water Valve: CLOSED")
        except Exception as err:
            print("Error processing command:", err)

    # 2. อ่านค่าเซนเซอร์และส่งให้บอร์ด 2 ตามช่วงเวลา
    if time.time() - last_send_time >= SEND_INTERVAL:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            payload = json.dumps({"temp": temp, "hum": hum})
            e.send(BOARD_2_MAC, payload)
            print(f"Sent sensor data: Temp={temp}C, Hum={hum}%")
            last_send_time = time.time()
        except Exception as err:
            print("Failed to read DHT22 or send via ESP-NOW:", err)

    time.sleep_ms(100)  # หน่วงเวลาสั้นๆ เพื่อไม่ให้ใช้ CPU เต็ม 100%
