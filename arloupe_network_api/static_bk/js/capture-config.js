/* 影像參數讀取、儲存與套用 */

function updateCaptureConfigActions() {
  const applyBtn = document.getElementById("applyCaptureConfigBtn");
  if (!applyBtn) return;
  applyBtn.disabled = captureBusy;
  if (captureBusy) {
    applyBtn.title = "請先停止串流與錄影後再套用設定";
  } else {
    applyBtn.title = "";
  }
}

async function loadCaptureConfig() {
  try {
    const res = await fetch("/api/config/capture");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    document.getElementById("configFps").value = String(data.fps || 30);
    document.getElementById("configBitrate").value = data.bitrate_kbps || 5000;
    document.getElementById("configSegmentSeconds").value = data.segment_seconds || 300;
    document.getElementById("configInputFps").textContent = `${data.input_fps || 60} fps`;
    document.getElementById("configKeyInt").textContent = `${data.key_int_max || data.fps || 30}`;
    document.getElementById("captureConfigRaw").textContent = JSON.stringify(data, null, 2);
    setMessage("captureConfigMessage", "影像參數已讀取", "ok");
  } catch (err) {
    setMessage("captureConfigMessage", `影像參數讀取失敗：${err}`, "danger");
    document.getElementById("captureConfigRaw").textContent = String(err);
  }
}

function getCaptureConfigFormData() {
  const fps = Number(document.getElementById("configFps").value);
  const bitrate = Number(document.getElementById("configBitrate").value);
  const segmentSeconds = Number(document.getElementById("configSegmentSeconds").value);

  return {
    input_fps: 60,
    fps: fps,
    bitrate_kbps: bitrate,
    segment_seconds: segmentSeconds,
    auto_key_int: true
  };
}

async function saveCaptureConfig(silent = false) {
  if (!silent) setMessage("captureConfigMessage", "正在儲存影像參數...", "warn");

  const res = await fetch("/api/config/capture", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(getCaptureConfigFormData())
  });

  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch (_) { data = { raw: text }; }

  if (!res.ok) {
    const detail = data.detail || data.raw || `HTTP ${res.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  document.getElementById("captureConfigRaw").textContent = JSON.stringify(data, null, 2);
  if (!silent) setMessage("captureConfigMessage", data.message || "影像參數已儲存", "ok");
  return data;
}

async function applyCaptureConfig() {
  if (captureBusy) {
    alert("請先停止串流與錄影後再套用設定。");
    return;
  }

  const ok = confirm("會先儲存設定，並重啟 7000 影像服務。確定要套用嗎？");
  if (!ok) return;

  setMessage("captureConfigMessage", "正在儲存並套用設定...", "warn");

  try {
    await saveCaptureConfig(true);
    const res = await fetch("/api/config/capture/apply", { method: "POST" });
    const text = await res.text();
    let data = {};
    try { data = text ? JSON.parse(text) : {}; } catch (_) { data = { raw: text }; }

    if (!res.ok) {
      const detail = data.detail || data.raw || `HTTP ${res.status}`;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }

    document.getElementById("captureConfigRaw").textContent = JSON.stringify(data, null, 2);
    setMessage("captureConfigMessage", data.message || "設定已套用", "ok");
    setTimeout(loadCaptureStatus, 1500);
  } catch (err) {
    setMessage("captureConfigMessage", `套用設定失敗：${err}`, "danger");
  }
}
