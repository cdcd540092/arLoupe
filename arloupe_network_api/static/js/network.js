/* 網路模式、Wi-Fi 與背景任務 */

function updateModeActions(mode) {
  const toHotspotBtn = document.getElementById("toHotspotBtn");
  const toWifiBtn = document.getElementById("toWifiBtn");

  if (!toHotspotBtn || !toWifiBtn) return;

  if (mode === "wifi") {
    toHotspotBtn.disabled = false;
    toWifiBtn.disabled = true;
  } else if (mode === "hotspot") {
    toHotspotBtn.disabled = true;
    toWifiBtn.disabled = false;
  } else {
    toHotspotBtn.disabled = false;
    toWifiBtn.disabled = false;
  }
}

async function loadStatus() {
  const modeEl = document.getElementById("mode");
  const ipv4El = document.getElementById("ipv4");
  const accessUrlEl = document.getElementById("accessUrl");
  const dhcpEl = document.getElementById("dhcp");

  if (!modeEl || !ipv4El || !accessUrlEl || !dhcpEl) return;

  try {
    const res = await fetch("/api/network/status");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    currentMode = data.mode || "unknown";

    modeEl.textContent = currentMode;
    ipv4El.textContent = data.ipv4 || "未知";
    accessUrlEl.textContent = data.access_url || "未知";
    dhcpEl.textContent = data.hotspot_dhcp || "unknown";

    modeEl.className =
      (currentMode === "hotspot" || currentMode === "wifi")
        ? "ok"
        : "warn";

    updateModeActions(currentMode);
  } catch (err) {
    currentMode = "unknown";
    modeEl.textContent = "讀取失敗";
    modeEl.className = "danger";
    updateModeActions("unknown");
  }
}

async function loadJobStatus() {
  try {
    const res = await fetch("/api/network/job/status");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    const statusEl = document.getElementById("jobStatus");

    if (!statusEl) return;

    statusEl.textContent = data.status || "unknown";
    statusEl.className =
      data.status === "success"
        ? "ok"
        : data.status === "failed"
          ? "danger"
          : data.status === "running"
            ? "warn"
            : "";

    document.getElementById("jobStep").textContent =
      data.step || "-";

    document.getElementById("jobMessage").textContent =
      data.message || "-";

    document.getElementById("jobSuggestion").textContent =
      data.suggestion || "-";

    document.getElementById("jobAccessUrl").textContent =
      data.access_url || "-";

    document.getElementById("jobError").textContent =
      data.error || "-";

    document.getElementById("jobRaw").textContent =
      JSON.stringify(data, null, 2);

    if (["success", "failed", "idle"].includes(data.status)) {
      stopJobPolling();
    }
  } catch (err) {
    const statusEl = document.getElementById("jobStatus");
    const errorEl = document.getElementById("jobError");

    if (statusEl) {
      statusEl.textContent = "讀取失敗";
      statusEl.className = "danger";
    }

    if (errorEl) {
      errorEl.textContent = String(err);
    }
  }
}

function startJobPolling() {
  stopJobPolling();
  loadJobStatus();
  jobPollTimer = setInterval(loadJobStatus, 2000);
}

function stopJobPolling() {
  if (jobPollTimer) {
    clearInterval(jobPollTimer);
    jobPollTimer = null;
  }
}

async function clearJobStatus() {
  try {
    await fetch("/api/network/job/clear", {
      method: "POST"
    });
  } finally {
    loadJobStatus();
  }
}

async function switchToHotspot() {
  if (!confirm("切換到熱點模式？")) return;

  setMessage("modeMessage", "正在切換到熱點...", "warn");

  try {
    const res = await fetch("/api/network/hotspot", {
      method: "POST"
    });

    const data = await res.json();

    setMessage(
      "modeMessage",
      data.message || "已送出切換指令",
      "warn"
    );

    startJobPolling();
  } catch (err) {
    setMessage(
      "modeMessage",
      "指令可能已送出，請改連 arLoupe-Setup。",
      "warn"
    );
  }
}

