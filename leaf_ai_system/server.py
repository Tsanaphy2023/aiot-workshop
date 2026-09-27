"""
Standalone Python Dual-Backend Server for Leaf AI Workshop
Runs an asynchronous REST API without requiring external web server frameworks.
Serves static assets, runs Object Detection with Bounding Boxes, and provides API endpoints on port 8008.
"""

import os
import sys
import json
import glob
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.detector import detect_leaf_lesions_and_objects, draw_bounding_boxes_on_image

PORT = 8008

class LeafAIRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PROJECT_ROOT), **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        action = qs.get("action", [""])[0]

        if parsed.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            if action == "get_sample_images":
                raw_dir = PROJECT_ROOT.parent / "leaf workshop"
                samples = []
                crops = ['corn_dataset', 'coffee_dataset', 'potato_dataset', 'BANANA', 'MANGO', 'ORANGE']
                for c in crops:
                    cp = raw_dir / c
                    if cp.is_dir():
                        for sub in cp.iterdir():
                            if sub.is_dir():
                                files = list(sub.glob("*.jpg"))
                                if files:
                                    f = files[0]
                                    rel = f"../leaf%20workshop/{urllib.parse.quote(c)}/{urllib.parse.quote(sub.name)}/{urllib.parse.quote(f.name)}"
                                    samples.append({
                                        "crop": c,
                                        "class": sub.name,
                                        "filename": f.name,
                                        "path": str(f),
                                        "url": rel
                                    })
                self.wfile.write(json.dumps({"status": "success", "samples": samples}, ensure_ascii=False).encode("utf-8"))
                return

            if action == "get_status":
                self.wfile.write(json.dumps({
                    "status": "success",
                    "backend": "python_standalone",
                    "port": PORT,
                    "crops": {
                        "corn": {"name": "ข้าวโพด (Corn)", "total": 3924},
                        "potato": {"name": "มันฝรั่ง (Potato)", "total": 901},
                        "orange": {"name": "ส้ม (Orange)", "total": 426},
                        "mango": {"name": "มะม่วง (Mango)", "total": 240},
                        "banana": {"name": "กล้วย (Banana)", "total": 205},
                        "coffee": {"name": "กาแฟ (Coffee)", "total": 150}
                    }
                }, ensure_ascii=False).encode("utf-8"))
                return

            self.wfile.write(json.dumps({"status": "python_backend_online", "port": PORT}).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        action = qs.get("action", [""])[0]

        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length)

        if action == "detect_bounding_boxes" or "detect_bounding_boxes" in str(post_body):
            # Parse multipart or urlencoded
            image_path = ""
            crop = "auto"
            conf = 0.35
            iou = 0.45

            # Simple extract
            body_str = post_body.decode("utf-8", errors="ignore")
            for line in body_str.split("\n"):
                if "image_path" in line:
                    parts = line.split("name=\"image_path\"")
                    if len(parts) > 1:
                        image_path = parts[1].strip("\r\n -").strip()
                if "crop" in line:
                    parts = line.split("name=\"crop\"")
                    if len(parts) > 1:
                        crop = parts[1].strip("\r\n -").strip()

            if not image_path:
                # Check default sample
                sample = list((PROJECT_ROOT.parent / "leaf workshop" / "corn_dataset" / "Blight").glob("*.jpg"))
                if sample:
                    image_path = str(sample[0])

            if os.path.exists(image_path):
                out_dir = PROJECT_ROOT / "outputs" / "detections"
                out_dir.mkdir(parents=True, exist_ok=True)
                ann_name = f"det_{Path(image_path).name}"
                out_file = out_dir / ann_name

                res = detect_leaf_lesions_and_objects(
                    image_path=image_path,
                    crop_type=crop,
                    conf_threshold=conf,
                    iou_threshold=iou
                )
                draw_bounding_boxes_on_image(image_path, res["detections"], str(out_file))
                res["annotated_image_url"] = f"outputs/detections/{ann_name}"

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "success",
                    "result": res,
                    "annotated_image_url": f"outputs/detections/{ann_name}"
                }, ensure_ascii=False).encode("utf-8"))
                return

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "received", "action": action}).encode("utf-8"))

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
