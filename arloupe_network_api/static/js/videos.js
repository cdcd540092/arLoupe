/* 錄影檔案：主從式預覽、Session 與影片選單 */

let selectedVideoContext = null;
let selectedVideoKey = "";
let selectedMetadataRequestId = 0;

/**
 * 建立影片的穩定識別值。
 */
function makeVideoKey(item, session, recordingDate) {
  return [
    recordingDate || item.recording_date || "",
    session.session_id || "",
    item.filename || ""
  ].join("|");
}

/**
 * 顯示片段編號。
 */
function formatSegmentLabel(item) {
  if (
    item.segment_index !== null &&
    item.segment_index !== undefined
  ) {
    return `seg${String(item.segment_index).padStart(5, "0")}`;
  }

  return "seg?";
}

/**
 * 更新日期選單。
 */
function updateVideoDateSelect(
  availableDates,
  selectedDate
) {
  const select = document.getElementById("videoDateSelect");
  if (!select) return;

  const currentValue = select.value;
  const nextValue =
    selectedDate || currentValue || "";

  select.innerHTML = "";

  const latestOption = document.createElement("option");
  latestOption.value = "";
  latestOption.textContent =
    availableDates && availableDates.length > 0
      ? `最新日期（${availableDates[0]}）`
      : "最新日期";

  select.appendChild(latestOption);

  (availableDates || []).forEach((dateText) => {
    const option = document.createElement("option");
    option.value = dateText;
    option.textContent = dateText;
    select.appendChild(option);
  });

  if (availableDates && availableDates.length > 1) {
    const allOption = document.createElement("option");
    allOption.value = "all";
    allOption.textContent = "全部日期";
    select.appendChild(allOption);
  }

  if (nextValue === "all") {
    select.value = "all";
  } else if (
    availableDates &&
    availableDates.includes(nextValue)
  ) {
    select.value = nextValue;
  } else {
    select.value = "";
  }
}

/**
 * 讀取錄影清單。
 */
async function loadVideoList(
  keepSelectedDate = false
) {
  const videoList = document.getElementById("videoList");
  const dateSelect =
    document.getElementById("videoDateSelect");

  if (!videoList) return;

  const selectedDate =
    keepSelectedDate && dateSelect
      ? dateSelect.value
      : "";

  const query = selectedDate
    ? `?date=${encodeURIComponent(selectedDate)}&limit=300`
    : "?limit=300";

  const previousSelectedKey = selectedVideoKey;

  setMessage("videoMessage", "載入中...", "warn");

  videoList.innerHTML =
    `<div class="text-secondary">載入中...</div>`;

  try {
    const res = await fetch(`/api/videos/list${query}`);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    updateVideoDateSelect(
      data.available_dates || [],
      data.selected_date || selectedDate || ""
    );

    videoList.innerHTML = "";

    const contexts = [];

    (data.dates || []).forEach((group, groupIndex) => {
      renderVideoDateGroup(
        group,
        videoList,
        contexts,
        groupIndex === 0
      );
    });

    if (contexts.length === 0) {
      clearSelectedVideo();

      videoList.innerHTML =
        `<div class="video-menu-empty">目前沒有錄影檔案。</div>`;

      setMessage(
        "videoMessage",
        "目前沒有錄影檔案",
        "warn"
      );

      return;
    }

    const preservedSelection = contexts.find(
      (context) => context.key === previousSelectedKey
    );

    selectVideoContext(
      preservedSelection || contexts[0],
      {
        scrollPreview: false
      }
    );

    const selectedText =
      data.selected_date === "all"
        ? "全部日期"
        : data.selected_date || "最新日期";

    setMessage(
      "videoMessage",
      `${selectedText}｜${data.total_sessions || 0} 個 Session，` +
      `${data.total_videos || data.total || 0} 個影片`,
      "ok"
    );
  } catch (err) {
    clearSelectedVideo();

    videoList.innerHTML =
      `<div class="danger">載入失敗：${escapeHtml(String(err))}</div>`;

    setMessage(
      "videoMessage",
      "錄影檔案載入失敗",
      "danger"
    );
  }
}

