# arLoupe 錄影檔案主從式版面 v7

## 本版調整

錄影檔案頁改成：

- 桌面版
  - 左側：大型影片預覽、影片資訊、下載與 Metadata
  - 右側：日期選擇、Session 與影片選單
  - 右側清單可以獨立捲動
  - 左側預覽在桌面版保持可見

- 手機與平板
  - 上方：影片預覽
  - 下方：日期、Session 與影片清單
  - 點選影片後會平滑捲動回預覽
  - 按鈕與影片選項加大，方便觸控

## 後端

不需要修改 FastAPI 或 API。

沿用：

```text
GET /api/videos/list
item.url
item.download_url
item.metadata_url
```

## 安裝

假設解壓後位於：

```text
/home/user/arloupe_video_master_detail_v7
```

執行：

```bash
cd ~/arloupe_network_api

cp -a static \
  "static_backup_before_video_v7_$(date +%Y%m%d_%H%M%S)"

cp -a ~/arloupe_video_master_detail_v7/. static/

sudo systemctl restart arloupe-network-api.service
```

Windows 瀏覽器按：

```text
Ctrl + F5
```

## 注意

本壓縮包不包含 Tabler vendor 檔案，不會覆蓋：

```text
static/vendor/tabler/css/tabler.min.css
static/vendor/tabler/js/tabler.min.js
```
