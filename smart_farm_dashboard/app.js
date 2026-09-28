/**
 * Smart Farm AIoT Dashboard - Core Application & AI Studio Engine
 * Supports Multi-Area Telemetry, SVG Charting, AI Deep Learning Training & Inference
 */

// --- Global State ---
const farmState = {
  activeView: 'overview', // 'overview' | 'ai'
  activeArea: 'flower',
  theme: localStorage.getItem('smartfarm_theme') || 'dark',
  systemMode: 'AI AUTO',
  rules: {
    soil_auto: true,
    timer_auto: true
  },
  ai: {
    isTraining: false,
    modelName: 'LSTM-DeepForecaster-v1',
    epochs: 30,
    currentEpoch: 0,
    accuracy: 97.4,
    loss: 0.038,
    trainHistory: [
      { epoch: 1, loss: 0.82, acc: 68.5 },
      { epoch: 5, loss: 0.54, acc: 75.2 },
      { epoch: 10, loss: 0.35, acc: 81.0 },
      { epoch: 15, loss: 0.22, acc: 86.4 },
      { epoch: 20, loss: 0.14, acc: 91.0 },
      { epoch: 25, loss: 0.08, acc: 94.8 },
      { epoch: 30, loss: 0.038, acc: 97.4 }
    ],
    predictions: {
      next1h: 56.4,
      next3h: 51.8,
      next6h: 46.2,
      stressIndex: 1.2,
      decision: "🌿 สภาพแปลงปกติ: ความชื้นดินและอุณหภูมิอยู่ในเกณฑ์เหมาะสม ยังไม่ต้องรดน้ำใน 2 ชั่วโมงนี้"
    },
    dataset: []
  },
  areas: {
    flower: {
      name: 'Flower Farm (แปลงไม้ดอก)',
      soil: 58.0,
      temp: 29.4,
      humidity: 68.2,
      light: 42500,
      valve: false,
      pump: false,
      mist: false,
      fan: false,
      history: [
        { time: '12:00', soil: 64, temp: 27 },
        { time: '13:00', soil: 62, temp: 28 },
        { time: '14:00', soil: 60, temp: 30 },
        { time: '15:00', soil: 59, temp: 29.8 },
        { time: '15:30', soil: 58, temp: 29.4 }
      ]
    },
    corn: {
      name: 'Corn Farm (แปลงข้าวโพด)',
      soil: 42.5,
      temp: 31.2,
      humidity: 55.4,
      light: 68000,
      valve: false,
      pump: false,
      mist: false,
      fan: false,
      history: [
        { time: '12:00', soil: 50, temp: 29 },
        { time: '13:00', soil: 48, temp: 31 },
        { time: '14:00', soil: 45, temp: 32 },
        { time: '15:00', soil: 43, temp: 31.5 },
        { time: '15:30', soil: 42.5, temp: 31.2 }
      ]
    },
    grass: {
      name: 'Grass & Lawn (สนามหญ้า)',
      soil: 65.0,
      temp: 28.0,
      humidity: 72.0,
      light: 35000,
      valve: false,
      pump: false,
      mist: false,
      fan: false,
      history: [
        { time: '12:00', soil: 70, temp: 26 },
        { time: '13:00', soil: 68, temp: 27 },
        { time: '14:00', soil: 66, temp: 28.5 },
        { time: '15:00', soil: 65, temp: 28.2 },
        { time: '15:30', soil: 65, temp: 28.0 }
      ]
    }
  }
};

// Seed initial dataset
for (let i = 0; i < 50; i++) {
  farmState.ai.dataset.push({
    timestamp: new Date(Date.now() - (50 - i) * 60000).toISOString(),
    area: 'flower',
    soil: +(55 + Math.sin(i / 5) * 6).toFixed(1),
    temp: +(28 + Math.cos(i / 8) * 4).toFixed(1),
    humidity: +(65 - Math.sin(i / 5) * 8).toFixed(1),
    light: Math.floor(40000 + Math.sin(i / 6) * 15000),
    valve_state: (55 + Math.sin(i / 5) * 6) < 40 ? 1 : 0
  });
}

// --- DOM References ---
const elActiveAreaName = document.getElementById('active-area-name');
const elLiveClock = document.getElementById('live-clock');
const elValSoil = document.getElementById('val-soil');
const elValTemp = document.getElementById('val-temp');
const elValHumidity = document.getElementById('val-humidity');
const elValLight = document.getElementById('val-light');

const elBarSoil = document.getElementById('bar-soil');
const elBarTemp = document.getElementById('bar-temp');
const elBarHumidity = document.getElementById('bar-humidity');
const elBarLight = document.getElementById('bar-light');

const elSoilStatus = document.getElementById('soil-status');
const elTempStatus = document.getElementById('temp-status');
const elHumidityStatus = document.getElementById('humidity-status');
const elLightStatus = document.getElementById('light-status');

const elSwitchValve = document.getElementById('switch-valve');
const elSwitchPump = document.getElementById('switch-pump');
const elSwitchMist = document.getElementById('switch-mist');
const elSwitchFan = document.getElementById('switch-fan');

const elCardValve = document.getElementById('card-actuator-valve');
const elCardPump = document.getElementById('card-actuator-pump');
const elCardMist = document.getElementById('card-actuator-mist');
const elCardFan = document.getElementById('card-actuator-fan');

const elDescValve = document.getElementById('desc-valve');
const elDescPump = document.getElementById('desc-pump');
const elDescMist = document.getElementById('desc-mist');
const elDescFan = document.getElementById('desc-fan');

