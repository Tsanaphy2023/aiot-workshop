# 🍃 Leaf AI Workshop: Deep Learning Classification & Edge AI Pipeline
**ระบบจัดเก็บชุดข้อมูล, แบ่ง Train/Val/Test แบบ Stratified และฝึกสอนโมเดลปัญญาประดิษฐ์จำแนกโรคพืชและคุณภาพผลผลิต**

---

## 📁 โครงสร้างระบบ (System Architecture)

```
leaf_ai_system/
├── config/
│   ├── __init__.py
│   └── config.py               # ตั้งค่าพาธ, รายชื่อคลาส, สัดส่วน Split, Hyperparameters
├── data/
│   └── splits/                 # เก็บผลลัพธ์การแบ่งชุดข้อมูล (train.csv, val.csv, test.csv)
│       ├── corn/
│       ├── coffee/
│       ├── potato/
│       └── all/
├── models/
│   ├── __init__.py
│   ├── leaf_net.py             # Custom Lightweight CNN สำหรับ Edge AI / ESP32
│   ├── transfer_learning.py    # MobileNetV2 และ ResNet18 สำหรับการจำแนกความแม่นยำสูง
│   └── export.py               # ส่งออกโมเดลเป็น .onnx และ TorchScript (.pt)
├── scripts/
│   ├── 01_split_dataset.py     # สคริปต์แบ่ง Train (70%) / Val (15%) / Test (15%) แบบ Stratified
│   ├── 02_train.py             # สคริปต์ฝึกสอนโมเดล (รองรับ Apple MPS GPU, CUDA, CPU)
│   ├── 03_evaluate.py          # สคริปต์ประเมินผลบน Test Set (Confusion Matrix, F1-Score)
│   └── 04_predict.py           # สคริปต์ทดสอบทำนายภาพเดี่ยว หรือทั้งโฟลเดอร์ (รองรับ JSON สำหรับ API)
├── utils/
│   ├── __init__.py
│   ├── dataset.py              # PyTorch Dataset Loader & Data Augmentation
│   ├── device.py               # ตรวจจับฮาร์ดแวร์ประมวลผล (Apple MPS / NVIDIA CUDA / CPU)
│   ├── metrics.py              # คำนวณ Accuracy, Precision, Recall, F1, Confusion Matrix Heatmap
│   └── visualizer.py           # วาดกราฟเปรียบเทียบ Loss & Accuracy Curves
├── outputs/
│   ├── checkpoints/            # บันทึกน้ำหนักโมเดลที่ดีที่สุด (best_model.pth)
│   ├── logs/                   # บันทึกประวัติการ Train (history.json)
│   └── reports/                # กราฟ Confusion Matrix และ Classification Report
├── index.html                  # 🌐 Web Application Portal แสดงและควบคุมทุกขั้นตอน
├── style.css                   # Glassmorphism & Cyber Emerald Design System
├── app.js                      # Client Application ควบคุม Live Training & Inference
├── server.py                   # Python Dual-Backend Server (Port 8008)
├── Leaf_AI_Training_Colab.ipynb # 🚀 Google Colab Notebook รันบน Tesla T4 GPU ฟรี
├── api/
│   └── api.php                 # Apache / XAMPP PHP REST API
├── requirements.txt            # ไลบรารีที่จำเป็น
└── README.md                   # คู่มือการใช้งานฉบับสมบูรณ์
```

---

## 🌐 1. การใช้งานผ่าน Web Application Portal

ระบบมาพร้อมกับเว็บแอปพลิเคชันแบบอินเตอร์แอคทีฟ สามารถเข้าใช้งานได้ทันทีผ่าน Browser:

