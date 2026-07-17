from __future__ import annotations

import shutil
from fastapi import HTTPException

from app.settings import ARLOUPECTL_BIN, ALLOWED_BLE_COMMANDS, BLE_QUERY_COMMANDS
from app.services.commands import run_cmd


def _arloupectl_bin() -> str:
    """取得 arloupectl 路徑。優先使用設定值，找不到再查 PATH。"""
    found = shutil.which(ARLOUPECTL_BIN) if "/" not in ARLOUPECTL_BIN else None
    if found:
        return found

    if shutil.which(ARLOUPECTL_BIN):
        return ARLOUPECTL_BIN

    fallback = shutil.which("arloupectl")
    if fallback:
        return fallback

    # 即使不存在也回傳設定值，讓錯誤訊息清楚顯示是哪個路徑失敗。
    return ARLOUPECTL_BIN


def run_ble_command(command: str) -> dict:
    """執行安全白名單內的 arloupectl 控制命令。"""
    command = command.strip()

    if command not in ALLOWED_BLE_COMMANDS:
        raise HTTPException(status_code=400, detail=f"不允許的 BLE 指令：{command}")

    result = run_cmd([_arloupectl_bin(), command], timeout=10, check_timeout=False)
    ok = result["returncode"] == 0

    return {
        "ok": ok,
        "command": command,
        "returncode": result["returncode"],
        "stdout": result["stdout"].strip(),
        "stderr": result["stderr"].strip(),
        "message": "指令已送出" if ok else "指令執行失敗",
    }


def run_ble_query(command: str) -> dict:
    """執行查詢型 arloupectl 命令，例如 status / services / help。"""
    command = command.strip()

    if command not in BLE_QUERY_COMMANDS:
        raise HTTPException(status_code=400, detail=f"不允許的 BLE 查詢：{command}")

    result = run_cmd([_arloupectl_bin(), command], timeout=10, check_timeout=False)
    ok = result["returncode"] == 0

    return {
        "ok": ok,
        "command": command,
        "returncode": result["returncode"],
        "stdout": result["stdout"].strip(),
        "stderr": result["stderr"].strip(),
        "message": "查詢完成" if ok else "查詢失敗",
    }
