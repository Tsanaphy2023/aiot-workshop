"""
Script to update Leaf_AI_Training_Colab.ipynb with Full-Version
YOLO11 Coffee Pathology & Mosquito Larvae Object Detection Pipelines.
"""

import json
from pathlib import Path

NOTEBOOK_PATH = Path(__file__).resolve().parent.parent / "Leaf_AI_Training_Colab.ipynb"

def create_markdown_cell(source_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source_lines]
    }

def create_code_cell(source_lines, cell_id=None):
    cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source_lines]
    }
    if cell_id:
        cell["id"] = cell_id
        cell["metadata"]["id"] = cell_id
    return cell

def main():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    new_cells = [
        # -------------------------------------------------------------
        # SECTION 11: YOLO11 SETUP
        # -------------------------------------------------------------
        create_markdown_cell([
            "---",
            "# ภาคพิเศษ: การฝึกสอนโมเดลตรวจจับวัตถุระดับสถานะศิลป์ (YOLO11 & YOLOv8)",
            "",
            "ในส่วนนี้เป็นการนำสถาปัตยกรรม **YOLO11 (Ultralytics)** มาใช้ตรวจจับวัตถุขนาดเล็กและรอยโรคพืชในระดับ Bounding Box รองรับทั้งงาน **พยาธิวิทยาพืช (Plant Pathology)** และงาน **เฝ้าระวังลูกน้ำยุงระบาดวิทยา (Vector Surveillance)** ผ่านคลาวด์ Roboflow Universe"
        ]),
        create_markdown_cell([
            "## 11. ติดตั้งไลบรารี YOLO11 และตรวจสอบการเชื่อมต่อ GPU",
            "",
            "ติดตั้งไลบรารี `ultralytics`, `supervision` และ `roboflow` พร้อมตรวจสอบสถานะชิปเร่งความเร็ว Tesla T4 GPU"
        ]),
        create_code_cell([
            "# ติดตั้งไลบรารีเวอร์ชันล่าสุดสำหรับการประมวลผล Computer Vision",
            "%pip install -q \"ultralytics==8.3.40\" supervision roboflow",
            "",
            "import ultralytics",
            "import torch",
            "",
            "# ตรวจสอบสภาพแวดล้อมระบบและชิป GPU",
            "ultralytics.checks()",
            "print(f\"CUDA Available: {torch.cuda.is_available()}\")",
            "if torch.cuda.is_available():",
            "    print(f\"Active GPU Device: {torch.cuda.get_device_name(0)}\")",
            "    print(f\"Total VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB\")"
        ], cell_id="yolo_setup_checks"),

        # -------------------------------------------------------------
        # SECTION 12: COFFEE PATHOLOGY DETECTION
        # -------------------------------------------------------------
        create_markdown_cell([
            "## 12. กรณีศึกษาที่ 1: ตรวจจับโรคใบกาแฟด้วย YOLO11 (Smart Select Coffee Pathology)",
            "",
            "ดาวน์โหลดชุดข้อมูลกาแฟ 3 คลาส (`leaf_rust`, `phoma`, `healthy`) ที่ผ่านการสกัดรอยโรคด้วย **Smart Select Bounding Box** จาก Roboflow มาฝึกสอนโมเดล YOLO11 Nano"
        ]),
        create_code_cell([
            "# ดาวน์โหลดชุดข้อมูลกาแฟ Smart Select จาก Roboflow",
            "from roboflow import Roboflow",
            "",
            "rf = Roboflow(api_key=\"tdetHe9WG2CTItfj0VHt\")",
            "project_coffee = rf.workspace(\"durian-nodisease\").project(\"aiot_workshop2026\")",
            "",
            "# ดาวน์โหลดเวอร์ชันล่าสุดสำหรับ YOLO11",
            "dataset_coffee = project_coffee.version(1).download(\"yolov11\")",
            "print(f\"✅ ชุดข้อมูลใบกาแฟพร้อมใช้งานที่: {dataset_coffee.location}\")"
        ], cell_id="download_coffee_yolo"),
        create_code_cell([
            "# สั่งฝึกสอนโมเดล YOLO11 Nano บนชุดข้อมูลโรคใบกาแฟ",
            "from ultralytics import YOLO",
            "",
            "# โหลด Pre-trained Weights YOLO11 Nano",
            "model_coffee = YOLO(\"yolo11n.pt\")",
            "",
            "# เริ่มกระบวนการฝึกสอน",
            "results_coffee = model_coffee.train(",
            "    data=f\"{dataset_coffee.location}/data.yaml\",",
            "    epochs=50,",
            "    imgsz=640,",
            "    batch=16,",
            "    device=0,",
            "    plots=True,",
            "    name=\"coffee_yolo11_run\"",
            ")"
        ], cell_id="train_coffee_yolo"),
        create_code_cell([
            "# ดูกราฟประวัติการฝึกสอนและค่าความแม่นยำ mAP50 / mAP50-95 ของโรคใบกาแฟ",
            "from IPython.display import Image, display",
            "import os",
            "",
            "results_img = \"runs/detect/coffee_yolo11_run/results.png\"",
            "if os.path.exists(results_img):",
            "    print(\"📊 กราฟผลการฝึกสอน YOLO11 (Box Loss, Class Loss, mAP50, Precision, Recall):\")",
            "    display(Image(results_img, width=800))",
            "else:",
            "    print(\"Results image not found yet.\")"
        ], cell_id="view_coffee_results"),

        # -------------------------------------------------------------
        # SECTION 13: MOSQUITO LARVAE SURVEILLANCE
        # -------------------------------------------------------------
        create_markdown_cell([
            "## 13. กรณีศึกษาที่ 2: โมเดลจำแนกชนิดลูกน้ำยุงระบาดวิทยา (Mosquito Larvae Surveillance)",
            "",
            "ตรวจจับและคัดแยกชนิดพันธุ์ลูกน้ำยุงลายและยุงรำคาญ 3 คลาสสำคัญทางการแพทย์และระบาดวิทยา:",
            "1. 🔴 **`Aedes_aegypti`** (ลูกน้ำยุงลายบ้าน — พาหะนำโรคไข้เลือดออก ชิคุนกุนยา ซิกา)",
            "2. 🟢 **`Aedes_albopictus`** (ลูกน้ำยุงลายสวน)",
            "3. 🟣 **`Culex_quinque`** (*Culex quinquefasciatus* — ลูกน้ำยุงรำคาญ พาหะโรคเท้าช้างและไข้สมองอักเสบ)",
            "",
            "ชุดข้อมูล Version 3 ประกอบด้วยภาพ **2,730 ภาพ** ผ่านการ Preprocessing & Augmentation ระดับสากลเรียบร้อยแล้ว"
        ]),
        create_code_cell([
            "# ดาวน์โหลดชุดข้อมูลลูกน้ำยุงลาย (Mosquito Larvae v3) ในฟอร์แมต yolo26",
            "from roboflow import Roboflow",
            "",
            "rf = Roboflow(api_key=\"tdetHe9WG2CTItfj0VHt\")",
            "project_mosquito = rf.workspace(\"durian-nodisease\").project(\"mosquito_larvae-ivnri\")",
            "",
            "# ดาวน์โหลด Version 3 ฟอร์แมต yolo26",
            "version_mosquito = project_mosquito.version(3)",
            "dataset_mosquito = version_mosquito.download(\"yolo26\")",
            "",
            "print(f\"✅ ชุดข้อมูลลูกน้ำยุงพร้อมใช้งานที่: {dataset_mosquito.location}\")"
        ], cell_id="download_mosquito_dataset"),
        create_code_cell([
            "# สั่งฝึกสอนโมเดลตรวจจับลูกน้ำยุงลายด้วย YOLO11",
            "from ultralytics import YOLO",
            "",
            "model_mosquito = YOLO(\"yolo11n.pt\")",
            "",
            "results_mosquito = model_mosquito.train(",
            "    data=f\"{dataset_mosquito.location}/data.yaml\",",
            "    epochs=50,",
            "    imgsz=640,",
            "    batch=16,",
            "    device=0,",
            "    plots=True,",
            "    name=\"mosquito_yolo11_run\"",
            ")"
        ], cell_id="train_mosquito_yolo"),
        create_code_cell([
            "# ประเมินผลความแม่นยำ mAP และ Confusion Matrix ของโมเดลตรวจจับลูกน้ำยุง",
            "metrics_mosquito = model_mosquito.val()",
            "print(f\"🎯 ค่าความแม่นยำเฉลี่ย mAP50: {metrics_mosquito.box.map50 * 100:.2f}%\")",
            "print(f\"🎯 ค่าความแม่นยำรวม mAP50-95: {metrics_mosquito.box.map * 100:.2f}%\")",
            "",
            "cm_mosquito_img = \"runs/detect/mosquito_yolo11_run/confusion_matrix.png\"",
            "if os.path.exists(cm_mosquito_img):",
            "    display(Image(cm_mosquito_img, width=650))"
        ], cell_id="val_mosquito_yolo"),

        # -------------------------------------------------------------
        # SECTION 14: EDGE AI EXPORT & QUANTIZATION
        # -------------------------------------------------------------
        create_markdown_cell([
            "## 14. ส่งออกโมเดลสู่มาตรฐานสากล (ONNX & TensorFlow Lite INT8) สำหรับ Edge AI & IoT",
            "",
            "แปลงโมเดลให้อยู่ในมาตรฐานเปิด **ONNX** สำหรับรันบน Raspberry Pi / Jetson และ **TensorFlow Lite INT8** สำหรับติดตั้งบนกล้องสมาร์ทฟาร์ม ESP32-S3"
        ]),
        create_code_cell([
            "# ส่งออกโมเดลโรคพืช (Coffee) สู่ ONNX และ TFLite",
            "best_coffee_weights = \"runs/detect/coffee_yolo11_run/weights/best.pt\"",
            "if os.path.exists(best_coffee_weights):",
            "    m_c = YOLO(best_coffee_weights)",
            "    m_c.export(format=\"onnx\", imgsz=640)",
            "    m_c.export(format=\"tflite\", imgsz=320, int8=True)",
            "    print(\"✅ ส่งออกโมเดลโรคใบกาแฟสู่ ONNX และ TFLite INT8 เรียบร้อย!\")",
            "",
            "# ส่งออกโมเดลลูกน้ำยุง (Mosquito) สู่ ONNX และ TFLite",
            "best_mosquito_weights = \"runs/detect/mosquito_yolo11_run/weights/best.pt\"",
            "if os.path.exists(best_mosquito_weights):",
            "    m_m = YOLO(best_mosquito_weights)",
            "    m_m.export(format=\"onnx\", imgsz=640)",
            "    m_m.export(format=\"tflite\", imgsz=320, int8=True)",
            "    print(\"✅ ส่งออกโมเดลลูกน้ำยุงสู่ ONNX และ TFLite INT8 เรียบร้อย!\")"
        ], cell_id="export_edge_ai_models"),
        create_code_cell([
            "# สรุปขนาดไฟล์โมเดลพร้อมดาวน์โหลดลงคอมพิวเตอร์",
            "import glob",
            "",
            "print(\"📦 รายการไฟล์โมเดล Edge AI พร้อมนำไปติดตั้งภาคสนาม:\")",
            "for pattern in [\"runs/detect/*_run/weights/best.onnx\", \"runs/detect/*_run/weights/*_int8.tflite\"]:",
            "    for mf in glob.glob(pattern):",
            "        sz_mb = os.path.getsize(mf) / (1024 * 1024)",
            "        print(f\"  - {mf} (ขนาด: {sz_mb:.2f} MB)\")",
            "",
            "# ปลด comment บรรทัดล่างสุดเพื่อดาวน์โหลดไฟล์ลงเครื่องคอมพิวเตอร์ผ่านเบราว์เซอร์:",
            "# from google.colab import files",
            "# files.download('runs/detect/coffee_yolo11_run/weights/best.onnx')"
        ], cell_id="list_exported_edge_models")
    ]

    nb["cells"].extend(new_cells)

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)

    print(f"🎉 Updated {NOTEBOOK_PATH.name} successfully!")
    print(f"📊 Total cells now: {len(nb['cells'])}")

if __name__ == "__main__":
    main()
