from pathlib import Path


# 專案根目錄：/home/user/arloupe_network_api
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# 網路任務狀態檔
JOB_FILE = Path("/tmp/arloupe_network_last_job.json")

# Wi-Fi / Hotspot 設定
WIFI_IFACE = "wlan0"
HOTSPOT_NAME = "arloupe-setup-hotspot"
HOTSPOT_SSID = "arLoupe-Setup"
HOTSPOT_DHCP_SERVICE = "arloupe-hotspot-dhcp.service"
ENTER_HOTSPOT_SCRIPT = "/usr/local/bin/arloupe-enter-hotspot.sh"
ENTER_WIFI_SCRIPT = "/usr/local/bin/arloupe-enter-wifi.sh"

# 本機錄影檔案目錄
# 不 import capture 專案的 config.py，避免 7001 設定頁被 GStreamer 相依性拖垮。
RECORDING_BASE_DIR = Path("/home/user/arloupe_data/recordings")
MAX_VIDEO_LIST_ITEMS = 200

# BLE / arLoupe remote control
ARLOUPECTL_BIN = "/usr/local/bin/arloupectl"
ALLOWED_BLE_COMMANDS = {
    "grid1", "grid2", "grid3", "grid4",
    "led", "minus", "photo", "plus", "power", "record",
    "temp_minus", "temp_plus",
}
BLE_QUERY_COMMANDS = {"status", "services", "help"}

# Capture / GStreamer runtime settings
CAPTURE_PROJECT_DIR = Path("/home/user/arloupe_v6_dynamic_recording")
CAPTURE_SETTINGS_FILE = CAPTURE_PROJECT_DIR / "capture_settings.json"
CAPTURE_CONFIG_FILE = CAPTURE_PROJECT_DIR / "config.py"
CAPTURE_API_BASE_URL = "http://127.0.0.1:7000"
CAPTURE_API_STATUS_URL = f"{CAPTURE_API_BASE_URL}/api/capture/status"
CAPTURE_SERVICE_NAME = "arloupe-capture-api.service"

# 只開放這些範圍，避免前端把 capture 設定寫壞
ALLOWED_OUTPUT_FPS = [30, 60]
ALLOWED_INPUT_FPS = [60]
MIN_BITRATE_KBPS = 1000
MAX_BITRATE_KBPS = 20000
MIN_SEGMENT_SECONDS = 10
MAX_SEGMENT_SECONDS = 1800

# Recording cleanup
CLEANUP_SCRIPT = CAPTURE_PROJECT_DIR / "cleanup.py"
CLEANUP_SETTINGS_FILE = CAPTURE_PROJECT_DIR / "cleanup_settings.json"
CLEANUP_PYTHON_BIN = str(CAPTURE_PROJECT_DIR / ".venv" / "bin" / "python")
