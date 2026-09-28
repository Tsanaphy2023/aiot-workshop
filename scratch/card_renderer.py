# -*- coding: utf-8 -*-
"""
Helper to render markdown snippets into styled HTML cards
"""
import re

def markdown_table_to_html(md_table):
    lines = [l.strip() for l in md_table.strip().split('\n') if l.strip()]
    if len(lines) < 2:
        return ""
    
    header_cols = [c.strip() for c in lines[0].strip('|').split('|')]
    # skip delimiter line (line 1)
    rows = []
    for l in lines[2:]:
        cols = [c.strip() for c in l.strip('|').split('|')]
        rows.append(cols)
    
    html = ['<table><thead><tr>']
    for h in header_cols:
        html.append(f'<th>{inline_md(h)}</th>')
    html.append('</tr></thead><tbody>')
    for r in rows:
        html.append('<tr>')
        for c in r:
            html.append(f'<td>{inline_md(c)}</td>')
        html.append('</tr>')
    html.append('</tbody></table>')
    return ''.join(html)

def inline_md(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.*?)`', r'<code class="code-inline">\1</code>', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text

def md_to_html_blocks(md_text):
    # Split into sections or paragraphs
    output = []
    lines = md_text.split('\n')
    i = 0
    in_table = False
    table_lines = []
    in_code = False
    code_lines = []
    code_lang = ""

    while i < len(lines):
        line = lines[i]
        
        # Code block
        if line.strip().startswith('```'):
            if not in_code:
                in_code = True
                code_lang = line.strip()[3:]
                code_lines = []
            else:
                in_code = False
                code_content = '\n'.join(code_lines)
                output.append(f'<pre><button class="copy-btn" onclick="copyCode(this)">📋 คัดลอก</button><code>{code_content}</code></pre>')
            i += 1
            continue
            
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Table block
        if '|' in line and not line.strip().startswith('#'):
            if not in_table:
                in_table = True
                table_lines = [line]
            else:
                table_lines.append(line)
            i += 1
            continue
        elif in_table:
            in_table = False
            output.append(markdown_table_to_html('\n'.join(table_lines)))
            table_lines = []

        # Headings
        if line.startswith('### '):
            output.append(f'<h3 class="sub-title">{inline_md(line[4:])}</h3>')
        elif line.startswith('## '):
            output.append(f'<h2 class="section-title">{inline_md(line[3:])}</h2>')
        elif line.startswith('#### '):
            output.append(f'<h4 style="font-size:16px; margin:14px 0 6px 0; color:#334155;">{inline_md(line[5:])}</h4>')
        elif line.strip().startswith('* ') or line.strip().startswith('- '):
            # List item
            output.append(f'<p style="margin-left:20px; text-indent:-15px;">• {inline_md(line.strip()[2:])}</p>')
        elif re.match(r'^\d+\.\s', line.strip()):
            m = re.match(r'^(\d+)\.\s(.*)', line.strip())
            output.append(f'<p style="margin-left:20px; text-indent:-15px;"><strong>{m.group(1)}.</strong> {inline_md(m.group(2))}</p>')
        elif line.strip().startswith('> [!'):
            callout_type = "important"
            if "WARNING" in line: callout_type = "warning"
            elif "TIP" in line: callout_type = "success"
            elif "CAUTION" in line or "DANGER" in line: callout_type = "danger"
            i += 1
            callout_body = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                callout_body.append(lines[i].strip().lstrip('>').strip())
                i += 1
            body_text = ' '.join(callout_body)
            output.append(f'<div class="callout {callout_type}"><div class="callout-icon">💡</div><div>{inline_md(body_text)}</div></div>')
            continue
        elif line.strip() == '---':
            output.append('<hr style="border:0; border-top:1px solid var(--border); margin:20px 0;">')
        elif line.strip():
            output.append(f'<p style="margin-bottom:12px;">{inline_md(line)}</p>')
        
        i += 1

    if in_table and table_lines:
        output.append(markdown_table_to_html('\n'.join(table_lines)))

    return '\n'.join(output)

def render_activity_html(data):
    cards = []
    
    # Card 1: Intro
    cards.append(f"""  <div class="card" id="intro">
    <h2 class="section-title"><span>📌</span> 1. บทนำและแนวคิดวิศวกรรม ({data['title_en']} Principles)</h2>
{md_to_html_blocks(data['intro_md'])}
  </div>""")

    # Card 2: Time Matrix
    cards.append(f"""  <div class="card" id="time-matrix">
    <h2 class="section-title"><span>⏱️</span> 2. แผนการจัดการเรียนรู้และเวลา (Facilitator Time Matrix)</h2>
    <p style="margin-bottom: 14px;"><strong>เวลารวม:</strong> {data['total_time']} นาที | <strong>รูปแบบการจัด:</strong> {data['format_desc']}</p>
    <div class="mermaid">
{data['gantt_mermaid']}
    </div>
{markdown_table_to_html(data['time_table_md'])}
  </div>""")

    # Card 3: Hardware BOM
    cards.append(f"""  <div class="card" id="hardware">
    <h2 class="section-title"><span>🔌</span> 3. รายการอุปกรณ์และการเชื่อมต่อ (Hardware BOM & Interfacing)</h2>
    <div class="mermaid">
{data['hardware_mermaid']}
    </div>
{markdown_table_to_html(data['bom_table_md'])}
  </div>""")

    # Card 4: Steps
    cards.append(f"""  <div class="card" id="steps">
    <h2 class="section-title"><span>🧪</span> 4. ขั้นตอนการทดลองอย่างละเอียดทีละขั้น (Step-by-Step Lab Protocol)</h2>
{md_to_html_blocks(data['steps_md'])}
  </div>""")

    # Card 5: Code
    code_raw = data['code_md'].strip()
    if code_raw.startswith('```'):
        lines = code_raw.split('\n')
        code_text = '\n'.join(lines[1:-1])
    else:
        code_text = code_raw
    cards.append(f"""  <div class="card" id="code">
    <h2 class="section-title"><span>💻</span> 5. โค้ดและการตั้งค่าสำเร็จรูป (Ready-to-use Configurations)</h2>
    <pre><button class="copy-btn" onclick="copyCode(this)">📋 คัดลอก</button><code>{code_text}</code></pre>
  </div>""")

    # Card 6: Answers
    cards.append(f"""  <div class="card" id="answers">
    <h2 class="section-title"><span>📝</span> 6. แนวทางการตรวจคำตอบและเฉลยใบงาน (Answer Key & Discussion)</h2>
{md_to_html_blocks(data['answers_md'])}
  </div>""")

    # Card 7: Troubleshooting
    cards.append(f"""  <div class="card" id="troubleshooting">
    <h2 class="section-title"><span>🛠️</span> 7. การแก้ไขปัญหาหน้างานที่พบบ่อย (Troubleshooting FAQ)</h2>
{markdown_table_to_html(data['troubleshooting_md'])}
  </div>""")

    # Card 8: Rubric
    cards.append(f"""  <div class="card" id="rubric">
    <h2 class="section-title"><span>📊</span> 8. เกณฑ์การประเมินผลการเรียนรู้ (Assessment Rubric)</h2>
{markdown_table_to_html(data['rubric_md'])}
  </div>""")

    return '\n\n'.join(cards)
