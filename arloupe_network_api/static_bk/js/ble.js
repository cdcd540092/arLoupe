/* arLoupe BLE 控制 */

async function runBleRequest(url, options = {}) {
  const res = await fetch(url, options);
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch (_) { data = { raw: text }; }

  if (!res.ok) {
    const detail = data.detail || data.raw || `HTTP ${res.status}`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function updateBleResult(data) {
  const ok = Boolean(data.ok);
  document.getElementById("bleStatus").textContent = ok ? "正常" : "失敗";
  document.getElementById("bleStatus").className = ok ? "ok" : "danger";
  document.getElementById("bleLastCommand").textContent = data.command || "-";
  document.getElementById("bleRaw").textContent = JSON.stringify(data, null, 2);

  const message = data.stdout || data.stderr || data.message || "完成";
  setMessage("bleMessage", message, ok ? "ok" : "danger");
}

async function sendBleCommand(command, needConfirm = false) {
  if (needConfirm && !confirm(`送出 ${command} 指令？`)) return;

  setMessage("bleMessage", `正在送出 ${command}...`, "warn");
  document.getElementById("bleLastCommand").textContent = command;

  try {
    const data = await runBleRequest("/api/ble/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: command })
    });
    updateBleResult(data);
  } catch (err) {
    document.getElementById("bleStatus").textContent = "失敗";
    document.getElementById("bleStatus").className = "danger";
    document.getElementById("bleRaw").textContent = String(err);
    setMessage("bleMessage", `BLE 指令失敗：${err}`, "danger");
  }
}

async function loadBleStatus() {
  setMessage("bleMessage", "正在讀取 BLE 狀態...", "warn");
  try {
    const data = await runBleRequest("/api/ble/status");
    updateBleResult(data);
  } catch (err) {
    document.getElementById("bleStatus").textContent = "讀取失敗";
    document.getElementById("bleStatus").className = "danger";
    document.getElementById("bleRaw").textContent = String(err);
    setMessage("bleMessage", `BLE 狀態讀取失敗：${err}`, "danger");
  }
}

async function loadBleServices() {
  setMessage("bleMessage", "正在讀取 BLE 服務...", "warn");
  try {
    const data = await runBleRequest("/api/ble/services");
    updateBleResult(data);
  } catch (err) {
    document.getElementById("bleRaw").textContent = String(err);
    setMessage("bleMessage", `BLE 服務讀取失敗：${err}`, "danger");
  }
}
