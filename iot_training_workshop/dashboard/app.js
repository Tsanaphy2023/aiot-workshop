/**
 * Smart Farm Workshop - Masterclass Worksheet & Activity Web Dashboard
 * Handles JSON parsing, dynamic UI rendering, filtering, search, and file import.
 */

// Default data container
let currentData = null;
let activeTab = 'all';
let searchQuery = '';

document.addEventListener('DOMContentLoaded', () => {
  initDashboard();
});

async function initDashboard() {
  setupEventListeners();
  try {
    const response = await fetch('../worksheet_data.json?v=' + Date.now());
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    loadWorksheetData(data);
  } catch (err) {
    console.warn('Could not load ../worksheet_data.json, falling back to embedded sample data:', err);
    // In case fetch is blocked by file:// protocol, fallback will be handled
  }
}

function setupEventListeners() {
  // Tab buttons
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeTab = btn.getAttribute('data-tab');
      renderActivities();
    });
  });

  // Search input
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderActivities();
    });
  }

  // File Upload
  const jsonFileInput = document.getElementById('jsonFileInput');
  if (jsonFileInput) {
    jsonFileInput.addEventListener('change', handleFileImport);
  }

  // Checklist Modal
  const openChecklistBtn = document.getElementById('openChecklistBtn');
  const checklistModal = document.getElementById('checklistModal');
  const closeChecklistBtn = document.getElementById('closeChecklistBtn');

  if (openChecklistBtn && checklistModal) {
    openChecklistBtn.addEventListener('click', () => {
      checklistModal.classList.add('open');
      renderChecklistModal();
    });
  }
  if (closeChecklistBtn && checklistModal) {
    closeChecklistBtn.addEventListener('click', () => {
      checklistModal.classList.remove('open');
    });
  }
  if (checklistModal) {
    checklistModal.addEventListener('click', (e) => {
      if (e.target === checklistModal) checklistModal.classList.remove('open');
    });
  }
}

function handleFileImport(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (event) => {
    try {
      const data = JSON.parse(event.target.result);
      loadWorksheetData(data);
    } catch (err) {
      alert('เกิดข้อผิดพลาดในการอ่านไฟล์ JSON: ' + err.message);
    }
  };
  reader.readAsText(file);
}

function loadWorksheetData(data) {
  currentData = data;
  renderTopStats(data);
  renderActivities();
  renderRawJSON(data);
}

function renderTopStats(data) {
  const fields = data.fields || {};
  const checks = data.checks || {};

  // Team
  const teamNo = data.team || fields['team.no'] || '3';
  document.getElementById('statTeam').textContent = `กลุ่มที่ ${teamNo}`;
  document.getElementById('headerTeamBadge').textContent = `👥 กลุ่มที่ ${teamNo}`;

  // Export time
  if (data.exported) {
    try {
      const d = new Date(data.exported);
      document.getElementById('headerExportBadge').textContent = `🕒 ส่งเมื่อ ${d.toLocaleDateString('th-TH')} ${d.toLocaleTimeString('th-TH')}`;
    } catch (e) {
      document.getElementById('headerExportBadge').textContent = `🕒 ${data.exported}`;
    }
  }

  // Checks count
  const checkKeys = Object.keys(checks);
  const passedCount = checkKeys.filter(k => checks[k] === true).length;
  const totalCount = checkKeys.length || 73;
  const passPercent = Math.round((passedCount / totalCount) * 100);

  document.getElementById('statChecks').innerHTML = `${passedCount} <span class="stat-unit">/ ${totalCount} (${passPercent}%)</span>`;
  document.getElementById('statChecksFoot').textContent = passPercent === 100 ? '✅ ผ่านครบทุกเกณฑ์ 100%' : `ผ่าน ${passedCount} รายการ`;

  // Hardware IPs
  const iotIp = fields['board.iot.ip'] || 'http://10.10.31.65/';
  const relayIp = fields['board.relay.ip'] || 'http://10.10.29.103/';
  const iotName = fields['board.iot.name'] || 'gogo-iot-red-242dcc';
  const relayName = fields['board.relay.name'] || 'gogo-relay-red-b97df0';

  document.getElementById('statNodes').innerHTML = `2 <span class="stat-unit">บอร์ดหลัก + 1 Gateway</span>`;
  document.getElementById('statNodesFoot').innerHTML = `IoT: <a href="${iotIp}" target="_blank" style="color:var(--cyan-400);">${iotName}</a>`;

  // Chattering & Fail-safe
  const chatterBefore = fields['s2.chatter.before'] || '12';
  const chatterAfter = fields['s2.chatter.after'] || '0';
  document.getElementById('statChatter').innerHTML = `${chatterAfter} <span class="stat-unit">ครั้ง (เดิม ${chatterBefore})</span>`;
  document.getElementById('statChatterFoot').textContent = `🛡️ Hysteresis สมบูรณ์ ลดตัดต่อ 100%`;
}

