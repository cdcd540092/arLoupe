/* 共用狀態與工具函式 */

let currentMode = "unknown";
let jobPollTimer = null;
let captureBusy = false;

/**
 * 更新訊息文字與狀態色彩。
 * 保留元素原本的基礎 class，只切換 ok / warn / danger。
 */
function setMessage(elementId, text, className) {
  const el = document.getElementById(elementId);
  if (!el) return;

  el.textContent = text;
  el.classList.remove("ok", "warn", "danger");

  if (className) {
    el.classList.add(className);
  }
}

/**
 * 將來源元素的文字與狀態 class 同步到所有 data-mirror-for。
 *
 * 例如：
 * <span id="captureRecording">未錄影</span>
 * <span data-mirror-for="captureRecording"></span>
 */
function initStatusMirrors() {
  const mirrors = document.querySelectorAll("[data-mirror-for]");
  const sourceIds = new Set();

  mirrors.forEach((mirror) => {
    const sourceId = mirror.dataset.mirrorFor;
    if (sourceId) sourceIds.add(sourceId);
  });

  const syncSource = (sourceId) => {
    const source = document.getElementById(sourceId);
    if (!source) return;

    document
      .querySelectorAll(`[data-mirror-for="${CSS.escape(sourceId)}"]`)
      .forEach((mirror) => {
        mirror.textContent = source.textContent;

        mirror.classList.remove("ok", "warn", "danger");

        ["ok", "warn", "danger"].forEach((statusClass) => {
          if (source.classList.contains(statusClass)) {
            mirror.classList.add(statusClass);
          }
        });
      });
  };

  sourceIds.forEach((sourceId) => {
    const source = document.getElementById(sourceId);
    if (!source) return;

    syncSource(sourceId);

    const observer = new MutationObserver(() => {
      syncSource(sourceId);
    });

    observer.observe(source, {
      attributes: true,
      childList: true,
      characterData: true,
      subtree: true,
      attributeFilter: ["class"]
    });
  });
}

function cssSafeId(text) {
  return btoa(unescape(encodeURIComponent(text)))
    .replaceAll("=", "")
    .replaceAll("+", "-")
    .replaceAll("/", "_");
}

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatSignal(net) {
  if (net.signal_dbm) return `${net.signal}% (${net.signal_dbm} dBm)`;
  if (net.signal) return `${net.signal}%`;
  return "未知";
}

function formatSecurity(net) {
  return net.security || "未知";
}

function formatScanSource(source) {
  if (source === "iw-ap-force") return "iw";
  if (source === "nmcli-fallback") return "nmcli";
  if (source === "nmcli") return "nmcli";
  return source || "未知";
}

function formatDuration(seconds) {
  if (seconds === null || seconds === undefined || seconds === "") {
    return "未知";
  }

  const total = Math.round(Number(seconds));
  if (!Number.isFinite(total)) return "未知";

  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const sec = total % 60;

  if (h > 0) {
    return `${h} 小時 ${String(m).padStart(2, "0")} 分`;
  }

  if (m > 0) {
    return `${m} 分 ${String(sec).padStart(2, "0")} 秒`;
  }

  return `${sec} 秒`;
}

function formatDateTime(text) {
  if (!text) return "未知時間";
  return String(text).replace("T", " ");
}
