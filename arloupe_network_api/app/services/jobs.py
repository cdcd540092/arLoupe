from __future__ import annotations

from datetime import datetime
import json

from app.settings import JOB_FILE


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def write_job(data: dict) -> None:
    """把目前網路任務狀態寫到 /tmp，讓前端可以查詢。"""
    payload = {
        "updated_at": now_iso(),
        **data,
    }
    JOB_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_job() -> dict:
    if not JOB_FILE.exists():
        return {
            "ok": True,
            "status": "idle",
            "message": "目前沒有網路任務",
            "updated_at": "",
        }

    try:
        return json.loads(JOB_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "status": "unknown",
            "message": "讀取任務狀態失敗",
            "error": str(exc),
        }


def clear_job() -> None:
    if JOB_FILE.exists():
        JOB_FILE.unlink()
