# 🌾 ระบบนิเวศ Zigbee เซนเซอร์สำหรับเกษตรแม่นยำ (Zigbee Sensors Ecosystem)

---

## 1. ภาพรวมระบบนิเวศเซนเซอร์ Zigbee (Sensors Landscape)

เซนเซอร์ Zigbee สำหรับงานเกษตรอัจฉริยะ (AIoT Smart Agriculture) สามารถแบ่งออกเป็น 4 หมวดหลักตามหน้าที่ตรวจวัด:

```
                  ┌──────────────────────────────────────────────┐
                  │       ZIGBEE AGRICULTURE SENSORS             │
                  └──────────────────────┬───────────────────────┘
                                         │
        ┌──────────────────┬─────────────┴──────────┬──────────────────┐
        ▼                  ▼                        ▼                  ▼
┌───────────────┐  ┌───────────────┐        ┌───────────────┐  ┌───────────────┐
│ เซนเซอร์ดิน    │  │ เซนเซอร์อากาศ  │        │ แสงและรังสี   │  │ น้ำและวาล์ว   │
│ Soil Sensors  │  │ Micro-climate │        │ Solar & Lux   │  │ Water & Flow  │
├───────────────┤  ├───────────────┤        ├───────────────┤  ├───────────────┤
│ • Moisture %  │  │ • Temp / Hum  │        │ • Lux Level   │  │ • Water Level │
│ • Soil Temp   │  │ • Pressure    │        │ • Solar W/m²  │  │ • Flow Rate   │
│ • Soil EC     │  │ • VPD         │        │ • UV Index    │  │ • Zigbee      │
│ • Soil NPK    │  │ • CO2 / TVOC  │        │ • PAR (PPFD)  │  │   Smart Valve │
└───────────────┘  └───────────────┘        └───────────────┘  └───────────────┘
```

---

## 2. หมวดหมู่เซนเซอร์ในระบบ

### 2.1 เซนเซอร์ตรวจวัดคุณภาพดิน (Soil Physics & Chemistry)
* **ความชื้นในดินเชิงปริมาตร (Volumetric Water Content - VWC %):** วัดด้วยหลักการ Frequency Domain Reflectometry (FDR) หรือ Capacitive ป้องกันปัญหาการสึกหรอของขั้วโลหะ
* **อุณหภูมิดิน (Soil Temperature):** บ่งบอกสภาวะการดูดซึมน้ำของรากพืช
* **การนำไฟฟ้าในดิน (Soil Electrical Conductivity - EC):** ชี้วัดความเข้มข้นของเกลือและปุ๋ยแร่ธาตุในสารละลายดิน (หน่วย mS/cm หรือ µS/cm)
* **ความเป็นกรด-ด่าง (Soil pH):** วัดความสมดุลเคมีที่รากพืชสามารถนำพาแร่ธาตุไปใช้ได้ (pH 5.5 – 6.8)
* **ธาตุอาหารหลักในดิน (Soil NPK):** ไนโตรเจน (N), ฟอสฟอรัส (P), โพแทสเซียม (K) ผ่านโพรบสแตนเลสเกรด 316L ทนกรดด่าง

### 2.2 เซนเซอร์สภาพแวดล้อมและจุลภูมิอากาศ (Micro-climate Sensors)
* **อุณหภูมิและความชื้นสัมพัทธ์ในอากาศ (Air Temperature & Relative Humidity):** ใช้ชิปความแม่นยำสูงตระกูล **Sensirion SHT30 / SHT31 / SHT40** ป้องกันด้วยแคปซูลกรองฝุ่นและละอองน้ำ PE Filter
* **ความกดอากาศ (Barometric Pressure):** เช่น Bosch BMP280 / BME280 สำหรับคำนวณระดับความสูงและสภาวะแนวโน้มของฝน
* **แรงดึงระเหยน้ำของอากาศ (Vapour Pressure Deficit - VPD):** คำนวณจากความสัมพันธ์ระหว่างอุณหภูมิผิวใบและความชื้นสัมพัทธ์ เป็นดัชนีสำคัญที่สุดในการคุมการคายน้ำของพืช
* **ก๊าซคาร์บอนไดออกไซด์ ($CO_2$):** เซนเซอร์แบบ Non-Dispersive Infrared (NDIR) เช่น Senseair S8 หรือ SCD40 ในโรงเรือนปิด

