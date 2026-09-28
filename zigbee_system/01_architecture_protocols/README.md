# 📡 สถาปัตยกรรมและโปรโตคอลระบบสื่อสารไร้สาย Zigbee 3.0 (Architecture & Protocol Stack)

---

## 1. วิวัฒนาการและมาตรฐานสากล (Standards & Evolution)

มาตรฐาน **Zigbee** ได้รับการพัฒนาและดูแลโดย **Connectivity Standards Alliance (CSA)** (เดิมชื่อ Zigbee Alliance) โดยมีรากฐานสำคัญบนมาตรฐานกายภาพและแมคเลเยอร์ของ **IEEE 802.15.4**

วิวัฒนาการที่สำคัญ:
* **Zigbee 1.0 / Zigbee 2004:** ยุคเริ่มต้น รองรับโครงสร้างพื้นฐาน
* **Zigbee 2006 / 2007 (Zigbee PRO):** เพิ่มขีดความสามารถการทำ Mesh Routing, การจัดการกลุ่ม (Multicast), ความปลอดภัยขั้นสูงระดับ 128-bit AES
* **Zigbee 3.0 (มาตรฐานปัจจุบัน):** เป็นก้าวสำคัญที่ทำการรวมโปรไฟล์เฉพาะทางทั้งหมดในอดีต (Home Automation - ZHA, Light Link - ZLL, Building Automation, Health Care) ให้กลายเป็น **"มาตรฐานหนึ่งเดียว (Unified Standard)"** ทำให้เซนเซอร์และอุปกรณ์ต่างผู้ผลิตสามารถ Pair และสื่อสารข้ามแบรนด์ได้อย่างสมบูรณ์

```
┌──────────────────────────────────────────────────────────┐
│             Application Layer / Profiles                 │
│         (Zigbee Cluster Library: ZCL 8 & BDB)            │
├──────────────────────────────────────────────────────────┤
│           Zigbee Device Objects (ZDO) & APS              │
│       (Device Discovery, Security & Binding Table)       │
├──────────────────────────────────────────────────────────┤
│                  Network Layer (NWK)                     │
│         (Mesh Routing, AODV, Neighbor Tables)            │
├──────────────────────────────────────────────────────────┤
│             IEEE 802.15.4 MAC Layer (CSMA/CA)            │
├──────────────────────────────────────────────────────────┤
│         IEEE 802.15.4 PHY Layer (2.4 GHz ISM / DSSS)     │
└──────────────────────────────────────────────────────────┘
```

---

## 2. โครงสร้างโปรโตคอลสแต็ก (Protocol Stack Breakdown)

### 2.1 ชั้นกายภาพและดาต้าลิงก์ (PHY & MAC: IEEE 802.15.4)
* **ความถี่พาหะ:** 2.4 GHz ISM Band (2400 – 2483.5 MHz)
* **จำนวนช่องสัญญาณ (Channels):** 16 ช่อง (ช่องที่ 11 ถึง 26) แต่ละช่องห่างกัน 5 MHz
* **เทคนิคการกล้ำสัญญาณ:** Direct Sequence Spread Spectrum (DSSS) ร่วมกับ O-QPSK (Offset Quadrature Phase Shift Keying)
* **การเข้าถึงตัวกลาง (Media Access):** CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance) ตรวจจับช่องสัญญาณว่างก่อนส่ง เพื่อป้องกันสัญญาณชนกัน
* **การหลบหลีกสัญญาณ Wi-Fi กวน:**
  * Wi-Fi มักใช้ Channel 1, 6, 11
  * **ช่องสัญญาณ Zigbee ที่แนะนำสำหรับงานฟาร์มและโรงเรือน:** **Channel 15, 20, 25** (โดยเฉพาะ **Channel 25** จะไม่ทับซ้อนกับ Wi-Fi Channel 11 เลย)

### 2.2 ชั้นเครือข่าย (Network Layer: NWK)
* ทำหน้าที่ค้นหาเส้นทาง (Route Discovery), สร้างและบำรุงรักษาเส้นทาง (Route Maintenance)
* ใช้ขั้นตอนวิธี **AODV (Ad-hoc On-Demand Distance Vector Routing)**
* มีการจัดเก็บ **Neighbor Table** และ **Routing Table** ในโหนด Router และ Coordinator

### 2.3 ชั้นประยุกต์และคลัสเตอร์ (Application Layer & ZCL)
* **ZDO (Zigbee Device Objects):** ควบคุมการ Join เข้าเครือข่าย, ขอ PAN ID, ตรวจสอบประเภทอุปกรณ์
* **ZCL (Zigbee Cluster Library):** ชุดคำสั่งและแอตทริบิวต์มาตรฐาน เช่น:
  * `Cluster 0x0402`: **Temperature Measurement** (ค่าอุณหภูมิคูณ 100)
  * `Cluster 0x0405`: **Relative Humidity Measurement** (ค่าความชื้นคูณ 100)
  * `Cluster 0x0400`: **Illuminance Measurement** (ค่าความเข้มแสง Lux)
  * `Cluster 0x0006`: **On/Off** (สำหรับควบคุมรีเลย์ ปั๊มน้ำ โซลินอยด์วาล์ว)
  * `Cluster 0x0001`: **Power Configuration** (เปอร์เซ็นต์แบตเตอรี่ และแรงดันไฟ)

---

## 3. ความปลอดภัยในระดับฮาร์ดแวร์ (Security Architecture)

Zigbee 3.0 มีระบบรักษาความปลอดภัยระดับองค์กร:
1. **การเข้ารหัสข้อมูล:** ใช้ **AES-128 (Advanced Encryption Standard 128-bit)** ทั้งในระดับ Network Layer และ Application Layer
2. **คีย์ความปลอดภัย 2 ชั้น:**
   * **Network Key:** คีย์กลางสำหรับโหนดทุกตัวในเครือข่ายเดียวกัน มีการสุ่มสร้างใหม่เมื่อสร้างเครือข่าย
   * **Link Key / Install Code:** คีย์เฉพาะคู่ระหว่าง Coordinator กับอุปกรณ์แต่ละตัว ใช้สำหรับเข้ารหัสข้อมูลในขั้นตอนการขอ Join ครั้งแรก ป้องกันการดักจับ Network Key ในอากาศ
3. **ป้องกัน Replay Attack:** มีการใส่ Frame Counter ที่เพิ่มขึ้นเรื่อยๆ หากมีบุคคลภายนอกดักจับแพ็กเกตแล้วส่งซ้ำ ระบบจะทิ้งแพ็กเกตนั้นทันที
