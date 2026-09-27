---
name: smart-farm-lineart-icon-designer
description: >-
  สถาปัตยกรรมและกระบวนการออกแบบไอคอนสมาร์ทฟาร์มและแอปพลิเคชัน AIoT สไตล์ลายเส้นมินิมอลร่วมสมัย (Minimalist Bio-Digital Line Art & App Icons)
  ครอบคลุมหลักการออกแบบ Geometric Line Art, แม่สีและแสงนีออน (Emerald & Mint Glow), ระบบไอคอนเวกเตอร์ SVG ความคมชัด 100%,
  สคริปต์ Python อัตโนมัติสำหรับ Generate ไอคอนลง Android Mipmap (mdpi-xxxhdpi), iOS AppIcon (1024x1024), Web Favicon, และ Flutter Assets
---

# 🌿 Smart Farm AIoT Line-Art Icon Designer & Automation Skill

**smart-farm-lineart-icon-designer** คือชุดทักษะ มาตรฐานสุนทรียศาสตร์ และเครื่องมืออัตโนมัติสำหรับการออกแบบชุดไอคอนและ App Launcher Icon สำหรับระบบเกษตรแม่นยำ ปัญญาประดิษฐ์ฝังตัว และแอปพลิเคชันสมาร์ทโฟน AIoT (Flutter / Android / iOS / Web) ในสไตล์ **Minimalist Bio-Digital Line Art** ที่ผสมผสานความเรียบหรูของธรรมชาติ (ใบไม้, หยดน้ำ, แสงแดด) เข้ากับความล้ำสมัยของเทคโนโลยีดิจิทัล (ลายวงจรพิมพ์ PCB, โหนดเซนเซอร์, คลื่นวิทยุไร้สาย ESP-NOW)

---

## 🎨 1. ปรัชญาและมาตรฐานการออกแบบ (Design Philosophy)

### 1.1 อัตลักษณ์สไตล์ลายเส้นมินิมอล (Minimalist Line Art Principles)
1. **Geometric Precision & Simplicity**:
   - ใช้รูปทรงเรขาคณิตบริสุทธิ์ (Pure Geometry: วงกลม, ส่วนโค้งรัศมีชัดเจน, เส้นตรงเชื่อมโยง 45°/90°)
   - ละเว้นรายละเอียดที่ซ้ำซ้อนหรือภาพถ่ายจริง คงไว้เฉพาะ "แก่นทางสายตา" (Visual Essence)
2. **Stroke-Based Hierarchy**:
   - เส้นขอบหลัก (Primary Silhouette): ความหนาเส้น `12px - 14px` (สำหรับแคนวาส 512x512)
   - เส้นโครงสร้างและวงจรภายใน (Inner Circuit Traces): ความหนาเส้น `8px - 10px`
   - จุดโหนดเซนเซอร์ (Sensor Nodes / Terminal Dots): วงกลมทึบรัศมี `8px - 10px` ที่ปลายเส้น
   - เส้นปลายมนและมุมมน (`stroke-linecap="round"`, `stroke-linejoin="round"`) เพิ่มความนุ่มนวลเป็นมิตร
3. **Bio-Digital Harmony**:
   - แกนกลางผสานรูปร่างใบไม้ (Organic Leaf) เข้ากับเส้นทางเดินสัญญาณข้อมูล (Data Bus / PCB Traces)
   - ด้านข้างมีเส้นคลื่นวิทยุไร้สาย (Broadcast Arcs) สื่อถึงการสื่อสารไร้เราเตอร์ ESP-NOW Long Range

---

## 🌈 2. ระบบชุดสี (Harmonious Color Palette System)

| บทบาทสี | ชื่อเฉดสี | รหัส HEX | วัตถุประสงค์การใช้งาน |
| :--- | :--- | :--- | :--- |
| **Primary Brand** | Neon Mint | `#20C997` / `#10B981` | เส้นขอบใบไม้, ลายวงจรหลัก, ปุ่มเปิดใช้งาน |
| **Secondary Accent** | Emerald Core | `#059669` / `#064E3B` | คลื่นวิทยุรอง, เงาตกกระทบ, โทนพื้นหลังธรรมชาติ |
| **Background Base** | Obsidian Dark | `#0B132B` / `#0F172A` | พื้นหลัง Squircle หรูหรา ขับเน้นเส้นเรืองแสง |
| **Water / Fluid** | Cyan Splash | `#06B6D4` / `#0DCAF0` | เซนเซอร์ความชื้นดิน, ปั๊มน้ำ, สวิตช์ลูกลอย |
| **Sunlight / Energy** | Solar Amber | `#EAB308` / `#F59E0B` | เซนเซอร์วัดแสง BH1750, หลอดไฟปลูกพืช |
| **Critical Warning** | Crimson Alert | `#DC2626` / `#EF4444` | สวิตช์ลูกลอยเตือนน้ำแห้ง, ตัวตัดฉุกเฉิน E-Stop |

