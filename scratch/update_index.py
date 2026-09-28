# -*- coding: utf-8 -*-
"""
Generate the Curriculum Grid HTML for คู่มือ/index.html
"""
import re

CURRICULUM_DATA = [
    {
        "session": "ช่วงที่ 1: การสำรวจและต่ออุปกรณ์พื้นฐาน (Sense, Act, Logic)",
        "session_desc": "ปูพื้นฐานการรับรู้ทางกายภาพ การขับโหลดกำลังสูง และการเชื่อมต่อเข้าสู่ระบบอัตโนมัติส่วนกลาง",
        "activities": [
            {
                "num": 1,
                "title_th": "รู้จักและทดลองอ่านค่าเซนเซอร์",
                "title_en": "Sense",
                "icon": "🌡️",
                "time": "45 นาที",
                "desc": "สถาปัตยกรรมบอร์ด GoGo-IoT (ESP32-C3), สวิตช์ลูกลอย (Dry Contact), เซนเซอร์ SHT30 ผ่าน I2C Bus, เซนเซอร์สั่นสะเทือน และการเปิด Web UI ผ่าน mDNS",
                "html_file": "activity_1_sense_guide.html",
                "md_file": "activity_1_sense_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-1.html",
                "color": "#0284c7"
            },
            {
                "num": 2,
                "title_th": "ต่อวงจรและสั่งงานหลอดไฟ",
                "title_en": "Act",
                "icon": "💡",
                "time": "45 นาที",
                "desc": "บอร์ดขับโหลด GoGo-Relay, การทำงานของรีเลย์กลไก, การแยกกักทางไฟฟ้า (Galvanic Isolation), ขั้ว COM/NO/NC, วงจรไฟฟ้า 12V DC และการสั่งงานผ่านเว็บ",
                "html_file": "activity_2_act_guide.html",
                "md_file": "activity_2_act_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-2.html",
                "color": "#059669"
            },
            {
                "num": 3,
                "title_th": "สร้างกฎควบคุมระบบ",
                "title_en": "Logic",
                "icon": "⚙️",
                "time": "50 นาที",
                "desc": "เชื่อมโยง Sense และ Act ผ่าน Home Assistant Automation Engine, ESPHome Native API, การตั้งค่า Threshold และการวิเคราะห์เส้นทางประเมินตรรกะด้วย Traces",
                "html_file": "activity_3_logic_guide.html",
                "md_file": "activity_3_logic_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-3.html",
                "color": "#4f46e5"
            }
        ]
    },
    {
        "session": "ช่วงที่ 2: ระบบควบคุมอัตโนมัติและความปลอดภัย (Think & Failure Lab)",
        "session_desc": "การยกระดับตรรกะสู่ความเสถียรสูง และการฝึกอบรมวิศวกรรมความปลอดภัยเชิงลึก (Fail-safe Engineering)",
        "activities": [
            {
                "num": 4,
                "title_th": "ตั้งกฎให้ระบบทำงานอัตโนมัติ",
                "title_en": "Think",
                "icon": "🧠",
                "time": "50 นาที",
                "desc": "แก้ปัญหาไฟกะพริบ/ปั๊มตัดต่อถี่ (Chattering) ด้วย Hysteresis Band, การจำกัดช่วงเวลาทำงาน (Time Condition), การต่อปั๊มน้ำจริง, และการสร้างสวิตช์ Auto/Manual Helper",
                "html_file": "activity_4_think_guide.html",
                "md_file": "activity_4_think_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-4.html",
                "color": "#d97706"
            },
            {
                "num": 5,
                "title_th": "จำลองปัญหาและเพิ่มระบบป้องกัน",
                "title_en": "Failure Lab",
                "icon": "🛡️",
                "time": "55 นาที",
                "desc": "จำลอง 4 สถานการณ์ความล้มเหลว (น้ำหมด Dry-run, ปั๊มไม่สั่น Stalled, บอร์ดดับ Unavailable, ปั๊มเดินแช่นาน Timeout), ตารางบำรุงรักษา และสถาปัตยกรรม Hardware Interlock",
                "html_file": "activity_5_failure_lab_guide.html",
                "md_file": "activity_5_failure_lab_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-5.html",
                "color": "#0284c7"
            }
        ]
    },
    {
        "session": "ช่วงที่ 3: การวิเคราะห์ข้อมูลและการออกแบบระบบฟาร์ม (History, Dashboard, Design)",
        "session_desc": "การใช้ข้อมูลอดีตเพื่อตัดสินใจ การออกแบบแดชบอร์ดให้ตอบโจทย์ผู้ใช้จริง และการคำนวณพลังงานโซลาร์",
        "activities": [
            {
                "num": 6,
                "title_th": "การอ่านข้อมูลที่บันทึกไว้ย้อนหลัง",
                "title_en": "History",
                "icon": "📈",
                "time": "45 นาที",
                "desc": "วิเคราะห์ข้อมูลอนุกรมเวลาใน History Graph และ Logbook, จับคู่ยอดกราฟกับเหตุการณ์ในแปลง, การวิเคราะห์ค่า Min/Max รอบวัน และการวินิจฉัยข้อมูลขาดหาย (Data Gaps)",
                "html_file": "activity_6_history_guide.html",
                "md_file": "activity_6_history_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-6.html",
                "color": "#0d9488"
            },
            {
                "num": 7,
                "title_th": "สร้างหน้าจอติดตามและควบคุมฟาร์ม",
                "title_en": "Dashboard",
                "icon": "📊",
                "time": "45 นาที",
                "desc": "ออกแบบ UI/UX สำหรับคนงานและเจ้าของฟาร์ม (User Persona), จัดลำดับความสำคัญของข้อมูล, สร้างการ์ด Lovelace (Gauge, Button, Entities) และทดสอบความง่ายกับเพื่อน",
                "html_file": "activity_7_dashboard_guide.html",
                "md_file": "activity_7_dashboard_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-7.html",
                "color": "#0284c7"
            },
            {
                "num": 8,
                "title_th": "ออกแบบระบบสำหรับฟาร์ม",
                "title_en": "Design",
                "icon": "📐",
                "time": "50 นาที",
                "desc": "เปรียบเทียบเครือข่ายฟาร์ม (Wi-Fi, ESP-NOW, LoRa, 4G), สถาปัตยกรรมคลาวด์/VPN, การคำนวณพลังงาน (Watt-hour/day), การเลือกแผงโซลาร์เซลล์ และชนิดแบตเตอรี่ LiFePO4",
                "html_file": "activity_8_farm_design_guide.html",
                "md_file": "activity_8_farm_design_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-8.html",
                "color": "#334155"
            }
        ]
    },
    {
        "session": "ช่วงที่ 4: ระบบโทรมาตรระยะไกลระดับแปลงฟาร์มด้วย ESP-NOW (Send, Receive, Bridge)",
        "session_desc": "ก้าวข้ามข้อจำกัดของ Wi-Fi ในแปลงไกลด้วยเทคโนโลยีไร้สาย ESP-NOW และการบริดจ์ข้อมูลเข้า Home Assistant",
        "activities": [
            {
                "num": 9,
                "title_th": "อัปเดตบอร์ดที่แปลงให้ส่งข้อมูลด้วย ESP-NOW",
                "title_en": "Send",
                "icon": "📡",
                "time": "45 นาที",
                "desc": "แฟลชเฟิร์มแวร์รุ่นใหม่ผ่าน Web Serial (ESP Web Tools บน Chrome), การส่งข้อมูลแบบ Connectionless Broadcast, การจดจำ MAC Address และการทำงานแบบ Dual-Stack",
                "html_file": "activity_9_espnow_send_guide.html",
                "md_file": "activity_9_espnow_send_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-9.html",
                "color": "#e11d48"
            },
            {
                "num": 10,
                "title_th": "เพิ่มบอร์ดตัวรับที่ตัวเรือน",
                "title_en": "Receive",
                "icon": "📥",
                "time": "45 นาที",
                "desc": "ติดตั้งเฟิร์มแวร์ตัวรับ (Gateway Node), จับคู่ด้วย MAC Address, ทดสอบระยะทางและสิ่งกีดขวาง (Range & RSSI Testing), และการจำลองแปลงเงียบ (Fail-to-Unknown Timeout)",
                "html_file": "activity_10_espnow_receive_guide.html",
                "md_file": "activity_10_espnow_receive_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-10.html",
                "color": "#7c3aed"
            },
            {
                "num": 11,
                "title_th": "นำข้อมูลจากแปลงไกลขึ้นแดชบอร์ด Home Assistant",
                "title_en": "Bridge",
                "icon": "🌉",
                "time": "45 นาที",
                "desc": "เชื่อมต่อเกตเวย์ตัวรับเข้า Home Assistant ผ่าน ESPHome, เปรียบเทียบค่าสองเส้นทาง, สร้างแดชบอร์ดแปลงไกล, และสร้าง Automation เฝ้าระวังแปลงเงียบ (Deadman Alert)",
                "html_file": "activity_11_bridge_guide.html",
                "md_file": "activity_11_bridge_guide.md",
                "render_file": "../iot_training_workshop/renders/activity-11.html",
                "color": "#0284c7"
            }
        ]
    }
]

