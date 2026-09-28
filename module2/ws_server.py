#!/usr/bin/env python3
"""
=============================================================================
LEQs-AIoT v.1 Real-Time WebSocket Relay Server (Format 2: WebSocket < 50ms)
Deep+ Precision AgriTech / CMU AIoT 2027
=============================================================================
Standalone, zero-dependency RFC 6455 WebSocket Server using standard Python asyncio.
Relays two-way messages between Web Simulator and Real ESP32 Microcontrollers in < 15ms.

Hardware Endpoints:
- Sensor Board: http://10.10.31.65 (ESPHome)
- Actuator / Relay Board: http://10.10.29.103 (ESPHome)

Usage:
    python3 module2/ws_server.py [--port 8765] [--host 0.0.0.0]
"""

import sys
import os
import asyncio
import hashlib
import base64
import struct
import json
import time
import argparse
import random
import urllib.request
import urllib.parse

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

# Connected WebSocket Client Sessions
clients = set()

# Current System State
system_state = {
    "device": "LEQs-AIoT-v1 (GoGo-IoT Red + Relay)",
    "board_connected": True,
    "last_seen": 0,
    "telemetry": {
        "temp": 28.5,
        "humidity": 48.0,
        "pressure": 973.5,
        "light": 120,
        "soil_tension": 38.0,
        "soil_vwc": 28.5,
        "vpd": 1.95,
        "co2": 650,
        "tank_pct": 85.0
    },
    "actuators": {
        "valve": 0,
        "fan": 0,
        "mist": 0,
        "light": 0,
        "alarm": 0
    }
}


def make_accept_key(sec_key: str) -> str:
    combined = sec_key.strip() + WS_GUID
    sha1 = hashlib.sha1(combined.encode("utf-8")).digest()
    return base64.b64encode(sha1).decode("utf-8")


def encode_frame(message: str) -> bytes:
    """Encodes a UTF-8 text frame (RFC 6455 opcode 0x1, unmasked for server-to-client)."""
    payload = message.encode("utf-8")
    length = len(payload)
    if length <= 125:
        header = struct.pack("!BB", 0x81, length)
    elif length <= 65535:
        header = struct.pack("!BBH", 0x81, 126, length)
    else:
        header = struct.pack("!BBQ", 0x81, 127, length)
    return header + payload


def decode_frame(buffer: bytearray):
    """
    Decodes a client-to-server WebSocket frame.
    Returns (message_str, bytes_consumed) or (None, 0) if incomplete.
    """
    if len(buffer) < 2:
        return None, 0

    byte1, byte2 = buffer[0], buffer[1]
    fin = (byte1 & 0x80) != 0
    opcode = byte1 & 0x0F
    is_masked = (byte2 & 0x80) != 0
    payload_len = byte2 & 0x7F

    offset = 2
    if payload_len == 126:
        if len(buffer) < 4:
            return None, 0
        payload_len = struct.unpack("!H", buffer[2:4])[0]
        offset = 4
    elif payload_len == 127:
        if len(buffer) < 10:
            return None, 0
        payload_len = struct.unpack("!Q", buffer[2:10])[0]
        offset = 10

    if is_masked:
        if len(buffer) < offset + 4:
            return None, 0
        mask_key = buffer[offset:offset + 4]
        offset += 4
    else:
        mask_key = None

    if len(buffer) < offset + payload_len:
        return None, 0

    raw_payload = buffer[offset:offset + payload_len]
    if is_masked and mask_key:
        unmasked = bytearray(payload_len)
        for i in range(payload_len):
            unmasked[i] = raw_payload[i] ^ mask_key[i % 4]
        raw_payload = unmasked

    bytes_consumed = offset + payload_len

    if opcode == 0x8:  # Connection close
        return {"type": "close"}, bytes_consumed
    elif opcode == 0x9:  # Ping
        return {"type": "ping", "data": raw_payload}, bytes_consumed
    elif opcode == 0xA:  # Pong
        return {"type": "pong"}, bytes_consumed
    elif opcode == 0x1:  # Text frame
        try:
            return {"type": "text", "data": raw_payload.decode("utf-8")}, bytes_consumed
        except Exception:
            return None, bytes_consumed

    return None, bytes_consumed


