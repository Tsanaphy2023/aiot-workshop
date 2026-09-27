"""
Roboflow Batch Annotation & Image Uploader
Uploads all 150 coffee dataset images and their YOLO bounding box annotations directly to Roboflow.
"""

import os
import sys
import time
import json
import base64
import urllib.request
import urllib.parse
from pathlib import Path

API_KEY = "tdetHe9WG2CTItfj0VHt"
PROJECT = "aiot_workshop2026"
WORKSPACE = "durian-nodisease"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT_ROOT / "outputs" / "coffee_yolo_dataset" / "images"
LABELS_DIR = PROJECT_ROOT / "outputs" / "coffee_yolo_dataset" / "labels"

def upload_single_image_and_annotation(img_path, label_path):
    img_name = img_path.name
    
    # 1. Read image as Base64
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("ascii")

    # Determine split
    split = "train"

    # 2. Upload image to Roboflow
    upload_url = f"https://api.roboflow.com/dataset/{PROJECT}/upload?api_key={API_KEY}&name={img_name}&split={split}"
    req = urllib.request.Request(
        upload_url,
        data=img_b64.encode("ascii"),
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            image_id = res.get("id")
    except Exception as e:
        return False, f"Image upload failed: {e}"

    if not image_id:
        return False, f"No image ID returned: {res}"

    # 3. Read annotation content
    if not label_path.exists():
        return True, f"Image uploaded (no label file): {image_id}"

    label_content = label_path.read_text(encoding="utf-8").strip()
    if not label_content:
        return True, f"Image uploaded (empty label): {image_id}"

    # 4. Upload annotation to Roboflow
    ann_url = f"https://api.roboflow.com/dataset/{PROJECT}/annotate/{image_id}?api_key={API_KEY}&name={img_path.stem}.txt"
    ann_req = urllib.request.Request(
        ann_url,
        data=label_content.encode("utf-8"),
        headers={"Content-Type": "text/plain"}
    )

    try:
        with urllib.request.urlopen(ann_req, timeout=30) as a_resp:
            a_res = json.loads(a_resp.read().decode("utf-8"))
            if a_res.get("success"):
                return True, f"Annotated successfully (ID: {image_id})"
            else:
                return False, f"Annotation failed: {a_res}"
    except Exception as e:
        return False, f"Annotation upload error: {e}"

def main():
    img_files = sorted(list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png")))
    total = len(img_files)

    print("=" * 65)
    print(f"🚀 Roboflow Automated Annotation Uploader")
    print(f"📦 Workspace: {WORKSPACE} | Project: {PROJECT}")
    print(f"🖼️ Total Images to Annotate: {total}")
    print("=" * 65)

    success_count = 0
    fail_count = 0

    for idx, img_path in enumerate(img_files, 1):
        label_path = LABELS_DIR / f"{img_path.stem}.txt"
        ok, msg = upload_single_image_and_annotation(img_path, label_path)

        if ok:
            success_count += 1
            status_icon = "✅"
        else:
            fail_count += 1
            status_icon = "❌"

        print(f"[{idx:3d}/{total}] {status_icon} {img_path.name}: {msg}")
        
        # Brief pause to respect API rate limits
        time.sleep(0.15)

    print("\n" + "=" * 65)
    print(f"🎉 Roboflow Annotation Upload Complete!")
    print(f"✅ Success: {success_count} / {total}")
    print(f"❌ Failed:  {fail_count}")
    print("=" * 65)

if __name__ == "__main__":
    main()
