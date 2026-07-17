from pydantic import BaseModel


class WifiConnectRequest(BaseModel):
    ssid: str
    password: str = ""


class SavedWifiConnectRequest(BaseModel):
    ssid: str = ""
    connection_name: str = ""


class WifiForgetRequest(BaseModel):
    ssid: str = ""
    connection_name: str = ""


class BleCommandRequest(BaseModel):
    command: str



class CaptureConfigUpdateRequest(BaseModel):
    input_fps: int | None = None
    fps: int | None = None
    bitrate_kbps: int | None = None
    segment_seconds: int | None = None
    key_int_max: int | None = None
    auto_key_int: bool = True

class CleanupSettingsUpdateRequest(BaseModel):
    retention_days: int | None = None
    low_free_gb: float | None = None
    target_free_gb: float | None = None
    delete_pending_when_critical: bool | None = None
    max_delete_sessions: int | None = None