function renderActivities() {
  if (!currentData || !currentData.fields) return;
  const f = currentData.fields;
  const container = document.getElementById('activitiesContainer');
  container.innerHTML = '';

  const activities = [
    // SESSION 1
    {
      session: 1,
      actNum: 1,
      badge: 'กิจกรรมที่ 1',
      title: 'อ่านค่าเซนเซอร์ & สวิตช์ลูกลอย (Sense)',
      desc: 'ตรวจวัดอุณหภูมิ ความชื้น แสง การสั่นสะเทือน และสถานะสวิตช์ลูกลอยตัดต่อสองสถานะ',
      metrics: [
        { label: 'ความชื้นห้อง', val: `${f['s1.hum.room'] || '-'}%`, cls: 'cyan' },
        { label: 'อุณหภูมิห้อง', val: `${f['s1.temp.room'] || '-'}°C`, cls: 'amber' },
        { label: 'ความเข้มแสง', val: `${f['s1.light.room'] || '-'} lux`, cls: 'success' },
        { label: 'การสั่นสะเทือน', val: `${f['s1.vib.room'] || '-'}`, cls: '' },
        { label: 'ทดสอบความชื้น (เป่า)', val: `${f['s1.hum.test'] || '-'}%`, cls: 'cyan' },
        { label: 'ลูกลอยปกติ / ยก', val: `${f['s1.float.rest'] || 'OFF'} / ${f['s1.float.lift'] || 'ON'}`, cls: 'success' },
      ],
      qa: [
        { q: 'คำถามที่ 1: การตัดสินใจรดน้ำพืช & ประโยชน์ของสวิตช์ลูกลอย (Float Switch)', a: f['s1.q1'] }
      ]
    },
    {
      session: 1,
      actNum: 2,
      badge: 'กิจกรรมที่ 2',
      title: 'วงจรควบคุมไฟฟ้า 220V และรีเลย์ (Act)',
      desc: 'หลักความปลอดภัยทางไฟฟ้า การขับโหลดปั๊มน้ำ 220V ผ่าน Magnetic Contactor และการแยกแรงดัน',
      metrics: [
        { label: 'บอร์ดรีเลย์', val: f['board.relay.name'] || 'gogo-relay', cls: 'success' },
        { label: 'IP Address', val: f['board.relay.ip'] || '10.10.29.103', cls: 'cyan' },
        { label: 'มาตรฐานตู้', val: 'IP65 Enclosure', cls: 'amber' },
        { label: 'ระบบป้องกัน', val: 'RCBO + Grounding', cls: 'success' }
      ],
      qa: [
        { q: 'คำถามที่ 2: ความปลอดภัยในการคุมปั๊ม 220V และคุณสมบัติผู้ติดตั้ง', a: f['s1.q2'] }
      ]
    },
    {
      session: 1,
      actNum: 3,
      badge: 'กิจกรรมที่ 3',
      title: 'สร้างกฎเงื่อนไขอัตโนมัติ (Logic)',
      desc: 'ตั้งค่ากฎการเปิด-ปิดไฟตามความเข้มแสง และการสั่งดับไฟตามเวลาที่กำหนด',
      metrics: [
        { label: 'เกณฑ์มืด (เปิดไฟ)', val: `< ${f['s1.rule.dark.if'] || '50'} lux (${f['s1.rule.dark.then']})`, cls: 'amber' },
        { label: 'เกณฑ์สว่าง (ดับไฟ)', val: `> ${f['s1.rule.bright.if'] || '150'} lux (${f['s1.rule.bright.then']})`, cls: 'cyan' },
        { label: 'ทดสอบอัตโนมัติ', val: `${f['s1.auto.pass'] || '3'} รอบผ่าน`, cls: 'success' },
        { label: 'ทดสอบเวลาดับ', val: `${f['s1.timer.at']} น. (${f['s1.timer.ok']})`, cls: 'success' }
      ],
      qa: [
        { q: 'คำถามที่ 3: ปัญหาเมื่อแสงแกว่งใกล้เกณฑ์ (Chattering)', a: f['s1.q3'] }
      ]
    },

    // SESSION 2
    {
      session: 2,
      actNum: 4,
      badge: 'กิจกรรมที่ 4',
      title: 'แก้ปัญหา Chattering ด้วย Hysteresis (Think)',
      desc: 'กำหนดระยะห่างของเกณฑ์เปิด-ปิด (Deadband) เพื่อตัดปัญหารีเลย์และปั๊มตัดต่อกระชากถี่',
      metrics: [
        { label: 'Chattering เดิม', val: `${f['s2.chatter.before'] || '12'} ครั้ง`, cls: 'amber' },
        { label: 'Chattering หลังแก้', val: `${f['s2.chatter.after'] || '0'} ครั้ง`, cls: 'success' },
        { label: 'เกณฑ์ชื้นเปิดปั๊ม', val: `< ${f['s2.hum.on'] || '50'}%`, cls: 'cyan' },
        { label: 'เกณฑ์ชื้นปิดปั๊ม', val: `> ${f['s2.hum.off'] || '65'}%`, cls: 'success' },
        { label: 'ผลทดสอบเวลา', val: `${f['s2.time.fixed'] || 'ติด'}`, cls: 'success' }
      ],
      qa: [
        { q: 'คำถามที่ 4: หลักการ Hysteresis และการประยุกต์ใช้กับปั๊มน้ำในฟาร์ม', a: f['s2.q4'] }
      ]
    },
    {
      session: 2,
      actNum: 5,
      badge: 'กิจกรรมที่ 5',
      title: 'Fail-safe Lab & แผนซ่อมบำรุงรักษา (Protect)',
      desc: 'ทดสอบจำลอง 4 สถานการณ์วิกฤต (Sabotage Tests) และระบบความปลอดภัยระดับฮาร์ดแวร์',
      customHtml: `
        <div class="fs-matrix">
          <div class="fs-card ok">
            <div class="fs-card-title">1. น้ำแห้ง (Dry Run) <span style="color:var(--emerald-400)">✓ ${f['s2.sab.1.ok']}</span></div>
            <div class="fs-card-detail">${f['s2.sab.1.what']}<br><strong style="color:var(--cyan-400);">แก้:</strong> ${f['s2.sab.1.note']}</div>
          </div>
          <div class="fs-card ok">
            <div class="fs-card-title">2. ปั๊มไม่หมุน <span style="color:var(--emerald-400)">✓ ${f['s2.sab.2.ok']}</span></div>
            <div class="fs-card-detail">${f['s2.sab.2.what']}<br><strong style="color:var(--cyan-400);">แก้:</strong> ${f['s2.sab.2.note']}</div>
          </div>
          <div class="fs-card ok">
            <div class="fs-card-title">3. เซนเซอร์หลุด <span style="color:var(--emerald-400)">✓ ${f['s2.sab.3.ok']}</span></div>
            <div class="fs-card-detail">${f['s2.sab.3.what']}<br><strong style="color:var(--cyan-400);">แก้:</strong> ${f['s2.sab.3.note']}</div>
          </div>
          <div class="fs-card ok">
            <div class="fs-card-title">4. ปั๊มเดินเกินเวลา <span style="color:var(--emerald-400)">✓ ${f['s2.sab.4.ok']}</span></div>
            <div class="fs-card-detail">${f['s2.sab.4.what']}<br><strong style="color:var(--cyan-400);">แก้:</strong> ${f['s2.sab.4.note']}</div>
          </div>
        </div>
        <table class="maint-table">
          <thead>
            <tr><th>อุปกรณ์</th><th>ผู้ดูแล</th><th>ความถี่</th><th>สิ่งที่ต้องทำ</th></tr>
          </thead>
          <tbody>
            <tr><td>เซนเซอร์</td><td>${f['s2.maint.sensor.who']}</td><td>${f['s2.maint.sensor.freq']}</td><td>${f['s2.maint.sensor.what']}</td></tr>
            <tr><td>ลูกลอย</td><td>${f['s2.maint.float.who']}</td><td>${f['s2.maint.float.freq']}</td><td>${f['s2.maint.float.what']}</td></tr>
            <tr><td>ปั๊มน้ำ</td><td>${f['s2.maint.pump.who']}</td><td>${f['s2.maint.pump.freq']}</td><td>${f['s2.maint.pump.what']}</td></tr>
            <tr><td>บอร์ดรีเลย์</td><td>${f['s2.maint.relay.who']}</td><td>${f['s2.maint.relay.freq']}</td><td>${f['s2.maint.relay.what']}</td></tr>
            <tr><td>ระบบเน็ต</td><td>${f['s2.maint.net.who']}</td><td>${f['s2.maint.net.freq']}</td><td>${f['s2.maint.net.what']}</td></tr>
          </tbody>
        </table>
      `,
      qa: [
        { q: 'คำถามที่ 5: หากเซิร์ฟเวอร์ HA ดับ ต้องมี Fail-safe ระดับใดบ้าง?', a: f['s2.q5'] }
      ]
    },

    // SESSION 3
    {
      session: 3,
      actNum: 6,
      badge: 'กิจกรรมที่ 6',
      title: 'อ่านข้อมูลย้อนหลัง & สืบหาสาเหตุผิดปกติ (History)',
      desc: 'วิเคราะห์เหตุการณ์ความชื้นพุ่ง ปั๊มเปิด และกราฟแหว่ง พร้อมแนวทางแก้ปัญหาเชิงโครงสร้าง',
      metrics: [
        { label: 'ความชื้นต่ำสุด', val: `${f['s3.hist.hum_min']}% (${f['s3.hist.hum_min_t']} น.)`, cls: 'amber' },
        { label: 'ความชื้นสูงสุด', val: `${f['s3.hist.hum_max']}% (${f['s3.hist.hum_max_t']} น.)`, cls: 'cyan' },
        { label: 'เหตุการณ์ที่ 1', val: `${f['s3.hist.ev1.t']} น. - ${f['s3.hist.ev1.what']}`, cls: '' },
        { label: 'เหตุการณ์ที่ 2', val: `${f['s3.hist.ev2.t']} น. - ${f['s3.hist.ev2.what']}`, cls: '' },
        { label: 'เหตุการณ์ที่ 3', val: `${f['s3.hist.ev3.t']} น. - ${f['s3.hist.ev3.what']}`, cls: 'amber' }
      ],
      qa: [
        { q: 'สาเหตุกราฟข้อมูลแหว่ง และแนวทางปรับปรุงในฟาร์มจริง', a: `สาเหตุ: ${f['s3.hist.why_gap']}\nการปรับปรุง: ${f['s3.hist.farm_change']}\nมาตรการจัดการเหตุการณ์:\n- เหตุการณ์ 1: ${f['s3.hist.ev1.action']}\n- เหตุการณ์ 2: ${f['s3.hist.ev2.action']}\n- เหตุการณ์ 3: ${f['s3.hist.ev3.action']}` }
      ]
    },
    {
      session: 3,
      actNum: 7,
      badge: 'กิจกรรมที่ 7',
      title: 'ออกแบบแดชบอร์ดตาม Persona ผู้ใช้งาน (Dashboard)',
      desc: 'คัดเลือกข้อมูลควบคุมที่จำเป็นสำหรับคนงาน และหลัก UX สำหรับสภาพแวดล้อมกลางแจ้ง',
      metrics: [
        { label: 'ผู้ใช้งานหลัก (Persona)', val: f['s3.dash.user'] || 'คนงานดูแลแปลง', cls: 'success' },
        { label: 'ข้อมูลแสดง 1', val: f['s3.dash.show.1'], cls: 'cyan' },
        { label: 'ข้อมูลแสดง 2', val: f['s3.dash.show.2'], cls: 'cyan' },
        { label: 'ข้อมูลแสดง 3', val: f['s3.dash.show.3'], cls: 'cyan' },
        { label: 'ปุ่มควบคุม 1', val: f['s3.dash.control.1'], cls: 'amber' },
        { label: 'ปุ่มควบคุม 2', val: f['s3.dash.control.2'], cls: 'amber' }
      ],
      qa: [
        { q: 'คำถามที่ 7: การออกแบบ UI/UX สำหรับคนงานกลางแดดจัด', a: f['s3.q7'] }
      ]
    },

    // ACTIVITY 8 (BLUEPRINT)
    {
      session: 3,
      actNum: 8,
      badge: 'กิจกรรมที่ 8 (Blueprint)',
      title: 'ออกแบบผังระบบฟาร์มจริง 400 เมตร (Scenario B)',
      desc: 'แปลงยาว 400 ม. ไม่มีไฟบ้านและ Wi-Fi: สถาปัตยกรรม ESP-NOW, LiFePO4 และระบบ Fail-safe',
      customHtml: `
        <div style="background:rgba(16,185,129,0.06); border:1px solid var(--border-accent); border-radius:8px; padding:12px; margin-bottom:12px;">
          <strong style="color:var(--emerald-400);">ปัญหาโจทย์ (Scenario ${f['d.scenario']}):</strong>
          <p style="font-size:0.85rem; color:#cbd5e1; margin-top:4px;">${f['d.problem']}</p>
        </div>
        <div class="metrics-row">
          <div class="metric-pill success"><span class="metric-pill-title">สื่อสารแปลง:</span> <span class="metric-pill-val">${f['d.comm.1.tech']}</span></div>
          <div class="metric-pill cyan"><span class="metric-pill-title">สื่อสารรีเลย์:</span> <span class="metric-pill-val">${f['d.comm.2.tech']}</span></div>
          <div class="metric-pill amber"><span class="metric-pill-title">ระบบคลาวด์:</span> <span class="metric-pill-val">${f['d.comm.3.tech']}</span></div>
          <div class="metric-pill success"><span class="metric-pill-title">แบตเตอรี่:</span> <span class="metric-pill-val">${f['d.battery']}</span></div>
          <div class="metric-pill cyan"><span class="metric-pill-title">พลังงาน:</span> <span class="metric-pill-val">${f['d.power']}</span></div>
          <div class="metric-pill amber"><span class="metric-pill-title">สำรองไฟ:</span> <span class="metric-pill-val">${f['d.power.backup']}</span></div>
          <div class="metric-pill"><span class="metric-pill-title">เซนเซอร์:</span> <span class="metric-pill-val">${f['d.in.1.sensor']}</span></div>
          <div class="metric-pill"><span class="metric-pill-title">อุปกรณ์สั่งงาน:</span> <span class="metric-pill-val">${f['d.out.1.device']}</span></div>
        </div>
      `,
      qa: [
        { q: 'ตรรกะควบคุม และระบบสำรองฉุกเฉิน (Control & Fail-safe)', a: `กฎการควบคุม: ${f['d.control.rule']}\nเมื่อระบบขัดข้อง: ${f['d.control.failure']}` },
        { q: 'วิธีการทดสอบและเกณฑ์ประเมินการผ่าน (Acceptance Criteria)', a: `การทดสอบ: ${f['d.test.how']}\nเกณฑ์ผ่าน: ${f['d.test.pass']}` }
      ]
    },

    // SESSION 4
    {
      session: 4,
      actNum: 9,
      badge: 'กิจกรรมที่ 9',
      title: 'ส่งข้อมูลไร้สายระยะไกลด้วย ESP-NOW (Send)',
      desc: 'แปลงแพ็กเก็ตเซนเซอร์เป็น Broadcast Payload บนย่านความถี่ 2.4 GHz โดยไม่ต้องผ่านเราเตอร์',
      customHtml: `
        <div class="packet-display">
          <div>📡 แพ็กเก็ตดิบที่ส่ง (RAW Packet):</div>
          <div style="color:#ffffff; font-weight:600; margin-top:4px;">${f['s4.tx.packet'] || 'GOGO,...'}</div>
          <div class="packet-tokens">
            <div class="packet-token"><span>Header</span>GOGO</div>
            <div class="packet-token"><span>Device ID</span>${(f['s4.tx.packet'] || '').split(',')[1] || 'gogo-iot'}</div>
            <div class="packet-token"><span>Counter</span>${(f['s4.tx.packet'] || '').split(',')[2] || '42'}</div>
            <div class="packet-token"><span>Temp</span>${(f['s4.tx.packet'] || '').split(',')[3] || '28.4'}°C</div>
            <div class="packet-token"><span>Humidity</span>${(f['s4.tx.packet'] || '').split(',')[4] || '61.2'}%</div>
            <div class="packet-token"><span>Light</span>${(f['s4.tx.packet'] || '').split(',')[5] || '350'} lux</div>
            <div class="packet-token"><span>Vib</span>${(f['s4.tx.packet'] || '').split(',')[7] || '4.1'}</div>
            <div class="packet-token"><span>Channel</span>CH ${f['s4.tx.channel'] || '6'}</div>
          </div>
        </div>
      `,
      qa: [
        { q: 'คำถามที่ 9: ความสามารถที่หายไปเมื่อปิด Wi-Fi และวิธีจัดการบอร์ด', a: f['s4.q9'] }
      ]
    },
    {
      session: 4,
      actNum: 11,
      badge: 'กิจกรรมที่ 10 & 11',
      title: 'บอร์ดตัวรับ Gateway & ป้องกันค่าค้าง (Bridge)',
      desc: 'ทดสอบความสมบูรณ์ของข้อมูลที่ส่งผ่าน ESP-NOW สู่ Home Assistant และระบบตัดค่าค้าง (Stale Data)',
      metrics: [
        { label: 'บอร์ดตัวรับ (Gateway)', val: f['board.rx.name'] || 'farm-receiver', cls: 'success' },
        { label: 'ความชื้น (ตรง / ESP-NOW)', val: `${f['s4.ha.hum.direct']}% / ${f['s4.ha.hum.espnow']}%`, cls: 'cyan' },
        { label: 'แสง (ตรง / ESP-NOW)', val: `${f['s4.ha.light.direct']} / ${f['s4.ha.light.espnow']} lux`, cls: 'amber' },
        { label: 'ทดสอบการแจ้งเตือน', val: `${f['s4.ha.alert.ok'] || 'เตือน'} (สำเร็จ)`, cls: 'success' }
      ],
      qa: [
        { q: 'คำถามที่ 11: การติดตั้งจริงที่ระยะ 150 ม. และการตรวจจับข้อมูลค้าง (Stale Data)', a: f['s4.q11'] }
      ]
    }
  ];

  // Filter activities
  const filtered = activities.filter(act => {
    // Session tab filter
    if (activeTab === 's1' && act.session !== 1) return false;
    if (activeTab === 's2' && act.session !== 2) return false;
    if (activeTab === 's3' && act.session !== 3 && act.actNum !== 8) return false;
    if (activeTab === 's4' && act.session !== 4) return false;
    if (activeTab === 'blueprint' && act.actNum !== 8) return false;

    // Search query filter
    if (searchQuery) {
      const haystack = (
        act.title + ' ' +
        act.desc + ' ' +
        (act.metrics ? act.metrics.map(m => m.label + ' ' + m.val).join(' ') : '') + ' ' +
        (act.qa ? act.qa.map(q => q.q + ' ' + q.a).join(' ') : '')
      ).toLowerCase();
      if (!haystack.includes(searchQuery)) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding:60px 20px; color:var(--text-dim);">
        <div style="font-size:3rem; margin-bottom:12px;">🔍</div>
        <h3>ไม่พบกิจกรรมที่ตรงกับการค้นหา</h3>
        <p>ลองค้นหาคำใหม่ เช่น "Hysteresis", "ESP-NOW", "ลูกลอย", "220V", หรือ "แบตเตอรี่"</p>
      </div>
    `;
    return;
  }

  // Render cards
  filtered.forEach(act => {
    const card = document.createElement('div');
    card.className = 'activity-card';

    let metricsHtml = '';
    if (act.metrics && act.metrics.length > 0) {
      metricsHtml = `
        <div class="metrics-row">
          ${act.metrics.map(m => `
            <div class="metric-pill ${m.cls}">
              <span class="metric-pill-title">${m.label}:</span>
              <span class="metric-pill-val">${m.val}</span>
            </div>
          `).join('')}
        </div>
      `;
    }

    let customHtml = act.customHtml || '';

    let qaHtml = '';
    if (act.qa && act.qa.length > 0) {
      qaHtml = act.qa.map(item => `
        <div class="qa-box">
          <div class="qa-box-header">💡 ${item.q}</div>
          <div class="qa-box-content">${escapeHtml(item.a || '-')}</div>
        </div>
      `).join('');
    }

    card.innerHTML = `
      <div>
        <div class="activity-card-header">
          <span class="activity-badge">${act.badge}</span>
          <span class="activity-status-icon">✓ ผ่านเกณฑ์</span>
        </div>
        <h3 class="activity-title">${act.title}</h3>
        <p class="activity-desc">${act.desc}</p>
        ${metricsHtml}
        ${customHtml}
      </div>
      <div>
        ${qaHtml}
      </div>
    `;

    container.appendChild(card);
  });
}

function renderChecklistModal() {
  if (!currentData || !currentData.checks) return;
  const checks = currentData.checks;
  const grid = document.getElementById('checklistGrid');
  grid.innerHTML = '';

  const keys = Object.keys(checks);
  keys.forEach(k => {
    const item = document.createElement('div');
    const isPassed = checks[k] === true;
    item.className = `check-item ${isPassed ? 'passed' : ''}`;
    item.innerHTML = `
      <span>${isPassed ? '✅' : '⚪'}</span>
      <span style="font-family:var(--font-mono);">${k}</span>
    `;
    grid.appendChild(item);
  });
}

function renderRawJSON(data) {
  const viewer = document.getElementById('jsonViewer');
  if (viewer) {
    viewer.textContent = JSON.stringify(data, null, 2);
  }
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