async function switchToDefaultWifi() {
  if (!confirm("切回預設 Wi-Fi？")) return;

  setMessage("modeMessage", "正在切回 Wi-Fi...", "warn");

  try {
    const res = await fetch("/api/network/wifi", {
      method: "POST"
    });

    const data = await res.json();

    setMessage(
      "modeMessage",
      data.message || "已送出切換指令",
      "warn"
    );

    startJobPolling();
  } catch (err) {
    setMessage(
      "modeMessage",
      "指令可能已送出，請改連外部 Wi-Fi。",
      "warn"
    );
  }
}

async function scanWifi() {
  const wifiCards = document.getElementById("wifiCards");
  const scanButton = document.getElementById("scanButton");
  const scanSourceEl = document.getElementById("scanSource");

  if (!wifiCards || !scanButton || !scanSourceEl) return;

  setMessage("wifiMessage", "掃描中...", "warn");
  scanButton.disabled = true;
  wifiCards.innerHTML =
    `<div class="text-secondary">掃描中...</div>`;

  try {
    const res = await fetch("/api/network/wifi/scan");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();

    wifiCards.innerHTML = "";
    scanSourceEl.textContent =
      `${data.scan_strategy || "未知"}｜${data.mode || "unknown"}`;

    if (!data.networks || data.networks.length === 0) {
      wifiCards.innerHTML =
        `<div class="text-secondary">找不到 Wi-Fi。</div>`;

      setMessage("wifiMessage", "找不到 Wi-Fi", "warn");
      return;
    }

    data.networks.forEach((net) => renderWifiCard(net));

    setMessage(
      "wifiMessage",
      `掃描完成，共 ${data.networks.length} 個`,
      "ok"
    );
  } catch (err) {
    wifiCards.innerHTML =
      `<div class="danger">掃描失敗：${escapeHtml(String(err))}</div>`;

    setMessage("wifiMessage", "掃描失敗", "danger");
  } finally {
    scanButton.disabled = false;
  }
}

function renderWifiCard(net) {
  const wifiCards = document.getElementById("wifiCards");
  if (!wifiCards) return;

  const id = cssSafeId(net.ssid);
  const card = document.createElement("div");

  card.className =
    "wifiCard" + (net.active ? " active" : "");

  const savedBadge = net.saved
    ? `<span class="badge bg-success-lt text-success me-1">已儲存</span>`
    : `<span class="badge bg-warning-lt text-warning me-1">未儲存</span>`;

  const activeBadge = net.active
    ? `<span class="badge bg-success-lt text-success me-1">目前連線</span>`
    : "";

  const connectionBadge = net.connection_name
    ? `<span class="badge bg-secondary-lt text-secondary me-1">${escapeHtml(net.connection_name)}</span>`
    : "";

  const connectButton = net.active
    ? ""
    : net.saved
      ? `
        <button
          type="button"
          class="btn btn-primary btn-sm"
          onclick='connectSavedWifi(
            ${escapeHtml(JSON.stringify(net.ssid))},
            ${escapeHtml(JSON.stringify(net.connection_name || ""))}
          )'
        >
          連線
        </button>
      `
      : `
        <button
          type="button"
          class="btn btn-primary btn-sm"
          onclick='showPasswordPanel(${escapeHtml(JSON.stringify(id))})'
        >
          輸入密碼
        </button>
      `;

  card.innerHTML = `
    <div class="wifiHeader">
      <div>
        <div class="ssid">${escapeHtml(net.ssid)}</div>
        <div class="mt-1">
          ${savedBadge}
          ${activeBadge}
          ${connectionBadge}
        </div>
      </div>

      <div class="buttonRow">
        ${connectButton}

        ${
          net.saved
            ? `
              <button
                type="button"
                class="btn btn-outline-secondary btn-sm"
                onclick='showPasswordPanel(${escapeHtml(JSON.stringify(id))})'
              >
                重新輸入密碼
              </button>
            `
            : ""
        }

        ${
          net.saved
            ? `
              <button
                type="button"
                class="btn btn-outline-danger btn-sm"
                onclick='forgetWifi(
                  ${escapeHtml(JSON.stringify(net.ssid))},
                  ${escapeHtml(JSON.stringify(net.connection_name || ""))}
                )'
              >
                刪除
              </button>
            `
            : ""
        }
      </div>
    </div>

    <div class="wifiMeta">
      訊號：${escapeHtml(formatSignal(net))}
      ｜ 安全性：${escapeHtml(formatSecurity(net))}
      ｜ 來源：${escapeHtml(formatScanSource(net.scan_source))}
    </div>

    <div id="panel-${id}" class="passwordPanel">
      <div class="mb-3">
        <label
          class="form-label"
          for="ssid-${id}"
        >
          SSID
        </label>

        <input
          id="ssid-${id}"
          class="form-control"
          value="${escapeHtml(net.ssid)}"
        />
      </div>

      <div class="mb-3">
        <label
          class="form-label"
          for="password-${id}"
        >
          Wi-Fi 密碼
        </label>

        <input
          id="password-${id}"
          class="form-control"
          type="password"
          placeholder="請輸入 Wi-Fi 密碼"
        />
      </div>

      <div class="buttonRow">
        <button
          type="button"
          class="btn btn-primary"
          onclick='connectWithPassword(${escapeHtml(JSON.stringify(id))})'
        >
          連線
        </button>

        <button
          type="button"
          class="btn btn-outline-secondary"
          onclick='hidePasswordPanel(${escapeHtml(JSON.stringify(id))})'
        >
          取消
        </button>
      </div>
    </div>
  `;

  wifiCards.appendChild(card);
}

