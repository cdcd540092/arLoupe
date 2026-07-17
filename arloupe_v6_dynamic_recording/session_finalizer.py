"""錄影停止後的 session 收尾整理。

主要處理三件事：
1. 固定段數錄影時，刪除 splitmuxsink 停止瞬間多開出的殘段。
2. 將合法的 .mp4.tmp 改名成正式 .mp4。
3. 補齊合法 MP4 segment 缺少的同名 JSON metadata。
"""

import time
from pathlib import Path
from typing import Optional

import config
from capture_paths import CaptureContext
from metadata_watcher import (
    TEMP_SUFFIX,
    TEMP_VIDEO_SUFFIX,
    finalize_temp_video,
    is_video_playable,
    normalize_video_path,
    parse_segment_info,
    write_metadata_json,
)


def _safe_unlink(path: Path) -> None:
    """安全刪除檔案；不存在就忽略。"""
    try:
        if path.exists():
            path.unlink()
            print(f"[INFO] Removed: {path.name}")
    except Exception as exc:
        print(f"[WARN] Failed to remove {path}: {exc}")


def _segment_index_for_session(video_path: Path, session_id: str) -> Optional[int]:
    """只接受目前 session 的 mp4 / mp4.tmp，並回傳 segment index。"""
    parsed_session_id, _device_id, segment_index = parse_segment_info(video_path.name)

    if parsed_session_id != session_id:
        return None

    return segment_index


def _delete_related_files(video_path: Path) -> None:
    """刪除某段影片以及它可能產生的相關 metadata / 暫存檔。"""
    final_path = normalize_video_path(video_path)
    temp_path = final_path.with_name(final_path.name + TEMP_SUFFIX)

    related_paths = [
        final_path,
        temp_path,
        final_path.with_suffix(".json"),
        final_path.with_suffix(".json.tmp"),
        final_path.with_suffix(".done"),
    ]

    for path in related_paths:
        _safe_unlink(path)


def _iter_session_video_paths(ctx: CaptureContext):
    """列出目前 session 的正式影片與暫存影片。"""
    patterns = [
        f"{ctx.session_id}_*_seg*.mp4",
        f"{ctx.session_id}_*_seg*.mp4.tmp",
    ]

    seen = set()
    for pattern in patterns:
        for path in sorted(ctx.segment_dir.glob(pattern)):
            if path not in seen:
                seen.add(path)
                yield path


def wait_until_video_playable(video_path: Path) -> bool:
    """等待影片可被 ffprobe 正常讀取。

    用在停止錄影後的最後一段，避免 mp4mux 還沒寫完 moov atom 就被改名。
    """
    timeout = float(getattr(config, "RECORD_FINALIZE_WAIT_SECONDS", 15.0))
    interval = float(getattr(config, "RECORD_FINALIZE_POLL_SECONDS", 0.5))
    deadline = time.time() + timeout

    while time.time() < deadline:
        if not video_path.exists():
            time.sleep(interval)
            continue

        if is_video_playable(video_path):
            return True

        time.sleep(interval)

    return is_video_playable(video_path)


def cleanup_extra_segments(ctx: CaptureContext) -> None:
    """固定段數模式下，只保留 seg00000 ~ seg{N-1}。

    例如 RECORD_SEGMENT_COUNT = 5，只保留 0~4。
    停止瞬間若多出 seg00005.mp4 或 seg00005.mp4.tmp，會在這裡刪掉。
    """
    if config.RECORD_CONTINUOUS:
        return

    segment_limit = int(config.RECORD_SEGMENT_COUNT)

    if segment_limit <= 0:
        print("[WARN] RECORD_SEGMENT_COUNT <= 0, skip cleanup_extra_segments")
        return

    for video_path in list(_iter_session_video_paths(ctx)):
        segment_index = _segment_index_for_session(video_path, ctx.session_id)

        if segment_index is None:
            continue

        if segment_index >= segment_limit:
            print(
                "[WARN] Extra segment detected: "
                f"{video_path.name} (index={segment_index}, limit={segment_limit})"
            )
            _delete_related_files(video_path)


def finalize_temp_segments(ctx: CaptureContext) -> None:
    """GStreamer 停止後，將可播放的 .mp4.tmp 改名成 .mp4。

    重點：不再無條件 force rename。必須等 ffprobe 驗證成功，
    確認 MP4 已經正常 finalize 後，才會改名成正式 .mp4。
    """
    for temp_path in sorted(ctx.segment_dir.glob(f"{ctx.session_id}_*_seg*.mp4.tmp")):
        segment_index = _segment_index_for_session(temp_path, ctx.session_id)
        if segment_index is None:
            continue

        if not config.RECORD_CONTINUOUS and segment_index >= int(config.RECORD_SEGMENT_COUNT):
            # 理論上 cleanup_extra_segments 已刪除，這裡再保護一次。
            continue

        if temp_path.stat().st_size <= 0:
            print(f"[WARN] Skip empty temp segment: {temp_path.name}")
            continue

        print(f"[INFO] Waiting for MP4 finalize: {temp_path.name}")
        if not wait_until_video_playable(temp_path):
            broken_path = temp_path.with_name(temp_path.name + ".broken")
            print(
                "[ERROR] MP4 did not finalize in time; keep it out of upload list: "
                f"{temp_path.name} -> {broken_path.name}"
            )
            try:
                temp_path.replace(broken_path)
            except Exception as exc:
                print(f"[WARN] Failed to mark broken segment {temp_path.name}: {exc}")
            continue

        finalize_temp_video(temp_path, force=True)


def ensure_missing_metadata(ctx: CaptureContext) -> None:
    """錄影停止後，替合法 MP4 補齊缺少的 JSON。

    metadata_watcher 可能在最後一段尚未穩定前就被停止，導致最後一段 MP4 有了，
    但同名 JSON 還沒產生。這裡會在 pipeline 完全停止後再補一次。
    """
    segment_limit: Optional[int] = None
    if not config.RECORD_CONTINUOUS:
        segment_limit = int(config.RECORD_SEGMENT_COUNT)

    valid_indices = set()

    for mp4_path in sorted(ctx.segment_dir.glob(f"{ctx.session_id}_*_seg*.mp4")):
        segment_index = _segment_index_for_session(mp4_path, ctx.session_id)

        if segment_index is None:
            continue

        if segment_limit is not None and segment_index >= segment_limit:
            # 理論上 cleanup_extra_segments 已經刪掉，這裡再保護一次。
            continue

        valid_indices.add(segment_index)

        if not mp4_path.exists() or mp4_path.stat().st_size <= 0:
            print(f"[WARN] Skip empty segment: {mp4_path.name}")
            continue

        if not is_video_playable(mp4_path):
            print(f"[WARN] Skip metadata because MP4 is not playable: {mp4_path.name}")
            continue

        json_path = mp4_path.with_suffix(".json")
        if not json_path.exists():
            print(f"[INFO] Missing metadata detected, creating: {json_path.name}")
            write_metadata_json(mp4_path)

    if segment_limit is not None:
        missing_indices = [i for i in range(segment_limit) if i not in valid_indices]
        if missing_indices:
            print(f"[WARN] Missing expected segment index: {missing_indices}")


def finalize_session(ctx: CaptureContext) -> None:
    """錄影完全停止後呼叫的總收尾流程。"""
    print("[INFO] Finalizing session files...")
    cleanup_extra_segments(ctx)
    finalize_temp_segments(ctx)
    ensure_missing_metadata(ctx)
    print("[INFO] Session finalization finished.")
