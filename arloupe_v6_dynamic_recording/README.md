# arLoupe V6：常駐 SRT 串流 + 動態開關錄影

這版是「版本 B」方向：

```text
開啟程式
  ↓
先只啟動 SRT 串流，不錄影
  ↓
按 r 中途開始錄影
  ↓
按 s 停止錄影，SRT 串流維持不中斷
  ↓
按 q 結束整個程式
```

## 重要差異

V5 是用 `gst-launch-1.0` 一次建立「錄影 + 串流」pipeline。  
V6 改成 Python GStreamer 控制：

```text
v4l2src
  ↓
videoconvert
  ↓
x264enc
  ↓
h264parse
  ↓
tee
  ├─ SRT 串流分支：常駐
  └─ 錄影分支：按 r 時動態新增，按 s 時移除
```

所以按 `s` 停止錄影時，理論上 SRT 串流不需要整條重啟。

## 安裝系統套件

V6 需要 Python GStreamer，不是 pip 套件。

```bash
sudo apt update
sudo apt install -y python3-gi python3-gst-1.0 gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0
```

如果你的 pipeline 缺少 `x264enc`、`srtsink`、`splitmuxsink` 等元件，可能還需要：

```bash
sudo apt install -y \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav
```

## 執行

```bash
cd arloupe_v6_dynamic_recording
python3 start_capture.py
```

啟動後會看到：

```text
Command:
  r = start recording
  s = stop recording
  q = quit
```

操作：

```text
r：開始錄影
s：停止錄影
q：結束程式
```

## config.py 常改設定

### 預設只串流，不錄影

```python
START_RECORDING_ON_BOOT = False
```

### 開機後立刻開始錄影

```python
START_RECORDING_ON_BOOT = True
```

### 每段影片長度

```python
SEGMENT_SECONDS = 300
```

測試時可以改成：

```python
SEGMENT_SECONDS = 10
```

### SRT 目標

```python
MEDIA_SERVER_IP = "192.168.1.174"
SRT_PORT = 8890
STREAM_PATH = "arloupe"
```

PI5 會推到：

```text
srt://MEDIA_SERVER_IP:SRT_PORT?streamid=publish:STREAM_PATH
```

## 錄影輸出

每次按 `r` 開始錄影，都會建立新的 session。

例如：

```text
/home/user/arloupe_data/recordings/2026-05-18/
├── session_20260518_203000.json
├── 20260518_203000_arloupe01_seg00000.mp4
├── 20260518_203000_arloupe01_seg00000.json
├── 20260518_203000_arloupe01_seg00001.mp4
└── 20260518_203000_arloupe01_seg00001.json
```

錄影過程中會先看到暫存檔：

```text
20260518_203000_arloupe01_seg00000.mp4.tmp
```

完成後才會改成：

```text
20260518_203000_arloupe01_seg00000.mp4
```

所以之後 uploader 只要處理 `.mp4`，不要處理 `.mp4.tmp`。

## 注意事項

這版是正式架構方向，但因為改成 Python GStreamer 動態控制，第一次在 PI5 上跑時需要實測：

1. 按 `r` 後是否正常產生 `.mp4.tmp`
2. 按 `s` 後最後一段是否能正確轉成 `.mp4`
3. 按 `s` 的瞬間 SRT 串流是否真的不中斷
4. `metadata_*.log` 是否有錯誤
5. 終端是否出現 GStreamer error / warning

如果停止錄影後最後一段 MP4 沒收好，可以先把 `config.py` 裡的等待時間調高：

```python
RECORD_STOP_EOS_WAIT_SECONDS = 5.0
```

## 測試影片資訊

```bash
ffprobe -hide_banner -select_streams v:0 \
  -show_entries stream=width,height,avg_frame_rate,r_frame_rate,nb_frames,duration,bit_rate \
  -of default=noprint_wrappers=1 \
  /home/user/arloupe_data/recordings/日期/影片檔.mp4
```

## V6 finalize 修正版：最後一段正常收尾

這版停止錄影時不會直接把最後的 `.mp4.tmp` 改成 `.mp4`。

流程改成：

```text
按 s 停止錄影
  ↓
阻擋錄影分支後續 buffer
  ↓
對錄影分支送 EOS
  ↓
等待 splitmuxsink / mp4mux 寫完 MP4 索引
  ↓
用 ffprobe 確認影片可播放
  ↓
成功才改名 .mp4.tmp → .mp4
  ↓
產生同名 metadata JSON
```

如果超過 `RECORD_FINALIZE_WAIT_SECONDS` 還是無法被 ffprobe 讀取，會改成：

```text
xxx.mp4.tmp.broken
```

這代表該段沒有正常收尾，不會被當成正式影片，也不會產生 metadata 或進入上傳流程。

可調參數在 `config.py`：

```python
RECORD_STOP_EOS_WAIT_SECONDS = 1.0
RECORD_FINALIZE_WAIT_SECONDS = 15.0
RECORD_FINALIZE_POLL_SECONDS = 0.5
FFPROBE_BIN = "ffprobe"
```

如果最後一段檔案較大或設備寫入較慢，可以把 `RECORD_FINALIZE_WAIT_SECONDS` 調到 20～30 秒。
