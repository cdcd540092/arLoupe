"""Watch recording segments, finalize temp videos, and write metadata."""

import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

import config
from capture_paths import build_cloud_key


TZ_TAIPEI = timezone(timedelta(hours=8))
TEMP_SUFFIX = getattr(config, "RECORDING_TEMP_SUFFIX", ".tmp")
FINAL_VIDEO_SUFFIX = ".mp4"
TEMP_VIDEO_SUFFIX = f"{FINAL_VIDEO_SUFFIX}{TEMP_SUFFIX}"


def now_iso() -> str:
    return datetime.now(TZ_TAIPEI).isoformat(timespec="seconds")


def datetime_from_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, TZ_TAIPEI).isoformat(timespec="seconds")


def probe_video_duration_seconds(video_path: Path) -> Optional[float]:
    """Return the duration in seconds when ffprobe can read the video."""
    if not video_path.exists() or video_path.stat().st_size <= 0:
        return None

    ffprobe_bin = getattr(config, "FFPROBE_BIN", "ffprobe")

    try:
        result = subprocess.run(
            [
                ffprobe_bin,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:
        print(f"[WARN] ffprobe failed to run for {video_path.name}: {exc}")
        return None

    if result.returncode != 0:
        err = result.stderr.strip()
        if err:
            print(f"[INFO] ffprobe not ready for {video_path.name}: {err}")
        return None

    try:
        duration = float(result.stdout.strip())
    except Exception:
        return None

    if duration <= 0:
        return None

    return duration


def is_video_playable(video_path: Path) -> bool:
    """Return True when ffprobe can read the MP4."""
    return probe_video_duration_seconds(video_path) is not None


def normalize_video_path(path: Path) -> Path:
    """Map xxx.mp4.tmp to the final xxx.mp4 path."""
    if path.name.endswith(TEMP_VIDEO_SUFFIX):
        return path.with_name(path.name[: -len(TEMP_SUFFIX)])
    return path


def parse_segment_info(filename: str):
    """Parse session_id, device_id, and segment_index from a segment filename."""
    if filename.endswith(TEMP_VIDEO_SUFFIX):
        filename = filename[: -len(TEMP_SUFFIX)]

    pattern = r"^(?P<date>\d{8})_(?P<time>\d{6})_(?P<device_id>.+?)_seg(?P<index>\d+)\.mp4$"
    match = re.match(pattern, filename)

    if not match:
        return None, None, None

    session_id = f"{match.group('date')}_{match.group('time')}"
    device_id = match.group("device_id")
    segment_index = int(match.group("index"))

    return session_id, device_id, segment_index


def session_id_to_datetime(session_id: str) -> Optional[datetime]:
    try:
        dt = datetime.strptime(session_id, "%Y%m%d_%H%M%S")
        return dt.replace(tzinfo=TZ_TAIPEI)
    except Exception:
        return None


def session_id_to_date_dir(session_id: str) -> Optional[str]:
    dt = session_id_to_datetime(session_id)
    return dt.strftime("%Y-%m-%d") if dt else None


def is_file_stable(path: Path, wait_seconds: float) -> bool:
    if not path.exists():
        return False

    size1 = path.stat().st_size
    time.sleep(wait_seconds)

    if not path.exists():
        return False

    size2 = path.stat().st_size
    return size1 == size2 and size2 > 0


def iter_session_video_files(segment_dir: Path):
    """Yield final MP4 files and temp MP4 files."""
    yield from segment_dir.glob("*.mp4")
    yield from segment_dir.glob("*.mp4.tmp")


def has_newer_segment(segment_dir: Path, session_id: str, segment_index: int) -> bool:
    """Return True when a newer segment already exists for the session."""
    for path in iter_session_video_files(segment_dir):
        parsed_session_id, _device_id, parsed_index = parse_segment_info(path.name)
        if parsed_session_id == session_id and parsed_index is not None:
            if parsed_index > segment_index:
                return True
    return False


def finalize_temp_video(temp_path: Path, force: bool = False) -> Optional[Path]:
    """Rename a finalized .mp4.tmp file to .mp4."""
    if not temp_path.name.endswith(TEMP_VIDEO_SUFFIX):
        return normalize_video_path(temp_path)

    final_path = normalize_video_path(temp_path)

    if final_path.exists():
        return final_path

    if not force and not is_file_stable(temp_path, config.FILE_STABLE_WAIT_SECONDS):
        print(f"[INFO] Still writing temp video: {temp_path.name}")
        return None

    # Always verify that the MP4 is readable before renaming it.
    if not is_video_playable(temp_path):
        print(f"[INFO] Temp video not finalized yet, keep as tmp: {temp_path.name}")
        return None

    try:
        temp_path.replace(final_path)
        print(f"[INFO] Video finalized: {temp_path.name} -> {final_path.name}")
        return final_path
    except Exception as exc:
        print(f"[WARN] Failed to finalize temp video {temp_path.name}: {exc}")
        return None


def build_metadata(mp4_path: Path) -> dict:
    mp4_path = normalize_video_path(mp4_path)
    stat = mp4_path.stat()
    actual_duration_seconds = probe_video_duration_seconds(mp4_path)

    session_id, parsed_device_id, segment_index = parse_segment_info(mp4_path.name)
    device_id = parsed_device_id or config.DEVICE_ID
    recording_date = session_id_to_date_dir(session_id) if session_id else None
    session_started_dt = session_id_to_datetime(session_id) if session_id else None

    segment_started_at = None
    segment_ended_at = None

    if session_started_dt is not None and segment_index is not None:
        segment_started_dt = session_started_dt + timedelta(
            seconds=segment_index * config.SEGMENT_SECONDS
        )
        duration_for_end = (
            actual_duration_seconds
            if actual_duration_seconds is not None
            else config.SEGMENT_SECONDS
        )
        segment_ended_dt = segment_started_dt + timedelta(seconds=duration_for_end)
        segment_started_at = segment_started_dt.isoformat(timespec="seconds")
        segment_ended_at = segment_ended_dt.isoformat(timespec="seconds")

    cloud_key = None
    if session_id and recording_date:
        cloud_key = build_cloud_key(recording_date, session_id, mp4_path.name)

    return {
        "schema_version": "1.0",
        "user_id": config.USER_ID,
        "device_id": device_id,
        "session_id": session_id,
        "recording_date": recording_date,
        "segment_index": segment_index,
        "file": {
            "filename": mp4_path.name,
            "local_path": str(mp4_path),
            "json_filename": mp4_path.with_suffix(".json").name,
            "file_size_bytes": stat.st_size,
            "file_modified_at": datetime_from_timestamp(stat.st_mtime),
            "cloud_key": cloud_key,
            "recording_temp_suffix": TEMP_SUFFIX,
        },
        "time": {
            "metadata_created_at": now_iso(),
            "session_started_at": session_started_dt.isoformat(timespec="seconds")
            if session_started_dt
            else None,
            "segment_started_at": segment_started_at,
            "segment_ended_at": segment_ended_at,
            "expected_duration_seconds": config.SEGMENT_SECONDS,
            "actual_duration_seconds": actual_duration_seconds,
            "time_note": "Segment start is estimated from session_id and segment_index; end uses ffprobe duration when available.",
        },
        "video": {
            "width": config.WIDTH,
            "height": config.HEIGHT,
            "fps": config.FPS,
            "input_pixel_format": config.INPUT_PIXEL_FORMAT,
            "encoded_pixel_format": config.ENCODE_PIXEL_FORMAT,
            "codec": config.CODEC,
            "bitrate_kbps": config.BITRATE_KBPS,
            "key_int_max": config.KEY_INT_MAX,
        },
        "recording": {
            "segment_seconds": config.SEGMENT_SECONDS,
            "container": "mp4",
            "muxer": "mp4mux",
            "segmenter": "splitmuxsink",
            "status": "recorded",
        },
        "stream": {
            "enabled": True,
            "protocol": "SRT",
            "media_server_ip": config.MEDIA_SERVER_IP,
            "srt_port": config.SRT_PORT,
            "stream_path": config.STREAM_PATH,
            "srt_latency": config.SRT_LATENCY,
            "tlpktdrop": config.SRT_TLPKTDROP,
            "snddropdelay": config.SRT_SNDDROPDELAY,
            "pkt_size": config.SRT_PKT_SIZE,
        },
        "pipeline_tuning": {
            "pre_encode_queue_buffers": config.PRE_ENCODE_QUEUE_BUFFERS,
            "record_queue_buffers": config.RECORD_QUEUE_BUFFERS,
            "stream_queue_buffers": config.STREAM_QUEUE_BUFFERS,
            "pre_encode_queue_leaky": config.PRE_ENCODE_QUEUE_LEAKY,
            "splitmuxsink_async_finalize": True,
            "splitmuxsink_send_keyframe_requests": True,
        },
        "upload": {
            "status": "pending",
            "uploaded_at": None,
            "retry_count": 0,
            "last_error": None,
        },
    }


def write_metadata_json(mp4_path: Path) -> None:
    mp4_path = normalize_video_path(mp4_path)
    json_path = mp4_path.with_suffix(".json")
    if json_path.exists():
        return

    if not is_video_playable(mp4_path):
        print(f"[WARN] Skip metadata because video is not playable yet: {mp4_path.name}")
        return

    metadata = build_metadata(mp4_path)
    tmp_path = json_path.with_suffix(".json.tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    tmp_path.replace(json_path)
    print(f"[INFO] Metadata created: {json_path.name}")


def process_final_mp4(mp4_path: Path, seen: set) -> None:
    if mp4_path in seen:
        return

    json_path = mp4_path.with_suffix(".json")
    if json_path.exists():
        seen.add(mp4_path)
        return

    print(f"[INFO] Final mp4 detected: {mp4_path.name}")

    if is_file_stable(mp4_path, config.FILE_STABLE_WAIT_SECONDS):
        write_metadata_json(mp4_path)
        seen.add(mp4_path)
    else:
        print(f"[INFO] Still writing final mp4: {mp4_path.name}")


def process_temp_mp4(temp_path: Path, seen: set) -> None:
    parsed_session_id, _device_id, segment_index = parse_segment_info(temp_path.name)
    if parsed_session_id is None or segment_index is None:
        return

    # Skip the currently recording tail segment so it is not renamed too early.
    if not has_newer_segment(temp_path.parent, parsed_session_id, segment_index):
        return

    final_path = finalize_temp_video(temp_path, force=False)
    if final_path is None:
        return

    process_final_mp4(final_path, seen)


def main() -> None:
    segment_dir = Path(os.environ.get("SEGMENT_DIR", str(config.BASE_RECORDING_DIR)))
    segment_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Metadata watcher started")
    print(f"[INFO] Watching: {segment_dir}")
    print(f"[INFO] Temp video suffix: {TEMP_VIDEO_SUFFIX}")
    print()

    seen = set()

    while True:
        for temp_path in sorted(segment_dir.glob("*.mp4.tmp")):
            process_temp_mp4(temp_path, seen)

        for mp4_path in sorted(segment_dir.glob("*.mp4")):
            process_final_mp4(mp4_path, seen)

        time.sleep(config.WATCH_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
