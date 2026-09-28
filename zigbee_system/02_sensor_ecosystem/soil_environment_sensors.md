# 🌿 รายละเอียดเซนเซอร์ดิน สภาพแวดล้อม และการแมปปิ้งแอตทริบิวต์ ZCL (Soil & Environment Sensors Specification)

---

## 1. การแมปปิ้งแอตทริบิวต์ Zigbee Cluster Library (ZCL Mapping)

เมื่อเซนเซอร์วัดค่ากายภาพได้ จะต้องแปลงค่าเป็นตัวเลขตามหน่วยที่กำหนดใน **Zigbee Cluster Library (ZCL)** แล้วส่งออกไปเป็น Attribute Data:

| พารามิเตอร์ตรวจวัด | Cluster ID | Attribute ID | Data Type | สูตรการแปลงค่าใน ZCL | หน่วยสากล |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **อุณหภูมิอากาศ (Air Temp)** | `0x0402` (Temperature) | `0x0000` | Signed 16-bit Int (`int16`) | $\text{Value} = \text{Temp (°C)} \times 100$ | 0.01 °C |
| **ความชื้นสัมพัทธ์ (Relative Hum)** | `0x0405` (Humidity) | `0x0000` | Unsigned 16-bit Int (`uint16`) | $\text{Value} = \text{Humidity (\%)} \times 100$ | 0.01 % |
| **ความกดอากาศ (Pressure)** | `0x0403` (Pressure) | `0x0000` | Signed 16-bit Int (`int16`) | $\text{Value} = \text{Pressure (hPa)}$ หรือ kPa | hPa |
| **ความเข้มแสง (Illuminance)** | `0x0400` (Illuminance) | `0x0000` | Unsigned 16-bit Int (`uint16`) | $\text{Value} = 10000 \times \log_{10}(\text{Lux}) + 1$ | 1 Lux |
| **ความชื้นในดิน (Soil Moisture %)** | `0x0405` หรือ `0x000C` (Analog Input) | `0x0055` (PresentValue) | Single Precision Float | ค่าความชื้น $0.0 - 100.0$ | % VWC |
| **การนำไฟฟ้าดิน (Soil EC)** | `0x000C` (Analog Input) | `0x0055` (PresentValue) | Single Precision Float | ค่าการนำไฟฟ้าดิน | µS/cm |
| **ความเป็นกรด-ด่าง (Soil pH)** | `0x000C` (Analog Input) | `0x0055` (PresentValue) | Single Precision Float | ค่าความเป็นกรดด่าง $0.0 - 14.0$ | pH |
| **เปอร์เซ็นต์แบตเตอรี่โหนด** | `0x0001` (Power Config) | `0x0021` (BatteryPercentage) | Unsigned 8-bit Int (`uint8`) | $\text{Value} = \text{Battery \%} \times 2$ (0-200) | 0.5 % |

---

## 2. เจาะลึกเซนเซอร์ยอดนิยมในงานเกษตร AIoT

### 2.1 เซนเซอร์สภาพอากาศ Sensirion SHT3x / SHT4x
* **อินเทอร์เฟซ:** $I^2C$ Bus (Default Address: `0x44` หรือ `0x45`)
* **ความแม่นยำ:** อุณหภูมิ $\pm 0.2^\circ C$, ความชื้นสัมพัทธ์ $\pm 1.5\% RH$
* **การใช้พลังงาน:** 
  * ขณะวัด (Measurement): $800\,\mu A$ (ใช้เวลาเพียง 4–15 ms)
  * โหมดสลีป (Low Power Sleep): **$0.2\,\mu A$** (ต่ำมาก เหมาะกับ Zigbee ZED ที่สุด)
* **การป้องกัน:** ใช้ปลอกกรองสแตนเลสหรือพลาสติกโพลีเอทิลีน (PE Sintered Filter Cap) ป้องกันละอองน้ำ แต่ไอน้ำและก๊าซผ่านเข้าได้สะดวก

### 2.2 เซนเซอร์ความชื้นในดินแบบเก็บประจุ (Capacitive Soil Moisture Probe)
* **ข้อดีเหนือกว่าแบบ Resistive ขั้วทองแดงทั่วไป:**
  * ไม่มีกระแสไฟฟ้าวิ่งผ่านเนื้อดินโดยตรง จึง **ไม่เกิดการกัดกร่อนด้วยไฟฟ้าเคมี (No Electrolysis Corrosion)**
  * แผ่นวงจรเคลือบเรซินกันน้ำ ทนทานนานหลายปี
* **หลักการทำงาน:** วัดการเปลี่ยนแปลงค่าไดอิเล็กทริกสัมพัทธ์ ($\varepsilon_r$) ของดิน
  * ดินแห้ง: $\varepsilon_r \approx 3 - 5$
  * น้ำ: $\varepsilon_r \approx 80$
* **สัญญาณขาออก:** แรงดันอนาล็อก $1.2V - 3.0V$ (ต่อเข้าขา ADC ของ ESP32-C6)

### 2.3 สูตรการคำนวณ Vapor Pressure Deficit (VPD) ประจำโหนด
ในแปลงโรงเรือน Zigbee โหนดหรือเกตเวย์สามารถคำนวณค่า VPD (หน่วย kPa) ได้จากอุณหภูมิ $T$ (°C) และความชื้นสัมพัทธ์ $RH$ (%):

$$VPD = VPsat \times \left(1 - \frac{RH}{100}\right)$$

โดยที่ความดันไออิ่มตัว $VPsat$ คำนวณจากสมการ Tetens:

$$VPsat = 0.61078 \times \exp\left(\frac{17.27 \times T}{T + 237.3}\right)$$

* **เกณฑ์การจัดการในโรงเรือน:**
  * $VPD < 0.4\,\text{kPa}$: ความชื้นสูงเกินไป เสี่ยงต่อเชื้อรา พืชไม่คายน้ำ
  * $0.8\,\text{kPa} \le VPD \le 1.2\,\text{kPa}$: **ช่วงทองคำ (Optimal Zone)** พืชสังเคราะห์แสงและดูดปุ๋ยได้สูงสุด
  * $VPD > 1.6\,\text{kPa}$: อากาศแห้งและร้อนจัด พืชปิดปากใบเพื่อรักษาตัว
