"""
Add Live Camera Inference cells to Colab Notebooks
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def get_camera_cells(subject="mosquito"):
    if subject == "mosquito":
        title = "## 10. เปิดใช้งานกล้องเว็บแคม (Webcam Live Inference) ตรวจจับลูกน้ำยุงสด"
        desc = "เชื่อมต่อกล้องโน้ตบุ๊กหรือเว็บแคมผ่านเบราว์เซอร์ เพื่อถ่ายภาพและนำโมเดลที่เพิ่งฝึกสอนเสร็จมารันตรวจจับลูกน้ำยุงแบบทันทีทันใด"
        model_code = "runs/detect/mosquito_larvae_yolo11/weights/best.pt"
    else:
        title = "## 15. เปิดใช้งานกล้องเว็บแคม (Webcam Live Inference) ส่องตรวจโรคใบพืชสด"
        desc = "เชื่อมต่อกล้องโน้ตบุ๊กหรือเว็บแคมผ่านเบราว์เซอร์ เพื่อส่องใบพืชจริงและให้โมเดล YOLO11 ตีกรอบระบุตำแหน่งรอยโรคสด"
        model_code = "runs/detect/coffee_yolo11_run/weights/best.pt"

    md_intro = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            f"{title}\n",
            "\n",
            f"{desc}\n",
            "\n",
            "> **วิธีใช้งาน:** กดรันเซลล์ด้านล่าง จากนั้นกดปุ่มอนุญาตให้เบราว์เซอร์เข้าถึงกล้อง (Allow Camera) เมื่อพร้อมให้คลิกปุ่ม **📸 ถ่ายภาพและตรวจจับ (Capture & Predict)** ระบบจะดึงภาพจากกล้องมารันโมเดล YOLO ทันที\n"
        ]
    }

    code_cam_fn = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# สร้างฟังก์ชันสะพานเชื่อมต่อกล้องเว็บแคมผ่านเบราว์เซอร์ (WebRTC Camera Bridge)\n",
            "from IPython.display import display, Javascript, Image as IPyImage\n",
            "from google.colab.output import eval_js\n",
            "from base64 import b64decode\n",
            "import cv2\n",
            "import numpy as np\n",
            "import PIL.Image\n",
            "import os\n",
            "\n",
            "def capture_photo_from_webcam(filename='webcam_capture.jpg', quality=0.85):\n",
            "    js = Javascript('''\n",
            "    async function takePhoto(quality) {\n",
            "      const div = document.createElement('div');\n",
            "      div.style.padding = '15px';\n",
            "      div.style.background = '#0F172A';\n",
            "      div.style.borderRadius = '16px';\n",
            "      div.style.border = '2px solid #7C3AED';\n",
            "      div.style.display = 'inline-block';\n",
            "      div.style.boxShadow = '0 10px 25px rgba(124, 58, 237, 0.3)';\n",
            "      \n",
            "      const title = document.createElement('div');\n",
            "      title.innerHTML = '🎥 <b>Edge AI Live Camera View</b> | ส่องวัตถุเข้าหน้ากล้อง';\n",
            "      title.style.color = '#E2E8F0';\n",
            "      title.style.marginBottom = '10px';\n",
            "      title.style.fontFamily = 'sans-serif';\n",
            "      div.appendChild(title);\n",
            "\n",
            "      const video = document.createElement('video');\n",
            "      video.style.display = 'block';\n",
            "      video.style.borderRadius = '10px';\n",
            "      video.style.width = '520px';\n",
            "      video.style.maxWidth = '100%';\n",
            "      \n",
            "      const captureBtn = document.createElement('button');\n",
            "      captureBtn.textContent = '📸 ถ่ายภาพและตรวจจับด้วยโมเดล (Capture & Predict)';\n",
            "      captureBtn.style.marginTop = '12px';\n",
            "      captureBtn.style.padding = '10px 22px';\n",
            "      captureBtn.style.background = 'linear-gradient(135deg, #7C3AED, #2563EB)';\n",
            "      captureBtn.style.color = 'white';\n",
            "      captureBtn.style.border = 'none';\n",
            "      captureBtn.style.borderRadius = '8px';\n",
            "      captureBtn.style.fontSize = '14px';\n",
            "      captureBtn.style.fontWeight = 'bold';\n",
            "      captureBtn.style.cursor = 'pointer';\n",
            "      captureBtn.style.boxShadow = '0 4px 12px rgba(124, 58, 237, 0.4)';\n",
            "      \n",
            "      const stream = await navigator.mediaDevices.getUserMedia({video: true});\n",
            "\n",
            "      document.body.appendChild(div);\n",
            "      div.appendChild(video);\n",
            "      div.appendChild(captureBtn);\n",
            "      video.srcObject = stream;\n",
            "      await video.play();\n",
            "\n",
            "      google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);\n",
            "      await new Promise((resolve) => captureBtn.onclick = resolve);\n",
            "\n",
            "      const canvas = document.createElement('canvas');\n",
            "      canvas.width = video.videoWidth;\n",
            "      canvas.height = video.videoHeight;\n",
            "      canvas.getContext('2d').drawImage(video, 0, 0);\n",
            "      stream.getVideoTracks()[0].stop();\n",
            "      div.remove();\n",
            "      return canvas.toDataURL('image/jpeg', quality);\n",
            "    }\n",
            "    ''')\n",
            "    display(js)\n",
            "    data = eval_js('takePhoto({})'.format(quality))\n",
            "    binary = b64decode(data.split(',')[1])\n",
            "    with open(filename, 'wb') as f:\n",
            "        f.write(binary)\n",
            "    return filename\n",
            "\n",
            "print('✅ ฟังก์ชันเปิดกล้องเว็บแคมพร้อมทำงานแล้ว!')\n"
        ]
    }

    code_run_cam = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# เรียกเปิดกล้อง ถ่ายภาพ และนำโมเดล YOLO มารันตรวจจับทันที\n",
            "from ultralytics import YOLO\n",
            "\n",
            "# ตรวจสอบโมเดลที่ดีที่สุด\n",
            f"target_weights = '{model_code}'\n",
            "if not os.path.exists(target_weights):\n",
            "    target_weights = 'yolo11n.pt'  # หากยังไม่ได้รันเทรน ให้ใช้ Base Model ทดสอบก่อน\n",
            "\n",
            "print(f\"📦 กำลังโหลดโมเดล: {target_weights}\")\n",
            "active_model = YOLO(target_weights)\n",
            "\n",
            "# 1. เปิดกล้องเว็บแคมบันทึกภาพสด\n",
            "captured_img = capture_photo_from_webcam('live_sample.jpg')\n",
            "print(f\"\\n📸 บันทึกภาพจากกล้องสำเร็จ: {captured_img}\")\n",
            "\n",
            "# 2. รันโมเดลทำนายและตีกรอบ Bounding Box\n",
            "results = active_model.predict(source=captured_img, conf=0.25, save=False)\n",
            "annotated_frame = results[0].plot()\n",
            "\n",
            "# 3. แสดงผลลัพธ์การตรวจจับบนหน้าจอ Colab\n",
            "boxes = results[0].boxes\n",
            "total_detected = len(boxes) if boxes is not None else 0\n",
            "print(f\"🎯 ตรวจพบวัตถุทั้งหมด: {total_detected} รายการ\")\n",
            "\n",
            "if boxes is not None:\n",
            "    for idx, box in enumerate(boxes):\n",
            "        cls_id = int(box.cls[0])\n",
            "        cls_name = active_model.names[cls_id]\n",
            "        conf = float(box.conf[0])\n",
            "        print(f\"  [{idx+1}] ชนิด: {cls_name} (ความมั่นใจ: {conf*100:.1f}%)\")\n",
            "\n",
            "# แปลง BGR -> RGB และแสดงภาพ\n",
            "rgb_res = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)\n",
            "display(PIL.Image.fromarray(rgb_res))\n"
        ]
    }

    return [md_intro, code_cam_fn, code_run_cam]

def update_notebook(path, subject):
    with open(path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = get_camera_cells(subject)
    nb["cells"].extend(cells)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"🎉 Added Camera Inference to {path.name}! Total cells: {len(nb['cells'])}")

def main():
    update_notebook(BASE_DIR / "Mosquito_AI_Training_Colab.ipynb", "mosquito")
    update_notebook(BASE_DIR / "Leaf_AI_Training_Colab.ipynb", "leaf")

if __name__ == "__main__":
    main()
