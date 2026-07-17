#!/usr/bin/env python3
"""arLoupe 錄影檔案清理工具。

設計原則：
1. 以 session 為單位清理，不單獨刪某一段影片。
2. 預設只清「已上傳」且超過保留天數的 session。
3. 不清 .mp4.tmp / .json.tmp / .broken 所在 session，避免刪到正在錄影或異常收尾資料。
4. 支援 preview / run / auto / status / settings，方便 7001 設定頁或 systemd timer 呼叫。
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Iterable, Optional

import config
from metadata_watcher import parse_segment_info


TZ_TAIPEI = timezone(timedelta(hours=8))
BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "cleanup_settings.json"

DEFAULT_SETTINGS = {
    "retention_days": 7,
    "low_free_gb": 20,
    "target_free_gb": 30,
    "delete_pending_when_critical": False,
    "max_delete_sessions": 0,
    "updated_at": None,
    "updated_by": "default",
}


@dataclass
class SessionGroup:
    recording_date: str
    session_id: str
    files: list[Path] = field(default_factory=list)
    mp4_files: list[Path] = field(default_factory=list)
    json_files: list[Path] = field(default_factory=list)
    uploaded_files: list[Path] = field(default_factory=list)
    temp_files: list[Path] = field(default_factory=list)
    broken_files: list[Path] = field(default_factory=list)

    @property
    def size_bytes(self) -> int:
        total = 0
        for path in self.files:
            try:
                if path.exists() and path.is_file():
                    total += path.stat().st_size
            except OSError:
                pass
        return total

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / 1024 / 1024, 2)

    @property
    def started_at(self) -> Optional[datetime]:
        try:
            dt = datetime.strptime(self.session_id, "%Y%m%d_%H%M%S")
            return dt.replace(tzinfo=TZ_TAIPEI)
        except Exception:
            return None

    def has_temp_or_broken(self) -> bool:
        return bool(self.temp_files or self.broken_files)


def now_iso() -> str:
    return datetime.now(TZ_TAIPEI).isoformat(timespec="seconds")


def gb(value_bytes: int | float) -> float:
    return round(float(value_bytes) / 1024 / 1024 / 1024, 2)


def load_settings() -> dict[str, Any]:
    settings = dict(DEFAULT_SETTINGS)
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                settings.update(data)
        except Exception as exc:
            settings["settings_warning"] = f"讀取 cleanup_settings.json 失敗：{exc}"

    # 型別保護
    settings["retention_days"] = int(settings.get("retention_days", DEFAULT_SETTINGS["retention_days"]))
    settings["low_free_gb"] = float(settings.get("low_free_gb", DEFAULT_SETTINGS["low_free_gb"]))
    settings["target_free_gb"] = float(settings.get("target_free_gb", DEFAULT_SETTINGS["target_free_gb"]))
    settings["delete_pending_when_critical"] = bool(settings.get("delete_pending_when_critical", False))
    settings["max_delete_sessions"] = int(settings.get("max_delete_sessions", 0) or 0)
    return settings


def save_settings(update: dict[str, Any]) -> dict[str, Any]:
    current = load_settings()

    allowed = {
        "retention_days",
        "low_free_gb",
        "target_free_gb",
        "delete_pending_when_critical",
        "max_delete_sessions",
    }

    for key, value in update.items():
        if key in allowed:
            current[key] = value

    # 驗證範圍，避免前端寫壞設定
    current["retention_days"] = max(0, min(3650, int(current.get("retention_days", 7))))
    current["low_free_gb"] = max(1.0, min(10000.0, float(current.get("low_free_gb", 20))))
    current["target_free_gb"] = max(current["low_free_gb"], min(10000.0, float(current.get("target_free_gb", 30))))
    current["delete_pending_when_critical"] = bool(current.get("delete_pending_when_critical", False))
    current["max_delete_sessions"] = max(0, min(100000, int(current.get("max_delete_sessions", 0) or 0)))
    current["updated_at"] = now_iso()
    current["updated_by"] = "arloupe-network-api"

    tmp_path = SETTINGS_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(SETTINGS_PATH)
    return current


def storage_status() -> dict[str, Any]:
    base = config.BASE_RECORDING_DIR
    base.mkdir(parents=True, exist_ok=True)

    usage = shutil.disk_usage(base)
    used = usage.total - usage.free
    used_percent = round((used / usage.total * 100.0), 1) if usage.total else 0.0

    return {
        "ok": True,
        "path": str(base),
        "total_gb": gb(usage.total),
        "used_gb": gb(used),
        "free_gb": gb(usage.free),
        "used_percent": used_percent,
    }


def iter_recording_date_dirs() -> Iterable[Path]:
    base = config.BASE_RECORDING_DIR
    if not base.exists():
        return []
    return sorted([p for p in base.iterdir() if p.is_dir()], reverse=True)


def session_id_from_path(path: Path) -> Optional[str]:
    if path.name.startswith("session_") and path.suffix == ".json":
        return path.stem.replace("session_", "", 1)

    session_id, _device_id, _segment_index = parse_segment_info(path.name)
    if session_id:
        return session_id

    # .uploaded 例如 20260621_143012_arloupe01_seg00000.uploaded
    if path.suffix == ".uploaded":
        fake_mp4_name = path.with_suffix(".mp4").name
        session_id, _device_id, _segment_index = parse_segment_info(fake_mp4_name)
        return session_id

    # .mp4.tmp.broken 這類檔名先粗略抓 session_id
    parts = path.name.split("_")
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        candidate = f"{parts[0]}_{parts[1]}"
        try:
            datetime.strptime(candidate, "%Y%m%d_%H%M%S")
            return candidate
        except Exception:
            return None

    return None


def group_sessions() -> list[SessionGroup]:
    groups: dict[tuple[str, str], SessionGroup] = {}

    for date_dir in iter_recording_date_dirs():
        recording_date = date_dir.name
        for path in sorted(date_dir.iterdir()):
            if not path.is_file():
                continue

            session_id = session_id_from_path(path)
            if not session_id:
                continue

            key = (recording_date, session_id)
            group = groups.setdefault(key, SessionGroup(recording_date=recording_date, session_id=session_id))
            group.files.append(path)

            name = path.name
            if name.endswith(".mp4"):
                group.mp4_files.append(path)
            elif name.endswith(".json"):
                group.json_files.append(path)
            elif name.endswith(".uploaded"):
                group.uploaded_files.append(path)
            elif ".tmp" in name:
                group.temp_files.append(path)
            elif ".broken" in name:
                group.broken_files.append(path)

    return sorted(groups.values(), key=lambda g: g.session_id, reverse=True)


def read_json(path: Path) -> Optional[dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def segment_uploaded(mp4_path: Path) -> bool:
    uploaded_marker = mp4_path.with_suffix(".uploaded")
    if uploaded_marker.exists():
        return True

    json_path = mp4_path.with_suffix(".json")
    data = read_json(json_path) if json_path.exists() else None
    if not data:
        return False

    return data.get("upload", {}).get("status") == "uploaded"


def session_uploaded(group: SessionGroup) -> bool:
    if not group.mp4_files:
        return False
    return all(segment_uploaded(path) for path in group.mp4_files)


def session_age_days(group: SessionGroup) -> Optional[float]:
    started = group.started_at
    if not started:
        return None
    return (datetime.now(TZ_TAIPEI) - started).total_seconds() / 86400.0


def classify_session(group: SessionGroup, settings: dict[str, Any]) -> dict[str, Any]:
    age_days = session_age_days(group)
    uploaded = session_uploaded(group)
    older_than_retention = age_days is not None and age_days >= float(settings["retention_days"])
    has_temp_or_broken = group.has_temp_or_broken()

    reasons = []
    eligible = True

    if has_temp_or_broken:
        eligible = False
        reasons.append("has_temp_or_broken")

    if not older_than_retention:
        eligible = False
        reasons.append("within_retention")

    if not uploaded:
        eligible = False
        reasons.append("not_uploaded")

    if eligible:
        reasons.append("uploaded_and_older_than_retention")

    return {
        "recording_date": group.recording_date,
        "session_id": group.session_id,
        "started_at": group.started_at.isoformat(timespec="seconds") if group.started_at else None,
        "age_days": round(age_days, 2) if age_days is not None else None,
        "size_bytes": group.size_bytes,
        "size_mb": group.size_mb,
        "file_count": len(group.files),
        "video_count": len(group.mp4_files),
        "json_count": len(group.json_files),
        "uploaded_marker_count": len(group.uploaded_files),
        "has_temp_or_broken": has_temp_or_broken,
        "uploaded": uploaded,
        "eligible": eligible,
        "reasons": reasons,
        "files": [path.name for path in group.files],
    }


def build_preview() -> dict[str, Any]:
    settings = load_settings()
    status = storage_status()
    sessions = [classify_session(group, settings) for group in group_sessions()]
    candidates = [s for s in sessions if s["eligible"]]

    freeable_bytes = sum(int(s["size_bytes"]) for s in candidates)
    should_auto_run = float(status["free_gb"]) < float(settings["low_free_gb"])

    return {
        "ok": True,
        "mode": "preview",
        "settings": settings,
        "storage": status,
        "should_auto_run": should_auto_run,
        "candidate_count": len(candidates),
        "freeable_gb": gb(freeable_bytes),
        "sessions_total": len(sessions),
        "candidates": candidates,
        "skipped": [s for s in sessions if not s["eligible"]][:100],
        "updated_at": now_iso(),
    }


def safe_delete_file(path: Path) -> tuple[bool, str]:
    try:
        if path.exists() and path.is_file():
            path.unlink()
            return True, "deleted"
        return True, "missing"
    except Exception as exc:
        return False, str(exc)


def delete_session(recording_date: str, session_id: str) -> dict[str, Any]:
    date_dir = config.BASE_RECORDING_DIR / recording_date
    group = None
    for candidate in group_sessions():
        if candidate.recording_date == recording_date and candidate.session_id == session_id:
            group = candidate
            break

    if group is None:
        return {
            "recording_date": recording_date,
            "session_id": session_id,
            "deleted": False,
            "error": "session_not_found",
            "freed_bytes": 0,
            "files": [],
        }

    freed_bytes = group.size_bytes
    files = []
    ok_all = True

    # 再保護一次：run 時不刪 tmp/broken 所在 session
    if group.has_temp_or_broken():
        return {
            "recording_date": recording_date,
            "session_id": session_id,
            "deleted": False,
            "error": "session_has_temp_or_broken_files",
            "freed_bytes": 0,
            "files": [p.name for p in group.files],
        }

    for path in sorted(group.files):
        ok, message = safe_delete_file(path)
        ok_all = ok_all and ok
        files.append({"name": path.name, "ok": ok, "message": message})

    # 如果日期資料夾空了，不強制刪，但可以順手移除空資料夾
    try:
        if date_dir.exists() and not any(date_dir.iterdir()):
            date_dir.rmdir()
    except Exception:
        pass

    return {
        "recording_date": recording_date,
        "session_id": session_id,
        "deleted": ok_all,
        "error": None if ok_all else "some_files_failed",
        "freed_bytes": freed_bytes if ok_all else 0,
        "freed_mb": gb(freed_bytes) * 1024 if ok_all else 0,
        "files": files,
    }


def run_cleanup(force: bool = False, auto: bool = False) -> dict[str, Any]:
    preview = build_preview()
    settings = preview["settings"]
    status = preview["storage"]
    candidates = preview["candidates"]

    if auto and not preview["should_auto_run"]:
        return {
            "ok": True,
            "mode": "auto",
            "ran": False,
            "message": "剩餘容量尚未低於門檻，不執行自動清理。",
            "preview": preview,
        }

    if not force and not auto:
        return {
            "ok": False,
            "mode": "run",
            "ran": False,
            "message": "為了避免誤刪，手動清理請加 --force。",
            "preview": preview,
        }

    max_delete = int(settings.get("max_delete_sessions", 0) or 0)
    deleted = []
    freed_bytes = 0

    # 最舊優先刪除
    ordered_candidates = sorted(candidates, key=lambda item: item.get("session_id", ""))

    for item in ordered_candidates:
        if max_delete > 0 and len(deleted) >= max_delete:
            break

        result = delete_session(item["recording_date"], item["session_id"])
        deleted.append(result)
        if result.get("deleted"):
            freed_bytes += int(result.get("freed_bytes", 0))

        if auto:
            current_free = storage_status()["free_gb"]
            if float(current_free) >= float(settings["target_free_gb"]):
                break

    return {
        "ok": True,
        "mode": "auto" if auto else "run",
        "ran": True,
        "deleted_sessions": sum(1 for item in deleted if item.get("deleted")),
        "failed_sessions": sum(1 for item in deleted if not item.get("deleted")),
        "freed_gb": gb(freed_bytes),
        "deleted": deleted,
        "storage_before": status,
        "storage_after": storage_status(),
        "updated_at": now_iso(),
    }


def print_result(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="arLoupe recording cleanup tool")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("status", "settings", "preview", "run", "auto", "update-settings"):
        p = sub.add_parser(name)
        p.add_argument("--json", action="store_true")
        if name == "run":
            p.add_argument("--force", action="store_true")

    args = parser.parse_args()

    if args.command == "status":
        print_result({"ok": True, "storage": storage_status(), "settings": load_settings()}, args.json)
    elif args.command == "settings":
        print_result({"ok": True, "settings": load_settings()}, args.json)
    elif args.command == "preview":
        print_result(build_preview(), args.json)
    elif args.command == "run":
        print_result(run_cleanup(force=bool(args.force), auto=False), args.json)
    elif args.command == "auto":
        print_result(run_cleanup(force=False, auto=True), args.json)
    elif args.command == "update-settings":
        try:
            update = json.loads(sys.stdin.read() or "{}")
        except Exception as exc:
            print_result({"ok": False, "error": f"invalid json stdin: {exc}"}, args.json)
            return 2
        print_result({"ok": True, "settings": save_settings(update)}, args.json)
    else:
        parser.print_help()
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
