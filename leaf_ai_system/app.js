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

  // =========================================================================
  // 9. Step 6: Object Detection & Bounding Box Studio
  // =========================================================================
  const btnJumpToBbox = document.getElementById("btn-jump-to-bbox");
  const btnModeAuto = document.getElementById("btn-mode-auto");
  const btnModeManual = document.getElementById("btn-mode-manual");
  const bboxCropSelect = document.getElementById("bbox-crop-select");
  const sliderConf = document.getElementById("slider-conf");
  const sliderIou = document.getElementById("slider-iou");
  const valConf = document.getElementById("val-conf");
  const valIou = document.getElementById("val-iou");

  const bboxDropzone = document.getElementById("bbox-dropzone");
  const bboxFileInput = document.getElementById("bbox-file-input");
  const bboxSamplePicks = document.getElementById("bbox-sample-picks");
  const manualLabelToolbar = document.getElementById("manual-label-toolbar");
  const manualClassSelect = document.getElementById("manual-class-select");
  const btnUndoBox = document.getElementById("btn-undo-box");
  const btnClearBoxes = document.getElementById("btn-clear-boxes");
  const btnDetectBbox = document.getElementById("btn-detect-bbox");

  const bboxEmpty = document.getElementById("bbox-empty");
  const bboxViewerWrap = document.getElementById("bbox-viewer-wrap");
  const bboxCanvas = document.getElementById("bbox-canvas");
  const bboxCtx = bboxCanvas ? bboxCanvas.getContext("2d") : null;

  const diagnosisBanner = document.getElementById("diagnosis-banner");
  const diagnosisTitle = document.getElementById("diagnosis-title");
  const diagnosisDesc = document.getElementById("diagnosis-desc");

  const statTotalBoxes = document.getElementById("stat-total-boxes");
  const statDamagePct = document.getElementById("stat-damage-pct");
  const statSeverity = document.getElementById("stat-severity");
  const bboxCountBadge = document.getElementById("bbox-count-badge");
  const bboxTableBody = document.getElementById("bbox-table-body");

  const btnExportYolo = document.getElementById("btn-export-yolo");
  const btnExportJson = document.getElementById("btn-export-json");
  const btnDownloadAnnotated = document.getElementById("btn-download-annotated");

  // Bounding Box State
  const bboxState = {
    mode: "auto", // "auto" or "manual"
    imageObj: null,
    imageSrc: "",
    imageFile: null,
    imagePath: "",
    boxes: [],
    activeBoxId: null,
    isDrawing: false,
    drawStart: { x: 0, y: 0 },
    currentMouse: { x: 0, y: 0 },
    confThreshold: 0.35,
    iouThreshold: 0.45,
  };

  const CLASS_COLORS = {
    Blight_Lesion: "#EF4444",
    Rust_Pustule: "#F59E0B",
    Spot_Damage: "#EC4899",
    Rotten_Defect: "#DC2626",
    Fruit_Body: "#3B82F6",
    Healthy_Area: "#10B981",
  };

  // 9.1 Mode Switcher (Auto AI vs Manual Labeler)
  if (btnModeAuto && btnModeManual) {
    btnModeAuto.addEventListener("click", () => {
      bboxState.mode = "auto";
      btnModeAuto.classList.add("active");
      btnModeManual.classList.remove("active");
      if (manualLabelToolbar) manualLabelToolbar.style.display = "none";
      if (btnDetectBbox) {
        btnDetectBbox.innerHTML = `<span>✨ สแกนและตีกรอบ Bounding Box ทันที (Detect Bounding Boxes)</span>`;
      }
      renderBboxCanvas();
    });

    btnModeManual.addEventListener("click", () => {
      bboxState.mode = "manual";
      btnModeManual.classList.add("active");
      btnModeAuto.classList.remove("active");
      if (manualLabelToolbar) manualLabelToolbar.style.display = "block";
      if (btnDetectBbox) {
        btnDetectBbox.innerHTML = `<span>💾 อัปเดตและบันทึก Bounding Box ที่วาด (Save Annotations)</span>`;
      }
      renderBboxCanvas();
    });
  }

  // 9.2 Sliders
  if (sliderConf && valConf) {
    sliderConf.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      bboxState.confThreshold = val / 100.0;
      valConf.textContent = `${val}%`;
    });
  }

  if (sliderIou && valIou) {
    sliderIou.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      bboxState.iouThreshold = val / 100.0;
      valIou.textContent = `${val}%`;
    });
  }

  // 9.3 Populate Sample Thumbnails for Bbox Studio
  function populateBboxSamples() {
    if (!bboxSamplePicks || !state.sampleImages.length) return;
    let html = "";
    state.sampleImages.slice(0, 10).forEach((s) => {
      html += `
        <div class="sample-pick-item" data-path="${s.path}" data-url="${s.url}" data-crop="${s.crop}" title="${s.class}">
          <img src="${s.url}" alt="${s.class}">
          <div class="pick-label">${s.class}</div>
        </div>
      `;
    });
    bboxSamplePicks.innerHTML = html;

    bboxSamplePicks.querySelectorAll(".sample-pick-item").forEach((el) => {
      el.addEventListener("click", () => {
        bboxSamplePicks.querySelectorAll(".sample-pick-item").forEach((b) => b.classList.remove("selected"));
        el.classList.add("selected");
        setBboxTargetImage({
          type: "path",
          path: el.getAttribute("data-path"),
          url: el.getAttribute("data-url"),
          crop: el.getAttribute("data-crop")
        });
      });
    });
  }

  // Set Target Image for Bounding Box Studio
  function setBboxTargetImage(source) {
    bboxState.boxes = [];
    bboxState.activeBoxId = null;

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      bboxState.imageObj = img;
      if (bboxEmpty) bboxEmpty.style.display = "none";
      if (bboxViewerWrap) bboxViewerWrap.style.display = "block";
      if (btnDetectBbox) btnDetectBbox.disabled = false;

      // Adjust canvas resolution to natural image dimensions
      bboxCanvas.width = img.naturalWidth || img.width;
      bboxCanvas.height = img.naturalHeight || img.height;

      renderBboxCanvas();
      updateBboxUIStats();
    };

    if (source.type === "file") {
      bboxState.imageFile = source.file;
      bboxState.imagePath = "";
      const reader = new FileReader();
      reader.onload = (e) => {
        bboxState.imageSrc = e.target.result;
        img.src = e.target.result;
      };
      reader.readAsDataURL(source.file);
    } else {
      bboxState.imageFile = null;
      bboxState.imagePath = source.path;
      bboxState.imageSrc = source.url;
      img.src = source.url;
      if (source.crop && bboxCropSelect) {
        const cropVal = source.crop.toLowerCase().replace("_dataset", "");
        if (["corn", "potato", "coffee", "orange", "mango", "banana"].includes(cropVal)) {
          bboxCropSelect.value = cropVal;
        }
      }
    }
  }

  // 9.4 Dropzone & File Input for Bbox Studio
  if (bboxDropzone && bboxFileInput) {
    bboxDropzone.addEventListener("click", () => bboxFileInput.click());
    bboxFileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        setBboxTargetImage({ type: "file", file: e.target.files[0] });
      }
    });

    bboxDropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      bboxDropzone.classList.add("drag-over");
    });
    bboxDropzone.addEventListener("dragleave", () => {
      bboxDropzone.classList.remove("drag-over");
    });
    bboxDropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      bboxDropzone.classList.remove("drag-over");
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        setBboxTargetImage({ type: "file", file: e.dataTransfer.files[0] });
      }
    });
  }

  // 9.5 Interactive Canvas Rendering (Drawing Bounding Boxes)
  function renderBboxCanvas() {
    if (!bboxCtx || !bboxState.imageObj) return;

    const w = bboxCanvas.width;
    const h = bboxCanvas.height;

    // Draw background image
    bboxCtx.clearRect(0, 0, w, h);
    bboxCtx.drawImage(bboxState.imageObj, 0, 0, w, h);

    // Draw each bounding box
    bboxState.boxes.forEach((b) => {
      const [bx, by, bw, bh] = b.bbox;
      const isSelected = b.id === bboxState.activeBoxId;
      const color = b.color || CLASS_COLORS[b.class] || "#EF4444";

      // 1. Semi-transparent fill
      bboxCtx.fillStyle = isSelected ? "rgba(239, 68, 68, 0.28)" : "rgba(0, 0, 0, 0.18)";
      bboxCtx.fillRect(bx, by, bw, bh);

      // 2. Glow effect if selected
      if (isSelected) {
        bboxCtx.shadowColor = color;
        bboxCtx.shadowBlur = 12;
      } else {
        bboxCtx.shadowColor = "transparent";
        bboxCtx.shadowBlur = 0;
      }

      // 3. Border line
      bboxCtx.strokeStyle = color;
      bboxCtx.lineWidth = isSelected ? 3.5 : 2.5;
      bboxCtx.strokeRect(bx, by, bw, bh);
      bboxCtx.shadowBlur = 0;

      // 4. Corner HUD brackets
      const cLen = Math.max(6, Math.min(22, Math.min(bw, bh) * 0.2));
      bboxCtx.lineWidth = isSelected ? 4.5 : 3.5;
      // Top-Left
      bboxCtx.beginPath();
      bboxCtx.moveTo(bx, by + cLen);
      bboxCtx.lineTo(bx, by);
      bboxCtx.lineTo(bx + cLen, by);
      bboxCtx.stroke();
      // Top-Right
      bboxCtx.beginPath();
      bboxCtx.moveTo(bx + bw - cLen, by);
      bboxCtx.lineTo(bx + bw, by);
      bboxCtx.lineTo(bx + bw, by + cLen);
      bboxCtx.stroke();
      // Bottom-Left
      bboxCtx.beginPath();
      bboxCtx.moveTo(bx, by + bh - cLen);
      bboxCtx.lineTo(bx, by + bh);
      bboxCtx.lineTo(bx + cLen, by + bh);
      bboxCtx.stroke();
      // Bottom-Right
      bboxCtx.beginPath();
      bboxCtx.moveTo(bx + bw - cLen, by + bh);
      bboxCtx.lineTo(bx + bw, by + bh);
      bboxCtx.lineTo(bx + bw, by + bh - cLen);
      bboxCtx.stroke();

      // 5. Label badge
      const confText = b.confidence_pct ? `${b.confidence_pct}%` : "100%";
      const labelText = `#${b.id} ${b.class} (${confText})`;
      bboxCtx.font = "bold 13px 'JetBrains Mono', sans-serif";
      const textMetrics = bboxCtx.measureText(labelText);
      const tagW = textMetrics.width + 12;
      const tagH = 20;
      const tagY = Math.max(0, by - tagH);

      bboxCtx.fillStyle = color;
      bboxCtx.fillRect(bx, tagY, tagW, tagH);

      bboxCtx.fillStyle = "#ffffff";
      bboxCtx.fillText(labelText, bx + 6, tagY + 14);
    });

    // Draw active drawing rubberband if in manual mode
    if (bboxState.isDrawing) {
      const rx = Math.min(bboxState.drawStart.x, bboxState.currentMouse.x);
      const ry = Math.min(bboxState.drawStart.y, bboxState.currentMouse.y);
      const rw = Math.abs(bboxState.currentMouse.x - bboxState.drawStart.x);
      const rh = Math.abs(bboxState.currentMouse.y - bboxState.drawStart.y);

      const selOpt = manualClassSelect ? manualClassSelect.options[manualClassSelect.selectedIndex] : null;
      const drawColor = selOpt ? selOpt.getAttribute("data-color") : "#EF4444";

      bboxCtx.strokeStyle = drawColor;
      bboxCtx.lineWidth = 2.5;
      bboxCtx.setLineDash([6, 4]);
      bboxCtx.strokeRect(rx, ry, rw, rh);
      bboxCtx.setLineDash([]);

      bboxCtx.fillStyle = "rgba(255, 255, 255, 0.15)";
      bboxCtx.fillRect(rx, ry, rw, rh);
    }
  }

  // 9.6 Canvas Mouse Events for Manual Labeling & Box Selection
  if (bboxCanvas) {
    function getCanvasCoordinates(e) {
      const rect = bboxCanvas.getBoundingClientRect();
      const scaleX = bboxCanvas.width / rect.width;
      const scaleY = bboxCanvas.height / rect.height;
      return {
        x: Math.round((e.clientX - rect.left) * scaleX),
        y: Math.round((e.clientY - rect.top) * scaleY),
      };
    }

    bboxCanvas.addEventListener("mousedown", (e) => {
      const coords = getCanvasCoordinates(e);

      if (bboxState.mode === "manual") {
        bboxState.isDrawing = true;
        bboxState.drawStart = coords;
        bboxState.currentMouse = coords;
      } else {
        // Auto Mode: check if clicked inside any box to select
        let clickedBox = null;
        for (let i = bboxState.boxes.length - 1; i >= 0; i--) {
          const b = bboxState.boxes[i];
          const [bx, by, bw, bh] = b.bbox;
          if (coords.x >= bx && coords.x <= bx + bw && coords.y >= by && coords.y <= by + bh) {
            clickedBox = b;
            break;
          }
        }
        bboxState.activeBoxId = clickedBox ? clickedBox.id : null;
        renderBboxCanvas();
        highlightTableRow(bboxState.activeBoxId);
      }
    });

    bboxCanvas.addEventListener("mousemove", (e) => {
      const coords = getCanvasCoordinates(e);
      bboxState.currentMouse = coords;

      if (bboxState.isDrawing) {
        renderBboxCanvas();
      }
    });

    bboxCanvas.addEventListener("mouseup", (e) => {
      if (!bboxState.isDrawing) return;
      bboxState.isDrawing = false;
      const coords = getCanvasCoordinates(e);

      const rx = Math.min(bboxState.drawStart.x, coords.x);
      const ry = Math.min(bboxState.drawStart.y, coords.y);
      const rw = Math.abs(coords.x - bboxState.drawStart.x);
      const rh = Math.abs(coords.y - bboxState.drawStart.y);

      // Ignore accidental tiny clicks
      if (rw < 8 || rh < 8) {
        renderBboxCanvas();
        return;
      }

      const selClass = manualClassSelect ? manualClassSelect.value : "Blight_Lesion";
      const selOpt = manualClassSelect ? manualClassSelect.options[manualClassSelect.selectedIndex] : null;
      const color = selOpt ? selOpt.getAttribute("data-color") : "#EF4444";

      const totalPx = bboxCanvas.width * bboxCanvas.height;
      const areaPx = rw * rh;
      const newId = bboxState.boxes.length + 1;

      // Calculate YOLO normalized coordinates
      const normCx = Number(((rx + rw / 2.0) / bboxCanvas.width).toFixed(5));
      const normCy = Number(((ry + rh / 2.0) / bboxCanvas.height).toFixed(5));
      const normW = Number((rw / bboxCanvas.width).toFixed(5));
      const normH = Number((rh / bboxCanvas.height).toFixed(5));

      bboxState.boxes.push({
        id: newId,
        class: selClass,
        confidence: 1.0,
        confidence_pct: 100.0,
        bbox: [rx, ry, rw, rh],
        yolo_bbox: [normCx, normCy, normW, normH],
        area_px: areaPx,
        area_pct: Number(((areaPx / totalPx) * 100).toFixed(2)),
        severity: areaPx > totalPx * 0.08 ? "High" : "Medium",
        color: color,
      });

      bboxState.activeBoxId = newId;
      renderBboxCanvas();
      updateBboxUIStats();
    });

    bboxCanvas.addEventListener("mouseleave", () => {
      if (bboxState.isDrawing) {
        bboxState.isDrawing = false;
        renderBboxCanvas();
      }
    });
  }

  // 9.7 Undo & Clear Boxes
  if (btnUndoBox) {
    btnUndoBox.addEventListener("click", () => {
      if (bboxState.boxes.length > 0) {
        bboxState.boxes.pop();
        bboxState.activeBoxId = null;
        renderBboxCanvas();
        updateBboxUIStats();
      }
    });
  }

  if (btnClearBoxes) {
    btnClearBoxes.addEventListener("click", () => {
      if (confirm("คุณต้องการลบ Bounding Box ทั้งหมดหรือไม่?")) {
        bboxState.boxes = [];
        bboxState.activeBoxId = null;
        renderBboxCanvas();
        updateBboxUIStats();
      }
    });
  }

  // 9.8 Execute AI Detection via Backend
  if (btnDetectBbox) {
    btnDetectBbox.addEventListener("click", async () => {
      if (!bboxState.imageObj) {
        alert("กรุณาเลือกหรืออัปโหลดภาพก่อนดำเนินการ");
        return;
      }

      if (bboxState.mode === "manual") {
        alert(`✅ บันทึก Bounding Box ทั้งหมด ${bboxState.boxes.length} กรอบเรียบร้อยแล้ว!`);
        return;
      }

      btnDetectBbox.disabled = true;
      btnDetectBbox.innerHTML = `<span>⏳ กำลังตรวจจับ Bounding Box (Analyzing Vision AI)...</span>`;

      try {
        const formData = new FormData();
        if (bboxState.imageFile) {
          formData.append("image", bboxState.imageFile);
        } else {
          formData.append("image_path", bboxState.imagePath);
        }
        formData.append("crop", bboxCropSelect ? bboxCropSelect.value : "auto");
        formData.append("conf_threshold", bboxState.confThreshold);
        formData.append("iou_threshold", bboxState.iouThreshold);

        const res = await fetch(`${API_URL}?action=detect_bounding_boxes`, {
          method: "POST",
          body: formData,
        });

        const data = await res.json();
        if (data.status === "success" && data.result) {
          const r = data.result;
          bboxState.boxes = r.detections || [];
          bboxState.activeBoxId = null;

          renderBboxCanvas();

          // Update Diagnosis Banner
          if (diagnosisBanner && diagnosisTitle && diagnosisDesc) {
            diagnosisTitle.textContent = `การวินิจฉัยโรค: ${r.health_status} (${r.diagnosis})`;
            diagnosisDesc.textContent = `คำแนะนำเชิงปฏิบัติ: ${r.recommendation}`;
            if (r.health_status === "Severe") {
              diagnosisBanner.style.background = "rgba(239, 68, 68, 0.15)";
              diagnosisBanner.style.borderColor = "rgba(239, 68, 68, 0.4)";
            } else if (r.health_status === "Moderate") {
              diagnosisBanner.style.background = "rgba(245, 158, 11, 0.15)";
              diagnosisBanner.style.borderColor = "rgba(245, 158, 11, 0.4)";
            } else {
              diagnosisBanner.style.background = "rgba(16, 185, 129, 0.15)";
              diagnosisBanner.style.borderColor = "rgba(16, 185, 129, 0.4)";
            }
          }

          updateBboxUIStats(r.damage_area_pct, r.health_status);
        } else {
          alert("ผลการตรวจจับ: " + (data.message || data.raw_output || "เกิดข้อผิดพลาด"));
        }
      } catch (err) {
        alert("Error: " + err.message);
      } finally {
        btnDetectBbox.disabled = false;
        btnDetectBbox.innerHTML = `<span>✨ สแกนและตีกรอบ Bounding Box ทันที (Detect Bounding Boxes)</span>`;
      }
    });
  }

  // 9.9 Update Table & Stats
  function updateBboxUIStats(damagePct, healthStatus) {
    const totalCount = bboxState.boxes.length;
    if (statTotalBoxes) statTotalBoxes.textContent = totalCount;
    if (bboxCountBadge) bboxCountBadge.textContent = `${totalCount} วัตถุที่ตรวจพบ`;

    if (damagePct !== undefined && statDamagePct) {
      statDamagePct.textContent = `${damagePct}%`;
    } else if (statDamagePct && bboxCanvas) {
      const totalPx = bboxCanvas.width * bboxCanvas.height;
      const sumArea = bboxState.boxes.reduce((acc, b) => acc + (b.area_px || 0), 0);
      statDamagePct.textContent = `${((sumArea / totalPx) * 100).toFixed(2)}%`;
    }

    if (healthStatus && statSeverity) {
      statSeverity.textContent = healthStatus;
    }

    // Populate Table
    if (bboxTableBody) {
      if (!bboxState.boxes.length) {
        bboxTableBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted p-4">ยังไม่มี Bounding Box ที่ตรวจพบ</td></tr>`;
        return;
      }

      let tbodyHtml = "";
      bboxState.boxes.forEach((b) => {
        const [x, y, w, h] = b.bbox;
        const [cx, cy, nw, nh] = b.yolo_bbox || [0, 0, 0, 0];
        const isSelected = b.id === bboxState.activeBoxId;
        const color = b.color || CLASS_COLORS[b.class] || "#EF4444";

        tbodyHtml += `
          <tr class="${isSelected ? 'active-box-row' : ''}" data-box-id="${b.id}">
            <td><strong>#${b.id}</strong></td>
            <td>
              <span class="badge" style="background: ${color}22; color: ${color}; border: 1px solid ${color}66;">
                ${b.class}
              </span>
            </td>
            <td><strong>${b.confidence_pct}%</strong></td>
            <td><code>[${x}, ${y}, ${w}, ${h}]</code></td>
            <td><code>${cx}, ${cy}, ${nw}, ${nh}</code></td>
            <td>${b.area_pct}%</td>
            <td>
              <button class="btn btn-xs btn-outline text-danger btn-del-box" data-id="${b.id}" title="ลบกรอบนี้">✕</button>
            </td>
          </tr>
        `;
      });

      bboxTableBody.innerHTML = tbodyHtml;

      // Row hover/click listeners
      bboxTableBody.querySelectorAll("tr").forEach((row) => {
        row.addEventListener("mouseenter", () => {
          const id = parseInt(row.getAttribute("data-box-id"), 10);
          bboxState.activeBoxId = id;
          renderBboxCanvas();
        });
        row.addEventListener("mouseleave", () => {
          bboxState.activeBoxId = null;
          renderBboxCanvas();
        });
      });

      // Delete buttons
      bboxTableBody.querySelectorAll(".btn-del-box").forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const delId = parseInt(btn.getAttribute("data-id"), 10);
          bboxState.boxes = bboxState.boxes.filter((b) => b.id !== delId);
          // Re-index
          bboxState.boxes.forEach((b, idx) => (b.id = idx + 1));
          renderBboxCanvas();
          updateBboxUIStats();
        });
      });
    }
  }

  function highlightTableRow(id) {
    if (!bboxTableBody) return;
    bboxTableBody.querySelectorAll("tr").forEach((r) => {
      if (parseInt(r.getAttribute("data-box-id"), 10) === id) {
        r.classList.add("active-box-row");
        r.scrollIntoView({ behavior: "smooth", block: "nearest" });
      } else {
        r.classList.remove("active-box-row");
      }
    });
  }

  // 9.10 Export Functions (YOLO format & Pascal VOC/JSON & Annotated Image)
  function downloadFile(content, fileName, contentType) {
    const a = document.createElement("a");
    const file = new Blob([content], { type: contentType });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  // Export YOLO txt: class_index center_x center_y width height
  if (btnExportYolo) {
    btnExportYolo.addEventListener("click", () => {
      if (!bboxState.boxes.length) {
        alert("ไม่มี Bounding Box สำหรับส่งออก");
        return;
      }
      const classMap = {
        Blight_Lesion: 0,
        Rust_Pustule: 1,
        Spot_Damage: 2,
        Rotten_Defect: 3,
        Fruit_Body: 4,
        Healthy_Area: 5,
      };

      let lines = [];
      bboxState.boxes.forEach((b) => {
        const clsIdx = classMap[b.class] !== undefined ? classMap[b.class] : 0;
        const [cx, cy, w, h] = b.yolo_bbox;
        lines.push(`${clsIdx} ${cx} ${cy} ${w} ${h}`);
      });

      downloadFile(lines.join("\n"), "labels_yolo.txt", "text/plain");
    });
  }

  // Export COCO / VOC JSON
  if (btnExportJson) {
    btnExportJson.addEventListener("click", () => {
      if (!bboxState.boxes.length) {
        alert("ไม่มี Bounding Box สำหรับส่งออก");
        return;
      }
      const exportData = {
        image: {
          file_name: bboxState.imagePath ? bboxState.imagePath.split("/").pop() : "uploaded_leaf.jpg",
          width: bboxCanvas.width,
          height: bboxCanvas.height,
        },
        annotations: bboxState.boxes.map((b) => ({
          id: b.id,
          category: b.class,
          confidence: b.confidence,
          bbox: b.bbox, // [x, y, w, h]
          yolo_normalized: b.yolo_bbox,
          area_px: b.area_px,
          area_pct: b.area_pct,
        })),
      };

      downloadFile(JSON.stringify(exportData, null, 2), "annotations_coco.json", "application/json");
    });
  }

  // Download Annotated Image Canvas
  if (btnDownloadAnnotated) {
    btnDownloadAnnotated.addEventListener("click", () => {
      if (!bboxCanvas) return;
      const link = document.createElement("a");
      link.download = "annotated_bounding_boxes.jpg";
      link.href = bboxCanvas.toDataURL("image/jpeg", 0.92);
      link.click();
    });
  }

  // 9.11 Jump from Tab 05 (Predict) to Tab 06 (Bounding Box)
  if (btnJumpToBbox) {
    btnJumpToBbox.addEventListener("click", () => {
      // Find tab button for bbox
      const tabBboxBtn = document.querySelector('[data-tab="tab-bbox"]');
      if (tabBboxBtn) {
        tabBboxBtn.click();
      }

      // If user selected an image in Tab 05, pass it directly
      if (state.selectedPredictImage) {
        setBboxTargetImage({
          type: "path",
          path: state.selectedPredictImage.path,
          url: state.selectedPredictImage.url,
          crop: state.selectedPredictImage.crop
        });

        // Auto trigger detection after a brief delay
        setTimeout(() => {
          if (btnDetectBbox && !btnDetectBbox.disabled) {
            btnDetectBbox.click();
          }
        }, 500);
      }
    });
  }

  // Initial call to populate sample images in Bbox tab when status loads
  const origFetchSystemStatus = fetchSystemStatus;
  fetchSystemStatus = async function() {
    await origFetchSystemStatus();
    populateBboxSamples();
  };

  // Initialize
  fetchSystemStatus();
});