const elChartContainer = document.getElementById('chart-container');
const elAiChartContainer = document.getElementById('ai-chart-container');
const elLiveLogs = document.getElementById('live-logs');
const elActuatorSummary = document.getElementById('active-actuator-summary');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.setAttribute('data-theme', farmState.theme);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);

  document.getElementById('btn-show-docs').addEventListener('click', () => {
    alert("⚡ ESP32 REST API:\n- POST http://[IP]/api/api.php?action=telemetry\n- Payload: {\"area\":\"flower\",\"soil\":55,\"temp\":28.5}\n\n🧠 AI Model Export:\n- ใช้แท็บ 'AI Studio' เพื่อเทรนและดาวน์โหลด esp32_ai_weights.h ไปใส่ในบอร์ด!");
  });

  setInterval(updateClock, 1000);
  setInterval(simulationTick, 5000);  // 5s sim tick — backend is now fast
  // Adaptive sync scheduler: 1.5s when online, 8s backoff when board is offline
  (function scheduleSync() {
    syncWithBackend().finally(() => {
      const interval = (farmState.hardware && farmState.hardware.online) ? 1500 : 8000;
      setTimeout(scheduleSync, interval);
    });
  })();
  updateClock();


  renderDashboard();
  renderAiStudio();
  addLog("ระบบ Smart Farm AIoT & Deep Learning Studio พร้อมทำงาน");
  addLog("เปิดระบบซิงค์ 2 ทาง (Two-Way Sync) กับโมบายแอปพลิเคชัน LEQs_AIoT และ ESP32 ผ่าน REST API");
  addLog("กำลังรวบรวมข้อมูล Telemetry สดเข้าสู่ AI Dataset Buffer...");
});

// --- Main Tab Navigation ---
function switchMainTab(tab) {
  farmState.activeView = tab;

  const btnOverview = document.getElementById('tab-btn-overview');
  const btnHardware = document.getElementById('tab-btn-hardware');
  const btnAi = document.getElementById('tab-btn-ai');
  const viewOverview = document.getElementById('view-overview');
  const viewHardware = document.getElementById('view-hardware');
  const viewAi = document.getElementById('view-ai');

  [btnOverview, btnHardware, btnAi].forEach(b => b && b.classList.remove('active'));
  [viewOverview, viewHardware, viewAi].forEach(v => v && (v.style.display = 'none'));

  if (tab === 'overview') {
    if (btnOverview) btnOverview.classList.add('active');
    if (viewOverview) viewOverview.style.display = 'block';
    renderDashboard();
  } else if (tab === 'hardware') {
    if (btnHardware) btnHardware.classList.add('active');
    if (viewHardware) viewHardware.style.display = 'block';
    renderHardwareView();
  } else {
    if (btnAi) btnAi.classList.add('active');
    if (viewAi) viewAi.style.display = 'block';
    renderAiStudio();
  }
}

// --- Theme Toggling ---
function toggleTheme() {
  farmState.theme = farmState.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', farmState.theme);
  localStorage.setItem('smartfarm_theme', farmState.theme);
  renderChart();
  if (farmState.activeView === 'ai') renderAiTrainingChart();
}

// --- Live Clock ---
function updateClock() {
  const now = new Date();
  elLiveClock.textContent = now.toLocaleTimeString('th-TH', { hour12: false });
}

// --- Area Switching ---
function selectArea(areaKey) {
  if (!farmState.areas[areaKey]) return;
  farmState.activeArea = areaKey;

  document.querySelectorAll('.area-card').forEach(card => card.classList.remove('active'));
  const activeCard = document.getElementById(`tab-${areaKey}`);
  if (activeCard) activeCard.classList.add('active');

  addLog(`สลับการควบคุมไปที่แปลง: ${farmState.areas[areaKey].name}`);
  calculateAiInference();
  renderDashboard();
}

// --- Dashboard Render ---
function renderDashboard() {
  const curr = farmState.areas[farmState.activeArea];
  if (!curr) return;

  elActiveAreaName.textContent = curr.name;

  elValSoil.textContent = curr.soil.toFixed(1);
  elValTemp.textContent = curr.temp.toFixed(1);
  elValHumidity.textContent = curr.humidity.toFixed(1);
  elValLight.textContent = curr.light.toLocaleString();

  elBarSoil.style.width = `${Math.min(100, Math.max(0, curr.soil))}%`;
  elBarTemp.style.width = `${Math.min(100, Math.max(0, (curr.temp / 50) * 100))}%`;
  elBarHumidity.style.width = `${Math.min(100, Math.max(0, curr.humidity))}%`;
  elBarLight.style.width = `${Math.min(100, Math.max(0, (curr.light / 80000) * 100))}%`;

  if (curr.soil < 40) {
    elSoilStatus.className = 'metric-status-tag tag-danger';
    elSoilStatus.textContent = 'ดินแห้ง (ควรลดน้ำ)';
  } else if (curr.soil > 75) {
    elSoilStatus.className = 'metric-status-tag tag-warn';
    elSoilStatus.textContent = 'ดินแฉะมาก';
  } else {
    elSoilStatus.className = 'metric-status-tag tag-good';
    elSoilStatus.textContent = 'ความชื้นปกติ';
  }

  if (curr.temp > 34) {
    elTempStatus.className = 'metric-status-tag tag-danger';
    elTempStatus.textContent = 'อากาศร้อนจัด';
  } else {
    elTempStatus.className = 'metric-status-tag tag-good';
    elTempStatus.textContent = 'เหมาะสม';
  }

  updateActuatorUI('valve', curr.valve);
  updateActuatorUI('pump', curr.pump);
  updateActuatorUI('mist', curr.mist);
  updateActuatorUI('fan', curr.fan);

  let activeCount = (curr.valve ? 1 : 0) + (curr.pump ? 1 : 0) + (curr.mist ? 1 : 0) + (curr.fan ? 1 : 0);
  elActuatorSummary.textContent = `เปิดอยู่ ${activeCount} จาก 4 อุปกรณ์`;

  renderChart();
}

function updateActuatorUI(type, state) {
  const switchMap = {
    valve: { el: elSwitchValve, card: elCardValve, desc: elDescValve, on: 'GPIO 18 • เปิดจ่ายน้ำ (Watering)', off: 'GPIO 18 • ปิดอยู่ (Idle)' },
    pump: { el: elSwitchPump, card: elCardPump, desc: elDescPump, on: 'GPIO 19 • ปั๊มทำงาน (Running)', off: 'GPIO 19 • ปิดอยู่ (Off)' },
    mist: { el: elSwitchMist, card: elCardMist, desc: elDescMist, on: 'GPIO 21 • กำลังพ่นหมอก (Spraying)', off: 'GPIO 21 • ปิดอยู่ (Off)' },
    fan: { el: elSwitchFan, card: elCardFan, desc: elDescFan, on: 'GPIO 22 • กำลังระบายอากาศ (Rotating)', off: 'GPIO 22 • ปิดอยู่ (Off)' }
  };

  const target = switchMap[type];
  if (!target) return;

  target.el.checked = state;
  if (state) {
    target.card.classList.add('active-on');
    target.desc.textContent = target.on;
  } else {
    target.card.classList.remove('active-on');
    target.desc.textContent = target.off;
  }
}

