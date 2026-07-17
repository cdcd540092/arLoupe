"""Storage and cleanup bridge for the arLoupe 7001 Web UI.

真正清理規則放在 arloupe_v6_dynamic_recording/cleanup.py。
7001 只負責觸發 preview / run / settings 並回傳結果給前端。
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.settings import CLEANUP_PYTHON_BIN, CLEANUP_SCRIPT


def _cleanup_python() -> str:
    path = Path(CLEANUP_PYTHON_BIN)
    if path.exists():
        return str(path)
    return "python3"


def _run_cleanup(args: list[str], stdin_data: dict[str, Any] | None = None, timeout: int = 60) -> dict[str, Any]:
    if not CLEANUP_SCRIPT.exists():
        raise HTTPException(status_code=500, detail=f"找不到 cleanup.py：{CLEANUP_SCRIPT}")

    cmd = [_cleanup_python(), str(CLEANUP_SCRIPT), *args, "--json"]

    try:
        result = subprocess.run(
            cmd,
            input=json.dumps(stdin_data, ensure_ascii=False) if stdin_data is not None else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(CLEANUP_SCRIPT.parent),
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="清理工具執行逾時")

    if result.returncode != 0:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "清理工具執行失敗",
                "cmd": " ".join(cmd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            },
        )

    try:
        return json.loads(result.stdout or "{}")
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"清理工具回傳不是合法 JSON：{exc}",
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
        )


def get_storage_status() -> dict[str, Any]:
    return _run_cleanup(["status"], timeout=20)


def get_cleanup_settings() -> dict[str, Any]:
    return _run_cleanup(["settings"], timeout=20)


def update_cleanup_settings(payload: dict[str, Any]) -> dict[str, Any]:
    return _run_cleanup(["update-settings"], stdin_data=payload, timeout=20)


def preview_cleanup() -> dict[str, Any]:
    return _run_cleanup(["preview"], timeout=30)


def run_cleanup() -> dict[str, Any]:
    # 手動按鈕使用 --force，但 cleanup.py 仍只會刪「已上傳且超過保留天數」的 session。
    return _run_cleanup(["run", "--force"], timeout=180)