👉 **URL เข้าใช้งาน (XAMPP / Apache):** [http://localhost/cmu_aiot/leaf_ai_system/](http://localhost/cmu_aiot/leaf_ai_system/)

> **ฟังก์ชันการทำงานบนเว็บ:**
> 1. **Data Explorer & Split:** เลือกพืช (6 ชนิด / 18 คลาส), ปรับ Slider สัดส่วน 70:15:15 แล้วกดรันการแบ่งจริง
> 2. **Model Specs:** เปรียบเทียบ MobileNetV2, ResNet18 และ LeafNet (Custom CNN) พร้อมปรับ Epochs, Batch, LR
> 3. **Live Training:** กดเริ่มเทรน พร้อมแถบแสดงผล Terminal Log สด และกราฟ Loss/Accuracy อัปเดตอัตโนมัติ
> 4. **Evaluation:** ดึงค่า Test Accuracy, Macro F1 และดูภาพ Confusion Matrix Heatmap
> 5. **Live Inference Playground:** ลากวางภาพใบไม้ หรือเลือกจากคลังตัวอย่างเพื่อกดวิเคราะห์โรคพืชและดู % ความมั่นใจ
> 6. **Edge AI Export:** กดส่งออกเป็นไฟล์ `.onnx` และ `.pt` (TorchScript) สำหรับบอร์ดสมองกลฝังตัว

---

## 🚀 2. การใช้งานบน Google Colab (One-Click GPU T4)

สำหรับผู้เข้าอบรมหรือผู้ใช้งานที่ต้องการฝึกสอนด้วยการเร่งความเร็วผ่าน **Free Cloud GPU (Tesla T4)**:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Tsanaphy2023/aiot-workshop/blob/main/leaf_ai_system/Leaf_AI_Training_Colab.ipynb)
[![GitHub Repository](https://img.shields.io/badge/GitHub-aiot--workshop-blue?logo=github)](https://github.com/Tsanaphy2023/aiot-workshop)

* คลิกปุ่ม **Open in Colab** ด้านบน
* เลือกเมนู `Runtime` -> `Change runtime type` -> เลือก **T4 GPU**
* กด `Run All` เพื่อโคลนโปรเจกต์จาก GitHub, เทรนโมเดล, ประเมินผล และดาวน์โหลดโมเดล `.onnx` กลับมาใช้งานได้ทันที!

---

## 💻 3. ขั้นตอนการใช้งานผ่าน Command Line (CLI)

### 0. สภาพแวดล้อมเสมือน (Virtual Environment)
ระบบได้จัดเตรียม `.venv` ด้วย `Python 3.11` และติดตั้ง `PyTorch (Apple MPS)`, `Torchvision`, `Scikit-Learn`, `Pandas`, `Matplotlib`, `Seaborn` เรียบร้อยแล้ว:

```bash
# เปิดใช้งาน Virtual Environment
source leaf_ai_system/.venv/bin/activate
cd leaf_ai_system
```

---

### ขั้นตอนที่ 1: แบ่งชุดข้อมูล Train / Val / Test (Stratified Splitting)
สคริปต์จะสแกนโฟลเดอร์ภาพ และทำการสุ่มแบ่งข้อมูลอย่างสมดุล (70% ฝึกสอน, 15% ตรวจสอบระหว่างเทรน, 15% ทดสอบจริง):

```bash
# ตัวอย่างที่ 1: แบ่งเฉพาะพืชข้าวโพด (Corn - 4 classes, 3,924 ภาพ)
python scripts/01_split_dataset.py --crop corn

# ตัวอย่างที่ 2: แบ่งกาแฟ (Coffee - 3 classes)
python scripts/01_split_dataset.py --crop coffee

# ตัวอย่างที่ 3: แบ่งมันฝรั่ง (Potato - 3 classes)
python scripts/01_split_dataset.py --crop potato

# ตัวอย่างที่ 4: รวมทุกพืชทุกคลาสเข้าด้วยกัน (All 18 classes)
python scripts/01_split_dataset.py --crop all

# ตัวเลือกเสริม: สร้างโฟลเดอร์แยก train/ val/ test/ ด้วย symlinks (ไม่เปลืองพื้นที่ฮาร์ดดิสก์)
python scripts/01_split_dataset.py --crop corn --create_dirs
```

---

### ขั้นตอนที่ 2: ฝึกสอนโมเดล (Model Training Pipeline)
สคริปต์จะดึงข้อมูลจาก `train.csv` และ `val.csv` มีระบบ Early Stopping, ปรับ Learning Rate แบบ Cosine Annealing, พร้อมตรวจจับ Apple Silicon GPU (MPS) หรือ NVIDIA CUDA อัตโนมัติ:

```bash
# เทรนโมเดล MobileNetV2 (แนะนำ: เร็วและแม่นยำสูง เหมาะกับ Edge AI)
python scripts/02_train.py --crop corn --backbone mobilenet_v2 --epochs 15 --batch_size 32 --lr 0.001

# เทรนโมเดล ResNet18
python scripts/02_train.py --crop corn --backbone resnet18 --epochs 15

# เทรนด้วย LeafNet (Custom Lightweight CNN ขนาดเบาเพียง 1.2M พารามิเตอร์)
python scripts/02_train.py --crop corn --backbone leaf_net --epochs 20
```

> **สิ่งที่ระบบจะบันทึกอัตโนมัติ:**
> - โมเดลน้ำหนักดีที่สุด: `outputs/checkpoints/<crop>_<backbone>_best.pth`
> - กราฟ Loss & Accuracy Curves: `outputs/reports/<crop>_<backbone>_curves.png`
> - ข้อมูลประวัติการเทรน: `outputs/logs/<crop>_<backbone>_history.json`

---

### ขั้นตอนที่ 3: ประเมินผลบนชุดทดสอบ (Model Evaluation)
ทดสอบโมเดลกับภาพที่ไม่เคยเห็นมาก่อนใน `test.csv` พร้อมสร้าง Heatmap Confusion Matrix:

```bash
python scripts/03_evaluate.py --checkpoint outputs/checkpoints/corn_mobilenet_v2_best.pth
```

> **ผลลัพธ์:**
> - ค่า Test Accuracy, Precision, Recall, F1-Score
> - แผนภาพความสับสน: `outputs/reports/corn_mobilenet_v2_confusion_matrix.png`
> - รายงานละเอียด: `outputs/reports/corn_mobilenet_v2_test_report.json`

---

### ขั้นตอนที่ 4: ทดสอบทำนายภาพ (Inference & Prediction)
ใช้ทำนายภาพเดี่ยวหรือประมวลผลทั้งโฟลเดอร์ รองรับการแสดงผล JSON สำหรับเชื่อมต่อกับระบบ Web หรือ Mobile Application:

```bash
# ทำนายภาพเดี่ยว พร้อมแสดง Top-3 ความมั่นใจ (%)
python scripts/04_predict.py \
  --checkpoint outputs/checkpoints/corn_mobilenet_v2_best.pth \
  --image "/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/leaf workshop/corn_dataset/Healthy/0a0684f8-142f-4c81-801a-8bb7f3693e50___R.S_HL 7935 copy.jpg"

# ส่งออกเป็น JSON สำหรับเชื่อมกับ PHP / Python Web API
python scripts/04_predict.py \
  --checkpoint outputs/checkpoints/corn_mobilenet_v2_best.pth \
  --image path/to/leaf.jpg --json
```

---

### ขั้นตอนที่ 5: ส่งออกโมเดลสำหรับ Edge AI / IoT (Model Export)
แปลงโมเดล PyTorch เป็น **ONNX** และ **TorchScript** เพื่อนำไปรันบน Raspberry Pi, Jetson Nano, หรือแปลงเป็น TFLite สำหรับ Edge Devices:

```bash
python models/export.py --checkpoint outputs/checkpoints/corn_mobilenet_v2_best.pth
```
