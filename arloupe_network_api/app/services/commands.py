from __future__ import annotations

import subprocess
from fastapi import HTTPException


def run_cmd(cmd: list[str], timeout: int = 30, check_timeout: bool = True) -> dict:
    """執行系統指令，回傳 stdout / stderr / returncode。"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "cmd": " ".join(cmd),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        if check_timeout:
            raise HTTPException(status_code=504, detail=f"Command timeout: {' '.join(cmd)}")
        return {
            "cmd": " ".join(cmd),
            "returncode": 124,
            "stdout": "",
            "stderr": f"Command timeout after {timeout}s",
        }


def run_cmd_for_job(cmd: list[str], timeout: int = 30) -> dict:
    """背景任務專用：不要丟 HTTPException，直接回傳 timeout 結果。"""
    return run_cmd(cmd, timeout=timeout, check_timeout=False)
