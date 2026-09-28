"""
Module 4: การเชื่อมต่อระบบฟาร์มสู่คลาวด์และแดชบอร์ด
ไฟล์: trigger_water.py (สคริปต์ตรวจสอบความชื้นและสั่งรดน้ำอัตโนมัติ รันผ่าน Cron job บน EC2/Server)
หน้าที่:
- อ่านค่าความชื้นล่าสุดจาก sensor_data.csv
- ถ้าความชื้นต่ำกว่าเกณฑ์ (< 80%) แปลว่าฝนไม่ตก -> ส่งคำสั่งเปิดน้ำ WATER_ON
- รอน้ำทำงานตามเวลาที่กำหนด (เช่น 60 วินาที) แล้วส่งคำสั่งปิดน้ำ WATER_OFF
"""

import csv
import time
import requests

CSV_FILE = 'sensor_data.csv'
EC2_API_URL = 'http://127.0.0.1:5000/api/trigger'

# กำหนดเกณฑ์ความชื้น (%) ถ้าสูงกว่านี้ถือว่าฝนตก/ดินชื้น ไม่ต้องรดน้ำ
HUMIDITY_THRESHOLD = 80.0
WATERING_DURATION_SEC = 60  # ระยะเวลารดน้ำ (เช่น 60 วินาที)

def get_latest_humidity():
    """อ่านค่าความชื้นแถวล่าสุดจากไฟล์ CSV"""
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
            if len(reader) > 1:  # มีข้อมูลอย่างน้อย 1 แถว (ไม่นับ header)
                latest_row = reader[-1]
                return float(latest_row[2])  # คอลัมน์ humidity
    except Exception as e:
        print("Error reading CSV:", e)
        return None

def main():
    hum = get_latest_humidity()
    if hum is None:
        print("No humidity data available. Skipping watering.")
        return

    print(f"Current humidity: {hum}%")

    if hum >= HUMIDITY_THRESHOLD:
        print(f"Humidity is high ({hum}% >= {HUMIDITY_THRESHOLD}%). Skipping watering due to rain/high moisture.")
    else:
        print("Humidity is low. Triggering watering sequence...")
        # 1. สั่งเปิดน้ำ
        requests.post(EC2_API_URL, json={'action': 'WATER_ON'})
        print(f"Waiting for {WATERING_DURATION_SEC} seconds...")
        # 2. รอน้ำทำงานตามเวลาที่กำหนด
        time.sleep(WATERING_DURATION_SEC)
        # 3. สั่งปิดน้ำ
        requests.post(EC2_API_URL, json={'action': 'WATER_OFF'})
        print("Watering sequence complete.")

if __name__ == '__main__':
    main()