/**
 * 產生日期群組。
 */
function renderVideoDateGroup(
  group,
  parent,
  contexts,
  isFirstGroup
) {
  const dateGroup = document.createElement("section");
  dateGroup.className = "video-menu-date-group";

  const title = document.createElement("div");
  title.className = "video-menu-date-title";
  title.textContent =
    `${group.date || "未知日期"}｜` +
    `${group.session_count || 0} 個 Session｜` +
    `${group.video_count || 0} 段`;

  dateGroup.appendChild(title);

  (group.sessions || []).forEach((session, sessionIndex) => {
    renderVideoSessionMenu(
      session,
      group.date || "",
      dateGroup,
      contexts,
      isFirstGroup && sessionIndex === 0
    );
  });

  parent.appendChild(dateGroup);
}

/**
 * 產生 Session 折疊選單。
 */
function renderVideoSessionMenu(
  session,
  recordingDate,
  parent,
  contexts,
  shouldOpen
) {
  const details = document.createElement("details");
  details.className = "video-menu-session";
  details.open = Boolean(shouldOpen);

  const sessionId =
    session.session_id || "unknown";

  const summary = document.createElement("summary");
  summary.className = "video-menu-session-summary";

  const summaryMain = document.createElement("div");
  summaryMain.className = "video-menu-session-main";

  const title = document.createElement("div");
  title.className = "video-menu-session-title";
  title.textContent = `Session ${sessionId}`;

  const meta = document.createElement("div");
  meta.className = "video-menu-session-meta";
  meta.textContent =
    `${formatDateTime(session.started_at)}｜` +
    `${session.segment_count || 0} 段｜` +
    `${session.total_size_mb || 0} MB｜` +
    `${formatDuration(session.total_duration_seconds)}`;

  summaryMain.appendChild(title);
  summaryMain.appendChild(meta);

  const countBadge = document.createElement("span");
  countBadge.className =
    "badge bg-secondary-lt text-secondary";
  countBadge.textContent =
    `${session.segment_count || 0} 段`;

  summary.appendChild(summaryMain);
  summary.appendChild(countBadge);

  const body = document.createElement("div");
  body.className = "video-menu-session-body";

  (session.videos || []).forEach((item) => {
    const context = {
      item,
      session,
      recordingDate:
        recordingDate || item.recording_date || "",
      key: makeVideoKey(
        item,
        session,
        recordingDate
      )
    };

    contexts.push(context);

    const menuItem = createVideoMenuItem(context);
    body.appendChild(menuItem);
  });

  details.appendChild(summary);
  details.appendChild(body);
  parent.appendChild(details);
}

/**
 * 產生右側的單一影片選項。
 */
function createVideoMenuItem(context) {
  const { item } = context;

  const button = document.createElement("button");
  button.type = "button";
  button.className = "video-menu-item";
  button.dataset.videoKey = context.key;
  button.setAttribute("aria-current", "false");

  const heading = document.createElement("div");
  heading.className = "video-menu-item-heading";

  const segment = document.createElement("span");
  segment.className = "video-menu-item-segment";
  segment.textContent = formatSegmentLabel(item);

  const metadataBadge = document.createElement("span");
  metadataBadge.className = item.metadata_exists
    ? "badge bg-success-lt text-success"
    : "badge bg-warning-lt text-warning";

  metadataBadge.textContent =
    item.metadata_exists ? "JSON" : "無 JSON";

  heading.appendChild(segment);
  heading.appendChild(metadataBadge);

  const filename = document.createElement("div");
  filename.className = "video-menu-item-filename";
  filename.textContent = item.filename || "未命名影片";

  const meta = document.createElement("div");
  meta.className = "video-menu-item-meta";
  meta.textContent =
    `${formatDuration(item.duration_seconds)}｜` +
    `${item.size_mb ?? "?"} MB｜` +
    `${item.upload_status || "unknown"}`;

  button.appendChild(heading);
  button.appendChild(filename);
  button.appendChild(meta);

  button.addEventListener("click", () => {
    selectVideoContext(context, {
      scrollPreview: window.innerWidth < 992
    });
  });

  return button;
}