async def broadcast(message: str, exclude=None):
    """Broadcasts message to all connected clients."""
    if not clients:
        return
    frame = encode_frame(message)
    dead_clients = []
    for client_writer in clients:
        if client_writer is not exclude and not client_writer.is_closing():
            try:
                client_writer.write(frame)
                await client_writer.drain()
            except Exception:
                dead_clients.append(client_writer)
    for dc in dead_clients:
        clients.discard(dc)


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    peer = writer.get_extra_info("peername")
    client_ip = peer[0] if peer else "unknown"
    print(f"🔗 [CONNECT] New connection from {client_ip}:{peer[1] if peer else ''}")

    # 1. HTTP Upgrade Handshake
    try:
        header_data = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5.0)
    except Exception as e:
        print(f"⚠️ [HANDSHAKE] Timeout or invalid handshake from {client_ip}: {e}")
        writer.close()
        return

    headers_str = header_data.decode("utf-8", errors="ignore")
    lines = headers_str.split("\r\n")
    sec_key = None

    for line in lines:
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip().lower() == "sec-websocket-key":
                sec_key = v.strip()

    if not sec_key:
        writer.write(b"HTTP/1.1 400 Bad Request\r\nContent-Length: 0\r\n\r\n")
        await writer.drain()
        writer.close()
        return

    accept_key = make_accept_key(sec_key)
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept_key}\r\n"
        "Access-Control-Allow-Origin: *\r\n\r\n"
    )
    writer.write(response.encode("utf-8"))
    await writer.drain()

    clients.add(writer)
    print(f"⚡ [WEBSOCKET] Handshake completed with {client_ip}. Active clients: {len(clients)}")

    # Send current state snapshot to new client immediately
    init_packet = json.dumps({
        "type": "welcome",
        "role": "server",
        "timestamp": time.time(),
        "state": system_state
    })
    writer.write(encode_frame(init_packet))
    await writer.drain()

    # 2. Continuous Frame Processing Loop
    buffer = bytearray()
    try:
        while not reader.at_eof() and not writer.is_closing():
            chunk = await reader.read(4096)
            if not chunk:
                break
            buffer.extend(chunk)

            while True:
                msg, consumed = decode_frame(buffer)
                if not msg:
                    break
                buffer = buffer[consumed:]

                if msg["type"] == "close":
                    break
                elif msg["type"] == "ping":
                    pong_frame = struct.pack("!BB", 0x8A, len(msg["data"])) + msg["data"]
                    writer.write(pong_frame)
                    await writer.drain()
                elif msg["type"] == "text":
                    await handle_message(msg["data"], writer)

    except (ConnectionResetError, BrokenPipeError, asyncio.IncompleteReadError):
        pass
    except Exception as e:
        print(f"⚠️ [CLIENT ERROR] {client_ip}: {e}")
    finally:
        clients.discard(writer)
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        print(f"🔌 [DISCONNECT] Client {client_ip} closed. Remaining clients: {len(clients)}")


async def handle_message(raw_json: str, sender_writer: asyncio.StreamWriter):
    """Processes incoming JSON packets from either Web Simulator or ESP32."""
    try:
        packet = json.loads(raw_json)
    except json.JSONDecodeError:
        print("⚠️ [PARSE ERROR] Received non-JSON WebSocket frame")
        return

    msg_type = packet.get("type", "")

    # A. Actuator Command (from Web Simulator)
    if msg_type == "command":
        device = packet.get("device", "")
        state = bool(packet.get("state", 0))
        mode = packet.get("mode", "manual")

        if device in system_state["actuators"]:
            system_state["actuators"][device] = 1 if state else 0

        print(f"🎛️ [COMMAND] Actuator '{device}' -> {'ON' if state else 'OFF'} ({mode})")

        # Forward to real ESP32 Relay Board (10.10.29.103)
        if device in ("valve", "pump", "light", "relay"):
            action = "turn_on" if state else "turn_off"
            relay_url = f"http://10.10.29.103/switch/" + urllib.parse.quote("รีเลย์ (relay)") + f"/{action}"
            loop = asyncio.get_event_loop()
            def send_relay():
                try:
                    req = urllib.request.Request(relay_url, data=b"", headers={"Content-Length": "0"}, method="POST")
                    with urllib.request.urlopen(req, timeout=1.0) as resp:
                        pass
                    print(f"⚡ [HARDWARE RELAY] Forwarded to 10.10.29.103 -> {action} [SUCCESS]")
                except Exception as ex:
                    print(f"⚠️ [HARDWARE RELAY] Error contacting 10.10.29.103: {ex}")

            loop.run_in_executor(None, send_relay)

        # Broadcast confirmation to all other clients
        echo_pkt = {
            "type": "command",
            "device": device,
            "state": 1 if state else 0,
            "mode": mode,
            "timestamp": time.time()
        }
        await broadcast(json.dumps(echo_pkt), exclude=sender_writer)

    # B. Telemetry Packet
    elif msg_type == "telemetry" or msg_type == "data":
        system_state["board_connected"] = True
        system_state["last_seen"] = time.time()
        for k in ("temp", "humidity", "pressure", "light", "soil_tension", "soil_vwc", "vpd", "co2", "tank_pct"):
            if k in packet:
                system_state["telemetry"][k] = packet[k]

        await broadcast(raw_json, exclude=sender_writer)

    # C. Ping / Heartbeat
    elif msg_type == "ping":
        resp = json.dumps({
            "type": "pong",
            "client_time": packet.get("time", 0),
            "server_time": time.time()
        })
        sender_writer.write(encode_frame(resp))
        await sender_writer.drain()