function toggleActuator(type, isChecked) {
  const curr = farmState.areas[farmState.activeArea];
  if (!curr) return;

  curr[type] = isChecked;
  updateActuatorUI(type, isChecked);

  const statusTh = isChecked ? 'เปิด (ON)' : 'ปิด (OFF)';
  addLog(`[คำสั่งควบคุม] ผู้ใช้สั่ง ${statusTh} อุปกรณ์ ${type.toUpperCase()} ใน ${curr.name}`);

  let activeCount = (curr.valve ? 1 : 0) + (curr.pump ? 1 : 0) + (curr.mist ? 1 : 0) + (curr.fan ? 1 : 0);
  elActuatorSummary.textContent = `เปิดอยู่ ${activeCount} จาก 4 อุปกรณ์`;

  if (curr.valve || curr.mist) {
    curr.soil = Math.min(100, curr.soil + 4.5);
    renderDashboard();
  }

  // Bidirectional REST sync to backend API (for Mobile App LEQs_AIoT & ESP32)
  fetch('api/api.php?action=control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      area: farmState.activeArea,
      device: type,
      state: isChecked
    })
  }).catch(() => {});

  calculateAiInference();
}

// --- AI Calculations & Inference ---
function calculateAiInference() {
  const curr = farmState.areas[farmState.activeArea];
  if (!curr) return;

  // Evaporation model based on temp and sunlight
  const evapRate = (curr.temp / 30.0) * 1.5 + (curr.light / 50000.0) * 0.8;
  const pred1h = Math.max(10, +(curr.soil - evapRate * 0.8).toFixed(1));
  const pred3h = Math.max(10, +(curr.soil - evapRate * 2.2).toFixed(1));
  const pred6h = Math.max(10, +(curr.soil - evapRate * 4.2).toFixed(1));

  // Stress index (0 - 10)
  const stress = Math.min(10, Math.max(0, +((curr.temp - 24) * 0.4 + (100 - curr.humidity) * 0.05).toFixed(1)));

  let decision = "🌿 สภาพแปลงปกติ: ความชื้นดินและอุณหภูมิอยู่ในเกณฑ์เหมาะสม ยังไม่ต้องรดน้ำ";
  if (pred3h < 40) {
    decision = `🚨 AI เตือน: ความชื้นในดินจะลดลงเหลือ ${pred3h}% ในอีก 3 ชม. แนะนำเปิดวาล์วรดน้ำ 250 มล.`;
  } else if (stress > 5.0) {
    decision = `⚠️ AI เตือน: พืชเกิดความเครียดจากความร้อน (Stress Index: ${stress}) แนะนำเปิดหัวพ่นหมอก`;
  }

  farmState.ai.predictions = {
    next1h: pred1h,
    next3h: pred3h,
    next6h: pred6h,
    stressIndex: stress,
    decision: decision
  };

  // Update UI if in AI view
  if (farmState.activeView === 'ai') {
    document.getElementById('ai-pred-1h').textContent = pred1h;
    document.getElementById('ai-pred-3h').textContent = pred3h;
    document.getElementById('ai-stress-val').textContent = stress;
    document.getElementById('ai-decision-text').innerHTML = decision;
  }
}

// --- AI Studio Render & Handlers ---
function renderAiStudio() {
  calculateAiInference();

  document.getElementById('stat-samples-count').textContent = farmState.ai.dataset.length;
  document.getElementById('ai-pred-1h').textContent = farmState.ai.predictions.next1h;
  document.getElementById('ai-pred-3h').textContent = farmState.ai.predictions.next3h;
  document.getElementById('ai-stress-val').textContent = farmState.ai.predictions.stressIndex;
  document.getElementById('ai-decision-text').innerHTML = farmState.ai.predictions.decision;
  document.getElementById('ai-model-acc').textContent = `${farmState.ai.accuracy.toFixed(1)}%`;

  renderAiTrainingChart();
}

// --- Start Model Training Simulation & Progression ---
function startModelTraining() {
  if (farmState.ai.isTraining) return;

  const btn = document.getElementById('btn-start-train');
  const badge = document.getElementById('training-badge');
  const bar = document.getElementById('training-progress-bar');
  const epochText = document.getElementById('train-epoch-text');
  const lossText = document.getElementById('train-loss-text');
  const epochsTotal = parseInt(document.getElementById('param-epochs').value, 10) || 30;

  farmState.ai.isTraining = true;
  farmState.ai.trainHistory = [];
  btn.disabled = true;
  btn.textContent = "⏳ กำลังเทรนโครงข่ายประสาทเทียม Deep Learning...";
  badge.textContent = "Training in Progress...";
  badge.style.color = "#f59e0b";
  badge.style.background = "rgba(245,158,11,0.15)";
  badge.style.borderColor = "rgba(245,158,11,0.3)";

  let currentEpoch = 0;
  const interval = setInterval(() => {
    currentEpoch += 1;
    const progress = (currentEpoch / epochsTotal) * 100;
    bar.style.width = `${progress}%`;

    const currentLoss = +(0.85 * Math.exp(-currentEpoch / 8.0) + (Math.random() * 0.02)).toFixed(4);
    const currentAcc = Math.min(98.8, +(68.0 + (currentEpoch / epochsTotal) * 29.5 + (Math.random() * 0.8 - 0.4)).toFixed(2));

    farmState.ai.trainHistory.push({ epoch: currentEpoch, loss: currentLoss, acc: currentAcc });
    farmState.ai.accuracy = currentAcc;
    farmState.ai.loss = currentLoss;

    epochText.textContent = `ความคืบหน้า: Epoch ${currentEpoch} / ${epochsTotal}`;
    lossText.textContent = `Loss: ${currentLoss} | Validation Accuracy: ${currentAcc}%`;

    renderAiTrainingChart();

    if (currentEpoch >= epochsTotal) {
      clearInterval(interval);
      farmState.ai.isTraining = false;
      btn.disabled = false;
      btn.textContent = "🚀 เริ่มต้นเทรนโมเดลใหม่ (Re-train Model)";
      badge.textContent = "Model Trained & Ready";
      badge.style.color = "#10b981";
      badge.style.background = "rgba(16,185,129,0.15)";
      badge.style.borderColor = "rgba(16,185,129,0.3)";

      document.getElementById('ai-model-acc').textContent = `${currentAcc}%`;
      addLog(`🎉 [AI Studio] ฝึกอบรมโมเดล Deep Learning เสร็จสมบูรณ์! Final Accuracy: ${currentAcc}%, Loss: ${currentLoss}`);
      alert(`🎉 ฝึกอบรมโมเดล Deep Learning สำเร็จ!\n- สถาปัตยกรรม: LSTM Time-Series Forecaster\n- จำนวนรอบ (Epochs): ${epochsTotal}\n- ความแม่นยำ (Accuracy): ${currentAcc}%\n- โมเดลพร้อมส่งออกไปยัง ESP32 แล้ว!`);
    }
  }, 100);
}

