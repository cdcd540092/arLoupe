/* 串流與錄影控制 */

function captureApiBase() {
  return `${window.location.protocol}//${window.location.hostname}:7000`;
}

function updateCaptureActions(data) {
  const streaming = Boolean(data.streaming);
  const recording = Boolean(data.recording);

  document.getElementById("captureStreaming").textContent = streaming ? "運作中" : "未啟動";
  document.getElementById("captureStreaming").className = streaming ? "ok" : "warn";
  document.getElementById("captureRecording").textContent = recording ? "錄影中" : "未錄影";
  document.getElementById("captureRecording").className = recording ? "danger" : "";
  document.getElementById("captureSession").textContent = data.session_id || "-";
  document.getElementById("captureDate").textContent = data.recording_date || "-";

  document.getElementById("startStreamBtn").disabled = streaming;
  document.getElementById("stopStreamBtn").disabled = !streaming || recording;
  document.getElementById("startRecordBtn").disabled = recording;
  document.getElementById("stopRecordBtn").disabled = !recording;

  captureBusy = streaming || recording;
  updateCaptureConfigActions();
}

async function loadCaptureStatus() {
  try {
    const res = await fetch(`${captureApiBase()}/api/capture/status`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    updateCaptureActions(data);
    setMessage("captureMessage", "", "");
  } catch (err) {
    document.getElementById("captureStreaming").textContent = "讀取失敗";
    document.getElementById("captureStreaming").className = "danger";
    document.getElementById("captureRecording").textContent = "讀取失敗";
    document.getElementById("captureRecording").className = "danger";
    setMessage("captureMessage", "無法連線到 7000 capture API，請確認 arloupe-capture-api.service 是否運作。", "danger");
  }
}

async function postCapture(path, body = null) {
  const options = { method: "POST" };
  if (body !== null) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }

  const res = await fetch(`${captureApiBase()}${path}`, options);
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch (_) { data = { raw: text }; }

  if (!res.ok) {
    const detail = data.detail || data.raw || `HTTP ${res.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

async function startStream() {
  setMessage("captureMessage", "正在啟動串流...", "warn");
  try {
    await postCapture("/api/stream/start");
    setMessage("captureMessage", "串流已啟動", "ok");
    setTimeout(loadStreamViewer, 800);
  } catch (err) {
    setMessage("captureMessage", `啟動串流失敗：${err}`, "danger");
  } finally {
    loadCaptureStatus();
  }
}

async function stopStream() {
  if (!confirm("停止串流？")) return;
  setMessage("captureMessage", "正在停止串流...", "warn");
  try {
    await postCapture("/api/stream/stop");
    setMessage("captureMessage", "串流已停止", "ok");
  } catch (err) {
    setMessage("captureMessage", `停止串流失敗：${err}`, "danger");
  } finally {
    loadCaptureStatus();
  }
}

async function startRecording() {
  setMessage("captureMessage", "正在開始錄影...", "warn");
  try {
    const data = await postCapture("/api/capture/start", {});
    setMessage("captureMessage", `錄影已開始：${data.session_id || ""}`, "ok");
  } catch (err) {
    setMessage("captureMessage", `開始錄影失敗：${err}`, "danger");
  } finally {
    loadCaptureStatus();
  }
}

async function stopRecording() {
  if (!confirm("停止錄影？")) return;
  setMessage("captureMessage", "正在停止錄影並收尾 MP4...", "warn");
  try {
    const data = await postCapture("/api/capture/stop");
    setMessage("captureMessage", `錄影已停止：${data.session_id || ""}`, "ok");
  } catch (err) {
    setMessage("captureMessage", `停止錄影失敗：${err}`, "danger");
  } finally {
    loadCaptureStatus();
  }
}
