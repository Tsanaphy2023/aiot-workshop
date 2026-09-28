import json

with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/pretest_40_data.json", "r", encoding="utf-8") as f:
    q40_list = json.load(f)

q40_js = json.dumps(q40_list, ensure_ascii=False, indent=2)

with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

target_anchor = "// 5. Pre-test & Post-test Interactive Quiz (Smart Farm IoT & Automation)"
if target_anchor not in app_js:
    print("Error: Target anchor not found in app.js")
    exit(1)

parts = app_js.split(target_anchor)
pre_part = parts[0]
post_part_full = parts[1]

render_anchor = "function renderQuiz() {"
if render_anchor not in post_part_full:
    print("Error: renderQuiz not found")
    exit(1)

post_parts = post_part_full.split(render_anchor)
old_questions_section = post_parts[0]
after_render_section = post_parts[1]

new_scenario = old_questions_section.replace("const quizQuestions = [", "const quizQuestionsScenario = [")

new_quiz_code = f"""// 5. Pre-test & Post-test Interactive Quiz (Dual Modes: Master 40 & Scenario 10)
// ==========================================================================

// A. Master Pre-test (40 ข้อ อ้างอิงจากหลักสูตร CMU Lifelong & SciRBRU AIoT)
const quizQuestionsMaster40 = {q40_js};

// B. Scenario Assessment Quiz (10 ข้อ วิเคราะห์สถานการณ์ Smart Farm IoT)
{new_scenario.strip()}

let activeQuizMode = 'pretest40';
let currentQuizQuestions = quizQuestionsMaster40;

function switchQuizMode(mode) {{
  activeQuizMode = mode;
  const btn40 = document.getElementById('btn-quiz-mode-40');
  const btn10 = document.getElementById('btn-quiz-mode-10');
  
  if (mode === 'pretest40') {{
    currentQuizQuestions = quizQuestionsMaster40;
    if (btn40) {{
      btn40.style.background = '';
      btn40.style.border = '';
      btn40.classList.add('active');
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
    if (btn40) {{
      btn40.style.background = 'transparent';
      btn40.style.border = '1px solid rgba(255,255,255,0.2)';
      btn40.classList.remove('active');
    }}
  }}
  const resultBox = document.getElementById('quiz-result-score');
  if (resultBox) resultBox.style.display = 'none';
  renderQuiz();
}}

function renderQuiz() {{
  const quizContainer = document.getElementById('quiz-questions-list');
  if (!quizContainer) return;

  quizContainer.innerHTML = '';
  currentQuizQuestions.forEach((item, index) => {{
    const qDiv = document.createElement('div');
    qDiv.className = 'question-box';
    qDiv.id = `q-box-${{index}}`;

    let optionsHtml = '';
    item.options.forEach((opt, optIndex) => {{
      optionsHtml += `
        <label class="choice-label" id="label-${{index}}-${{optIndex}}">
          <input type="radio" name="q_${{index}}" value="${{optIndex}}">
          <span>${{opt}}</span>
        </label>
      `;
    }});

    qDiv.innerHTML = `
      <div class="question-title">${{item.q}}</div>
      <div class="choice-options">${{optionsHtml}}</div>
      <div class="quiz-feedback" id="feedback-${{index}}" style="display:none; margin-top:0.8rem; font-size:0.85rem; padding:0.6rem; border-radius:6px;"></div>
    `;

    quizContainer.appendChild(qDiv);
  }});
}}
"""

grade_anchor = "function gradeQuiz() {"
after_grade = after_render_section.split(grade_anchor)[1]
grade_code_clean = after_grade.replace("quizQuestions.length", "currentQuizQuestions.length").replace("quizQuestions.forEach", "currentQuizQuestions.forEach")

new_full_app_js = pre_part + new_quiz_code + "\nfunction gradeQuiz() {" + grade_code_clean

with open("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/scirbru_ydai2026/app.js", "w", encoding="utf-8") as f:
    f.write(new_full_app_js)

print("Updated app.js successfully!")
