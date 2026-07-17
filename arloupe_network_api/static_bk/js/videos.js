/* 錄影日期、Session、影片與 Metadata */

function videoPanelId(item, suffix) {
  return `${suffix}-${cssSafeId(item.recording_date + "-" + item.filename)}`;
}

function updateVideoDateSelect(availableDates, selectedDate) {
  const select = document.getElementById("videoDateSelect");
  if (!select) return;

  const currentValue = select.value;
  const nextValue = selectedDate || currentValue || "";
  select.innerHTML = "";

  const latestOption = document.createElement("option");
  latestOption.value = "";
  latestOption.textContent = availableDates && availableDates.length > 0
    ? `最新日期（${availableDates[0]}）`
    : "最新日期";
  select.appendChild(latestOption);

  (availableDates || []).forEach(dateText => {
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
  } else if (availableDates && availableDates.includes(nextValue)) {
    select.value = nextValue;
  } else {
    select.value = "";
  }
}

async function loadVideoList(keepSelectedDate = false) {
  const videoList = document.getElementById("videoList");
  const dateSelect = document.getElementById("videoDateSelect");
  const selectedDate = keepSelectedDate && dateSelect ? dateSelect.value : "";
  const query = selectedDate ? `?date=${encodeURIComponent(selectedDate)}&limit=300` : "?limit=300";

  setMessage("videoMessage", "載入中...", "warn");
  videoList.innerHTML = `<div class="small">載入中...</div>`;

  try {
    const res = await fetch(`/api/videos/list${query}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    updateVideoDateSelect(data.available_dates || [], data.selected_date || selectedDate || "");
    videoList.innerHTML = "";

    if (!data.dates || data.dates.length === 0) {
      videoList.innerHTML = `<div class="small">目前沒有錄影檔案。</div>`;
      setMessage("videoMessage", "目前沒有錄影檔案", "warn");
      return;
    }

    data.dates.forEach(group => renderVideoDateGroup(group));

    const selectedText = data.selected_date === "all"
      ? "全部日期"
      : (data.selected_date || "最新日期");
    setMessage(
      "videoMessage",
      `${selectedText}｜${data.total_sessions || 0} 個 session，${data.total_videos || data.total || 0} 個影片`,
      "ok"
    );
  } catch (err) {
    videoList.innerHTML = `<div class="danger">載入失敗：${escapeHtml(String(err))}</div>`;
    setMessage("videoMessage", "錄影檔案載入失敗", "danger");
  }
}

function renderVideoDateGroup(group) {
  const videoList = document.getElementById("videoList");
  const title = document.createElement("div");
  title.className = "videoDate";
  title.textContent = `${group.date || "未知日期"} ｜ ${group.session_count || 0} 個 session ｜ ${group.video_count || 0} 段`;
  videoList.appendChild(title);

  (group.sessions || []).forEach(session => renderVideoSession(session, videoList));
}

function renderVideoSession(session, parent) {
  const details = document.createElement("details");
  details.className = "sessionCard";

  const startedAt = formatDateTime(session.started_at);
  const durationText = formatDuration(session.total_duration_seconds);
  const sizeText = `${session.total_size_mb || 0} MB`;
  const uploadText = session.upload_status || "unknown";
  const sessionId = session.session_id || "unknown";

  details.innerHTML = `
    <summary>
      <div class="sessionSummary">
        <div>
          <div class="sessionTitle">Session ${escapeHtml(sessionId)}</div>
          <div class="sessionMeta">${escapeHtml(startedAt)} ｜ ${session.segment_count || 0} 段 ｜ ${escapeHtml(sizeText)} ｜ ${escapeHtml(durationText)}</div>
        </div>
        <div>
          ${session.device_id ? `<span class="pill grayPill">${escapeHtml(session.device_id)}</span>` : ""}
          <span class="pill grayPill">${escapeHtml(uploadText)}</span>
          <span class="pill ${session.metadata_count === session.segment_count ? "okPill" : "warnPill"}">JSON ${session.metadata_count || 0}/${session.segment_count || 0}</span>
        </div>
      </div>
    </summary>
    <div class="sessionBody"></div>
  `;

  const body = details.querySelector(".sessionBody");
  (session.videos || []).forEach(item => renderVideoItem(item, body));
  parent.appendChild(details);
}

function renderVideoItem(item, parent) {
  const card = document.createElement("div");
  card.className = "videoCard";

  const playerId = videoPanelId(item, "player");
  const metaId = videoPanelId(item, "meta");
  const durationText = formatDuration(item.duration_seconds);
  const uploadText = item.upload_status || "unknown";
  const segText = item.segment_index !== null && item.segment_index !== undefined
    ? `seg${String(item.segment_index).padStart(5, "0")}`
    : "seg?";
  const metadataButton = item.metadata_exists
    ? `<button onclick='toggleVideoMetadata(${JSON.stringify(metaId)}, ${JSON.stringify(item.metadata_url)})'>Metadata</button>`
    : "";

  card.innerHTML = `
    <div class="videoHeader">
      <div>
        <div class="videoTitle">${escapeHtml(segText)} ｜ ${escapeHtml(item.filename)}</div>
        <div>
          ${item.metadata_exists ? `<span class="pill okPill">JSON</span>` : `<span class="pill warnPill">無 JSON</span>`}
          <span class="pill grayPill">${escapeHtml(uploadText)}</span>
        </div>
      </div>
      <div class="buttonRow">
        <button class="primary" onclick='toggleVideoPlayer(${JSON.stringify(playerId)}, ${JSON.stringify(item.url)})'>播放</button>
        <a href="${escapeHtml(item.download_url || item.url)}" download>
          <button type="button">下載</button>
        </a>
        ${metadataButton}
      </div>
    </div>
    <div class="videoMeta">
      大小：${escapeHtml(String(item.size_mb))} MB ｜ 時長：${escapeHtml(durationText)} ｜ 修改：${escapeHtml(item.modified_at || "-")}
    </div>
    <div id="${playerId}" class="videoPanel"></div>
    <div id="${metaId}" class="metaPanel">
      <pre>尚未載入</pre>
    </div>
  `;

  parent.appendChild(card);
}

function toggleVideoPlayer(panelId, url) {
  const panel = document.getElementById(panelId);
  if (!panel) return;

  if (panel.style.display === "block") {
    panel.style.display = "none";
    panel.innerHTML = "";
    return;
  }

  panel.style.display = "block";
  panel.innerHTML = `
    <video controls preload="metadata" src="${escapeHtml(url)}"></video>
  `;
}

async function toggleVideoMetadata(panelId, url) {
  const panel = document.getElementById(panelId);
  if (!panel) return;

  if (panel.style.display === "block") {
    panel.style.display = "none";
    return;
  }

  panel.style.display = "block";
  panel.innerHTML = `<pre>載入中...</pre>`;

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    panel.innerHTML = `<pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre>`;
  } catch (err) {
    panel.innerHTML = `<pre>Metadata 載入失敗：${escapeHtml(String(err))}</pre>`;
  }
}