function showPasswordPanel(id) {
  const panel = document.getElementById(`panel-${id}`);
  if (!panel) return;

  panel.style.display = "block";

  const passwordEl = document.getElementById(`password-${id}`);
  if (passwordEl) passwordEl.focus();
}

function hidePasswordPanel(id) {
  const panel = document.getElementById(`panel-${id}`);
  if (panel) panel.style.display = "none";
}

async function connectSavedWifi(ssid, connectionName) {
  if (!confirm(`連線到 ${ssid || connectionName}？`)) return;

  setMessage(
    "wifiMessage",
    `正在連線到 ${ssid || connectionName}...`,
    "warn"
  );

  await clearJobStatus();

  try {
    const res = await fetch(
      "/api/network/wifi/connect-saved",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ssid: ssid,
          connection_name: connectionName
        })
      }
    );

    const data = await res.json();

    setMessage(
      "wifiMessage",
      data.message || "已開始連線",
      "warn"
    );

    startJobPolling();
  } catch (err) {
    setMessage(
      "wifiMessage",
      "指令可能已送出，請查看是否已切換 Wi-Fi。",
      "warn"
    );
  }
}

async function connectWithPassword(id) {
  const ssidEl = document.getElementById(`ssid-${id}`);
  const passwordEl = document.getElementById(`password-${id}`);

  if (!ssidEl || !passwordEl) return;

  const ssid = ssidEl.value.trim();
  const password = passwordEl.value;

  if (!ssid) {
    alert("SSID 不可為空");
    return;
  }

  if (!confirm(`連線到 ${ssid}？`)) return;

  setMessage(
    "wifiMessage",
    `正在連線到 ${ssid}...`,
    "warn"
  );

  await clearJobStatus();

  try {
    const res = await fetch(
      "/api/network/wifi/connect",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ssid: ssid,
          password: password
        })
      }
    );

    const data = await res.json();

    setMessage(
      "wifiMessage",
      data.message || "已開始連線",
      "warn"
    );

    startJobPolling();
  } catch (err) {
    setMessage(
      "wifiMessage",
      "指令可能已送出，請查看是否已切換 Wi-Fi。",
      "warn"
    );
  }
}

async function forgetWifi(ssid, connectionName) {
  if (!confirm(`刪除 ${ssid || connectionName}？`)) return;

  setMessage(
    "wifiMessage",
    `正在刪除 ${ssid || connectionName}...`,
    "warn"
  );

  await clearJobStatus();

  try {
    const res = await fetch(
      "/api/network/wifi/forget",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ssid: ssid,
          connection_name: connectionName
        })
      }
    );

    const data = await res.json();

    setMessage(
      "wifiMessage",
      data.message || "已送出刪除指令",
      "warn"
    );

    startJobPolling();
    setTimeout(scanWifi, 2500);
  } catch (err) {
    setMessage(
      "wifiMessage",
      `刪除失敗：${String(err)}`,
      "danger"
    );
  }
}