/**
 * 選取影片並更新左側預覽。
 */
function selectVideoContext(
  context,
  options = {}
) {
  if (!context || !context.item) return;

  const {
    scrollPreview = false
  } = options;

  selectedVideoContext = context;
  selectedVideoKey = context.key;

  document
    .querySelectorAll(".video-menu-item")
    .forEach((button) => {
      const isActive =
        button.dataset.videoKey === context.key;

      button.classList.toggle("active", isActive);
      button.setAttribute(
        "aria-current",
        isActive ? "true" : "false"
      );

      if (isActive) {
        const sessionDetails =
          button.closest(".video-menu-session");

        if (sessionDetails) {
          sessionDetails.open = true;
        }
      }
    });

  const { item, session, recordingDate } = context;

  const player =
    document.getElementById("videoPreviewPlayer");

  const placeholder =
    document.getElementById("videoPreviewPlaceholder");

  if (player) {
    player.pause();
    player.src = item.url || "";
    player.hidden = false;
    player.load();
  }

  if (placeholder) {
    placeholder.hidden = true;
  }

  const segmentLabel = formatSegmentLabel(item);

  setText(
    "selectedVideoTitle",
    `${segmentLabel}｜${item.filename || "未命名影片"}`
  );

  setText(
    "selectedVideoSubtitle",
    `${formatDateTime(session.started_at)}｜` +
    `${item.upload_status || "unknown"}`
  );

  setText(
    "selectedVideoSession",
    session.session_id || "-"
  );

  setText(
    "selectedVideoDate",
    recordingDate || item.recording_date || "-"
  );

  setText(
    "selectedVideoDuration",
    formatDuration(item.duration_seconds)
  );

  setText(
    "selectedVideoSize",
    `${item.size_mb ?? "?"} MB`
  );

  setText(
    "selectedVideoModified",
    item.modified_at || "-"
  );

  setText(
    "selectedVideoMetadataStatus",
    item.metadata_exists ? "有 JSON" : "無 JSON"
  );

  updateSelectedUploadBadge(
    item.upload_status || "unknown"
  );

  const downloadLink =
    document.getElementById("selectedVideoDownload");

  if (downloadLink) {
    downloadLink.href =
      item.download_url || item.url || "#";

    downloadLink.download =
      item.filename || "video.mp4";

    downloadLink.setAttribute(
      "aria-disabled",
      "false"
    );

    downloadLink.removeAttribute("tabindex");
  }

  const metadataButton =
    document.getElementById("selectedVideoMetadataBtn");

  if (metadataButton) {
    metadataButton.disabled =
      !item.metadata_exists || !item.metadata_url;
  }

  closeSelectedVideoMetadata();

  if (scrollPreview) {
    const previewPanel =
      document.querySelector(".video-preview-panel");

    if (previewPanel) {
      previewPanel.scrollIntoView({
        behavior: "smooth",
        block: "start"
      });
    }
  }
}

/**
 * 清除左側預覽。
 */