### 2.3 เซนเซอร์แสงและรังสีดวงอาทิตย์ (Solar Radiation & Light)
* **ความเข้มแสง (Illuminance - Lux):** ชิป BH1750 หรือ OPT3001
* **รังสีดวงอาทิตย์เพื่อการสังเคราะห์แสง (Photosynthetically Active Radiation - PAR / PPFD):** วัดปริมาณโฟตอนช่วงความยาวคลื่น 400–700 nm ($\mu mol \cdot m^{-2} \cdot s^{-1}$)

### 2.4 เซนเซอร์ตรวจวัดน้ำและวาล์วสั่งการ (Water & Actuation)
* **ระดับน้ำในถัง/บ่อพัก:** Ultrasonic Distance Sensor (JSN-SR04T กันน้ำ) หรือ Hydrostatic Pressure Submersible Sensor
* **วาล์วน้ำ Zigbee อัจฉริยะ (Zigbee Smart Water Valve):** ควบคุมบอลวาล์วหรือโซลินอยด์วาล์วด้วยแบตเตอรี่ในตัว เปิด-ปิดตามรอบเวลาหรือปริมาณลิตรน้ำ

---

## 3. แกลเลอรีภาพจำลองและภาพการติดตั้งจริง (Visual Gallery & Field Deployment)

เพื่อความเข้าใจและสร้างแรงบันดาลใจในการออกแบบและการนำไปติดตั้งใช้งานจริง ระบบได้จัดเตรียมชุดภาพคุณภาพสูง ทั้งในรูปแบบภาพถ่ายเชิงวิศวกรรมสมจริง (Photorealistic) และภาพสไตล์ 3D Pixar & Studio Ghibli สำหรับสื่อการสอนและแดชบอร์ด:

### 3.1 ภาพสมจริงการติดตั้งใช้งานในพื้นที่ (Photorealistic Field Deployment)

| โหนดเซนเซอร์วัดดินในโรงเรือน (IP68 Solar Node) | เครือข่ายไร้สาย Zigbee Mesh ในแปลงผลไม้ |
| :---: | :---: |
| ![Zigbee Soil Sensor in Greenhouse](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/assets/images/zigbee_soil_sensor_realistic.jpg) | ![Zigbee Mesh Orchard Deployment](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/assets/images/zigbee_farm_mesh_realistic.jpg) |
| *ภาพที่ 1: โหนดวัดความชื้น/อุณหภูมิดิน IP68 พร้อมแผงโซลาร์เซลล์ขนาดเล็กในแปลงผักโรงเรือน* | *ภาพที่ 2: การกระจายตัวของโครงข่าย Zigbee Mesh Topology ครอบคลุมแปลงผลไม้เชื่อมต่อสู่เกตเวย์หลัก* |

### 3.2 ภาพสไตล์ 3D Pixar & Studio Ghibli (Creative & Educational Aesthetics)

| หุ่นยนต์เซนเซอร์ AIoT สไตล์ 3D Pixar | โรงเรือนอัจฉริยะสไตล์ Studio Ghibli |
| :---: | :---: |
| ![3D Pixar Zigbee Sensor Companion](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/assets/images/zigbee_sensor_pixar_3d.jpg) | ![Studio Ghibli Greenhouse](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/assets/images/zigbee_greenhouse_ghibli.jpg) |
| *ภาพที่ 3: หุ่นยนต์เซนเซอร์ AIoT Sprout ตรวจวัดสภาวะแปลงสตรอว์เบอร์รี สไตล์ 3D Pixar Animation* | *ภาพที่ 4: เซนเซอร์ Zigbee สไตล์อนิเมะ Studio Ghibli คลาสสิก ละมุนตา สำหรับสื่อการสอน* |

---

## 4. สารบัญเอกสารในโฟลเดอร์นี้

* [soil_environment_sensors.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/02_sensor_ecosystem/soil_environment_sensors.md) - เจาะลึกสเปกเซนเซอร์ดิน อากาศ แสง และการแมปปิ้งแอตทริบิวต์ ZCL
* [commercial_vs_custom.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/02_sensor_ecosystem/commercial_vs_custom.md) - บทวิเคราะห์เปรียบเทียบเซนเซอร์สำเร็จรูป (Tuya/Sonoff) vs พัฒนาเอง (ESP32-C6)
* [industrial_modbus_bridge.md](file:///Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/zigbee_system/02_sensor_ecosystem/industrial_modbus_bridge.md) - การสร้าง Zigbee Bridge แปลงสัญญาณ RS485 Modbus RTU สำหรับโพรบ NPK อุตสาหกรรม

