# Module 9: ปฏิบัติการสร้าง AI Model ตรวจสอบและจำแนกโรคพืช
**(Plant Disease Classification & Computer Vision Deployment)**

หลักสูตร: นวัตกรเกษตรอัจฉริยะ AIoT สำหรับเกษตรแม่นยำ รุ่นที่ 1 (วิทยาลัยการศึกษาตลอดชีวิต มหาวิทยาลัยเชียงใหม่)

---

## 📌 ไฟล์เอกสารในโฟลเดอร์นี้
* 📄 [**Module9.pdf**](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module9/Module9.pdf) *(19 หน้า)*: คอมพิวเตอร์วิทัศน์: จำแนกโรคพืชจากใบด้วย Machine Learning จากแนวคิดสู่การลงมือทำจริงบน Google Colab
* 📝 **ข้อความสกัด:** [Module_9_extracted.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module9/extracted_text/Module_9_extracted.txt)

---

## 💡 สรุปสาระสำคัญของเนื้อหา
1. **การเรียนรู้ของมนุษย์ vs ปัญญาประดิษฐ์:**
   * มนุษย์เรียนรู้โรคพืชจากประสบการณ์และการจดจำรูปแบบรอยโรคบนใบ
   * AI ใช้เครือข่ายประสาทเทียม (Deep Learning / CNN) เพื่อคำนวณและสกัด Feature ทางสถิติของพิกเซลสี รูปร่าง และลวดลายรอยโรค
2. **ขั้นตอนการปฏิบัติการบน Google Colab:**
   * โหลด Dataset ภาพใบพืช
   * ทำ Data Preprocessing และ Image Normalization
   * เทรนโมเดลด้วย Transfer Learning
   * บันทึกโมเดลและส่งออก (Export) ไปใช้บนอุปกรณ์ Edge Gateway ในแปลงเกษตร
