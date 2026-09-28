import json

# 1. Load 45-question dataset
with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/pretest_45_data.json", "r", encoding="utf-8") as f:
    q45_list = json.load(f)

q45_js = json.dumps(q45_list, ensure_ascii=False, indent=2)

# 2. Update app.js
with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

# Replace Master 40 with Master 45 in app.js
# We can find the boundary between Master definition and Scenario definition
start_tag = "// A. Master Pre-test"
scenario_tag = "// B. Scenario Assessment Quiz"
render_tag = "function renderQuiz() {"

if start_tag in app_js and scenario_tag in app_js and render_tag in app_js:
    part1 = app_js.split(start_tag)[0]
    remainder = app_js.split(start_tag)[1]
    
    scenario_section = remainder.split(scenario_tag)[1].split(render_tag)[0]
    after_render = remainder.split(render_tag)[1]
    
    # Extract only the const quizQuestionsScenario array from scenario_section
    scenario_code = scenario_section.split("let activeQuizMode")[0].strip()
    
    new_middle = f"""// A. Master Pre-test (45 ข้อ อ้างอิงจากหลักสูตร CMU Lifelong & SciRBRU AIoT)
const quizQuestionsMaster45 = {q45_js};

// B. Scenario Assessment Quiz (10 ข้อ วิเคราะห์สถานการณ์ Smart Farm IoT)
{scenario_code}

let activeQuizMode = 'pretest45';
let currentQuizQuestions = quizQuestionsMaster45;

function switchQuizMode(mode) {{
  activeQuizMode = mode;
  const btn45 = document.getElementById('btn-quiz-mode-45') || document.getElementById('btn-quiz-mode-40');
  const btn10 = document.getElementById('btn-quiz-mode-10');
  
  if (mode === 'pretest45' || mode === 'pretest40') {{
    currentQuizQuestions = quizQuestionsMaster45;
    if (btn45) {{
      btn45.style.background = '';
      btn45.style.border = '';
      btn45.classList.add('active');
    }}
    if (btn10) {{
      btn10.style.background = 'transparent';
      btn10.style.border = '1px solid rgba(255,255,255,0.2)';
      btn10.classList.remove('active');
    }}
  }} else {{
    currentQuizQuestions = quizQuestionsScenario;
    if (btn10) {{
      btn10.style.background = '';
      btn10.style.border = '';
      btn10.classList.add('active');
    }}
    if (btn45) {{
      btn45.style.background = 'transparent';
      btn45.style.border = '1px solid rgba(255,255,255,0.2)';
      btn45.classList.remove('active');
    }}
  }}
  const resultBox = document.getElementById('quiz-result-score');
  if (resultBox) resultBox.style.display = 'none';
  renderQuiz();
}}

"""
    new_app_js = part1 + new_middle + render_tag + after_render
    with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/app.js", "w", encoding="utf-8") as f:
        f.write(new_app_js)
    print("Updated app.js successfully with quizQuestionsMaster45!")
else:
    print("Error locating tags in app.js")

# 3. Update index.html
with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/index.html", "r", encoding="utf-8") as f:
    index_html = f.read()

index_html = index_html.replace('id="btn-quiz-mode-40"', 'id="btn-quiz-mode-45"')
index_html = index_html.replace("switchQuizMode('pretest40')", "switchQuizMode('pretest45')")
index_html = index_html.replace("Master 40 ข้อ", "Master 45 ข้อ (อัปเดตล่าสุด)")
index_html = index_html.replace("worksheet_pretest_40.pdf", "worksheet_pretest_45.pdf")
index_html = index_html.replace("worksheet_pretest_40.html", "worksheet_pretest_45.html")
index_html = index_html.replace("ดาวน์โหลดใบงาน PDF", "ดาวน์โหลดใบงาน PDF (45 ข้อ)")

with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)
print("Updated index.html successfully!")
