#!/usr/bin/env python3

import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Tuple

import requests

import config
from metadata_watcher import parse_segment_info, session_id_to_date_dir
import config

# Windows 模擬後端 IP
# 正式，ex. https://api.example.com
#UPLOAD_API_BASE_URL = ""
UPLOAD_API_BASE_URL = "http://192.168.1.173:8000"
#UPLOAD_API_BASE_URL = "http://172.20.10.12:8000"

# 幾秒描一次
SCAN_INTERVAL_SECONDS = 5

# 檢查檔案大小穩定的等待秒數
FILE_STABLE_WAIT_SECONDS = 2

# 單次上傳 timeout，秒
REQUEST_TIMEOUT_SECONDS = 60


def sha256_file(path: Path) -> str:

    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def is_file_stable(path: Path, wait_seconds: float) -> bool:
    """
    確認檔案沒有繼續變大。
    避免上傳到還沒寫完的檔案。
    """
    if not path.exists():
        return False

    size1 = path.stat().st_size
    time.sleep(wait_seconds)

    if not path.exists():
        return False

    size2 = path.stat().st_size
    return size1 == size2 and size2 > 0


def get_relative_or_absolute_url(url: str) -> str:
    """
    mock server 回傳的是 /upload/...
    真正 S3 presigned URL 會是 https://...
    所以這裡做相容處理。
    """
    if url.startswith("http://") or url.startswith("https://"):
        return url

    return UPLOAD_API_BASE_URL.rstrip("/") + url