---

## 📐 3. ข้อกำหนดขนาดและ Platform Mipmaps

ชุดเครื่องมือของสกิลนี้จะสร้างไฟล์ไอคอนขนาดต่างๆ ตามมาตรฐานระบบปฏิบัติการอย่างถูกต้อง:

### Android Launcher Mipmaps (`android/app/src/main/res/`):
* `mipmap-mdpi/ic_launcher.png`: **48 x 48 px**
* `mipmap-hdpi/ic_launcher.png`: **72 x 72 px**
* `mipmap-xhdpi/ic_launcher.png`: **96 x 96 px**
* `mipmap-xxhdpi/ic_launcher.png`: **144 x 144 px**
* `mipmap-xxxhdpi/ic_launcher.png`: **192 x 192 px**

### Apple iOS AppIcon (`ios/Runner/Assets.xcassets/AppIcon.appiconset/`):
* `Icon-App-1024x1024@1x.png`: **1024 x 1024 px** (App Store Master)

### Web Application & PWA (`web/`):
* `favicon.png`: **32 x 32 px**
* `icons/Icon-192.png`: **192 x 192 px**
* `icons/Icon-512.png`: **512 x 512 px**

---

## 🛠️ 4. สคริปต์อัตโนมัติ (Automation Tooling)

สกิลนี้มาพร้อมสคริปต์ Python ในโฟลเดอร์ `scripts/generate_app_icons.py` ซึ่งสามารถประมวลผล Master Image ปรับความละเอียด และกระจายลงสู่โฟลเดอร์ของระบบปฏิบัติการอัตโนมัติ

### การเรียกใช้งาน:
```bash
python3 .agents/skills/smart-farm-lineart-icon-designer/scripts/generate_app_icons.py \
  --source "Flutter AIoT/assets/icons/app_icon.png" \
  --project-dir "Flutter AIoT"
```

---

## 📑 5. รายการชุดไอคอนเวกเตอร์ SVG ในคลัง (Icon Inventory)

| ชื่อไฟล์ | วัตถุประสงค์ในระบบ AIoT | ลักษณะสไตล์ลายเส้น |
| :--- | :--- | :--- |
| `app_icon.svg` | Master App Launcher Icon | Squircle เข้ม + ใบไม้ชีวภาพผสานลายวงจร + คลื่นวิทยุ |
| `sensor_leaf.svg` | เซนเซอร์ชีวภาพ & ความชื้น | โครงร่างใบไม้เรขาคณิต พร้อมจุดโหนดกระจายสัญญาณ |
| `water_pump.svg` | รีเลย์ปั๊มน้ำ & วาล์วน้ำ | ตัวเรือนปั๊มหอยโข่งแบบมินิมอล + ท่อทางเดินน้ำ + หยดน้ำ |
| `grow_light.svg` | หลอดไฟปลูกพืช / แสงแดด | เส้นขอบหลอดไฟสไตล์ฟิลาเมนต์ + รัศมีแสงแบบ Stroke |
| `brain_rules.svg` | สมองกลและกฎอัตโนมัติ (Think) | ตัวประมวลผลไมโครคอนโทรลเลอร์พร้อมขาพิน IO รอบทิศ |
| `espnow_tower.svg` | สะพานสื่อสารวิทยุ ESP-NOW | เสาส่งสัญญาณโครงข่ายไร้สาย + วงคลื่นวิทยุสะท้อน |
| `float_switch.svg` | สวิตช์ลูกลอยตรวจระดับน้ำ | ก้านลูกลอยแนวตั้ง + ทุ่นลอย + เส้นระลอกน้ำสองชั้น |
| `analytics_trend.svg` | การวิเคราะห์ข้อมูลย้อนหลัง | แกนพิกัด XY + เส้นกราฟแบบโหนดจุดตรวจวัด 60 จุด |
