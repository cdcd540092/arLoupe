/* 即時串流播放器 */

function streamViewerUrl() {
  return `${window.location.protocol}//${window.location.hostname}:8889/arloupe`;
}

function loadStreamViewer() {
  const frame = document.getElementById("streamFrame");
  const url = streamViewerUrl();

  if (!frame) return;

  frame.src = url;
  document.getElementById("streamViewerUrlText").textContent = url;
  setMessage("streamViewerMessage", `已載入即時畫面：${url}`, "ok");
}

function reloadStreamViewer() {
  const frame = document.getElementById("streamFrame");
  if (!frame) return;

  if (!frame.src) {
    loadStreamViewer();
    return;
  }

  const currentUrl = frame.src;
  frame.src = "";
  setTimeout(() => {
    frame.src = currentUrl;
  }, 200);

  setMessage("streamViewerMessage", "已重新載入即時畫面", "ok");
}

function openStreamViewer() {
  window.open(streamViewerUrl(), "_blank");
}