def load_json(path: Path) -> dict:
    """讀取 metadata JSON。"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_atomic(path: Path, data: dict) -> None:
    """
    安全寫入 JSON：
    先寫 .tmp，再 rename 成正式檔，避免寫一半中斷。
    """
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    tmp_path.replace(path)


def update_upload_status(
    json_path: Path,
    status: str,
    retry_count: Optional[int] = None,
    last_error: Optional[str] = None,
) -> None:
    """更新 metadata JSON 裡面的 upload 狀態。"""
    data = load_json(json_path)

    upload = data.setdefault("upload", {})
    upload["status"] = status
    upload["last_error"] = last_error

    if retry_count is not None:
        upload["retry_count"] = retry_count

    if status == "uploaded":
        upload["uploaded_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    save_json_atomic(json_path, data)


def get_retry_count(json_path: Path) -> int:
    """取得目前 retry 次數。"""
    try:
        data = load_json(json_path)
        return int(data.get("upload", {}).get("retry_count", 0) or 0)
    except Exception:
        return 0


def build_init_payload(mp4_path: Path, json_path: Path) -> Optional[dict]:
    """
    建立 /uploads/init 要送給後端的資料。

    檔名格式需要符合：
    20260517_182707_arloupe01_seg00000.mp4
    """
    session_id, device_id, segment_index = parse_segment_info(mp4_path.name)

    if session_id is None or device_id is None or segment_index is None:
        print(f"[WARN] Skip invalid filename: {mp4_path.name}")
        return None

    recording_date = session_id_to_date_dir(session_id)

    if recording_date is None:
        print(f"[WARN] Cannot parse recording date: {mp4_path.name}")
        return None

    return {
        "device_id": device_id,
        "session_id": session_id,
        "recording_date": recording_date,
        "segment_index": segment_index,
        "mp4_filename": mp4_path.name,
        "json_filename": json_path.name,
        "mp4_size_bytes": mp4_path.stat().st_size,
        "json_size_bytes": json_path.stat().st_size,
        "mp4_sha256": sha256_file(mp4_path),
        "json_sha256": sha256_file(json_path),
    }


def init_upload(payload: dict) -> dict:
    """向後端要求 upload URL。"""
    url = f"{UPLOAD_API_BASE_URL}/api/recordings/uploads/init"

    resp = requests.post(
        url,
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()

    return resp.json()


def put_file(upload_url: str, file_path: Path, content_type: str) -> None:
    """PUT 檔案到 mock upload URL 或未來的 S3 presigned URL。"""
    url = get_relative_or_absolute_url(upload_url)

    headers = {
        "Content-Type": content_type,
    }

    with open(file_path, "rb") as f:
        resp = requests.put(
            url,
            data=f,
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    resp.raise_for_status()


def complete_upload(payload: dict, init_response: dict) -> None:
    """通知後端這段影片已經上傳完成。"""
    url = f"{UPLOAD_API_BASE_URL}/api/recordings/uploads/complete"

    complete_payload = {
        "recording_id": init_response["recording_id"],
        "device_id": payload["device_id"],
        "session_id": payload["session_id"],
        "segment_index": payload["segment_index"],
        "mp4_s3_key": init_response.get("mp4_s3_key"),
        "json_s3_key": init_response.get("json_s3_key"),
        "mp4_sha256": payload["mp4_sha256"],
        "json_sha256": payload["json_sha256"],
    }

    resp = requests.post(
        url,
        json=complete_payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()


def mark_uploaded(mp4_path: Path) -> None:
    """建立 .uploaded 標記，避免下次重複上傳。"""
    uploaded_path = mp4_path.with_suffix(".uploaded")
    uploaded_path.write_text("uploaded\n", encoding="utf-8")


def should_upload(mp4_path: Path) -> Tuple[bool, Optional[Path]]:
    """
    判斷某個 MP4 是否可以上傳。

    條件：
    1. 不是 .tmp
    2. 同名 .json 存在
    3. .uploaded 不存在
    4. mp4 和 json 都穩定
    """
    if mp4_path.name.endswith(".tmp"):
        return False, None

    json_path = mp4_path.with_suffix(".json")
    uploaded_path = mp4_path.with_suffix(".uploaded")

    if uploaded_path.exists():
        return False, None

    if not json_path.exists():
        return False, None

    if not is_file_stable(mp4_path, FILE_STABLE_WAIT_SECONDS):
        print(f"[INFO] MP4 still writing: {mp4_path.name}")
        return False, None

    if not is_file_stable(json_path, FILE_STABLE_WAIT_SECONDS):
        print(f"[INFO] JSON still writing: {json_path.name}")
        return False, None

    return True, json_path


def upload_one(mp4_path: Path, json_path: Path) -> bool:
    """上傳一段 MP4 + JSON。成功回傳 True，失敗回傳 False。"""
    print(f"[INFO] Upload candidate: {mp4_path.name}")

    retry_count = get_retry_count(json_path)

    try:
        update_upload_status(
            json_path,
            status="uploading",
            retry_count=retry_count,
            last_error=None,
        )

        payload = build_init_payload(mp4_path, json_path)
        if payload is None:
            return False

        print("[INFO] init upload...")
        init_response = init_upload(payload)

        print("[INFO] PUT MP4...")
        put_file(
            init_response["mp4_upload_url"],
            mp4_path,
            content_type="video/mp4",
        )

        print("[INFO] PUT JSON...")
        put_file(
            init_response["json_upload_url"],
            json_path,
            content_type="application/json",
        )

        print("[INFO] complete upload...")
        complete_upload(payload, init_response)

        update_upload_status(
            json_path,
            status="uploaded",
            retry_count=retry_count,
            last_error=None,
        )

        mark_uploaded(mp4_path)

        print(f"[INFO] Upload success: {mp4_path.name}")
        return True

    except Exception as exc:
        retry_count += 1
        error_msg = str(exc)

        print(f"[WARN] Upload failed: {mp4_path.name}")
        print(f"[WARN] Error: {error_msg}")

        update_upload_status(
            json_path,
            status="pending",
            retry_count=retry_count,
            last_error=error_msg,
        )

        return False


def iter_recording_dirs():
    """
    掃描所有日期資料夾。
    例如：
    /home/user/arloupe_data/recordings/2026-05-17/
    """
    base_dir = config.BASE_RECORDING_DIR

    if not base_dir.exists():
        return

    for date_dir in sorted(base_dir.iterdir()):
        if date_dir.is_dir():
            yield date_dir


def scan_once() -> None:
    """掃描一次，找到第一個可上傳檔案就處理。"""
    for date_dir in iter_recording_dirs():
        for mp4_path in sorted(date_dir.glob("*.mp4")):
            ok, json_path = should_upload(mp4_path)
            if not ok or json_path is None:
                continue

            # 同時間只處理一支，避免搶錄影與串流資源
            upload_one(mp4_path, json_path)
            return


def main() -> None:
    print("[INFO] arLoupe uploader started")
    print(f"[INFO] BASE_RECORDING_DIR={config.BASE_RECORDING_DIR}")
    print(f"[INFO] UPLOAD_API_BASE_URL={UPLOAD_API_BASE_URL}")
    print("[INFO] Upload mode: one file at a time")
    print()

    while True:
        scan_once()
        time.sleep(SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
