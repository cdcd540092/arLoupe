"""Read and update capture runtime settings for arLoupe Capture API.

This module does not import the capture project's config.py because the 7001
settings page should stay independent from GStreamer runtime dependencies.
"""

from __future__ import annotations

import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.settings import (
    ALLOWED_INPUT_FPS,
    ALLOWED_OUTPUT_FPS,
    CAPTURE_API_STATUS_URL,
    CAPTURE_CONFIG_FILE,
    CAPTURE_PROJECT_DIR,
    CAPTURE_SERVICE_NAME,
    CAPTURE_SETTINGS_FILE,
    MAX_BITRATE_KBPS,
    MAX_SEGMENT_SECONDS,
    MIN_BITRATE_KBPS,
    MIN_SEGMENT_SECONDS,
)

DEFAULT_CAPTURE_SETTINGS = {
    "INPUT_FPS": 60,
    "FPS": 30,
    "BITRATE_KBPS": 5000,
    "KEY_INT_MAX": 30,
    "SEGMENT_SECONDS": 300,
}

CONFIG_KEYS = ["INPUT_FPS", "FPS", "BITRATE_KBPS", "KEY_INT_MAX", "SEGMENT_SECONDS"]


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"讀取設定檔失敗：{exc}")


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def _parse_config_py_defaults() -> dict[str, int]:
    """Best-effort parse of simple NAME = 123 values from capture config.py."""
    values = dict(DEFAULT_CAPTURE_SETTINGS)
    if not CAPTURE_CONFIG_FILE.exists():
        return values

    try:
        text = CAPTURE_CONFIG_FILE.read_text(encoding="utf-8")
    except Exception:
        return values

    for key in CONFIG_KEYS:
        match = re.search(rf"^\s*{re.escape(key)}\s*=\s*([0-9]+)\s*$", text, re.MULTILINE)
        if match:
            values[key] = int(match.group(1))

    if "INPUT_FPS" not in values or not values.get("INPUT_FPS"):
        values["INPUT_FPS"] = int(values.get("FPS", 30))

    return values


def _normalize_settings(data: dict[str, Any]) -> dict[str, int]:
    base = _parse_config_py_defaults()
    saved = _read_json(CAPTURE_SETTINGS_FILE)

    for key in CONFIG_KEYS:
        if key in saved:
            try:
                base[key] = int(saved[key])
            except Exception:
                pass
        if key in data and data[key] is not None:
            try:
                base[key] = int(data[key])
            except Exception:
                raise HTTPException(status_code=400, detail=f"{key} 必須是整數")

    validate_capture_settings(base)
    return base


def validate_capture_settings(values: dict[str, int]) -> None:
    input_fps = int(values.get("INPUT_FPS", 60))
    fps = int(values.get("FPS", 30))
    bitrate = int(values.get("BITRATE_KBPS", 5000))
    key_int = int(values.get("KEY_INT_MAX", fps))
    segment = int(values.get("SEGMENT_SECONDS", 300))

    if input_fps not in ALLOWED_INPUT_FPS:
        raise HTTPException(status_code=400, detail=f"來源 FPS 目前只允許：{ALLOWED_INPUT_FPS}")
    if fps not in ALLOWED_OUTPUT_FPS:
        raise HTTPException(status_code=400, detail=f"輸出 FPS 只允許：{ALLOWED_OUTPUT_FPS}")
    if bitrate < MIN_BITRATE_KBPS or bitrate > MAX_BITRATE_KBPS:
        raise HTTPException(status_code=400, detail=f"位元率需介於 {MIN_BITRATE_KBPS}～{MAX_BITRATE_KBPS} kbps")
    if segment < MIN_SEGMENT_SECONDS or segment > MAX_SEGMENT_SECONDS:
        raise HTTPException(status_code=400, detail=f"分段時長需介於 {MIN_SEGMENT_SECONDS}～{MAX_SEGMENT_SECONDS} 秒")
    if key_int < 1 or key_int > 300:
        raise HTTPException(status_code=400, detail="Keyframe 間隔需介於 1～300")


def get_capture_config() -> dict[str, Any]:
    values = _normalize_settings({})
    return {
        "ok": True,
        "settings_file": str(CAPTURE_SETTINGS_FILE),
        "config_file": str(CAPTURE_CONFIG_FILE),
        "capture_project_dir": str(CAPTURE_PROJECT_DIR),
        "input_fps": values["INPUT_FPS"],
        "fps": values["FPS"],
        "bitrate_kbps": values["BITRATE_KBPS"],
        "key_int_max": values["KEY_INT_MAX"],
        "segment_seconds": values["SEGMENT_SECONDS"],
        "requires_restart": True,
        "note": "修改後需套用並重啟 arloupe-capture-api.service，且串流/錄影中不能套用。",
    }


def update_capture_config(payload: dict[str, Any]) -> dict[str, Any]:
    data = dict(payload)

    # 前端預設使用自動 keyframe：1 秒一個 keyframe。
    auto_key_int = bool(data.pop("auto_key_int", True))
    if "fps" in data and data.get("fps") is not None:
        data["FPS"] = data.pop("fps")
    if "input_fps" in data and data.get("input_fps") is not None:
        data["INPUT_FPS"] = data.pop("input_fps")
    if "bitrate_kbps" in data and data.get("bitrate_kbps") is not None:
        data["BITRATE_KBPS"] = data.pop("bitrate_kbps")
    if "segment_seconds" in data and data.get("segment_seconds") is not None:
        data["SEGMENT_SECONDS"] = data.pop("segment_seconds")
    if "key_int_max" in data and data.get("key_int_max") is not None:
        data["KEY_INT_MAX"] = data.pop("key_int_max")

    merged = _normalize_settings(data)
    if auto_key_int:
        merged["KEY_INT_MAX"] = merged["FPS"]

    validate_capture_settings(merged)

    output = {key: int(merged[key]) for key in CONFIG_KEYS}
    output["updated_at"] = _now_iso()
    output["updated_by"] = "arloupe-network-api"
    _write_json_atomic(CAPTURE_SETTINGS_FILE, output)

    return {
        **get_capture_config(),
        "message": "影像參數已儲存，尚未套用。請在停止串流與錄影後按『套用並重啟影像服務』。",
    }


def get_capture_api_status() -> dict[str, Any]:
    try:
        with urllib.request.urlopen(CAPTURE_API_STATUS_URL, timeout=3) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=503, detail=f"無法連線到 Capture API：{exc}")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"讀取 Capture API 狀態失敗：{exc}")


def apply_capture_config() -> dict[str, Any]:
    status = get_capture_api_status()
    if status.get("recording"):
        raise HTTPException(status_code=409, detail="目前正在錄影，請先停止錄影後再套用設定。")
    if status.get("streaming"):
        raise HTTPException(status_code=409, detail="目前正在串流，請先停止串流後再套用設定。")

    result = subprocess.run(
        ["sudo", "systemctl", "restart", CAPTURE_SERVICE_NAME],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "重啟影像服務失敗",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            },
        )

    return {
        "ok": True,
        "message": "設定已套用，影像服務已重啟。",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "settings": get_capture_config(),
    }
