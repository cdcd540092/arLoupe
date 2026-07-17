/* 頁面初始化與定期狀態更新 */

document.addEventListener("DOMContentLoaded", () => {
  loadStatus();
  loadStorageStatus();
  loadCleanupSettings();
  loadCaptureStatus();
  loadJobStatus();
  loadVideoList();
  loadBleStatus();
  loadCaptureConfig();

  // 每 5 秒更新一次串流與錄影狀態。
  setInterval(loadCaptureStatus, 5000);
});

window.addEventListener("beforeunload", () => {
  stopJobPolling();
});
