# -*- coding: utf-8 -*-
"""
Full Generator for Activity Guides 1, 2, 3, 4, 6, 7, 8, 9, 10, 11
Creates both Markdown (.md) and HTML (.html) files in /Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/คู่มือ/
"""

import os
import sys

OUTPUT_DIR = "/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/คู่มือ"
os.makedirs(OUTPUT_DIR, exist_ok=True)

sys.path.append("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scratch")

from build_all_guides import get_html_template, generate_markdown
from card_renderer import render_activity_html

HTML_TEMPLATE = get_html_template()

# Load data definitions for all activities
from act_data_1_to_4 import ACTIVITIES_1_TO_4
from act_data_6_to_8 import ACTIVITIES_6_TO_8
from act_data_9_to_11 import ACTIVITIES_9_TO_11

ALL_ACTIVITIES = {
    **ACTIVITIES_1_TO_4,
    **ACTIVITIES_6_TO_8,
    **ACTIVITIES_9_TO_11
}

# Activity navigation mapping
ACT_NAV = [
    (1, "activity_1_sense_guide.html", "กิจกรรมที่ 1 (Sense)"),
    (2, "activity_2_act_guide.html", "กิจกรรมที่ 2 (Act)"),
    (3, "activity_3_logic_guide.html", "กิจกรรมที่ 3 (Logic)"),
    (4, "activity_4_think_guide.html", "กิจกรรมที่ 4 (Think)"),
    (5, "activity_5_failure_lab_guide.html", "กิจกรรมที่ 5 (Failure Lab)"),
    (6, "activity_6_history_guide.html", "กิจกรรมที่ 6 (History)"),
    (7, "activity_7_dashboard_guide.html", "กิจกรรมที่ 7 (Dashboard)"),
    (8, "activity_8_farm_design_guide.html", "กิจกรรมที่ 8 (Design)"),
    (9, "activity_9_espnow_send_guide.html", "กิจกรรมที่ 9 (Send)"),
    (10, "activity_10_espnow_receive_guide.html", "กิจกรรมที่ 10 (Receive)"),
    (11, "activity_11_bridge_guide.html", "กิจกรรมที่ 11 (Bridge)")
]

def build_guides():
    print(f"Generating guides into {OUTPUT_DIR}...")
    for num, data in ALL_ACTIVITIES.items():
        # Find prev and next links
        curr_idx = num - 1
        prev_link = ACT_NAV[curr_idx - 1] if curr_idx > 0 else None
        next_link = ACT_NAV[curr_idx + 1] if curr_idx < len(ACT_NAV) - 1 else None

        prev_btn = f'<a href="{prev_link[1]}" class="btn btn-outline">⬅️ {prev_link[2]}</a>' if prev_link else '<span style="opacity:0.4;">⬅️ ก่อนหน้า</span>'
        next_btn = f'<a href="{next_link[1]}" class="btn btn-primary">{next_link[2]} ➡️</a>' if next_link else '<span style="opacity:0.4;">ถัดไป ➡️</span>'

        # Render HTML content using card_renderer
        cards_html = render_activity_html(data)

        # Generate HTML content
        html_content = HTML_TEMPLATE.format(
            num=data['num'],
            title_th=data['title_th'],
            title_en=data['title_en'],
            icon=data['icon'],
            primary_color=data['primary_color'],
            primary_dark=data['primary_dark'],
            primary_light=data['primary_light'],
            header_desc=data['header_desc'],
            content_html=cards_html,
            prev_btn=prev_btn,
            next_btn=next_btn
        )

        html_filename = f"{data['file_base']}.html"
        html_path = os.path.join(OUTPUT_DIR, html_filename)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✓ Created HTML: {html_filename} ({len(html_content):,} bytes)")

        # Generate Markdown
        md_content = generate_markdown(data)
        md_filename = f"{data['file_base']}.md"
        md_path = os.path.join(OUTPUT_DIR, md_filename)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"✓ Created MD:   {md_filename} ({len(md_content):,} bytes)")

if __name__ == '__main__':
    build_guides()
