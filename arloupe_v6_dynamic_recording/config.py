

from pathlib import Path


# =========================
# 使用者 / 設備
# =========================

USER_ID = "user001"
DEVICE_ID = "arloupe01"


# =========================
# 資料夾
# =========================

BASE_RECORDING_DIR = Path("/home/user/arloupe_data/recordings")
BASE_LOG_DIR = Path("/home/user/arloupe_data/logs")


# =========================
# 影像設定
# =========================
'''
#HDMI INPUT
VIDEO_DEVICE = "/dev/video0"
WIDTH = 1920
HEIGHT = 1080
INPUT_FPS = 60
FPS = 60

INPUT_PIXEL_FORMAT = "UYVY"
ENCODE_PIXEL_FORMAT = "I420"
CODEC = "H.264"

BITRATE_KBPS = 8000
KEY_INT_MAX = 60

'''
#HDMI TO USB CAPTURE
VIDEO_DEVICE = "/dev/video8"  # 之後建議改成 /dev/v4l/by-id/... 固定路徑
WIDTH = 1920
HEIGHT = 1080
INPUT_FPS = 30
FPS = 30

INPUT_PIXEL_FORMAT = "MJPG"
ENCODE_PIXEL_FORMAT = "I420"
CODEC = "H.264"

BITRATE_KBPS = 10000
KEY_INT_MAX = 30

# =========================
# 錄影設定
# =========================

# 影片時常
SEGMENT_SECONDS = 11

# 分段補償秒數：使用者設定不變，GStreamer 內部多給一點時間，避免實際影片少約 1 秒
SEGMENT_TIME_PADDING_SECONDS = 0.5

START_RECORDING_ON_BOOT = False


RECORD_CONTINUOUS = True
RECORD_SEGMENT_COUNT = 1


RECORDING_TEMP_SUFFIX = ".tmp"


RECORD_STOP_EOS_WAIT_SECONDS = 1.0


RECORD_FINALIZE_WAIT_SECONDS = 15.0
RECORD_FINALIZE_POLL_SECONDS = 0.5


FFPROBE_BIN = "ffprobe"


# =========================
# 低延遲用
# =========================

PRE_ENCODE_QUEUE_BUFFERS = 10
RECORD_QUEUE_BUFFERS = 180
STREAM_QUEUE_BUFFERS = 5
PRE_ENCODE_QUEUE_LEAKY = True


# =========================
# SRT / MediaMTX
# =========================

#MEDIA_SERVER_IP = "20.41.113.226"
#MEDIA_SERVER_IP = "192.168.1.173"
#MEDIA_SERVER_IP = "172.20.10.12"
MEDIA_SERVER_IP = "127.0.0.1"
#MEDIA_SERVER_IP = "192.168.0.20"
SRT_PORT = 8890
STREAM_PATH = "arloupe"

SRT_LATENCY = 30
SRT_TLPKTDROP = 1
SRT_SNDDROPDELAY = 0
SRT_PKT_SIZE = 1316


# =========================
# 雲端路徑
# =========================

CLOUD_RECORDING_PREFIX = "users"


# =========================
# Metadata watcher
# =========================

FILE_STABLE_WAIT_SECONDS = 2.0
WATCH_INTERVAL_SECONDS = 2.0

# ARLOUPE_CAPTURE_SETTINGS_JSON_BEGIN
# 由 7001 設定頁寫入 capture_settings.json，再由這裡覆蓋預設影像參數。
# 這樣前端不用直接改 Python config.py，降低寫壞設定檔的風險。
try:
    import json as _arloupe_json
    from pathlib import Path as _ArloupePath

    _arloupe_settings_path = _ArloupePath(__file__).with_name("capture_settings.json")
    if _arloupe_settings_path.exists():
        _arloupe_data = _arloupe_json.loads(_arloupe_settings_path.read_text(encoding="utf-8"))
        for _arloupe_key in ("INPUT_FPS", "FPS", "BITRATE_KBPS", "KEY_INT_MAX", "SEGMENT_SECONDS"):
            if _arloupe_key in _arloupe_data:
                globals()[_arloupe_key] = int(_arloupe_data[_arloupe_key])
except Exception as _arloupe_exc:
    print(f"[WARN] Failed to load capture_settings.json: {_arloupe_exc}")
# ARLOUPE_CAPTURE_SETTINGS_JSON_END

