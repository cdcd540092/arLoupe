/* 儲存空間與自動清理 */

async function loadStorageStatus() {
  try {
    const res = await fetch("/api/storage/status");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const storage = data.storage || data;

    document.getElementById("storageFree").textContent = `${storage.free_gb ?? "?"} GB`;
    document.getElementById("storageUsed").textContent = `${storage.used_gb ?? "?"} GB`;
    document.getElementById("storageTotal").textContent = `${storage.total_gb ?? "?"} GB`;
    document.getElementById("storagePercent").textContent = `${storage.used_percent ?? "?"}%`;
    document.getElementById("cleanupRaw").textContent = JSON.stringify(data, null, 2);
    setMessage("storageMessage", `容量已更新：剩餘 ${storage.free_gb ?? "?"} GB`, "ok");
  } catch (err) {
    setMessage("storageMessage", `容量讀取失敗：${err}`, "danger");
  }
}

async function loadCleanupSettings() {
  try {
    const res = await fetch("/api/storage/cleanup/settings");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const s = data.settings || {};

    document.getElementById("cleanupRetentionDays").value = s.retention_days ?? 7;
    document.getElementById("cleanupLowFreeGb").value = s.low_free_gb ?? 20;
    document.getElementById("cleanupTargetFreeGb").value = s.target_free_gb ?? 30;
    document.getElementById("cleanupMaxDeleteSessions").value = s.max_delete_sessions ?? 0;
    document.getElementById("cleanupRaw").textContent = JSON.stringify(data, null, 2);
    setMessage("storageMessage", "清理設定已讀取", "ok");
  } catch (err) {
    setMessage("storageMessage", `清理設定讀取失敗：${err}`, "danger");
  }
}

async function saveCleanupSettings() {
  const payload = {
    retention_days: Number(document.getElementById("cleanupRetentionDays").value || 7),
    low_free_gb: Number(document.getElementById("cleanupLowFreeGb").value || 20),
    target_free_gb: Number(document.getElementById("cleanupTargetFreeGb").value || 30),
    max_delete_sessions: Number(document.getElementById("cleanupMaxDeleteSessions").value || 0),
    delete_pending_when_critical: false
  };

  setMessage("storageMessage", "正在儲存清理設定...", "warn");
  try {
    const res = await fetch("/api/storage/cleanup/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(data.detail || data));
    document.getElementById("cleanupRaw").textContent = JSON.stringify(data, null, 2);
    setMessage("storageMessage", "清理設定已儲存", "ok");
  } catch (err) {
    setMessage("storageMessage", `清理設定儲存失敗：${err}`, "danger");
  }
}

function renderCleanupPreview(data) {
  const box = document.getElementById("cleanupPreview");
  const candidates = data.candidates || [];
  box.innerHTML = "";

  if (candidates.length === 0) {
    box.innerHTML = `<div class="small">沒有符合條件的可清理 session。</div>`;
    return;
  }

  candidates.slice(0, 20).forEach(item => {
    const div = document.createElement("div");
    div.className = "cleanupItem";
    div.innerHTML = `
      <div class="cleanupItemTitle">${escapeHtml(item.recording_date)} ｜ ${escapeHtml(item.session_id)}</div>
      <div class="small">
        ${escapeHtml(String(item.video_count || 0))} 段 ｜ ${escapeHtml(String(item.size_mb || 0))} MB ｜ ${escapeHtml(String(item.age_days || "?"))} 天前
      </div>
    `;
    box.appendChild(div);
  });

  if (candidates.length > 20) {
    const more = document.createElement("div");
    more.className = "small";
    more.textContent = `還有 ${candidates.length - 20} 個 session 未顯示。`;
    box.appendChild(more);
  }
}

async function previewCleanup() {
  setMessage("storageMessage", "正在預覽可清理資料...", "warn");
  try {
    const res = await fetch("/api/storage/cleanup/preview");
    const data = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(data.detail || data));
    document.getElementById("cleanupRaw").textContent = JSON.stringify(data, null, 2);
    renderCleanupPreview(data);
    setMessage("storageMessage", `可清理 ${data.candidate_count || 0} 個 session，約 ${data.freeable_gb || 0} GB`, "ok");
    loadStorageStatus();
  } catch (err) {
    setMessage("storageMessage", `清理預覽失敗：${err}`, "danger");
  }
}

async function runCleanup() {
  if (!confirm("確定要刪除已上傳且超過保留天數的舊錄影？\n\n此動作無法復原。")) return;

  setMessage("storageMessage", "正在執行清理...", "warn");
  try {
    const res = await fetch("/api/storage/cleanup/run", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(data.detail || data));
    document.getElementById("cleanupRaw").textContent = JSON.stringify(data, null, 2);
    setMessage("storageMessage", `清理完成：刪除 ${data.deleted_sessions || 0} 個 session，釋放 ${data.freed_gb || 0} GB`, "ok");
    await loadStorageStatus();
    await previewCleanup();
    await loadVideoList(true);
  } catch (err) {
    setMessage("storageMessage", `清理失敗：${err}`, "danger");
  }
}
