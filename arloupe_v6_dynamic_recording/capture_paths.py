"""路徑與 session 相關工具。"""

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path

import config


TZ_TAIPEI = timezone(timedelta(hours=8))


@dataclass(frozen=True)
class CaptureContext:
    session_id: str
    recording_date: str
    segment_dir: Path
    log_dir: Path


def now_taipei() -> datetime:
    return datetime.now(TZ_TAIPEI)


def build_context() -> CaptureContext:
    now = now_taipei()
    session_id = now.strftime("%Y%m%d_%H%M%S")
    recording_date = now.strftime("%Y-%m-%d")

    segment_dir = config.BASE_RECORDING_DIR / recording_date
    log_dir = config.BASE_LOG_DIR / recording_date

    segment_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    return CaptureContext(
        session_id=session_id,
        recording_date=recording_date,
        segment_dir=segment_dir,
        log_dir=log_dir,
    )


def build_cloud_session_prefix(recording_date: str, session_id: str) -> str:
    return (
        f"{config.CLOUD_RECORDING_PREFIX}/"
        f"{config.USER_ID}/"
        f"recordings/"
        f"{recording_date}/"
        f"{session_id}/"
    )


def build_cloud_key(recording_date: str, session_id: str, filename: str) -> str:
    return f"{build_cloud_session_prefix(recording_date, session_id)}{filename}"