def generate_curriculum_html():
    out = []
    out.append('    <!-- Section 6: Comprehensive Workshop Curriculum & Facilitator Guides -->')
    out.append('    <div class="card" style="margin-top: 24px; border-left: 5px solid #0284c7; background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);">')
    out.append('      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">')
    out.append('        <h2 style="margin: 0; font-size: 1.45rem; color: #0f172a; border-bottom: none; padding-bottom: 0;">📚 ชุดคู่มือการจัดกิจกรรมเชิงปฏิบัติการ 11 กิจกรรม (Full Workshop Guides)</h2>')
    out.append('        <span style="background: #0284c7; color: white; padding: 5px 14px; border-radius: 999px; font-size: 13px; font-weight: 600;">คู่มือมาตรฐานสำหรับวิทยากร & ผู้เรียน</span>')
    out.append('      </div>')
    out.append('      <p style="color: #475569; font-size: 14.5px; margin-bottom: 24px; line-height: 1.6;">')
    out.append('        คู่มือมาตรฐานฉบับสมบูรณ์สำหรับวิทยากร ผู้ช่วยสอน (TA) และผู้เข้าอบรม ในการจัดกิจกรรมเชิงปฏิบัติการ Smart Farm AIoT ทั้ง 4 ช่วง (11 กิจกรรม) แต่ละคู่มือประกอบด้วย บทนำวิศวกรรม, แผนคุมเวลา (Facilitator Matrix), ผังวงจรฮาร์ดแวร์, โค้ด YAML/Config สำเร็จรูป, เฉลยใบงานครบถ้วน, การแก้ไขปัญหาหน้างาน (FAQ) และเกณฑ์การประเมิน 20 คะแนน')
    out.append('      </p>')

    for s_idx, session in enumerate(CURRICULUM_DATA, 1):
        out.append(f'      <div style="margin-bottom: 28px;">')
        out.append(f'        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">')
        out.append(f'          <span style="background: #e0f2fe; color: #0369a1; padding: 2px 10px; border-radius: 6px; font-size: 12.5px; font-weight: 700;">SESSION {s_idx}</span>')
        out.append(f'          <h3 style="margin: 0; font-size: 1.15rem; color: #1e293b;">{session["session"]}</h3>')
        out.append(f'        </div>')
        out.append(f'        <p style="font-size: 13.5px; color: #64748b; margin-bottom: 14px;">{session["session_desc"]}</p>')
        
        out.append('        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">')
        for act in session["activities"]:
            out.append(f"""          <div style="background: white; border: 1px solid var(--border); border-top: 4px solid {act['color']}; padding: 18px; border-radius: 10px; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; justify-content: space-between;">
            <div>
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <span style="font-size: 24px;">{act['icon']}</span>
                <span style="background: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 6px; font-size: 11.5px; font-weight: 600;">⏱️ {act['time']}</span>
              </div>
              <h4 style="margin: 0 0 6px 0; font-size: 15px; color: #0f172a; line-height: 1.4;">กิจกรรมที่ {act['num']}: {act['title_th']} <span style="font-size: 13px; color: #64748b; font-weight: 400;">({act['title_en']})</span></h4>
              <p style="font-size: 13px; color: #64748b; line-height: 1.5; margin-bottom: 16px;">{act['desc']}</p>
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px; padding-top: 12px; border-top: 1px solid #f1f5f9;">
              <a href="{act['html_file']}" target="_blank" style="display: flex; align-items: center; justify-content: center; gap: 6px; background: {act['color']}; color: white; padding: 7px 12px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 600;">
                📖 เปิดคู่มือฉบับสมบูรณ์ (HTML) ↗
              </a>
              <div style="display: flex; gap: 6px;">
                <a href="{act['render_file']}" target="_blank" style="flex: 1; text-align: center; background: white; color: {act['color']}; border: 1px solid {act['color']}; padding: 5px 8px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 500;">
                  📝 ใบงาน
                </a>
                <a href="{act['md_file']}" target="_blank" style="flex: 1; text-align: center; background: #f8fafc; color: #475569; border: 1px solid var(--border); padding: 5px 8px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 500;">
                  📄 โค้ด .md
                </a>
              </div>
            </div>
          </div>""")
        out.append('        </div>')
        out.append('      </div>')

    out.append('    </div>')
    return '\n'.join(out)

# Update index.html
with open('/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/คู่มือ/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the single Activity 5 section with the new comprehensive curriculum
pattern = r'<!-- Section: Activity 5 Failure Lab Guide -->.*?</div>\s*</div>\s*(?=<!-- Section 7: Assessment)'
replacement = generate_curriculum_html() + '\n\n'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/คู่มือ/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Updated index.html: new size {len(new_content):,} bytes")
