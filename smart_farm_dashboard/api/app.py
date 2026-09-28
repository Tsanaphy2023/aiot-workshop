"""
Smart Farm AIoT - Python Lightweight Backend Server (Flask / Python 3)
Run with: python3 app.py
Accessible at: http://localhost:5000/
"""

from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='../')

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "areas": {
                "flower": {"name": "Flower Farm", "soil": 58.0, "temp": 29.4, "humidity": 68.2, "light": 42500, "valve": False, "pump": False, "mist": False, "fan": False},
                "corn": {"name": "Corn Farm", "soil": 42.5, "temp": 31.2, "humidity": 55.4, "light": 68000, "valve": False, "pump": False, "mist": False, "fan": False},
                "grass": {"name": "Grass & Lawn", "soil": 65.0, "temp": 28.0, "humidity": 72.0, "light": 35000, "valve": False, "pump": False, "mist": False, "fan": False}
            },
            "history": []
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def serve_index():
    return send_from_directory('../', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../', path)

@app.route('/api/status', methods=['GET'])
def get_status():
    data = load_data()
    return jsonify({"status": "success", "data": data})

@app.route('/api/telemetry', methods=['POST'])
def post_telemetry():
    req = request.get_json() or {}
    area = req.get('area', 'flower')
    data = load_data()

    if area not in data['areas']:
        area = 'flower'

    for field in ['soil', 'temp', 'humidity', 'light']:
        if field in req:
            data['areas'][area][field] = float(req[field])

    data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data['history'].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "area": area,
        "soil": data['areas'][area]['soil'],
        "temp": data['areas'][area]['temp']
    })

    if len(data['history']) > 50:
        data['history'].pop(0)

    save_data(data)

    # Return current actuator commands for ESP32
    return jsonify({
        "status": "success",
        "commands": {
            "valve": data['areas'][area]['valve'],
            "pump": data['areas'][area]['pump'],
            "mist": data['areas'][area]['mist'],
            "fan": data['areas'][area]['fan']
        }
    })

@app.route('/api/control', methods=['POST'])
def post_control():
    req = request.get_json() or {}
    area = req.get('area', 'flower')
    device = req.get('device', 'valve')
    state = bool(req.get('state', False))

    data = load_data()
    if area in data['areas'] and device in data['areas'][area]:
        data['areas'][area][device] = state
        data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data(data)
        return jsonify({"status": "success", "message": f"{device} set to {state}"})
    return jsonify({"status": "error", "message": "Invalid area or device"}), 400

if __name__ == '__main__':
    print("🚀 Smart Farm Server running at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