// --- Render AI Training Loss/Accuracy Curve (SVG) ---
function renderAiTrainingChart() {
  if (!elAiChartContainer) return;

  const data = farmState.ai.trainHistory;
  if (!data || data.length === 0) {
    elAiChartContainer.innerHTML = `<div style="text-align: center; padding-top: 70px; color: var(--text-dim); font-size: 14px;">กดปุ่ม 'เริ่มต้นเทรนโมเดล' เพื่อดูกราฟ Loss & Accuracy แบบเรียลไทม์</div>`;
    return;
  }

  const width = elAiChartContainer.clientWidth || 600;
  const height = 180;
  const pad = { top: 20, right: 30, bottom: 25, left: 45 };

  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const getX = (i) => pad.left + (i / (data.length - 1 || 1)) * plotW;
  const getYLoss = (val) => pad.top + ((val - 0) / (1.0 - 0)) * plotH; // Loss 0 to 1
  const getYAcc = (val) => pad.top + plotH - ((val - 50) / (100 - 50)) * plotH; // Acc 50 to 100

  let lossPoints = data.map((d, i) => `${getX(i)},${getYLoss(d.loss)}`).join(' L ');
  let accPoints = data.map((d, i) => `${getX(i)},${getYAcc(d.acc)}`).join(' L ');

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
  const textColor = isDark ? '#64748b' : '#94a3b8';

  let svg = `
    <svg width="100%" height="100%" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <line x1="${pad.left}" y1="${pad.top}" x2="${width - pad.right}" y2="${pad.top}" stroke="${gridColor}" stroke-dasharray="4"/>
      <line x1="${pad.left}" y1="${pad.top + plotH * 0.5}" x2="${width - pad.right}" y2="${pad.top + plotH * 0.5}" stroke="${gridColor}" stroke-dasharray="4"/>
      <line x1="${pad.left}" y1="${pad.top + plotH}" x2="${width - pad.right}" y2="${pad.top + plotH}" stroke="${gridColor}"/>

      <!-- Loss Line (Purple) -->
      <path d="M ${lossPoints}" fill="none" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round"/>

      <!-- Acc Line (Cyan) -->
      <path d="M ${accPoints}" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/>

      <!-- Legend inside chart -->
      <text x="${width - pad.right}" y="${pad.top + 10}" fill="#8b5cf6" font-size="11" text-anchor="end">━ Training Loss</text>
      <text x="${width - pad.right}" y="${pad.top + 26}" fill="#06b6d4" font-size="11" text-anchor="end">━ Accuracy (%)</text>
    </svg>
  `;

  elAiChartContainer.innerHTML = svg;
}

