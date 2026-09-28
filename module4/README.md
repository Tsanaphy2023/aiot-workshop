# Module 4: การเชื่อมต่อระบบฟาร์มสู่คลาวด์และแดชบอร์ด
**(Agri-Cloud Connectivity & Dashboard)**

หลักสูตร: นวัตกรเกษตรอัจฉริยะ AIoT สำหรับเกษตรแม่นยำ รุ่นที่ 1 (วิทยาลัยการศึกษาตลอดชีวิต มหาวิทยาลัยเชียงใหม่)

---

## 📌 สารบัญและไฟล์ในโมดูล
* 🎬 **ไฟล์วิดีโอบรรยาย (1080p Full HD, 16:43 นาที):** [Module4_video.mp4](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/Module4_video.mp4)
* 📝 **สคริปต์ถอดคำบรรยายเสียงภาษาไทย:** [Module_4_lecture_transcript.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/extracted_text/Module_4_lecture_transcript.txt) *(257 บรรทัด)*
* 📄 **ไฟล์เอกสารประกอบการสอน:** [Module4.pdf](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/Module4.pdf) *(สไลด์ 25 หน้า)*
* 📝 **ข้อความสกัดจากสไลด์:** [Module_4_extracted.txt](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/extracted_text/Module_4_extracted.txt)
* 💻 **ซอร์สโค้ดในโฟลเดอร์ `src/`:**
  * [board1_garden.py](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/src/board1_garden.py): โค้ด MicroPython บอร์ด 1 ในสวน (ESP-NOW + DHT22 + Relay วาล์วน้ำ)
  * [board2_home_bridge.py](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/src/board2_home_bridge.py): โค้ด MicroPython บอร์ด 2 ในบ้าน (Wi-Fi + ESP-NOW + HTTP POST to Cloud)
  * [server_app.py](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/src/server_app.py): สคริปต์ Flask API รันบน AWS EC2/Server บันทึก CSV และจัดคิวคำสั่ง
  * [trigger_water.py](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/module4/src/trigger_water.py): สคริปต์ตรวจสอบความชื้นอัตโนมัติ สั่งรดน้ำผ่าน Cron job

---

## 1. สถาปัตยกรรมระบบ 2 ทางเลือก (System Architectures)