function clearSelectedVideo() {
  selectedVideoContext = null;
  selectedVideoKey = "";
  selectedMetadataRequestId += 1;

  const player =
    document.getElementById("videoPreviewPlayer");

  const placeholder =
    document.getElementById("videoPreviewPlaceholder");

  if (player) {
    player.pause();
    player.removeAttribute("src");
    player.load();
    player.hidden = true;
  }

  if (placeholder) {
    placeholder.hidden = false;
  }

  setText(
    "selectedVideoTitle",
    "尚未選擇影片"
  );

  setText(
    "selectedVideoSubtitle",
    "尚未選擇錄影片段。"
  );

  [
    "selectedVideoSession",
    "selectedVideoDate",
    "selectedVideoDuration",
    "selectedVideoSize",
    "selectedVideoModified",
    "selectedVideoMetadataStatus"
  ].forEach((id) => setText(id, "-"));

  updateSelectedUploadBadge("-");

  const downloadLink =
    document.getElementById("selectedVideoDownload");

  if (downloadLink) {
    downloadLink.href = "#";
    downloadLink.setAttribute(
      "aria-disabled",
      "true"
    );
    downloadLink.setAttribute("tabindex", "-1");
  }

  const metadataButton =
    document.getElementById("selectedVideoMetadataBtn");

  if (metadataButton) {
    metadataButton.disabled = true;
  }

  closeSelectedVideoMetadata();
}

/**
 * 顯示或收合目前影片的 Metadata。
 */
async function toggleSelectedVideoMetadata() {
  const panel =
    document.getElementById("selectedVideoMetadataPanel");

  const raw =
    document.getElementById("selectedVideoMetadataRaw");

  if (!panel || !raw) return;

  if (!panel.hidden) {
    closeSelectedVideoMetadata();
    return;
  }

  const context = selectedVideoContext;

  if (
    !context ||
    !context.item ||
    !context.item.metadata_exists ||
    !context.item.metadata_url
  ) {
    return;
  }

  panel.hidden = false;
  raw.textContent = "載入中...";

  const requestId = ++selectedMetadataRequestId;

  try {
    const res = await fetch(
      context.item.metadata_url
    );

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();

    if (requestId !== selectedMetadataRequestId) {
      return;
    }

    raw.textContent =
      JSON.stringify(data, null, 2);
  } catch (err) {
    if (requestId !== selectedMetadataRequestId) {
      return;
    }

    raw.textContent =
      `Metadata 載入失敗：${String(err)}`;
  }
}

/**
 * 收合 Metadata。
 */
function closeSelectedVideoMetadata() {
  selectedMetadataRequestId += 1;

  const panel =
    document.getElementById("selectedVideoMetadataPanel");

  const raw =
    document.getElementById("selectedVideoMetadataRaw");

  if (panel) {
    panel.hidden = true;
  }

  if (raw) {
    raw.textContent = "尚未載入";
  }
}

/**
 * 安全更新文字。
 */
function setText(elementId, text) {
  const element =
    document.getElementById(elementId);

  if (element) {
    element.textContent = text;
  }
}

/**
 * 更新上傳狀態 Badge。
 */
function updateSelectedUploadBadge(status) {
  const badge =
    document.getElementById("selectedVideoUploadBadge");

  if (!badge) return;

  badge.textContent = status || "-";

  badge.classList.remove(
    "bg-success-lt",
    "text-success",
    "bg-warning-lt",
    "text-warning",
    "bg-secondary-lt",
    "text-secondary"
  );

  const normalized =
    String(status || "").toLowerCase();

  if (
    normalized === "uploaded" ||
    normalized === "success" ||
    normalized === "done"
  ) {
    badge.classList.add(
      "bg-success-lt",
      "text-success"
    );
  } else if (
    normalized === "pending" ||
    normalized === "uploading"
  ) {
    badge.classList.add(
      "bg-warning-lt",
      "text-warning"
    );
  } else {
    badge.classList.add(
      "bg-secondary-lt",
      "text-secondary"
    );
  }
}

/**
 * 防止停用狀態的下載按鈕導向頁首。
 */
document.addEventListener("click", (event) => {
  const downloadLink =
    event.target.closest("#selectedVideoDownload");

  if (
    downloadLink &&
    downloadLink.getAttribute("aria-disabled") === "true"
  ) {
    event.preventDefault();
  }
});
