"""
Module 4: การเชื่อมต่อระบบฟาร์มสู่คลาวด์และแดชบอร์ด
ไฟล์: server_app.py (รันบน Cloud Server / AWS EC2 / Raspberry Pi)
หน้าที่:
- เปิด REST API บน Port 5000
- รับข้อมูลเซนเซอร์จากบอร์ด 2 บันทึกลง sensor_data.csv
- จัดการคิวคำสั่งเปิด/ปิดน้ำ (Command Queue)
- มี Endpoint /api/trigger ให้สคริปต์อัตโนมัติหรือแดชบอร์ดสั่งงาน
"""

from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)
CSV_FILE = 'sensor_data.csv'
pending_command = "NONE"

# สร้างไฟล์ CSV และ header หากยังไม่มี
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temperature', 'humidity'])

@app.route('/api/data', methods=['POST'])
def receive_data():
    """ รับค่าอุณหภูมิความชื้นจากบอร์ด 2 และเขียนลงไฟล์ CSV """
    data = request.get_json()
    if not data or 'temp' not in data or 'hum' not in data:
        return jsonify({'error': 'Invalid payload'}), 400

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    temp = data['temp']
    hum = data['hum']

    # บันทึกลง CSV
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([now, temp, hum])

    print(f"[{now}] Saved: Temp={temp}°C, Hum={hum}%")
    return jsonify({'status': 'success'}), 200

@app.route('/api/command', methods=['GET'])
def get_command():
    """ ให้บอร์ด 2 มาคอยถามว่ามีคำสั่งรดน้ำหรือไม่ (Polling) """
    global pending_command
    cmd = pending_command
    pending_command = "NONE"  # เคลียร์คำสั่งหลังอ่านแล้ว
    return jsonify({'cmd': cmd}), 200

@app.route('/api/trigger', methods=['POST'])
def trigger_watering():
    """ API สำหรับสคริปต์ภายนอกหรือ Cron job ในการสั่งรดน้ำ """
    global pending_command
    data = request.get_json() or {}
    action = data.get('action', 'WATER_ON')
    pending_command = action
    print(f"Triggered command set to: {pending_command}")
    return jsonify({'status': 'command queued', 'cmd': pending_command}), 200

if __name__ == '__main__':
    # รันบน Port 5000
    app.run(host='0.0.0.0', port=5000)
