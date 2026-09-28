# Module 8: เครือข่ายไร้สายระยะไกล (LoRa) และระบบพลังงานหมุนเวียนสำหรับแปลงเกษตร
**(LoRa Long-Range Wireless & Renewable Solar MPPT Energy for Precision Farming)**

## 1. ขอบเขตเนื้อหา
โมดูลนี้ถ่ายทอดเทคโนโลยีการสื่อสารระยะไกลและระบบพลังงานอิสระสำหรับอุปกรณ์ IoT ในแปลงเกษตรขนาดใหญ่ แบ่งเป็น 2 ส่วนหลัก:

1. **เครือข่ายไร้สายระยะไกล LoRa (Module 8.1):**
   * หลักการทำงานของ LoRa (Long Range) เทคโนโลยีไร้สายพลังงานต่ำพิเศษ (Low-Power Wide-Area Network: LPWAN)
   * จุดเด่นด้านระยะทางรับส่งหลายกิโลเมตร ความทนทานต่อสัญญาณรบกวน และประหยัดพลังงาน
   * การใช้งานย่านความถี่ 915 MHz (และ AS923) ในประเทศไทย
   * การเปรียบเทียบเชิงสมรรถนะ: LoRa vs Wi-Fi vs Bluetooth vs Cellular
   * สถาปัตยกรรมโครงข่าย Node, Gateway, Network Server และ Application Server

2. **ระบบพลังงานหมุนเวียนสำหรับอุปกรณ์ IoT ในพื้นที่ห่างไกล (Module 8.2):**
   * ข้อจำกัดของการเดินสายไฟในสวน (สาย THW ฝังดินไม่ได้ / สาย NYY ราคาแพง 80 บาท/เมตร)
   * ทางเลือกการใช้แผงโซลาร์เซลล์ (Solar Panel 12V 10–15W ชนิด Polycrystalline หันหน้าทิศใต้ เอียง 15 องศา)
   * วงจรชาร์จแบตเตอรี่อัจฉริยะ **XL4015 5A MPPT Buck Converter**
   * การจูนปรับแต่งปุ่มควบคุม 3 ตัวบนบอร์ด XL4015:
     - **CV (Constant Voltage):** ปรับแรงดันตัดชาร์จสูงสุด สำหรับแบตเตอรี่ LiFePO4 3.2V ปรับไว้ที่ **3.65V**
     - **CC (Constant Current):** จำกัดกระแสชาร์จให้อยู่ในเกณฑ์ปลอดภัย **0.2C – 0.5C** (เช่น แบตเตอรี่ 14Ah ปรับกระแส 7A)
     - **MPPT / VISET (Input Voltage Control):** ล็อคจุดทำงานแรงดันแผงโซลาร์เซลล์ที่ให้กำลังงานสูงสุด

---

## 2. ไฟล์เอกสารประกอบการสอน (PDF)
* [`Module 8.1.pdf`](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module8/Module%208.1.pdf): เครือข่ายไร้สายระยะไกลสำหรับเกษตรแปลงใหญ่ (LoRa/LoRaWAN) *(ขนาด 10.38 MB)*
* [`Module 8.2.pdf`](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module8/Module%208.2.pdf): ระบบพลังงานหมุนเวียนสำหรับอุปกรณ์ IoT ในพื้นที่ (Solar & LiFePO4 Battery Tuning) *(ขนาด 10.62 MB)*

ข้อความที่สกัดจากเอกสารทั้งหมดจัดเก็บไว้ที่:
* [`extracted_text/Module_8_1_extracted.txt`](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module8/extracted_text/Module_8_1_extracted.txt)
* [`extracted_text/Module_8_2_extracted.txt`](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module8/extracted_text/Module_8_2_extracted.txt)