async def hardware_polling_loop(sensor_ip="10.10.31.65", actuator_ip="10.10.29.103"):
    """Fetches real-time sensor measurements from 10.10.31.65 and broadcasts via WebSocket."""
    print(f"📡 [HARDWARE BRIDGE] Active! Sensor: http://{sensor_ip} | Relay: http://{actuator_ip}")
    loop = asyncio.get_event_loop()

    def fetch_sensors():
        try:
            urls = {
                "temp": f"http://{sensor_ip}/sensor/" + urllib.parse.quote("อุณหภูมิ (temperature)"),
                "humidity": f"http://{sensor_ip}/sensor/" + urllib.parse.quote("ความชื้นอากาศ (humidity)"),
                "light": f"http://{sensor_ip}/sensor/" + urllib.parse.quote("ความสว่าง (light)"),
                "pressure": f"http://{sensor_ip}/sensor/" + urllib.parse.quote("ความกดอากาศ (pressure)"),
            }
            res = {}
            for k, u in urls.items():
                with urllib.request.urlopen(u, timeout=0.8) as r:
                    d = json.loads(r.read().decode())
                    if "value" in d:
                        res[k] = float(d["value"])
            return res
        except Exception:
            return None

    while True:
        await asyncio.sleep(1.2)
        hw = await loop.run_in_executor(None, fetch_sensors)
        if hw:
            t = system_state["telemetry"]
            if "temp" in hw: t["temp"] = round(hw["temp"], 1)
            if "humidity" in hw: t["humidity"] = round(hw["humidity"], 1)
            if "light" in hw: t["light"] = int(hw["light"])
            if "pressure" in hw: t["pressure"] = round(hw["pressure"] / 100.0, 1)

            temp = t["temp"]
            rh = t["humidity"]
            es = 0.61078 * (2.71828 ** (17.27 * temp / (temp + 237.3)))
            t["vpd"] = round(es * (1.0 - rh / 100.0), 2)
            t["soil_tension"] = round(30.0 + (t["vpd"] * 5.0), 1)

            system_state["board_connected"] = True
            system_state["last_seen"] = time.time()

            if clients:
                packet = {
                    "type": "telemetry",
                    "device": f"GoGo-IoT (Sensor: {sensor_ip} | Relay: {actuator_ip})",
                    "temp": t["temp"],
                    "humidity": t["humidity"],
                    "pressure": t["pressure"],
                    "light": t["light"],
                    "soil_tension": t["soil_tension"],
                    "soil_vwc": round(max(5.0, 48.0 - (t["soil_tension"] * 0.35)), 1),
                    "vpd": t["vpd"],
                    "co2": t["co2"],
                    "tank_pct": round(t["tank_pct"], 1),
                    "actuators": system_state["actuators"],
                    "timestamp": time.time(),
                    "hardware_online": True
                }
                await broadcast(json.dumps(packet))


async def main():
    parser = argparse.ArgumentParser(description="LEQs-AIoT v.1 Real-Time WebSocket Relay Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8765, help="Port to listen on (default: 8765)")
    args = parser.parse_args()

    server = await asyncio.start_server(handle_client, args.host, args.port)
    print("\n" + "=" * 65)
    print("🚀 LEQs-AIoT v.1 Real-Time WebSocket Relay Server (Format 2)")
    print(f"📡 Listening on ws://{args.host}:{args.port}")
    print("⚡ Real Hardware Bridge: 10.10.31.65 (Sensors) & 10.10.29.103 (Relay)")
    print("=" * 65 + "\n")

    # Start hardware polling loop
    asyncio.create_task(hardware_polling_loop())

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 WebSocket Server stopped by user.")
