# arLoupe 手機版檢查紀錄 v8

## 測試尺寸

- 360 × 800
- 375 × 667
- 390 × 844
- 430 × 932
- 768 × 1024
- 844 × 390 橫向

## 檢查頁面

- arLoupe 即時串流與裝置控制
- 錄影檔案主從式預覽
- 網路設定與長 SSID
- 儲存管理
- 影像設定
- Metadata 長字串
- 長 Session ID 與長影片檔名

## 本版修正

- 手機與平板按鈕觸控高度提高到至少 44px。
- 即時畫面標題與載入按鈕分成上下兩列。
- 串流與錄影控制改為兩欄。
- Wi-Fi 操作按鈕不會被長 SSID 擠出畫面。
- SSID 含單引號或雙引號時，動態按鈕事件仍可正常執行。
- 輸入框使用 16px，避免 iPhone Safari 自動放大。
- 長影片檔名最多顯示兩行。
- Metadata、JSON 與錯誤內容不會造成整頁水平捲動。
- Capture 與 BLE 狀態更新不再覆蓋原本版面 class。
- 374px 以下的窄手機，影片資訊與日期工具列改為單欄。
- 手機橫向限制錄影預覽最大寬度，避免播放器過高。

## 部署

```bash
cd ~/arloupe_network_api

cp -a static \
  "static_backup_before_mobile_v8_$(date +%Y%m%d_%H%M%S)"

cp -a ~/arloupe_mobile_verified_v8/. static/

sudo systemctl restart arloupe-network-api.service
```

瀏覽器更新後請執行強制重新整理。


## v9 影像設定提醒修正

- 提醒改成「套用前提醒」標題與內容兩區。
- `capture_settings.json` 保持完整，不再逐字換行。
- 手機上兩段提醒文字會自然上下排列。
- 7000 影像服務提示保留。
