"""arLoupe V6 startup entry point."""

import config
from capture_controller import DynamicCaptureController


def print_startup_info() -> None:
    print("=" * 72)
    print("[INFO] arLoupe Capture V6 - Dynamic Recording")
    print(f"[INFO] User ID       : {config.USER_ID}")
    print(f"[INFO] Device ID     : {config.DEVICE_ID}")
    print(f"[INFO] Video device  : {config.VIDEO_DEVICE}")
    print(f"[INFO] Resolution    : {config.WIDTH}x{config.HEIGHT}@{config.FPS}")
    print(f"[INFO] Bitrate       : {config.BITRATE_KBPS} kbps")
    print(f"[INFO] Segment length: {config.SEGMENT_SECONDS} seconds")
    print(f"[INFO] Start record  : {config.START_RECORDING_ON_BOOT}")
    print(f"[INFO] SRT target    : {config.MEDIA_SERVER_IP}:{config.SRT_PORT}")
    print(f"[INFO] Stream path   : {config.STREAM_PATH}")
    print("=" * 72)
    print()


def main() -> None:
    print_startup_info()
    controller = DynamicCaptureController()
    controller.start_streaming()
    controller.run_command_loop()


if __name__ == "__main__":
    main()
