"""
Standalone Python Dual-Backend Server for Leaf AI Workshop
Runs an asynchronous REST API without requiring external web server frameworks.
Serves static assets and provides API endpoints on port 8008.
"""

import os
import sys
import json
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PORT = 8008

class LeafAIRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.startswith("/api/"):
            # Proxy to api.php or return JSON status
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "python_backend_online", "port": PORT}).encode("utf-8"))
            return
        return super().do_GET()

def run_server():
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, LeafAIRequestHandler)
    print(f"🌿 Leaf AI Python Server running at: http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
