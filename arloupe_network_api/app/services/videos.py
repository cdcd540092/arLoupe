from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re

from fastapi import HTTPException

from app.settings import RECORDING_BASE_DIR, MAX_VIDEO_LIST_ITEMS


def path_is_under(child: Path, parent: Path) -> bool:
    """確認 child resolve 後仍在 parent 裡面，避免 path traversal。"""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def validate_recording_date(recording_date: str) -> str:
    """只接受 YYYY-MM-DD 日期資料夾。"""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", recording_date):
        raise HTTPException(status_code=400, detail="日期格式錯誤，需為 YYYY-MM-DD")
    return recording_date


def safe_recording_file(recording_date: str, filename: str, allowed_suffixes: tuple[str, ...]) -> Path:
    """
    建立安全的錄影檔案路徑。
    不允許 ../ 或子資料夾，只允許指定副檔名。
    """
    recording_date = validate_recording_date(recording_date)
    name = Path(filename).name

    if name != filename:
        raise HTTPException(status_code=400, detail="檔名不可包含路徑")

    if not any(name.endswith(suffix) for suffix in allowed_suffixes):
        raise HTTPException(status_code=400, detail="不允許的檔案類型")

    path = RECORDING_BASE_DIR / recording_date / name

    if not path_is_under(path, RECORDING_BASE_DIR):
        raise HTTPException(status_code=400, detail="檔案路徑不合法")

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="找不到檔案")

    return path


def parse_video_filename(filename: str) -> dict:
    """
    解析影片檔名：
    20260613_233000_arloupe01_seg00000.mp4
    """
    match = re.match(
        r"^(?P<date>\d{8})_(?P<time>\d{6})_(?P<device_id>.+?)_seg(?P<segment_index>\d+)\.mp4$",
        filename,
    )

    if not match:
        return {
            "session_id": "",
            "device_id": "",
            "segment_index": None,
        }

    return {
        "session_id": f"{match.group('date')}_{match.group('time')}",
        "device_id": match.group("device_id"),
        "segment_index": int(match.group("segment_index")),
    }


def session_started_at_from_id(session_id: str) -> str:
    """把 20260621_143012 轉成人比較好讀的時間。"""
    if not session_id:
        return ""

    try:
        dt = datetime.strptime(session_id, "%Y%m%d_%H%M%S")
        return dt.isoformat(timespec="seconds")
    except Exception:
        return ""


def load_video_metadata(json_path: Path) -> dict:
    """讀取影片同名 metadata JSON。失敗時回傳空資料，不讓列表 API 整個失敗。"""
    if not json_path.exists() or not json_path.is_file():
        return {}

    try:
        return json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def video_item_from_path(mp4_path: Path) -> dict:
    """把單一 MP4 轉成前端需要的資料。"""
    stat = mp4_path.stat()
    recording_date = mp4_path.parent.name
    metadata_path = mp4_path.with_suffix(".json")
    metadata = load_video_metadata(metadata_path)
    parsed = parse_video_filename(mp4_path.name)

    duration = (
        metadata.get("time", {}).get("actual_duration_seconds")
        or metadata.get("time", {}).get("expected_duration_seconds")
    )
    upload_status = metadata.get("upload", {}).get("status", "unknown") if metadata else "no_metadata"

    return {
        "filename": mp4_path.name,
        "recording_date": recording_date,
        "size_bytes": stat.st_size,
        "size_mb": round(stat.st_size / 1024 / 1024, 2),
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "metadata_exists": metadata_path.exists(),
        "metadata_filename": metadata_path.name if metadata_path.exists() else "",
        "duration_seconds": duration,
        "upload_status": upload_status,
        "session_id": parsed["session_id"],
        "device_id": parsed["device_id"],
        "segment_index": parsed["segment_index"],
        "url": f"/api/videos/file/{recording_date}/{mp4_path.name}",
        "download_url": f"/api/videos/file/{recording_date}/{mp4_path.name}?download=1",
        "metadata_url": f"/api/videos/metadata/{recording_date}/{metadata_path.name}" if metadata_path.exists() else "",
    }


def _session_upload_summary(videos: list[dict]) -> str:
    statuses = [video.get("upload_status") or "unknown" for video in videos]
    if not statuses:
        return "unknown"

    unique = set(statuses)
    if len(unique) == 1:
        return statuses[0]

    uploaded = statuses.count("uploaded")
    pending = statuses.count("pending")
    failed = len([s for s in statuses if s not in {"uploaded", "pending", "no_metadata", "unknown"}])

    parts = []
    if uploaded:
        parts.append(f"uploaded {uploaded}")
    if pending:
        parts.append(f"pending {pending}")
    if failed:
        parts.append(f"failed {failed}")
    if not parts:
        parts.append("mixed")
    return ", ".join(parts)


