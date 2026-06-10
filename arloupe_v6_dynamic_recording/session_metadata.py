"""Build session metadata JSON files."""

import json
from pathlib import Path

import config
from capture_paths import CaptureContext, build_cloud_session_prefix, now_taipei


def get_recording_mode_metadata() -> dict:
    if config.RECORD_CONTINUOUS:
        return {
            "mode": "continuous",
            "segment_count_limit": None,
            "expected_total_seconds": None,
            "note": "Record continuously until Ctrl+C or process stop.",
        }

    expected_total_seconds = config.SEGMENT_SECONDS * config.RECORD_SEGMENT_COUNT

    return {
        "mode": "fixed_segment_count",
        "segment_count_limit": config.RECORD_SEGMENT_COUNT,
        "expected_total_seconds": expected_total_seconds,
        "note": "Record a fixed number of segments for testing.",
    }


def write_session_metadata(ctx: CaptureContext) -> Path:
    path = ctx.segment_dir / f"session_{ctx.session_id}.json"

    metadata = {
        "schema_version": "1.0",
        "user_id": config.USER_ID,
        "device_id": config.DEVICE_ID,
        "session_id": ctx.session_id,
        "recording_date": ctx.recording_date,
        "started_at": now_taipei().isoformat(timespec="seconds"),
        "local": {
            "segment_dir": str(ctx.segment_dir),
        },
        "cloud": {
            "session_prefix": build_cloud_session_prefix(
                ctx.recording_date,
                ctx.session_id,
            ),
        },
        "video": {
            "video_device": config.VIDEO_DEVICE,
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
            "segmenter": "splitmuxsink",
            **get_recording_mode_metadata(),
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
    }

    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    tmp_path.replace(path)
    return path