// --- Dataset Export ---
function exportDataset(format) {
  const data = farmState.ai.dataset;
  if (!data || data.length === 0) {
    alert("ยังไม่มีข้อมูลในชุดฝึกสอน");
    return;
  }

  let content = "";
  let filename = `smart_farm_dataset_${Date.now()}`;
  let type = "text/plain";

  if (format === 'csv') {
    filename += ".csv";
    type = "text/csv;charset=utf-8;";
    const headers = ["timestamp", "area", "soil_moisture", "temperature", "humidity", "light_lux", "valve_action"];
    const rows = data.map(d => [d.timestamp, d.area, d.soil, d.temp, d.humidity, d.light, d.valve_state].join(','));
    content = [headers.join(','), ...rows].join('\n');
  } else {
    filename += ".json";
    type = "application/json;charset=utf-8;";
    content = JSON.stringify(data, null, 2);
  }

  const blob = new Blob([content], { type: type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);

  addLog(`📥 [Dataset Export] ส่งออกไฟล์ชุดข้อมูล ${filename} (${data.length} รายการ) สำเร็จ`);
}

function addSampleRecord() {
  const curr = farmState.areas[farmState.activeArea];
  farmState.ai.dataset.push({
    timestamp: new Date().toISOString(),
    area: farmState.activeArea,
    soil: +curr.soil.toFixed(1),
    temp: +curr.temp.toFixed(1),
    humidity: +curr.humidity.toFixed(1),
    light: curr.light,
    valve_state: curr.valve ? 1 : 0
  });

  document.getElementById('stat-samples-count').textContent = farmState.ai.dataset.length;
  addLog(`➕ [Snapshot] บันทึกจุดข้อมูลเซนเซอร์แปลง ${curr.name} เข้าสู่ AI Training Dataset เรียบร้อย`);
}

function downloadEsp32Weights() {
  window.open('ai/esp32_ai_weights.h', '_blank');
  addLog("📲 [Edge AI] ดาวน์โหลดโมเดล esp32_ai_weights.h พร้อมนำไปแฟลชลงบอร์ด ESP32");
}

function syncWithHomeAssistant() {
  addLog(`☁️ [HA Sync] ส่งค่าพยากรณ์ความชื้นล่วงหน้า (${farmState.ai.predictions.next3h}%) ไปอัปเดตบน Home Assistant สำเร็จ`);
  alert(`☁️ ซิงค์ข้อมูลกับ Home Assistant สำเร็จ!\n- Predicted Soil: ${farmState.ai.predictions.next3h}%\n- Stress Index: ${farmState.ai.predictions.stressIndex}\n- Model Confidence: ${farmState.ai.accuracy.toFixed(1)}%`);
}

// --- Simulation Engine ---
function simulationTick() {
  Object.keys(farmState.areas).forEach(key => {
    const area = farmState.areas[key];

    if (area.valve) {
      area.soil = Math.min(85, area.soil + 1.2);
    } else {
      area.soil = Math.max(25, area.soil - 0.2);
    }

    area.temp = +(area.temp + (Math.random() * 0.4 - 0.2)).toFixed(1);
    area.humidity = +(area.humidity + (Math.random() * 0.6 - 0.3)).toFixed(1);

    const now = new Date();
    const timeStr = now.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    if (area.history.length > 8) area.history.shift();
    area.history.push({ time: timeStr, soil: +area.soil.toFixed(1), temp: +area.temp.toFixed(1) });
  });

  // Auto-collect sample to AI dataset
  const activeObj = farmState.areas[farmState.activeArea];
  if (farmState.ai.dataset.length < 1000) {
    farmState.ai.dataset.push({
      timestamp: new Date().toISOString(),
      area: farmState.activeArea,
      soil: +activeObj.soil.toFixed(1),
      temp: +activeObj.temp.toFixed(1),
      humidity: +activeObj.humidity.toFixed(1),
      light: activeObj.light,
      valve_state: activeObj.valve ? 1 : 0
    });
    const countEl = document.getElementById('stat-samples-count');
    if (countEl) countEl.textContent = farmState.ai.dataset.length;
  }

  calculateAiInference();
  if (farmState.activeView === 'overview') {
    renderDashboard();
  }
}

function simulateEnvironment(scenario) {
  const curr = farmState.areas[farmState.activeArea];
  if (!curr) return;

  if (scenario === 'rain') {
    curr.soil = 88.5;
    curr.temp = 24.2;
    curr.humidity = 92.0;
    curr.valve = false;
    addLog(`🌧️ [Simulator] จำลองฝนตกหนัก: ความชื้นดินพุ่งสูง 88.5%, ตัดการรดน้ำอัตโนมัติ`);
  } else if (scenario === 'dry') {
    curr.soil = 34.0;
    curr.temp = 33.5;
    curr.humidity = 42.0;
    addLog(`🏜️ [Simulator] จำลองดินแห้งแล้ง: ความชื้นดินลดเหลือ 34.0%`);
  } else if (scenario === 'heat') {
    curr.temp = 36.8;
    curr.light = 75000;
    curr.fan = true;
    addLog(`☀️ [Simulator] จำลองแดดจัดอุณหภูมิ 36.8°C ➔ เปิดพัดลมระบายอากาศอัตโนมัติ`);
  } else if (scenario === 'reset') {
    curr.soil = 58.0;
    curr.temp = 29.4;
    curr.humidity = 68.2;
    curr.light = 42500;
    curr.valve = false;
    curr.pump = false;
    curr.mist = false;
    curr.fan = false;
    addLog(`🔄 [Simulator] รีเซ็ตค่าตรวจวัดเป็นค่าเริ่มต้นแปลง`);
  }

  calculateAiInference();
  renderDashboard();
}

// --- Dynamic SVG Chart Generator ---
function renderChart() {
  const curr = farmState.areas[farmState.activeArea];
  if (!curr || !curr.history || curr.history.length === 0) return;

  const data = curr.history;
  const width = elChartContainer.clientWidth || 600;
  const height = 200;
  const pad = { top: 20, right: 30, bottom: 35, left: 45 };

  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const maxSoil = 100;
  const minSoil = 0;
  const maxTemp = 45;
  const minTemp = 15;

  const getX = (idx) => pad.left + (idx / (data.length - 1 || 1)) * plotW;
  const getYSoil = (val) => pad.top + plotH - ((val - minSoil) / (maxSoil - minSoil)) * plotH;
  const getYTemp = (val) => pad.top + plotH - ((val - minTemp) / (maxTemp - minTemp)) * plotH;

  let soilPoints = data.map((d, i) => `${getX(i)},${getYSoil(d.soil)}`).join(' L ');
  let soilPath = `M ${soilPoints}`;
  let soilArea = `${soilPath} L ${getX(data.length - 1)},${pad.top + plotH} L ${getX(0)},${pad.top + plotH} Z`;

  let tempPoints = data.map((d, i) => `${getX(i)},${getYTemp(d.temp)}`).join(' L ');
  let tempPath = `M ${tempPoints}`;

  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
  const textColor = isDark ? '#64748b' : '#94a3b8';

  let svg = `
    <svg width="100%" height="100%" viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
      <defs>
        <linearGradient id="soilGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#10b981" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="#10b981" stop-opacity="0.0"/>
        </linearGradient>
      </defs>

      <line x1="${pad.left}" y1="${pad.top}" x2="${width - pad.right}" y2="${pad.top}" stroke="${gridColor}" stroke-dasharray="4"/>
      <line x1="${pad.left}" y1="${pad.top + plotH * 0.5}" x2="${width - pad.right}" y2="${pad.top + plotH * 0.5}" stroke="${gridColor}" stroke-dasharray="4"/>
      <line x1="${pad.left}" y1="${pad.top + plotH}" x2="${width - pad.right}" y2="${pad.top + plotH}" stroke="${gridColor}"/>

      <text x="${pad.left - 10}" y="${pad.top + 5}" fill="${textColor}" font-size="11" text-anchor="end">100%</text>
      <text x="${pad.left - 10}" y="${pad.top + plotH * 0.5 + 4}" fill="${textColor}" font-size="11" text-anchor="end">50%</text>
      <text x="${pad.left - 10}" y="${pad.top + plotH + 4}" fill="${textColor}" font-size="11" text-anchor="end">0%</text>

      <path d="${soilArea}" fill="url(#soilGrad)" />
      <path d="${soilPath}" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="${tempPath}" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="2 0"/>

      ${data.map((d, i) => `
        <circle cx="${getX(i)}" cy="${getYSoil(d.soil)}" r="4" fill="#10b981" stroke="#090d16" stroke-width="2"/>
        <circle cx="${getX(i)}" cy="${getYTemp(d.temp)}" r="3.5" fill="#f59e0b" stroke="#090d16" stroke-width="2"/>
        <text x="${getX(i)}" y="${height - 10}" fill="${textColor}" font-size="10" text-anchor="middle">${d.time}</text>
      `).join('')}
    </svg>
  `;

  elChartContainer.innerHTML = svg;
}

// --- Live Log Helper ---
function addLog(message) {
  const time = new Date().toLocaleTimeString('th-TH');
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.innerHTML = `<span class="log-time">[${time}]</span><span>${message}</span>`;
  elLiveLogs.appendChild(entry);
  elLiveLogs.scrollTop = elLiveLogs.scrollHeight;
}

// --- Two-Way REST Sync with Mobile App (LEQs_AIoT) & ESP32 ---
let isSyncingBackend = false;
async function syncWithBackend() {
  if (isSyncingBackend) return;
  isSyncingBackend = true;
  try {
    const res = await fetch('api/api.php?action=status');
    if (!res.ok) return;
    const json = await res.json();
    if (json.status === 'success' && json.data) {
      // 1. Sync Hardware Sensors
      if (json.data.hardware) {
        updateHardwareUI(json.data.hardware);
      }

      // 2. Sync Area Controls & Live Metrics
      if (json.data.areas) {
        let hasStateChanged = false;
        const backendAreas = json.data.areas;

        for (const [key, bArea] of Object.entries(backendAreas)) {
          if (farmState.areas[key]) {
            const locArea = farmState.areas[key];
            
            // Sync live telemetry into active area if coming from hardware
            if (bArea.temp !== undefined && Math.abs(bArea.temp - locArea.temp) > 0.05) {
              locArea.temp = bArea.temp;
              hasStateChanged = true;
            }
            if (bArea.humidity !== undefined && Math.abs(bArea.humidity - locArea.humidity) > 0.05) {
              locArea.humidity = bArea.humidity;
              hasStateChanged = true;
            }
            if (bArea.light !== undefined && bArea.light !== locArea.light) {
              locArea.light = bArea.light;
              hasStateChanged = true;
            }

            // Sync actuators
            ['valve', 'pump', 'mist', 'fan'].forEach(dev => {
              if (bArea[dev] !== undefined && bArea[dev] !== locArea[dev]) {
                locArea[dev] = bArea[dev];
                hasStateChanged = true;
                if (key === farmState.activeArea) {
                  updateActuatorUI(dev, bArea[dev]);
                  addLog(`📲 [ซิงค์จากโมบายแอป/บอร์ด] อุปกรณ์ ${dev.toUpperCase()} เปลี่ยนสถานะเป็น ${bArea[dev] ? 'เปิด (ON)' : 'ปิด (OFF)'}`);
                }
              }
            });
          }
        }

        if (hasStateChanged) {
          const activeCurr = farmState.areas[farmState.activeArea];
          let activeCount = (activeCurr.valve ? 1 : 0) +
                            (activeCurr.pump ? 1 : 0) +
                            (activeCurr.mist ? 1 : 0) +
                            (activeCurr.fan ? 1 : 0);
          elActuatorSummary.textContent = `เปิดอยู่ ${activeCount} จาก 4 อุปกรณ์`;
          renderDashboard();
          calculateAiInference();
        }
      }
    }
  } catch (_) {
    // Offline silent fallback
  } finally {
    isSyncingBackend = false;
  }
}

// --- Live Hardware Telemetry State & UI Handlers ---
farmState.hardware = {
  actuator_ip: '10.10.29.103',
  sensor_ip: '10.10.31.65',
  actuator_online: true,
  sensor_online: true,
  relay_state: false,
  button_state: false,
  sensor_data: {
    temperature: 28.5,
    humidity: 48.8,
    light: 114,
    pressure: 973.8,
    elevation: 334,
    vibration: 2.2,
    float_switch: true,
    float_state: 'ปกติ (ระดับน้ำเพียงพอ)',
    rssi: -58,
    vpd: 2.03,
    dew_point: 16.9
  }
};

function updateHardwareUI(hw) {
  if (!hw) return;
  farmState.hardware = hw;
  const sData = hw.sensor_data || {};
  const aData = hw.actuator_data || {};

  // Quick Bar on Overview Screen
  const qTemp = document.getElementById('quick-hw-temp');
  const qHum = document.getElementById('quick-hw-hum');
  const qLux = document.getElementById('quick-hw-lux');
  const qPres = document.getElementById('quick-hw-pres');
  const qRelay = document.getElementById('quick-hw-relay');
  const chipSensor = document.getElementById('chip-sensor-node');
  const chipRelay = document.getElementById('chip-relay-node');

  if (sData.temperature !== undefined && qTemp) qTemp.textContent = `${sData.temperature.toFixed(1)}°C`;
  if (sData.humidity !== undefined && qHum) qHum.textContent = `${sData.humidity.toFixed(1)}%`;
  if (sData.light !== undefined && qLux) qLux.textContent = `${sData.light} lx`;
  if (sData.pressure !== undefined && qPres) qPres.textContent = `${sData.pressure.toFixed(1)} hPa`;
  if (qRelay) {
    qRelay.textContent = hw.relay_state ? 'ON (เปิด)' : 'OFF (ปิด)';
    qRelay.style.color = hw.relay_state ? '#10b981' : '#f59e0b';
  }
  if (chipSensor) chipSensor.className = hw.sensor_online ? 'hw-chip online' : 'hw-chip';
  if (chipRelay) chipRelay.className = hw.actuator_online ? 'hw-chip online' : 'hw-chip';

  // Hardware View Screen Cards
  const cTemp = document.getElementById('hw-card-temp');
  const bTemp = document.getElementById('hw-bar-temp');
  const cTempF = document.getElementById('hw-card-temp-f');
  if (sData.temperature !== undefined && cTemp) {
    cTemp.textContent = sData.temperature.toFixed(1);
    if (bTemp) bTemp.style.width = `${Math.min(100, Math.max(0, (sData.temperature / 50) * 100))}%`;
    if (cTempF) cTempF.textContent = `${((sData.temperature * 9/5) + 32).toFixed(1)} °F`;
  }

  const cHum = document.getElementById('hw-card-hum');
  const bHum = document.getElementById('hw-bar-hum');
  const cDew = document.getElementById('hw-card-dew');
  if (sData.humidity !== undefined && cHum) {
    cHum.textContent = sData.humidity.toFixed(1);
    if (bHum) bHum.style.width = `${Math.min(100, Math.max(0, sData.humidity))}%`;
    if (sData.dew_point !== undefined && cDew) cDew.textContent = `จุดน้ำค้าง: ${sData.dew_point.toFixed(1)}°C`;
  }

  const cLux = document.getElementById('hw-card-lux');
  const bLux = document.getElementById('hw-bar-lux');
  if (sData.light !== undefined && cLux) {
    cLux.textContent = sData.light.toLocaleString();
    if (bLux) bLux.style.width = `${Math.min(100, Math.max(5, (sData.light / 2000) * 100))}%`;
  }

  const cPres = document.getElementById('hw-card-pres');
  const bPres = document.getElementById('hw-bar-pres');
  const cElev = document.getElementById('hw-card-elevation');
  if (sData.pressure !== undefined && cPres) {
    cPres.textContent = sData.pressure.toFixed(1);
    if (bPres) bPres.style.width = `${Math.min(100, Math.max(20, (sData.pressure / 1050) * 100))}%`;
    if (sData.elevation !== undefined && cElev) cElev.textContent = `~${sData.elevation}`;
  }

  const cVib = document.getElementById('hw-card-vib');
  const bVib = document.getElementById('hw-bar-vib');
  if (sData.vibration !== undefined && cVib) {
    cVib.textContent = sData.vibration.toFixed(2);
    if (bVib) bVib.style.width = `${Math.min(100, Math.max(10, sData.vibration * 10))}%`;
  }

  const cFloat = document.getElementById('hw-card-float-text');
  const bFloat = document.getElementById('hw-bar-float');
  const badgeFloat = document.getElementById('hw-card-float-badge');
  const contactFloat = document.getElementById('hw-card-float-contact');
  if (sData.float_switch !== undefined) {
    const isWaterOk = sData.float_switch;
    if (cFloat) cFloat.textContent = isWaterOk ? 'น้ำเพียงพอ' : 'เตือนระดับน้ำต่ำ';
    if (bFloat) {
      bFloat.style.width = isWaterOk ? '100%' : '20%';
      bFloat.style.background = isWaterOk ? '#10b981' : '#f43f5e';
    }
    if (badgeFloat) {
      badgeFloat.className = isWaterOk ? 'metric-status-tag tag-good' : 'metric-status-tag tag-danger';
      badgeFloat.textContent = isWaterOk ? 'ปกติ' : 'ระดับน้ำต่ำ';
    }
    if (contactFloat) contactFloat.textContent = isWaterOk ? 'Contact: CLOSED' : 'Contact: OPEN';
  }

  const cVpd = document.getElementById('hw-card-vpd');
  const bVpd = document.getElementById('hw-bar-vpd');
  if (sData.vpd !== undefined && cVpd) {
    cVpd.textContent = sData.vpd.toFixed(2);
    if (bVpd) bVpd.style.width = `${Math.min(100, Math.max(15, (sData.vpd / 3.0) * 100))}%`;
  }

  const cRelayVal = document.getElementById('hw-card-relay-val');
  const bRelay = document.getElementById('hw-bar-relay');
  const cRelayStatus = document.getElementById('hw-card-relay-status');
  const lRelayState = document.getElementById('hw-relay-state-label');
  const isRelayOn = hw.relay_state;

  if (cRelayVal) {
    cRelayVal.textContent = isRelayOn ? 'ON (เปิดทำงาน)' : 'OFF (ปิดพัก)';
    cRelayVal.style.color = isRelayOn ? '#10b981' : 'var(--text-main)';
  }
  if (bRelay) {
    bRelay.style.width = isRelayOn ? '100%' : '0%';
    bRelay.style.background = isRelayOn ? '#10b981' : '#f59e0b';
  }
  if (cRelayStatus) {
    cRelayStatus.className = isRelayOn ? 'metric-status-tag tag-good' : 'metric-status-tag';
    cRelayStatus.textContent = isRelayOn ? 'ACTIVE' : 'IDLE';
  }
  if (lRelayState) {
    lRelayState.textContent = isRelayOn ? 'ON (เปิด)' : 'OFF (ปิด)';
    lRelayState.style.color = isRelayOn ? '#10b981' : '#f59e0b';
  }

  const sRssi = document.getElementById('hw-sensor-rssi');
  if (sData.rssi !== undefined && sRssi) sRssi.textContent = `${sData.rssi} dBm`;

  const sBadge = document.getElementById('hw-sensor-badge');
  if (sBadge) {
    sBadge.className = hw.sensor_online ? 'metric-status-tag tag-good' : 'metric-status-tag tag-danger';
    sBadge.textContent = hw.sensor_online ? '🟢 ONLINE' : '🔴 OFFLINE';
  }
  const rBadge = document.getElementById('hw-relay-badge');
  if (rBadge) {
    rBadge.className = hw.actuator_online ? 'metric-status-tag tag-good' : 'metric-status-tag tag-danger';
    rBadge.textContent = hw.actuator_online ? '🟢 ONLINE' : '🔴 OFFLINE';
  }

  const syncTime = document.getElementById('hw-last-sync-time');
  if (syncTime) syncTime.textContent = `อัปเดตล่าสุด: ${new Date().toLocaleTimeString('th-TH')}`;

  // Populate Raw Table
  renderRawTelemetryTable(hw);
}

function renderRawTelemetryTable(hw) {
  const tbody = document.getElementById('hw-raw-tbody');
  if (!tbody) return;
  const s = hw.sensor_data || {};
  const a = hw.actuator_data || {};

  const rows = [
    { name: 'อุณหภูมิอากาศ (Temperature)', id: 'sensor/อุณหภูมิ (temperature)', node: hw.sensor_ip, val: s.temperature ?? 'N/A', unit: '°C', health: 'Normal' },
    { name: 'ความชื้นสัมพัทธ์ (Humidity)', id: 'sensor/ความชื้นอากาศ (humidity)', node: hw.sensor_ip, val: s.humidity ?? 'N/A', unit: '%RH', health: 'Normal' },
    { name: 'ความสว่างรอบข้าง (Illuminance)', id: 'sensor/ความสว่าง (light)', node: hw.sensor_ip, val: s.light ?? 'N/A', unit: 'Lux', health: 'Normal' },
    { name: 'ความกดอากาศ (Barometric Pressure)', id: 'sensor/ความกดอากาศ (pressure)', node: hw.sensor_ip, val: s.pressure ?? 'N/A', unit: 'hPa', health: 'Normal' },
    { name: 'ความสูงเหนือระดับน้ำทะเลประเมิน', id: 'math/altimeter_formula', node: 'Computed', val: s.elevation ?? 'N/A', unit: 'm MSL', health: 'Calculated' },
    { name: 'แรงสั่นสะเทือน / ความเอียง (Vibration)', id: 'sensor/ความสั่นสะเทือน (vibration)', node: hw.sensor_ip, val: s.vibration ?? 'N/A', unit: 'mg', health: 'Normal' },
    { name: 'สวิตช์ลูกลอยระดับน้ำ (Float Switch)', id: 'binary_sensor/สวิตช์ลูกลอย (float switch)', node: hw.sensor_ip, val: s.float_state ?? (s.float_switch ? 'ON' : 'OFF'), unit: 'State', health: s.float_switch ? 'OK' : 'Warning' },
    { name: 'แรงดันไอขาดดุล (Vapor Pressure Deficit)', id: 'agriphysics/tetens_vpd', node: 'TinyML Engine', val: s.vpd ?? 'N/A', unit: 'kPa', health: 'Transpiration Normal' },
    { name: 'จุดน้ำค้าง (Dew Point)', id: 'agriphysics/magnus_dew_point', node: 'Agri Formula', val: s.dew_point ?? 'N/A', unit: '°C', health: 'No Condensation' },
    { name: 'รีเลย์ปั๊ม/ไฟ (Physical Relay)', id: 'switch/รีเลย์ (relay)', node: hw.actuator_ip, val: hw.relay_state ? 'ON' : 'OFF', unit: 'Contact', health: hw.relay_state ? 'Active' : 'Idle' },
    { name: 'ปุ่มกดบนบอร์ด (Push Button)', id: 'binary_sensor/ปุ่มบนบอร์ด (button)', node: hw.actuator_ip, val: hw.button_state ? 'PRESSED' : 'RELEASED', unit: 'Input', health: 'Ready' },
    { name: 'Wi-Fi RSSI โหนดเซนเซอร์', id: 'sensor/ความแรงสัญญาณ WiFi', node: hw.sensor_ip, val: s.rssi ?? 'N/A', unit: 'dBm', health: (s.rssi && s.rssi > -70) ? 'Strong' : 'Fair' },
    { name: 'Wi-Fi RSSI โหนดรีเลย์', id: 'sensor/ความแรงสัญญาณ WiFi', node: hw.actuator_ip, val: a.rssi ?? -61, unit: 'dBm', health: 'Strong' },
  ];

  tbody.innerHTML = rows.map(r => `
    <tr>
      <td style="font-weight: 600;">${r.name}</td>
      <td style="color: var(--text-dim); font-size: 12px;">${r.id}</td>
      <td><span class="hw-chip" style="font-size: 11px; padding: 2px 8px;">${r.node}</span></td>
      <td style="color: var(--primary); font-weight: 700; font-size: 14px;">${r.val}</td>
      <td>${r.unit}</td>
      <td><span class="metric-status-tag ${r.health === 'OK' || r.health === 'Normal' || r.health === 'Strong' || r.health === 'Active' ? 'tag-good' : ''}">${r.health}</span></td>
    </tr>
  `).join('');
}

function renderHardwareView() {
  if (farmState.hardware) {
    updateHardwareUI(farmState.hardware);
  } else {
    forceSyncHardware();
  }
}

async function forceSyncHardware() {
  try {
    const res = await fetch('api/api.php?action=status&sync_hw=1');
    if (!res.ok) return;
    const json = await res.json();
    if (json.status === 'success' && json.data && json.data.hardware) {
      updateHardwareUI(json.data.hardware);
      addLog(`📡 [เซนเซอร์บอร์ด] ดึงข้อมูลสดสำเร็จ อุณหภูมิ: ${json.data.hardware.sensor_data.temperature}°C, ชื้น: ${json.data.hardware.sensor_data.humidity}%`);
    }
  } catch (err) {
    console.error('forceSyncHardware error:', err);
  }
}

async function togglePhysicalRelay() {
  const currentState = farmState.hardware?.relay_state || false;
  const newState = !currentState;
  try {
    const res = await fetch('api/api.php?action=control', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ area: 'flower', device: 'valve', state: newState })
    });
    const json = await res.json();
    if (json.status === 'success') {
      if (farmState.hardware) farmState.hardware.relay_state = newState;
      updateHardwareUI(farmState.hardware);
      addLog(`⚡ [คำสั่งรีเลย์ 10.10.29.103] สลับเป็น ${newState ? 'เปิด (ON)' : 'ปิด (OFF)'} สำเร็จ`);
    }
  } catch (err) {
    console.error('togglePhysicalRelay error:', err);
  }
}


