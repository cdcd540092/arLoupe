# arLoupe 前端拆分版

這個版本只做結構拆分，沒有修改既有 API 路徑、按鈕名稱或操作流程。

## 目錄

```text
arloupe_ui_split/
├─ index.html
├─ css/
│  └─ styles.css
└─ js/
   ├─ common.js
   ├─ network.js
   ├─ capture.js
   ├─ stream.js
   ├─ capture-config.js
   ├─ videos.js
   ├─ ble.js
   ├─ storage.js
   └─ main.js
```

## 各檔案用途

- `common.js`：共用狀態、訊息顯示、字串與時間格式化。
- `network.js`：目前網路狀態、熱點切換、Wi-Fi 掃描與連線任務。
- `capture.js`：串流、開始錄影、停止錄影與 Capture API。
- `stream.js`：MediaMTX 即時畫面的 iframe 載入與重新整理。
- `capture-config.js`：FPS、位元率、分段時間等設定。
- `videos.js`：錄影日期、Session、影片播放、下載與 Metadata。
- `ble.js`：倍率、LED、色溫、格柵、拍照、錄影鍵與電源。
- `storage.js`：容量狀態、清理設定、預覽與執行刪除。
- `main.js`：頁面啟動時載入資料，以及每 5 秒更新影像狀態。

## 部署到 Pi 5

先備份原本的 HTML 與靜態檔案目錄，再把整個資料夾結構一起放到目前 Web 服務的靜態網站根目錄。不要只複製 `index.html`，`css` 與 `js` 子目錄也必須一併保留。

例如原本網站根目錄是 `/opt/arloupe-network-ui/static/`：

```bash
sudo cp -a /opt/arloupe-network-ui/static /opt/arloupe-network-ui/static_backup_$(date +%Y%m%d_%H%M%S)
sudo cp -a arloupe_ui_split/. /opt/arloupe-network-ui/static/
```

實際路徑請以目前提供這個 HTML 的服務設定為準。

## Windows 本機檢查畫面

在 PowerShell 進入資料夾後：

```powershell
cd arloupe_ui_split
py -m http.server 8080
```

瀏覽器開啟 `http://127.0.0.1:8080`。本機只能檢查畫面與 JavaScript 是否載入；因為 API 不在 Windows 本機，網路、錄影與 BLE 功能可能顯示連線失敗，屬正常現象。

## 注意

目前仍保留 HTML 中的 `onclick` 與 `onchange`，目的是降低第一次拆分的風險。下一階段再改成 Vue 3 元件與事件綁定會比較安全。
