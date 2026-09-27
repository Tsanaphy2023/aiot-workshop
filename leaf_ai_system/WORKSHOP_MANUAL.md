# 🍃 Leaf AI Workshop Manual: Computer Vision & Edge AI Classification
### คู่มือการจัดกิจกรรมเชิงปฏิบัติการ: กิจกรรมที่ 12 — ปัญญาประดิษฐ์คอมพิวเตอร์วิทัศน์จำแนกโรคพืชและประเมินคุณภาพผลผลิต
**โครงการ Smart Farm AIoT Workshop | มหาวิทยาลัยราชภัฏรำไพพรรณี (RBRU) × มหาวิทยาลัยเชียงใหม่ (CMU)**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Tsanaphy2023/aiot-workshop/blob/main/leaf_ai_system/Leaf_AI_Training_Colab.ipynb)
[![GitHub Repository](https://img.shields.io/badge/GitHub-aiot--workshop-blue?logo=github)](https://github.com/Tsanaphy2023/aiot-workshop)
[![Web Portal](https://img.shields.io/badge/Web%20Portal-Leaf%20AI%20Studio-00e676)](http://localhost/cmu_aiot/leaf_ai_system/)

---

## 🎯 1. วัตถุประสงค์และผลลัพธ์การเรียนรู้ (Learning Outcomes)

เมื่อสิ้นสุดการจัดกิจกรรมเชิงปฏิบัติการนี้ ผู้เรียนสามารถ:
1. **อธิบายหลักการคอมพิวเตอร์วิทัศน์สำหรับสมาร์ทฟาร์ม (Remembering & Understanding):** อธิบายขั้นตอนการประมวลผลภาพใบพืช การทำ Normalization และการจำแนกโรคด้วย Deep Convolutional Neural Networks (CNN) ได้
2. **จัดการชุดข้อมูลและแบ่งข้อมูลแบบแบ่งชั้น (Applying):** ดำเนินการแบ่งชุดข้อมูลภาพถ่ายใบพืช 5,846 ภาพ เป็น Train (70%), Validation (15%), และ Test (15%) แบบ **Stratified Split** เพื่อรักษาสัดส่วนของทุกคลาสโรคให้สมดุลได้
3. **ฝึกสอนและปรับแต่งไฮเปอร์พารามิเตอร์ (Analyzing & Evaluating):** สั่งรันการฝึกสอนโมเดลบนเครื่องคอมพิวเตอร์จริง (Local MPS/CUDA) หรือบนคลาวด์ GPU (Google Colab Tesla T4) และวิเคราะห์ประสิทธิภาพผ่าน **Confusion Matrix**, **Macro F1-Score**, Precision และ Recall ได้
4. **ประยุกต์ส่งออกโมเดลสู่ระบบฝังตัว (Creating):** แปลงน้ำหนักโมเดล PyTorch (`.pth`) เป็นรูปแบบ **ONNX** และ **TorchScript (`.pt`)** เพื่อนำไปบูรณาการใช้งานร่วมกับกล้องติดแปลงเกษตร (Edge AI Camera / ESP32-CAM / Raspberry Pi) ได้

---

## ⏱️ 2. ตารางแผนการจัดการเรียนรู้ 60 นาที (Facilitator Matrix)

| ช่วงเวลา | หัวข้อกิจกรรม | การจัดกิจกรรม / วิธีปฏิบัติ | ทรัพยากร / สื่อการสอน |
| :--- | :--- | :--- | :--- |
| **00:00 - 10:00** | **12.1 สำรวจข้อมูลและแบ่งสัดส่วน Stratified Split** | - อธิบายชุดข้อมูล 6 พืช 18 คลาส (5,846 ภาพ)<br>- เปิดพอร์ทัลแท็บที่ 1 เลือกพืช และสั่งรันการแบ่ง Train/Val/Test 70:15:15 | - Web Portal แท็บ 01<br>- `scripts/01_split_dataset.py` |
| **10:00 - 20:00** | **12.2 เปรียบเทียบสถาปัตยกรรมโครงข่ายประสาทเทียม** | - บรรยายสถาปัตยกรรม MobileNetV2, ResNet18 และ LeafNet (Custom Lightweight CNN)<br>- อภิปรายข้อจำกัดของหน่วยความจำบนบอร์ด Edge AI | - Web Portal แท็บ 02<br>- โมเดล `leaf_net.py` |
| **20:00 - 35:00** | **12.3 ปฏิบัติการฝึกสอนโมเดลจริง (Live Model Training)** | - ให้ผู้เรียนกดเริ่มเทรนบนเว็บ หรือเปิดรันบน Google Colab GPU T4<br>- สังเกต Terminal Log สด และกราฟ Loss/Accuracy Curves | - Web Portal แท็บ 03<br>- Colab Notebook One-Click Badge |
| **35:00 - 45:00** | **12.4 ประเมินผลและวิเคราะห์แผนภาพความสับสน** | - รันประเมินผลบน Test Set (15% Unseen Data)<br>- วิเคราะห์ค่า Heatmap บนแนวทแยงมุม และหาคลาสที่มีความสับสน | - Web Portal แท็บ 04<br>- `outputs/reports/*.png` |
| **45:00 - 55:00** | **12.5 ห้องทดลองทำนายภาพโรคพืชสด (Inference Playground)** | - นำเข้าภาพใบพืชตัวอย่าง หรืออัปโหลดภาพใบพืชสด<br>- สังเกตผลลัพธ์การวินิจฉัยโรคและแถบเปอร์เซ็นต์ความมั่นใจ Top-3 | - Web Portal แท็บ 05<br>- คลังภาพ `data/` |
| **55:00 - 60:00** | **12.6 ส่งออกโมเดลสู่ Edge AI และสรุปคำถามชวนคิด** | - สั่งแปลงโมเดลเป็น `.onnx` และ `.pt`<br>- สรุปภาพรวมและประเมินแบบทดสอบ 12-Q | - Web Portal แท็บ 06<br>- `models/export.py` |

---

## 💻 3. สถาปัตยกรรมระบบและไฮไลต์ทางเทคนิค (System Architecture)

```
leaf_ai_system/
├── config/config.py               # ตั้งค่าพาธ, รายชื่อคลาส, สัดส่วน Split, Hyperparameters
├── data/splits/                   # เก็บไฟล์ดัชนีแบ่งชุดข้อมูล (train.csv, val.csv, test.csv)
├── models/
│   ├── leaf_net.py                # Lightweight CNN (1.2M Params) สำหรับชิปไมโครคอนโทรลเลอร์
│   ├── transfer_learning.py       # MobileNetV2 และ ResNet18 Pre-trained
│   └── export.py                  # โมดูลส่งออกเป็น ONNX / TorchScript (.pt)
├── scripts/
│   ├── 01_split_dataset.py        # Stratified Train/Val/Test Splitter
│   ├── 02_train.py                # Deep Learning Trainer (Apple MPS / CUDA / CPU)
│   ├── 03_evaluate.py             # Evaluator (Confusion Matrix & F1-Score)
│   └── 04_predict.py              # CLI & JSON Inference Engine
├── utils/                         # Datasets, Device Detector, Metrics, Visualizer
├── outputs/                       # Checkpoints (.pth), Training Logs, Reports (.png)
├── index.html                     # 🌐 Cyber Emerald Glassmorphism Web Portal
├── style.css                      # Modern Responsive Design System
├── app.js                         # Web Client Controller
├── server.py                      # Python Standalone Server (Port 8008)
├── api/api.php                    # Apache / XAMPP REST API
└── Leaf_AI_Training_Colab.ipynb   # 🚀 Google Colab Notebook with GPU T4
```

### ข้อมูลเชิงลึกชุดข้อมูลใบพืช (Dataset Breakdown):
| ชนิดพืช (Crop) | จำนวนภาพรวม | รายชื่อคลาสโรคและสุขภาพใบ |
| :--- | :--- | :--- |
| **Corn (ข้าวโพด)** | 3,924 ภาพ | Blight, Common Rust, Gray Leaf Spot, Healthy |
| **Potato (มันฝรั่ง)** | 904 ภาพ | Early Blight, Late Blight, Healthy |
| **Coffee (กาแฟ)** | 153 ภาพ | Rust, Cercospora Leaf Spot, Phoma Leaf Spot, Healthy |
| **Orange (ส้ม)** | 429 ภาพ | Citrus Canker, Black Spot, Healthy |
| **Mango (มะม่วง)** | 243 ภาพ | Anthracnose, Bacterial Canker, Healthy |
| **Banana (กล้วย)** | 208 ภาพ | Black Sigatoka, Cordana Leaf Spot, Healthy |
| **รวมทั้งสิ้น (6 พืช)** | **5,846 ภาพ** | **18 คลาสจำแนก** |

---

## 🛠️ 4. ขั้นตอนการปฏิบัติการอย่างละเอียด (Step-by-Step Execution)

### ช่องทางที่ 1: ปฏิบัติการผ่าน Web Application Portal (แนะนำสำหรับผู้เรียนทั่วไป)

1. **เข้าสู่ระบบ:**
   * เปิด Google Chrome หรือเบราว์เซอร์ไปที่: [http://localhost/cmu_aiot/leaf_ai_system/](http://localhost/cmu_aiot/leaf_ai_system/)
   * สังเกตแถบสถานะด้านบนขวา: ต้องขึ้นสถานะ **🟢 Online**
2. **ขั้นตอน 01 (สำรวจ & แบ่งข้อมูล):**
   * เลือกพืช เช่น `ข้าวโพด (Corn)`
   * สังเกตแถบ Slider อัตราส่วน 70% Train, 15% Val, 15% Test
   * คลิกปุ่ม **"⚡ สั่งรันการแบ่งชุดข้อมูลจริง (Execute Real Split)"**
   * ระบบจะแสดงตารางแจกแจงจำนวนภาพของแต่ละคลาสอย่างสมดุล
3. **ขั้นตอน 02 (สถาปัตยกรรม & ไฮเปอร์พารามิเตอร์):**
   * คลิกเลือกโมเดล **MobileNetV2** หรือ **LeafNet**
   * ปรับตั้งค่า: Epochs = 15, Batch Size = 32, Learning Rate = 0.001
4. **ขั้นตอน 03 (สั่งฝึกสอนโมเดลจริง):**
   * สำหรับเครื่องที่มี GPU/MPS: คลิกปุ่ม **"▶ เริ่มต้นฝึกสอนบนเครื่องจริง"** แล้วสังเกตหน้าต่าง Terminal Output แบบสด
   * สำหรับผู้เรียนที่ต้องการใช้ Cloud GPU ฟรี: คลิกปุ่ม **"🚀 เปิดรันใน Google Colab"**
5. **ขั้นตอน 04 (ประเมินผล & แผนภาพความสับสน):**
   * คลิกปุ่ม **"🔍 สั่งประเมินผลบน Test Set"**
   * วิเคราะห์ค่า Test Accuracy, Macro F1, Precision, Recall และแผนภาพ **Confusion Matrix Heatmap**
6. **ขั้นตอน 05 (ห้องทดลองทำนายภาพโรคพืช):**
   * คลิกเลือกภาพตัวอย่างจากคลัง หรือลากวางไฟล์ภาพใบไม้จริงจากคอมพิวเตอร์
   * คลิกปุ่ม **"✨ วิเคราะห์และทำนายโรคพืช (Predict Now)"**
   * ตรวจสอบผลลัพธ์คลาสที่มีความน่าจะเป็นสูงสุดและเปอร์เซ็นต์ความมั่นใจ (Confidence Gauge)
7. **ขั้นตอน 06 (ส่งออก Edge AI):**
   * คลิกปุ่ม **"💾 แปลงและส่งออกโมเดล (Export Models)"**
   * ดาวน์โหลดไฟล์ `.onnx` และ `.pt` พร้อมไฟล์ Metadata เพื่อนำไปใส่ในแอปพลิเคชันหรือบอร์ดสมองกลฝังตัว

---

### ช่องทางที่ 2: ปฏิบัติการผ่าน Google Colab (One-Click Cloud GPU T4)

เหมาะสำหรับการจัดอบรมที่ผู้เรียนใช้คอมพิวเตอร์พกพาทั่วไปที่ไม่มีการ์ดจอแยก:
1. เปิดลิงก์: [Google Colab: Leaf_AI_Training_Colab.ipynb](https://colab.research.google.com/github/Tsanaphy2023/aiot-workshop/blob/main/leaf_ai_system/Leaf_AI_Training_Colab.ipynb)
2. ไปที่เมนู `Runtime` -> `Change runtime type` -> เลือก **T4 GPU** -> กด `Save`
3. กดปุ่ม `Run all` (Ctrl+F9)
4. โค้ดจะทำการ:
   * Clone โค้ดจาก GitHub `https://github.com/Tsanaphy2023/aiot-workshop`
   * สั่งรันการแบ่ง Train/Val/Test
   * ฝึกสอนโมเดลด้วยความเร็วสูงผ่าน CUDA
   * วาดกราฟผลการประเมิน Confusion Matrix Heatmap
   * แปลงโมเดลเป็น `.onnx` และมีปุ่มดาวน์โหลดไฟล์กลับสู่เครื่องคอมพิวเตอร์อัตโนมัติ

---

### ช่องทางที่ 3: ปฏิบัติการผ่าน Command Line Interface (CLI)

สำหรับวิทยากรหรือผู้ช่วยสอน (TA) ที่ต้องการรันและควบคุมการประมวลผลผ่าน Terminal:

```bash
# 1. เข้าสู่โฟลเดอร์ระบบและเปิดใช้งานสภาพแวดล้อมเสมือน
cd /Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/leaf_ai_system
source .venv/bin/activate

# 2. แบ่งชุดข้อมูลพืชกาแฟแบบ Stratified Split (70:15:15)
python scripts/01_split_dataset.py --crop coffee --train-ratio 0.70 --val-ratio 0.15 --test-ratio 0.15

# 3. สั่งฝึกสอนโมเดล MobileNetV2 ด้วย Apple MPS หรือ CUDA
python scripts/02_train.py --crop coffee --model mobilenet_v2 --epochs 15 --batch-size 16 --lr 0.001

# 4. ประเมินผลโมเดลบนชุดทดสอบ Test Set
python scripts/03_evaluate.py --crop coffee --model mobilenet_v2

# 5. สั่งทดสอบทำนายภาพใบพืชเดี่ยว
python scripts/04_predict.py --image "data/splits/coffee/test.csv" --model mobilenet_v2 --crop coffee

# 6. ส่งออกโมเดลเป็น ONNX และ TorchScript
python models/export.py --crop coffee --model mobilenet_v2
```

---

## ⚠️ 5. ปัญหาที่พบบ่อยและแนวทางแก้ไข (Troubleshooting)

1. **แถบสถานะบนหน้าเว็บขึ้นสีแดง (Offline):**
   * **สาเหตุ:** XAMPP Apache หรือ Python Server ยังไม่ได้เปิดทำงาน
   * **วิธีแก้:** เปิดโปรแกรม XAMPP Control Panel แล้วกด Start Apache หรือเปิด Terminal รันคำสั่ง `python server.py` ในโฟลเดอร์ `leaf_ai_system`
2. **การเทรนบนคอมพิวเตอร์ใช้เวลานานเกินไป:**
   * **สาเหตุ:** เครื่องคอมพิวเตอร์ไม่มีการ์ดจอแยก หรือไม่ได้ติดตั้งไดรเวอร์ CUDA/MPS ทำให้ PyTorch รันบน CPU
   * **วิธีแก้:** ให้เปลี่ยนไปใช้การรันผ่าน **Google Colab (ปุ่มสีส้ม)** ซึ่งจะได้รับ GPU Tesla T4 ฟรีจาก Google
3. **โมเดลสับสนระหว่างอาการโรคที่เกิดจุดใบคล้ายกัน:**
   * **สาเหตุ:** สภาพแสง ความละเอียดของภาพ หรืออาการโรคระยะแรกเริ่มที่มีรอยโรคคล้ายคลึงกัน (เช่น Early Blight กับ Late Blight ในมันฝรั่ง)
   * **วิธีแก้:** วิเคราะห์แถวของคลาสนั้นใน **Confusion Matrix**, เพิ่มเทคนิค Data Augmentation (เช่น ColorJitter, RandomAffine) หรือเพิ่มจำนวนรอบการฝึกสอน (Epochs)

---

## 📝 6. แบบทดสอบวัดผลการเรียนรู้และคำถามชวนคิด (Assessment & Discussion)

1. **คำถาม:** เพราะเหตุใดการแบ่งชุดข้อมูลแบบ **Stratified Splitting** จึงมีความสำคัญอย่างยิ่งสำหรับชุดข้อมูลโรคพืชทางการเกษตร?
   * *แนวตอบ:* เพราะโรคพืชในธรรมชาติมีอัตราการเกิดที่ไม่เท่ากัน (Class Imbalance) การสุ่มแบ่งแบบ Stratified จะการันตีว่าในทุกชุดข้อมูล (Train, Val, Test) จะมีสัดส่วนของโรคพืชทุกชนิดเท่าเทียมกัน ทำให้โมเดลได้เรียนรู้และถูกทดสอบกับทุกโรคอย่างเที่ยงธรรม
2. **คำถาม:** สถาปัตยกรรม **LeafNet** มีจุดเด่นอย่างไรเมื่อเทียบกับ **MobileNetV2** และ **ResNet18**?
   * *แนวตอบ:* LeafNet มีขนาดพารามิเตอร์เพียงประมาณ 1.2 ล้านพารามิเตอร์ และไฟล์โมเดลขนาดเล็กเพียงประมาณ 4.8MB จึงสามารถนำไปติดตั้งลงในหน่วยความจำแฟลชของบอร์ดไมโครคอนโทรลเลอร์ขนาดเล็ก (เช่น ESP32-S3) สำหรับระบบ Edge AI ในแปลงเกษตรได้โดยตรง
3. **คำถาม:** เหตุใดในงานคัดแยกโรคพืช เราจึงไม่ควรพิจารณาเฉพาะค่า **Accuracy** เพียงอย่างเดียว?
   * *แนวตอบ:* เพราะหากชุดข้อมูลมีภาพใบปกติ (Healthy) เป็นส่วนใหญ่ โมเดลที่ทายแต่ใบปกติก็จะได้ค่า Accuracy สูง แต่ไม่สามารถตรวจจับโรคจริงได้ จึงจำเป็นต้องพิจารณา **Confusion Matrix**, **Macro F1-Score**, **Precision** และ **Recall** ร่วมด้วยเสมอ
