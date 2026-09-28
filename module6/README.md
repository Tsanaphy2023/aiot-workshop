# Module 6: ปฏิบัติการ AI Model คัดแยกผลผลิต และจำแนกโรคพืช
**(AI Object Detection on Conveyor & Plant Disease Classification)**

หลักสูตร: นวัตกรเกษตรอัจฉริยะ AIoT สำหรับเกษตรแม่นยำ รุ่นที่ 1 (วิทยาลัยการศึกษาตลอดชีวิต มหาวิทยาลัยเชียงใหม่)

---

## 📌 ไฟล์และสื่อการเรียนรู้ในโฟลเดอร์นี้
* 🎬 **ไฟล์วิดีโอบรรยาย (1080p Full HD, 36:46 นาที):** [Module6_video.mp4](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module6/Module6_video.mp4)
* 📝 **สคริปต์ถอดคำบรรยายเสียงภาษาไทย:** [Module_6_lecture_transcript.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module6/extracted_text/Module_6_lecture_transcript.txt) *(557 บรรทัด)*
* 📄 [**Module 6.1.pdf**](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module6/Module%206.1.pdf) *(34 หน้า)*: จากทฤษฎีสู่การชี้เป้าวัตถุบนสายพานด้วย **Roboflow** (การยกระดับ AI จากทายทั้งภาพ มาเป็นการตีกรอบตำแหน่ง Object Detection)
* 📄 [**Module 6.2.pdf**](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module6/Module%206.2.pdf) *(19 หน้า)*: คอมพิวเตอร์วิทัศน์: จำแนกโรคพืชจากใบด้วย **Machine Learning บน Google Colab**
* 📝 **ข้อความสกัด:**
  * [Module_6_1_extracted.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module6/extracted_text/Module_6_1_extracted.txt)
  * [Module_6_2_extracted.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module6/extracted_text/Module_6_2_extracted.txt)

---

## 💡 สรุปสาระสำคัญของเนื้อหา

### 1. การเปลี่ยนผ่านจาก Image Classification สู่ Object Detection (Roboflow)
* **ข้อจำกัดของการจำแนกภาพแบบเดิม (Image Classification):** โมเดลจะตอบได้แค่ว่าภาพนี้คืออะไรทั้งรูป (ทายทีละลูก) ถ้ามีผลผลิตหลายผลในกล้องเดียวจะคัดแยกไม่ได้
* **การใช้ Object Detection (เช่น YOLO Architecture):**
  * สามารถระบุตำแหน่งของผลผลิตแต่ละผลด้วย **Bounding Box** ($x, y, w, h$)
  * สามารถตรวจนับและคัดแยกผลผลิตหลายเกรด (ดิบ/สุก/มีตำหนิ) ที่เคลื่อนที่บนสายพานลำเลียงได้พร้อมกันในเฟรมเดียว
* **ขั้นตอนบน Roboflow:**
  1. อัปโหลดชุดภาพผลผลิตจากสายพานจริง
  2. การทำ **Data Annotation** ตีกรอบวัตถุและกำหนด Label (Class)
  3. การทำ **Data Augmentation** เพิ่มความหลากหลาย (หมุนภาพ, ปรับความสว่าง, Noise)
  4. Export Dataset สู่รูปแบบที่พร้อมเทรนโมเดล (YOLOv8/YOLOv11 PyTorch TXT format)

### 2. การจำแนกโรคพืชจากใบด้วย Machine Learning บน Google Colab
* การรวบรวม Dataset ภาพใบพืชสุขภาพดี และใบที่เป็นโรคต่างๆ (เช่น เชื้อรา, ไวรัส, แมลงทำลาย)
* การใช้ **Convolutional Neural Networks (CNN)** หรือ **Transfer Learning (MobileNet / ResNet)**
* การวัดผลประสิทธิภาพของโมเดลด้วย **Accuracy**, **Precision**, **Recall** และ **Confusion Matrix**
* การแปลงโมเดลสู่ **TFLite / ONNX** เพื่อนำไปรันบนอุปกรณ์ประมวลผลปลายทาง (Edge AI)

---

## 3. สรุปประเด็นข้อสอบสำคัญ (Quiz Highlights)
* **ความแตกต่างระหว่าง Classification กับ Object Detection:**
  * **Classification:** ทายผลลัพธ์ภาพรวมทั้งภาพ เหมาะกับภาพเดี่ยวตรงกลาง ไม่สามารถบอกพิกัดตำแหน่งได้
  * **Object Detection:** สามารถตีกรอบ Bounding Box ชี้พิกัดตำแหน่ง ($x, y, w, h$) ของวัตถุแต่ละชิ้นบนสายพานลำเลียงได้พร้อมกันในภาพเดียว
* **เครื่องมือออนไลน์สำหรับจัดการภาพและวาดกรอบ Bounding Box:**
  * **Roboflow (roboflow.com):** แพลตฟอร์มบนเว็บเบราว์เซอร์สำหรับทำ Data Annotation (วาด Bounding Box), Data Augmentation และส่งออก Dataset สำหรับเทรนโมเดล YOLO
* **หลักการตั้งชื่อกลุ่ม (Class Name) ในการสอน AI:**
  * **ใช้คำสั้น สื่อความหมาย และสะกดให้เหมือนกันทุกรูป (เช่น `healthy`, `rotten`):** เพราะคอมพิวเตอร์เป็นระบบ Case-Sensitive การพิมพ์สลับพิมพ์เล็ก-ใหญ่หรือสะกดไม่ตรงกันจะทำให้ระบบมองเป็นคนละคลาสทันที
* **จำนวนรูปถ่ายขั้นต่ำที่แนะนำต่อ 1 Class สำหรับเริ่มต้น:**
  * **20 รูปถ่ายต่อ 1 Class (ขั้นต่ำ)** โดยต้องคละมุมมอง คละสภาพแสง และถ่ายบนฉากหลังจริง จากนั้นใช้ Data Augmentation เพิ่มจำนวนภาพเป็น 3 เท่า (60 ภาพ)
* **ลักษณะการถ่ายภาพที่ดีที่สุดสำหรับสอน AI:**
  * **คละมุมมอง (บน/ข้าง/เอียง), คละสภาพแสง (เช้า/บ่าย/แสงไฟ) และมีฉากหลังเป็นสายพานจริง:** เพื่อให้ AI ทำงานได้แม่นยำในหน้างานจริง ไม่เกิด Overfitting กับฉากหลังสตูดิโอ





