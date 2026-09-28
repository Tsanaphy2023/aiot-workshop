/**
 * ESPHome Web Auto-Sync & Web Serial Detection Module
 * Deep+ Precision AgriTech / CMU AIoT 2027
 *
 * Provides:
 * 1. BroadcastChannel cross-tab synchronization with https://web.esphome.io/
 * 2. Direct Web Serial USB one-click Auto-Detect (reads DEVICE NAME and IP ADDRESS)
 * 3. Bookmarklet script generation for https://web.esphome.io/
 */

(function () {
  'use strict';

  // 1. Cross-Tab Sync via BroadcastChannel
  const CHANNEL_NAME = 'esphome_device_sync';
  let syncChannel = null;
  try {
    syncChannel = new BroadcastChannel(CHANNEL_NAME);
  } catch (e) {
    console.warn('[ESPHome Sync] BroadcastChannel not supported in this environment');
  }

  function showToast(msg, isSuccess = true) {
    let toast = document.getElementById('esphome-sync-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'esphome-sync-toast';
      toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 99999;
        padding: 12px 20px;
        border-radius: 10px;
        font-family: 'Prompt', -apple-system, sans-serif;
        font-size: 0.95rem;
        font-weight: 600;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 90vw;
      `;
      document.body.appendChild(toast);
    }
    toast.style.background = isSuccess ? '#1b5e20' : '#c62828';
    toast.style.color = '#ffffff';
    toast.style.border = isSuccess ? '1.5px solid #4caf50' : '1.5px solid #ef5350';
    toast.innerHTML = (isSuccess ? '⚡ ' : '⚠️ ') + msg;
    toast.style.transform = 'translateY(0)';
    toast.style.opacity = '1';

    setTimeout(() => {
      toast.style.transform = 'translateY(20px)';
      toast.style.opacity = '0';
    }, 4500);
  }

  function applyDetectedData(name, ip) {
    let applied = false;

    // Detect target fields based on current page
    const isAct1 = window.location.pathname.includes('activity-1') || document.querySelector('input[data-k="board.iot.name"]');
    const isAct2 = window.location.pathname.includes('activity-2') || document.querySelector('input[data-k="board.relay.name"]');

    let nameKeys = [];
    let ipKeys = [];

    if (isAct1) {
      nameKeys.push('board.iot.name');
      ipKeys.push('board.iot.ip');
    }
    if (isAct2) {
      nameKeys.push('board.relay.name');
      ipKeys.push('board.relay.ip');
    }
    // General fallbacks
    nameKeys.push('board.name', 'device.name');
    ipKeys.push('board.ip', 'device.ip');

    // Fill inputs
    if (name) {
      nameKeys.forEach(k => {
        document.querySelectorAll(`input[data-k="${k}"]`).forEach(el => {
          el.value = name;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          el.style.backgroundColor = '#e8f5e9';
          setTimeout(() => { el.style.backgroundColor = ''; }, 2000);
          applied = true;
        });
      });
    }

    if (ip) {
      ipKeys.forEach(k => {
        document.querySelectorAll(`input[data-k="${k}"]`).forEach(el => {
          el.value = ip;
          el.dispatchEvent(new Event('input', { bubbles: true }));
          el.dispatchEvent(new Event('change', { bubbles: true }));
          el.style.backgroundColor = '#e8f5e9';
          setTimeout(() => { el.style.backgroundColor = ''; }, 2000);
          applied = true;
        });
      });
    }

    // In Simulator (if present)
    const boardIpEl = document.getElementById('bridgeBoardIp');
    if (boardIpEl && ip) {
      boardIpEl.innerText = ip;
      applied = true;
    }
    const wsInputEl = document.getElementById('wsServerUrl');
    if (wsInputEl && ip && (wsInputEl.value.includes('localhost') || wsInputEl.value.includes('0.0.0.0'))) {
      wsInputEl.value = `ws://${ip}:8765`;
    }

    if (applied) {
      showToast(`ดึงข้อมูลสำเร็จ: <b>${name || ''}</b> (IP: <b>${ip || ''}</b>) กรอกลงใบงานอัตโนมัติแล้ว!`);
    }

    return applied;
  }

  // Listen to cross-tab broadcast from web.esphome.io
  if (syncChannel) {
    syncChannel.onmessage = function (event) {
      if (event.data && (event.data.name || event.data.ip)) {
        console.log('[ESPHome Sync] Received cross-tab device info:', event.data);
        applyDetectedData(event.data.name, event.data.ip);
      }
    };
  }

  // 2. Direct Web Serial USB Auto-Detect
  async function connectUsbAutoDetect(btn) {
    if (!navigator.serial) {
      alert('เบราว์เซอร์นี้ยังไม่รองรับ Web Serial API กรุณาเปิดด้วย Google Chrome หรือ Microsoft Edge');
      return;
    }

    const origText = btn ? btn.innerHTML : '';
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⌛ กำลังเลือกพอร์ต USB...';
    }

    let port = null;
    try {
      port = await navigator.serial.requestPort();
    } catch (e) {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origText;
      }
      return; // User cancelled
    }

    try {
      if (btn) btn.innerHTML = '⚡ กำลังรีเซ็ตและอ่าน Log บอร์ด...';
      showToast('กำลังเชื่อมต่อพอร์ต USB และฟังข้อความจากบอร์ด ESPHome...');

      await port.open({ baudRate: 115200 });

      // Reset ESP32 via DTR/RTS signals
      await port.setSignals({ dataTerminalReady: false, requestToSend: true });
      await new Promise(r => setTimeout(r, 120));
      await port.setSignals({ dataTerminalReady: false, requestToSend: false });

      const textDecoder = new TextDecoderStream();
      const readableClosed = port.readable.pipeTo(textDecoder.writable);
      const reader = textDecoder.readable.getReader();

      let logBuffer = '';
      let detectedName = null;
      let detectedIp = null;
      const startTime = Date.now();
      const timeoutMs = 25000; // Wait up to 25s for Wi-Fi connection IP

      while (Date.now() - startTime < timeoutMs) {
        const readPromise = reader.read();
        const timeoutPromise = new Promise(r => setTimeout(() => r({ value: null, done: false }), 2000));
        const res = await Promise.race([readPromise, timeoutPromise]);

        if (res && res.value) {
          logBuffer += res.value;

          // Parse Name
          if (!detectedName) {
            const m = logBuffer.match(/DEVICE NAME:\s*([a-zA-Z0-9_\-]+)/i)
              || logBuffer.match(/(?:Device Name|Hostname):\s*'?([a-zA-Z0-9_\-]+)'?/i)
              || logBuffer.match(/(gogo-(?:relay|iot)-(?:red|green|blue)-[a-zA-Z0-9]+)/i);
            if (m) {
              detectedName = m[1];
              showToast(`ตรวจพบชื่อบอร์ด: <b>${detectedName}</b> กำลังรอ IP...`);
            }
          }

          // Parse IP Address
          if (!detectedIp) {
            const m = logBuffer.match(/IP ADDRESS:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/i)
              || logBuffer.match(/IP Address:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/i)
              || logBuffer.match(/station IP:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)/i);
            if (m) {
              detectedIp = m[1];
            }
          }

          if (detectedName && detectedIp) break;
        }

        const elapsed = Math.round((Date.now() - startTime) / 1000);
        if (btn) btn.innerHTML = `⚡ กำลังฟัง Log (${elapsed}s) Name: ${detectedName || '...'} IP: ${detectedIp || '...'}`;
      }

      try {
        reader.cancel();
        await readableClosed.catch(() => {});
        await port.close();
      } catch (e) {}

      if (detectedName || detectedIp) {
        applyDetectedData(detectedName, detectedIp);
        if (syncChannel) {
          syncChannel.postMessage({ name: detectedName, ip: detectedIp, time: Date.now() });
        }
      } else {
        showToast('ไม่พบข้อมูลชื่อบอร์ดหรือ IP จาก Log กรุณากดปุ่ม Reset บนบอร์ดหรือลองใหม่', false);
      }

    } catch (err) {
      console.error(err);
      showToast('เกิดข้อผิดพลาดในการเชื่อมต่อ Serial: ' + (err.message || err), false);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origText;
      }
    }
  }

  // 3. Auto-Inject the "USB Auto-Detect" and "Sync helper" into the page UI
  function injectSyncButtons() {
    const isAct1 = document.querySelector('input[data-k="board.iot.name"]');
    const isAct2 = document.querySelector('input[data-k="board.relay.name"]');

    if (!isAct1 && !isAct2) return;

    const targetInputs = document.querySelectorAll('input[data-k="board.iot.name"], input[data-k="board.relay.name"]');
    targetInputs.forEach(input => {
      if (input.dataset.syncInjected) return;
      input.dataset.syncInjected = 'true';

      const wrap = document.createElement('span');
      wrap.className = 'esphome-sync-wrap';
      wrap.style.cssText = 'display: inline-flex; align-items: center; gap: 6px; margin-left: 6px; vertical-align: middle;';

      const usbBtn = document.createElement('button');
      usbBtn.type = 'button';
      usbBtn.className = 'btn-usb-detect';
      usbBtn.title = 'คลิกเพื่อต่อสาย USB แล้วดึงชื่อและ IP จากบอร์ดอัตโนมัติ';
      usbBtn.style.cssText = `
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 10px;
        font-family: 'Prompt', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        background: linear-gradient(135deg, #2e7d32, #1b5e20);
        color: #ffffff;
        border: 1px solid #7cb342;
        border-radius: 999px;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        transition: transform 0.15s, background 0.15s;
        line-height: 1.6;
      `;
      usbBtn.innerHTML = '⚡ อ่านจาก USB อัตโนมัติ';
      usbBtn.onmouseenter = () => { usbBtn.style.transform = 'translateY(-1px)'; };
      usbBtn.onmouseleave = () => { usbBtn.style.transform = 'translateY(0)'; };
      usbBtn.onclick = () => connectUsbAutoDetect(usbBtn);

      const bookmarkLink = document.createElement('a');
      bookmarkLink.href = `javascript:(function(){function getAllText(root){let t=root.innerText||'';let w=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT);let n;while(n=w.nextNode()){if(n.shadowRoot)t+='\\n'+getAllText(n.shadowRoot);}return t;}let full=getAllText(document.body);let nm=full.match(/DEVICE NAME:\\s*([a-zA-Z0-9_\\-]+)/i)||full.match(/(?:Device Name|Hostname):\\s*'?([a-zA-Z0-9_\\-]+)'?/i)||full.match(/(gogo-(?:relay|iot)-(?:red|green|blue)-[a-zA-Z0-9]+)/i);let ipm=full.match(/IP ADDRESS:\\s*([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)/i)||full.match(/IP Address:\\s*([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)/i)||full.match(/station IP:\\s*([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)/i);let name=nm?nm[1]:'';let ip=ipm?ipm[1]:'';if(!name&&!ip){alert('⚠️ ยังไม่พบ Name หรือ IP ใน Log ของหน้า web.esphome.io กรุณากด Reset device แล้วลองใหม่');return;}let ch=new BroadcastChannel('esphome_device_sync');ch.postMessage({name:name,ip:ip,time:Date.now()});alert('✅ ดึงข้อมูลสำเร็จ!\\nชื่อบอร์ด: '+name+'\\nIP: '+ip+'\\nส่งไปยังใบงานอัตโนมัติแล้ว!');})();`;
      bookmarkLink.title = 'ลากปุ่มนี้ไปวางที่แถบบุ๊กมาร์ก (Bookmarks Bar) เพื่อใช้กดดึงค่าจากหน้า web.esphome.io';
      bookmarkLink.style.cssText = `
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 2px 8px;
        font-family: 'Prompt', sans-serif;
        font-size: 0.72rem;
        background: #fff8e1;
        color: #b78103;
        border: 1px dashed #f5a524;
        border-radius: 999px;
        text-decoration: none;
        cursor: grab;
      `;
      bookmarkLink.innerHTML = '📌 ปุ่มลัด web.esphome.io';

      wrap.appendChild(usbBtn);
      wrap.appendChild(bookmarkLink);
      input.parentNode.insertBefore(wrap, input.nextSibling);
    });
  }

  // Expose global methods
  window.esphomeSync = {
    connectUsbAutoDetect,
    applyDetectedData
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectSyncButtons);
  } else {
    injectSyncButtons();
  }
})();