### ทางเลือกที่ 1: Local Smart Farm ด้วย Home Assistant & ESPHome
* **บอร์ดลูกข่าย (Nodes):** บอร์ด ESP32-C3 เชื่อมต่อเซนเซอร์และวาล์วน้ำ แฟลชเฟิร์มแวร์ด้วย **ESPHome** ผ่านเว็บเบราว์เซอร์ ([web.esphome.io](https://web.esphome.io/))
* **ฮับควบคุมในบ้าน:** คอมพิวเตอร์บอร์ดเดี่ยว **Raspberry Pi** รันระบบ **Home Assistant** (`http://homeassistant.local:8123`)
* **การเชื่อมต่อ:** ต่อผ่าน Wi-Fi Router 4G/5G SIM หรือ Personal Hotspot ในพื้นที่ฟาร์ม
* **ข้อดี:** ดูแดชบอร์ด ควบคุมวาล์ว และเขียนเงื่อนไขอัตโนมัติ (Automations) ผ่าน YAML ได้สะดวกรวดเร็ว ไม่ต้องเขียนโปรแกรมระดับต่ำ

---

### ทางเลือกที่ 2: Distributed Multi-Node + Cloud Dashboard (AWS EC2 + Flask + Grafana)
* **โหนดในสวน (Garden Node - บอร์ด 1):**
  * ใช้พลังงานแสงอาทิตย์ (แผงโซลาร์ + แบตเตอรี่ LiFePO4 + ชาร์จเจอร์)
  * บอร์ด ESP32-C3 อ่านค่าเซนเซอร์ DHT22 และขับรีเลย์วาล์วน้ำ
  * สื่อสารระยะไกลสู่บ้านด้วย **ESP-NOW** (ประหยัดพลังงาน ไม่ต้องพึ่งพา Wi-Fi Router ในแปลง)
* **บริดจ์ในบ้าน (Home Bridge - บอร์ด 2):**
  * บอร์ด ESP32-C3 ต่อไฟบ้าน รับสัญญาณ ESP-NOW จากบอร์ด 1
  * เชื่อมต่อ Wi-Fi ในบ้าน ยิงส่งข้อมูลขึ้น Cloud ด้วย HTTP POST
  * คอย Poll ดึงคำสั่งรดน้ำจาก Cloud ทุกๆ 15 วินาที แล้วส่งต่อไปสั่งบอร์ด 1 ผ่าน ESP-NOW
* **คลาวด์เซิร์ฟเวอร์ (AWS EC2):**
  * รัน **Flask Web API** (`server_app.py`) รับข้อมูลและเก็บลง `sensor_data.csv`
  * ติดตั้ง **MQTT Broker** และ **Grafana Dashboard** เพื่อแสดงผลกราฟแบบ Real-time บนมือถือ
  * รันสคริปต์ตรวจสอบเงื่อนไขความชื้นและสภาพฝน (`trigger_water.py`) ผ่าน **Linux Cron Job**

---

## 2. การติดตั้งและใช้งานฝั่ง Server (AWS EC2)

```bash
# 1. ติดตั้ง Dependencies
pip3 install flask requests

# 2. รัน Flask Server ในพื้นหลัง (Background Service)
nohup python3 server_app.py > server.log 2>&1 &

# 3. ตั้งเวลา Cron Job รดน้ำอัตโนมัติ (ตัวอย่าง: ทุกวัน 07:00 น. และ 17:00 น.)
# พิมพ์คำสั่ง: crontab -e
0 7,17 * * * /usr/bin/python3 /path/to/cmu_aiot/module4/src/trigger_water.py >> /path/to/cmu_aiot/module4/watering.log 2>&1
```

---

## 3. สรุปประเด็นข้อสอบและแนวคิดสถาปัตยกรรมสำคัญ (Key Concepts & Quiz Highlights)

1. **วัตถุประสงค์ของ ESP-NOW ในระบบ:**
   * ใช้สำหรับส่งข้อมูลเซนเซอร์และรับคำสั่งควบคุมระหว่างบอร์ดในสวนกับบอร์ดในบ้านโดยตรง โดยไม่ต้องเชื่อมต่อ Wi-Fi Router ช่วยประหยัดพลังงานแบตเตอรี่ (ตื่นส่งไวระดับมิลลิวินาทีแล้วหลับลึก) และแก้ปัญหาจุดอับสัญญาณในสวน
2. **หน้าที่ของบอร์ด 1 (โหนดในสวน - Garden Node):**
   * อ่านค่าเซนเซอร์ (DHT22) แล้วส่งออกไปผ่าน ESP-NOW และคอยรับคำสั่งเปิด-ปิดรีเลย์เพื่อควบคุมวาล์วน้ำ
3. **หน้าที่ของบอร์ด 2 (โหนดบริดจ์ในบ้าน - Home Bridge):**
   * เป็นสะพานเชื่อม รับข้อมูลจากบอร์ดในสวนผ่าน ESP-NOW แล้วส่งต่อขึ้น Cloud API (AWS EC2) ผ่าน Wi-Fi และดึงคำสั่งรดน้ำส่งกลับไปยังบอร์ดในสวน
4. **การตั้งค่าอุปกรณ์ด้วยเฟิร์มแวร์ ESPHome:**
   * กำหนดค่าผ่าน **ไฟล์ YAML** (`.yaml` / `.yml`) ซึ่งเป็นรูปแบบ Declarative โดยไม่ต้องเขียนโค้ดภาษา C++ ด้วยตัวเอง
5. **การเข้าใช้งานแดชบอร์ด Home Assistant บน Raspberry Pi:**
   * เปิดผ่านเบราว์เซอร์ที่อยู่: **`http://homeassistant.local:8123`** (พอร์ตมาตรฐาน 8123)
6. **เทคโนโลยีการสื่อสาร LoRa & LoRaWAN:**
   * **LoRa:** ออกแบบมาสำหรับงาน **Telemetry** ส่งข้อมูลขนาดเล็ก (**หลักสิบถึงไม่เกิน 250 ไบต์**) ระยะไกลมาก ใช้พลังงานต่ำมาก
   * **Duty Cycle ในไทย (กสทช. 920-925 MHz):** **ไม่เกิน 1%** (ส่งได้รวมไม่เกิน 36 วินาทีต่อ 1 ชั่วโมง)
   * **LoRaWAN vs Custom LoRa:** LoRaWAN ต้องพึ่งพา Gateway และ Network Server บนคลาวด์ พร้อมความปลอดภัย AES-128 บิต ส่วน Custom LoRa ควบคุมคลื่นวิทยุส่งตรงระหว่างบอร์ดโดยไม่ต้องพึ่งพาคลาวด์
   * **การเพิ่มระยะส่ง LoRa:** ต่อหัว **u.FL ผ่านสายแปลงเป็น SMA เข้ากับสายอากาศเกนสูง (High-Gain Antenna)** และยกเสาให้สูงพ้นสิ่งกีดขวาง (ห้ามจ่ายไฟ 5V เพราะชิปรองรับได้แค่ 3.3V)

