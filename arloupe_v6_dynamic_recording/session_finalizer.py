"""Post-recording cleanup for session files."""

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
    """Delete a file if it exists."""
    try:
        if path.exists():
            path.unlink()
            print(f"[INFO] Removed: {path.name}")
    except Exception as exc:
        print(f"[WARN] Failed to remove {path}: {exc}")


def _segment_index_for_session(video_path: Path, session_id: str) -> Optional[int]:
    """Return the segment index for the current session only."""
    parsed_session_id, _device_id, segment_index = parse_segment_info(video_path.name)

    if parsed_session_id != session_id:
        return None

    return segment_index


def _delete_related_files(video_path: Path) -> None:
    """Delete a segment and its related metadata or temp files."""
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
    """Yield final and temp videos for the current session."""
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
    """Wait until ffprobe can read the video."""
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
    """In fixed-count mode, keep only seg00000 to seg{N-1}."""
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
    """Rename playable .mp4.tmp files to .mp4 after GStreamer stops."""
    for temp_path in sorted(ctx.segment_dir.glob(f"{ctx.session_id}_*_seg*.mp4.tmp")):
        segment_index = _segment_index_for_session(temp_path, ctx.session_id)
        if segment_index is None:
            continue

        if not config.RECORD_CONTINUOUS and segment_index >= int(config.RECORD_SEGMENT_COUNT):
            # Defensive check; cleanup_extra_segments should have removed these.
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
    """Backfill missing JSON metadata for valid MP4 files."""
    segment_limit: Optional[int] = None
    if not config.RECORD_CONTINUOUS:
        segment_limit = int(config.RECORD_SEGMENT_COUNT)

    valid_indices = set()

    for mp4_path in sorted(ctx.segment_dir.glob(f"{ctx.session_id}_*_seg*.mp4")):
        segment_index = _segment_index_for_session(mp4_path, ctx.session_id)

        if segment_index is None:
            continue

        if segment_limit is not None and segment_index >= segment_limit:
            # Defensive check; cleanup_extra_segments should have removed these.
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
    """Run the full post-recording cleanup."""
    print("[INFO] Finalizing session files...")
    cleanup_extra_segments(ctx)
    finalize_temp_segments(ctx)
    ensure_missing_metadata(ctx)
    print("[INFO] Session finalization finished.")