def session_item_from_videos(session_id: str, videos: list[dict]) -> dict:
    """把同一個 session 的片段整理成一筆 session 摘要。"""
    videos = sorted(
        videos,
        key=lambda item: item.get("segment_index") if item.get("segment_index") is not None else 999999,
    )

    total_size_bytes = sum(int(item.get("size_bytes") or 0) for item in videos)
    duration_values = []
    for item in videos:
        try:
            value = float(item.get("duration_seconds"))
        except Exception:
            continue
        if value > 0:
            duration_values.append(value)

    device_id = ""
    for item in videos:
        if item.get("device_id"):
            device_id = item["device_id"]
            break

    last_modified = ""
    if videos:
        last_modified = max(str(item.get("modified_at") or "") for item in videos)

    return {
        "session_id": session_id,
        "started_at": session_started_at_from_id(session_id),
        "device_id": device_id,
        "segment_count": len(videos),
        "total_size_bytes": total_size_bytes,
        "total_size_mb": round(total_size_bytes / 1024 / 1024, 2),
        "total_duration_seconds": round(sum(duration_values), 2) if duration_values else None,
        "upload_status": _session_upload_summary(videos),
        "metadata_count": sum(1 for item in videos if item.get("metadata_exists")),
        "last_modified": last_modified,
        "videos": videos,
    }


def get_available_recording_dates() -> list[str]:
    """回傳目前錄影資料夾裡可用的日期，最新日期在前。"""
    if not RECORDING_BASE_DIR.exists():
        return []

    dates = [
        path.name
        for path in RECORDING_BASE_DIR.iterdir()
        if path.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.name)
    ]
    return sorted(dates, reverse=True)


def list_local_videos(date: str = "", limit: int = MAX_VIDEO_LIST_ITEMS) -> dict:
    """
    列出本機錄影檔案。
    預設只回傳最新日期；date=all 才回傳全部日期。
    回傳格式：日期 → Session → 分段影片。
    只列正式 .mp4，不列 .mp4.tmp / .broken。
    """
    limit = max(1, min(int(limit or MAX_VIDEO_LIST_ITEMS), 1000))
    available_dates = get_available_recording_dates()

    if not RECORDING_BASE_DIR.exists() or not available_dates:
        return {
            "ok": True,
            "base_dir": str(RECORDING_BASE_DIR),
            "selected_date": "",
            "available_dates": [],
            "total": 0,
            "total_videos": 0,
            "total_sessions": 0,
            "dates": [],
        }

    requested_date = (date or "").strip()

    if requested_date.lower() == "all":
        selected_date = "all"
        date_dirs = [RECORDING_BASE_DIR / item for item in available_dates]
    elif requested_date:
        selected_date = validate_recording_date(requested_date)
        target = RECORDING_BASE_DIR / selected_date
        date_dirs = [target] if target.exists() and target.is_dir() else []
    else:
        # 預設只顯示最新日期，避免天數多時頁面太長。
        selected_date = available_dates[0]
        date_dirs = [RECORDING_BASE_DIR / selected_date]

    grouped_dates = []
    total_videos = 0
    total_sessions = 0

    for date_dir in date_dirs:
        if not date_dir.exists() or not date_dir.is_dir():
            continue

        mp4_paths = sorted(date_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        session_map: dict[str, list[dict]] = {}

        for mp4_path in mp4_paths:
            if total_videos >= limit:
                break

            if mp4_path.name.endswith(".tmp") or mp4_path.name.endswith(".broken"):
                continue

            item = video_item_from_path(mp4_path)
            session_id = item.get("session_id") or "unknown"
            session_map.setdefault(session_id, []).append(item)
            total_videos += 1

        sessions = [session_item_from_videos(session_id, videos) for session_id, videos in session_map.items()]
        sessions = sorted(
            sessions,
            key=lambda item: item.get("started_at") or item.get("last_modified") or "",
            reverse=True,
        )

        if sessions:
            total_sessions += len(sessions)
            grouped_dates.append({
                "date": date_dir.name,
                "session_count": len(sessions),
                "video_count": sum(session["segment_count"] for session in sessions),
                "sessions": sessions,
            })

        if total_videos >= limit:
            break

    return {
        "ok": True,
        "base_dir": str(RECORDING_BASE_DIR),
        "selected_date": selected_date,
        "available_dates": available_dates,
        "total": total_videos,
        "total_videos": total_videos,
        "total_sessions": total_sessions,
        "dates": grouped_dates,
    }
