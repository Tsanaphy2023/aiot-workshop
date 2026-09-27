/**
 * Leaf AI Studio & Workshop Client Application
 * Handles Tabs, Backend Communication, Live Training Polls, and Inference Playground
 */

document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "api/api.php";

  // App State
  const state = {
    selectedCrop: "corn",
    selectedModel: "mobilenet_v2",
    trainRatio: 0.70,
    valRatio: 0.15,
    testRatio: 0.15,
    isTraining: false,
    pollInterval: null,
    sampleImages: [],
    selectedPredictImage: null,
    systemInfo: null,
  };

  // Elements
  const statusDot = document.querySelector(".status-dot");
  const statusText = document.getElementById("status-text");
  const kpiHardware = document.getElementById("kpi-hardware");
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  // Step 1: Split Elements
  const selectCrop = document.getElementById("select-crop");
  const inputTrainRatio = document.getElementById("input-train-ratio");
  const inputValRatio = document.getElementById("input-val-ratio");
  const inputTestRatio = document.getElementById("input-test-ratio");
  const valTrainRatio = document.getElementById("val-train-ratio");
  const valValRatio = document.getElementById("val-val-ratio");
  const valTestRatio = document.getElementById("val-test-ratio");
  const btnRunSplit = document.getElementById("btn-run-split");
  const splitSummaryContainer = document.getElementById("split-summary-container");
  const sampleGallery = document.getElementById("sample-gallery");

  // Step 2: Model Elements
  const modelCards = document.querySelectorAll(".model-card");
  const inputEpochs = document.getElementById("input-epochs");
  const inputBatchSize = document.getElementById("input-batch-size");
  const inputLr = document.getElementById("input-lr");

  // Step 3: Train Elements
  const btnStartTrain = document.getElementById("btn-start-train");
  const btnRefreshLog = document.getElementById("btn-refresh-log");
  const trainTerminal = document.getElementById("train-terminal");
  const curvesImg = document.getElementById("curves-img");

  // Step 4: Eval Elements
  const btnRunEval = document.getElementById("btn-run-eval");
  const metricAcc = document.getElementById("metric-acc");
  const metricF1 = document.getElementById("metric-f1");
  const metricWf1 = document.getElementById("metric-wf1");
  const cmImg = document.getElementById("cm-img");
  const evalReportTbody = document.getElementById("eval-report-tbody");

  // Step 5: Predict Elements
  const dropzone = document.getElementById("upload-dropzone");
  const fileInput = document.getElementById("file-input");
  const samplePicksGrid = document.getElementById("sample-picks-grid");
  const btnPredictNow = document.getElementById("btn-predict-now");
  const predictEmpty = document.getElementById("predict-empty");
  const predictResultBox = document.getElementById("predict-result-box");
  const predictPreviewImg = document.getElementById("predict-preview-img");
  const resultClassName = document.getElementById("result-class-name");
  const resultConfVal = document.getElementById("result-conf-val");
  const resultBarFill = document.getElementById("result-bar-fill");
  const topProbsList = document.getElementById("top-probs-list");

  // Step 6: Export Elements
  const btnRunExport = document.getElementById("btn-run-export");
  const exportedFilesList = document.getElementById("exported-files-list");

  // =========================================================================
  // 1. Tab Switching
  // =========================================================================
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });

  // =========================================================================
  // 2. Fetch System Status & Initial Data
  // =========================================================================
  async function fetchSystemStatus() {
    try {
      const res = await fetch(`${API_URL}?action=get_status`);
      if (!res.ok) throw new Error("API not reachable");
      const data = await res.json();
      state.systemInfo = data;

      statusText.textContent = `Online (${data.hardware} | ${data.backend})`;
      if (kpiHardware) {
        kpiHardware.textContent = data.hardware;
      }

      // Render initial split summary for currently selected crop
      if (data.existing_splits && data.existing_splits[state.selectedCrop]) {
        renderSplitSummary(data.existing_splits[state.selectedCrop]);
      }

      // Load sample images
      fetchSampleImages();
    } catch (err) {
      statusText.textContent = "Backend Offline (กรุณาเปิด XAMPP หรือ server.py)";
      statusDot.style.backgroundColor = "#ef4444";
      console.warn("Status fetch failed:", err);
    }
  }

  // =========================================================================
  // 3. Step 1: Split Sliders & Real Split Execution
  // =========================================================================
  function updateRatios() {
    let train = parseInt(inputTrainRatio.value);
    let val = parseInt(inputValRatio.value);
    if (train + val > 95) {
      val = 95 - train;
      inputValRatio.value = val;
    }
    const test = 100 - train - val;
    inputTestRatio.value = test;

    valTrainRatio.textContent = `${train}%`;
    valValRatio.textContent = `${val}%`;
    valTestRatio.textContent = `${test}%`;

    state.trainRatio = train / 100.0;
    state.valRatio = val / 100.0;
    state.testRatio = test / 100.0;
  }

  inputTrainRatio.addEventListener("input", updateRatios);
  inputValRatio.addEventListener("input", updateRatios);

  selectCrop.addEventListener("change", (e) => {
    state.selectedCrop = e.target.value;
    if (state.systemInfo?.existing_splits?.[state.selectedCrop]) {
      renderSplitSummary(state.systemInfo.existing_splits[state.selectedCrop]);
    } else {
      splitSummaryContainer.innerHTML = `
        <div class="text-center p-6 text-muted">
          ยังไม่ได้แบ่งชุดข้อมูลสำหรับ <strong>${state.selectedCrop}</strong><br>
          กรุณากดปุ่ม <em>"สั่งรันการแบ่งชุดข้อมูลจริง"</em> ด้านซ้าย
        </div>`;
    }
    renderSampleGalleryForCrop(state.selectedCrop);
  });

  function renderSplitSummary(summary) {
    if (!summary || !summary.distribution) {
      splitSummaryContainer.innerHTML = `<div class="text-muted p-4">ไม่มีข้อมูลการแบ่ง</div>`;
      return;
    }

    const dist = summary.distribution;
    let html = `
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>คลาส (Class Name)</th>
              <th>Train (70%)</th>
              <th>Val (15%)</th>
              <th>Test (15%)</th>
              <th>รวม</th>
            </tr>
          </thead>
          <tbody>
    `;

    for (const [clsName, counts] of Object.entries(dist)) {
      html += `
        <tr>
          <td><strong>${clsName}</strong></td>
          <td>${counts.train}</td>
          <td>${counts.val}</td>
          <td>${counts.test}</td>
          <td><strong>${counts.total}</strong></td>
        </tr>
      `;
    }

    html += `
          </tbody>
        </table>
      </div>
      <div class="mt-2 text-sm text-muted">
        ไฟล์ถูกจัดเก็บแล้วที่: <code>data/splits/${summary.crop}/(train.csv, val.csv, test.csv)</code>
      </div>
    `;

    splitSummaryContainer.innerHTML = html;
  }

  btnRunSplit.addEventListener("click", async () => {
    btnRunSplit.disabled = true;
    btnRunSplit.innerHTML = `<span>⏳ กำลังประมวลผลการแบ่งข้อมูล...</span>`;

    try {
      const formData = new FormData();
      formData.append("crop", state.selectedCrop);
      formData.append("train_ratio", state.trainRatio);
      formData.append("val_ratio", state.valRatio);
      formData.append("test_ratio", state.testRatio);
      formData.append("seed", document.getElementById("input-seed").value);

      const res = await fetch(`${API_URL}?action=split`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.status === "success" && data.summary) {
        renderSplitSummary(data.summary);
        alert(`✅ แบ่งชุดข้อมูล ${state.selectedCrop.toUpperCase()} สำเร็จเรียบร้อย!`);
      } else {
        alert("ข้อความจากระบบ: " + (data.output || "เกิดข้อผิดพลาดในการแบ่งข้อมูล"));
      }
    } catch (err) {
      alert("ไม่สามารถเชื่อมต่อ Backend เพื่อรันการแบ่งข้อมูล: " + err.message);
    } finally {
      btnRunSplit.disabled = false;
      btnRunSplit.innerHTML = `<span>⚡ สั่งรันการแบ่งชุดข้อมูลจริง (Execute Real Split)</span>`;
    }
  });

  // =========================================================================
  // 4. Step 2: Model Architecture Selection
  // =========================================================================
  modelCards.forEach(card => {
    card.addEventListener("click", () => {
      modelCards.forEach(c => c.classList.remove("selected"));
      card.classList.add("selected");
      state.selectedModel = card.getAttribute("data-model");
    });
  });

  // =========================================================================
  // 5. Step 3: Model Training
  // =========================================================================
  btnStartTrain.addEventListener("click", async () => {
    const epochs = inputEpochs.value;
    const batchSize = inputBatchSize.value;
    const lr = inputLr.value;

    const confirmMsg = `ยืนยันการเริ่มฝึกสอน?\n- ชนิดพืช: ${state.selectedCrop}\n- โมเดล: ${state.selectedModel}\n- Epochs: ${epochs}\n- Batch Size: ${batchSize}\n- Learning Rate: ${lr}`;
    if (!confirm(confirmMsg)) return;

    btnStartTrain.disabled = true;
    btnStartTrain.innerHTML = `<span>⏳ กำลังฝึกสอนโมเดล...</span>`;
    trainTerminal.textContent = `🚀 เริ่มต้นรันสคริปต์การฝึกสอนโมเดล...\nTarget: ${state.selectedCrop} | Model: ${state.selectedModel} | Epochs: ${epochs}\n`;

    try {
      const formData = new FormData();
      formData.append("crop", state.selectedCrop);
      formData.append("backbone", state.selectedModel);
      formData.append("epochs", epochs);
      formData.append("batch_size", batchSize);
      formData.append("lr", lr);

      const res = await fetch(`${API_URL}?action=train`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.status === "started") {
        state.isTraining = true;
        startTrainPolling();
      } else {
        alert("ไม่สามารถเริ่มการฝึกสอนได้: " + (data.message || "Error"));
        btnStartTrain.disabled = false;
        btnStartTrain.innerHTML = `<span>▶ เริ่มต้นฝึกสอนบนเครื่องจริง (Start Local Train)</span>`;
      }
    } catch (err) {
      alert("Error: " + err.message);
      btnStartTrain.disabled = false;
      btnStartTrain.innerHTML = `<span>▶ เริ่มต้นฝึกสอนบนเครื่องจริง (Start Local Train)</span>`;
    }
  });

  function startTrainPolling() {
    if (state.pollInterval) clearInterval(state.pollInterval);

    state.pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}?action=train_status`);
        const data = await res.json();

        if (data.log) {
          trainTerminal.textContent = data.log;
          trainTerminal.scrollTop = trainTerminal.scrollHeight;
        }

        if (!data.running && state.isTraining) {
          state.isTraining = false;
          clearInterval(state.pollInterval);
          btnStartTrain.disabled = false;
          btnStartTrain.innerHTML = `<span>▶ เริ่มต้นฝึกสอนบนเครื่องจริง (Start Local Train)</span>`;
          alert("🎉 การฝึกสอนโมเดลเสร็จสิ้นสมบูรณ์!");

          // Reload curves
          curvesImg.src = `outputs/reports/${state.selectedCrop}_${state.selectedModel}_curves.png?t=${Date.now()}`;
          curvesImg.style.display = "block";
          document.getElementById("no-curves-msg").style.display = "none";
        }
      } catch (err) {
        console.error("Poll error:", err);
      }
    }, 2000);
  }

  btnRefreshLog.addEventListener("click", async () => {
    try {
      const res = await fetch(`${API_URL}?action=train_status`);
      const data = await res.json();
      if (data.log) {
        trainTerminal.textContent = data.log;
        trainTerminal.scrollTop = trainTerminal.scrollHeight;
      }
    } catch (e) {}
  });

  // =========================================================================
  // 6. Step 4: Evaluation
  // =========================================================================
  btnRunEval.addEventListener("click", async () => {
    btnRunEval.disabled = true;
    btnRunEval.innerHTML = `<span>⏳ กำลังประเมินผลบน Test Set...</span>`;

    try {
      const formData = new FormData();
      const res = await fetch(`${API_URL}?action=evaluate`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.status === "success" && data.reports && data.reports.length > 0) {
        const latestReport = data.reports[data.reports.length - 1];
        if (latestReport.accuracy) {
          metricAcc.textContent = `${(latestReport.accuracy * 100).toFixed(2)}%`;
        }
        if (latestReport.macro_avg?.f1_score) {
          metricF1.textContent = `${(latestReport.macro_avg.f1_score * 100).toFixed(2)}%`;
        }
        if (latestReport.weighted_avg?.f1_score) {
          metricWf1.textContent = `${(latestReport.weighted_avg.f1_score * 100).toFixed(2)}%`;
        }

        // Render per-class table
        if (latestReport.per_class) {
          let rows = "";
          for (const [cls, met] of Object.entries(latestReport.per_class)) {
            rows += `
              <tr>
                <td><strong>${cls}</strong></td>
                <td>${met.precision.toFixed(2)}</td>
                <td>${met.recall.toFixed(2)}</td>
                <td>${met.f1_score.toFixed(2)}</td>
                <td>${met.support}</td>
              </tr>
            `;
          }
          evalReportTbody.innerHTML = rows;
        }

        // Reload Confusion Matrix
        cmImg.src = `outputs/reports/coffee_leaf_net_confusion_matrix.png?t=${Date.now()}`;
        alert("✅ ประเมินผลโมเดลบน Test Set เรียบร้อย!");
      } else {
        alert("ผลการประเมิน: " + (data.output || "เสร็จสิ้น"));
      }
    } catch (err) {
      alert("Error during evaluation: " + err.message);
    } finally {
      btnRunEval.disabled = false;
      btnRunEval.innerHTML = `<span>🔍 สั่งประเมินผลบน Test Set (Run Evaluation)</span>`;
    }
  });

  // =========================================================================
  // 7. Step 5: Live Inference Playground
  // =========================================================================
  async function fetchSampleImages() {
    try {
      const res = await fetch(`${API_URL}?action=get_sample_images`);
      const data = await res.json();
      if (data.status === "success" && data.samples) {
        state.sampleImages = data.samples;
        renderSamplePicks();
        renderSampleGalleryForCrop(state.selectedCrop);
      }
    } catch (e) {
      console.warn("Could not load sample images:", e);
    }
  }

  function renderSamplePicks() {
    samplePicksGrid.innerHTML = "";
    state.sampleImages.forEach((img, idx) => {
      const thumb = document.createElement("img");
      thumb.src = img.url;
      thumb.className = "sample-thumb";
      thumb.title = `${img.crop} / ${img.class}`;
      thumb.addEventListener("click", () => {
        document.querySelectorAll(".sample-thumb").forEach(t => t.classList.remove("selected"));
        thumb.classList.add("selected");
        state.selectedPredictImage = { type: "path", path: img.path, url: img.url };
        predictPreviewImg.src = img.url;
        btnPredictNow.disabled = false;
        dropzone.querySelector("h4").textContent = `เลือกภาพตัวอย่าง: ${img.class} (${img.filename})`;
      });
      samplePicksGrid.appendChild(thumb);
    });
  }

  function renderSampleGalleryForCrop(cropKey) {
    if (!sampleGallery) return;
    sampleGallery.innerHTML = "";
    const filtered = state.sampleImages.filter(s => {
      if (cropKey === "all") return true;
      return s.crop.toLowerCase().includes(cropKey.toLowerCase());
    });

    filtered.forEach(item => {
      const card = document.createElement("div");
      card.className = "sample-gallery-card";
      card.innerHTML = `
        <img src="${item.url}" alt="${item.class}">
        <span>${item.class}</span>
      `;
      sampleGallery.appendChild(card);
    });
  }

  // File Upload Handlers
  dropzone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  });

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dragover");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  function handleFileSelected(file) {
    const reader = new FileReader();
    reader.onload = (event) => {
      predictPreviewImg.src = event.target.result;
      state.selectedPredictImage = { type: "file", file: file };
      btnPredictNow.disabled = false;
      dropzone.querySelector("h4").textContent = `เลือกไฟล์: ${file.name}`;
      document.querySelectorAll(".sample-thumb").forEach(t => t.classList.remove("selected"));
    };
    reader.readAsDataURL(file);
  }

  btnPredictNow.addEventListener("click", async () => {
    if (!state.selectedPredictImage) return;

    btnPredictNow.disabled = true;
    btnPredictNow.innerHTML = `<span>⏳ กำลังวิเคราะห์และทำนาย...</span>`;

    try {
      const formData = new FormData();
      if (state.selectedPredictImage.type === "file") {
        formData.append("image", state.selectedPredictImage.file);
      } else {
        formData.append("image_path", state.selectedPredictImage.path);
      }

      const res = await fetch(`${API_URL}?action=predict`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.status === "success" && data.result) {
        const r = data.result;
        predictEmpty.style.display = "none";
        predictResultBox.style.display = "block";

        resultClassName.textContent = r.predicted_class;
        resultConfVal.textContent = `${r.confidence_percent}%`;
        resultBarFill.style.width = `${r.confidence_percent}%`;

        // Render Top K list
        let probsHtml = "";
        if (r.top_k) {
          r.top_k.forEach((item, idx) => {
            probsHtml += `
              <div class="prob-row">
                <span>#${idx + 1} ${item.class}</span>
                <strong>${item.confidence}%</strong>
              </div>
            `;
          });
        }
        topProbsList.innerHTML = probsHtml;
      } else {
        alert("ผลการทำนาย: " + (data.message || data.raw_output || "เกิดข้อผิดพลาด"));
      }
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      btnPredictNow.disabled = false;
      btnPredictNow.innerHTML = `<span>✨ วิเคราะห์และทำนายโรคพืช (Predict Now)</span>`;
    }
  });

  // =========================================================================
  // 8. Step 6: Export Models
  // =========================================================================
  btnRunExport.addEventListener("click", async () => {
    btnRunExport.disabled = true;
    btnRunExport.innerHTML = `<span>⏳ กำลังส่งออกโมเดล ONNX & TorchScript...</span>`;

    try {
      const formData = new FormData();
      const res = await fetch(`${API_URL}?action=export`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.status === "success" && data.exported_files) {
        let html = "";
        data.exported_files.forEach(f => {
          html += `
            <div class="file-item">
              <div class="file-icon">📦</div>
              <div class="file-info">
                <div class="file-name">${f.filename}</div>
                <div class="file-meta">ขนาดไฟล์: ${f.filesize_mb} MB</div>
              </div>
              <a href="${f.url}" download class="btn btn-sm btn-outline">ดาวน์โหลด</a>
            </div>
          `;
        });
        exportedFilesList.innerHTML = html;
        alert("✅ ส่งออกโมเดล ONNX และ TorchScript สำเร็จเรียบร้อย!");
      } else {
        alert("ข้อความ: " + (data.output || "Error"));
      }
    } catch (err) {
      alert("Error: " + err.message);
    } finally {
      btnRunExport.disabled = false;
      btnRunExport.innerHTML = `<span>💾 แปลงและส่งออกโมเดล (Export Models)</span>`;
    }
  });

  // Initialize
  fetchSystemStatus();
});
