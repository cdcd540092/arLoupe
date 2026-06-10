"""Dynamic recording controller for arLoupe V6.

This program uses Python GStreamer to keep one pipeline running:

    v4l2src -> videoconvert -> x264enc -> h264parse -> tee
                                                     ├─ always-on SRT branch
                                                     └─ recording branch added and removed at runtime
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TextIO

try:
    import gi

    gi.require_version("Gst", "1.0")
    from gi.repository import Gst, GLib  # type: ignore
except Exception as exc:  # pragma: no cover - shown only when system packages are missing
    raise SystemExit(
        "無法載入 Python GStreamer。請先在 PI5 安裝：\n"
        "sudo apt update\n"
        "sudo apt install -y python3-gi python3-gst-1.0 "
        "gir1.2-gstreamer-1.0 gir1.2-gst-plugins-base-1.0\n"
        f"原始錯誤：{exc}"
    )

import config
from capture_paths import CaptureContext, build_context
from session_finalizer import finalize_session
from session_metadata import write_session_metadata


BASE_DIR = Path(__file__).resolve().parent


@dataclass
class RecordingSession:
    """State for the active recording session."""

    ctx: CaptureContext
    bin: Gst.Bin
    tee_pad: Gst.Pad
    watcher_proc: subprocess.Popen
    watcher_log: TextIO
    log_path: Path


class DynamicCaptureController:
    """Manage the permanent stream and the dynamic recording branch."""

    def __init__(self) -> None:
        Gst.init(None)

        self.pipeline: Gst.Pipeline = self._build_base_pipeline()
        self.tee: Gst.Element = self.pipeline.get_by_name("t")
        if self.tee is None:
            raise RuntimeError("找不到 tee element: t")

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self._on_bus_message)

        self._lock = threading.RLock()
        self._recording: Optional[RecordingSession] = None
        self._quit_requested = False

    # Pipeline setup

    def _build_base_pipeline(self) -> Gst.Pipeline:
        """Build the base pipeline with the streaming branch only."""

        leaky_arg = "leaky=downstream" if config.PRE_ENCODE_QUEUE_LEAKY else ""
        srt_uri = (
            f"srt://{config.MEDIA_SERVER_IP}:{config.SRT_PORT}"
            f"?mode=caller"
            f"&streamid=publish:{config.STREAM_PATH}"
            f"&transtype=live"
            f"&latency={config.SRT_LATENCY}"
            f"&tlpktdrop={config.SRT_TLPKTDROP}"
            f"&snddropdelay={config.SRT_SNDDROPDELAY}"
            f"&pkt_size={config.SRT_PKT_SIZE}"
        )

        # The recording branch is attached to tee only when recording starts.
        pipeline_desc = f"""
            v4l2src name=source device={config.VIDEO_DEVICE} io-mode=mmap do-timestamp=true !
            video/x-raw,format=UYVY,width={config.WIDTH},height={config.HEIGHT},framerate={config.FPS}/1 !
            queue max-size-buffers={config.PRE_ENCODE_QUEUE_BUFFERS} max-size-time=0 max-size-bytes=0 {leaky_arg} !
            videoconvert !
            video/x-raw,format=I420,width={config.WIDTH},height={config.HEIGHT},framerate={config.FPS}/1 !
            queue max-size-buffers={config.PRE_ENCODE_QUEUE_BUFFERS} max-size-time=0 max-size-bytes=0 {leaky_arg} !
            x264enc bitrate={config.BITRATE_KBPS} speed-preset=ultrafast tune=zerolatency
                key-int-max={config.KEY_INT_MAX} bframes=0 byte-stream=true
                sliced-threads=true threads=4 vbv-buf-capacity=100 !
            h264parse config-interval=-1 !
            video/x-h264,stream-format=byte-stream,alignment=au,framerate={config.FPS}/1 !
            tee name=t allow-not-linked=true
            t. ! queue max-size-buffers={config.STREAM_QUEUE_BUFFERS} max-size-time=0 max-size-bytes=0 leaky=downstream !
            h264parse !
            mpegtsmux alignment=7 !
            queue max-size-buffers={config.STREAM_QUEUE_BUFFERS} max-size-time=0 max-size-bytes=0 leaky=downstream !
            srtsink uri="{srt_uri}" sync=false async=false
        """

        pipeline = Gst.parse_launch(pipeline_desc)
        if not isinstance(pipeline, Gst.Pipeline):
            raise RuntimeError("GStreamer pipeline 建立失敗")
        return pipeline

    def _create_record_bin(self, ctx: CaptureContext) -> Gst.Bin:
        """Build the recording branch: queue -> h264parse -> splitmuxsink."""

        record_bin = Gst.Bin.new(f"record_bin_{ctx.session_id}")
        if record_bin is None:
            raise RuntimeError("record_bin 建立失敗")

        queue = Gst.ElementFactory.make("queue", f"record_queue_{ctx.session_id}")
        parser = Gst.ElementFactory.make("h264parse", f"record_h264parse_{ctx.session_id}")
        sink = Gst.ElementFactory.make("splitmuxsink", f"record_splitmuxsink_{ctx.session_id}")

        if queue is None or parser is None or sink is None:
            raise RuntimeError("錄影分支 element 建立失敗，請確認 GStreamer plugins 是否完整")

        queue.set_property("max-size-buffers", int(config.RECORD_QUEUE_BUFFERS))
        queue.set_property("max-size-time", 0)
        queue.set_property("max-size-bytes", 0)

        location = str(
            ctx.segment_dir
            / f"{ctx.session_id}_{config.DEVICE_ID}_seg%05d.mp4{config.RECORDING_TEMP_SUFFIX}"
        )

        sink.set_property("location", location)
        sink.set_property("max-size-time", int(config.SEGMENT_SECONDS * 1_000_000_000))
        sink.set_property("async-finalize", True)
        sink.set_property("send-keyframe-requests", True)
        sink.set_property("muxer-factory", "mp4mux")

        record_bin.add(queue)
        record_bin.add(parser)
        record_bin.add(sink)

        if not queue.link(parser):
            raise RuntimeError("record queue -> h264parse 連接失敗")
        if not parser.link(sink):
            raise RuntimeError("record h264parse -> splitmuxsink 連接失敗")

        sink_pad = queue.get_static_pad("sink")
        ghost_pad = Gst.GhostPad.new("sink", sink_pad)
        if ghost_pad is None:
            raise RuntimeError("record_bin ghost pad 建立失敗")
        record_bin.add_pad(ghost_pad)

        return record_bin

    # Metadata watcher

    def _start_metadata_watcher(self, ctx: CaptureContext) -> tuple[subprocess.Popen, TextIO, Path]:
        """Start a dedicated metadata watcher for the session."""

        env = os.environ.copy()
        env.update(
            {
                "USER_ID": config.USER_ID,
                "DEVICE_ID": config.DEVICE_ID,
                "SESSION_ID": ctx.session_id,
                "SEGMENT_DIR": str(ctx.segment_dir),
            }
        )

        log_path = ctx.log_dir / f"metadata_{ctx.session_id}.log"
        log_file = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(BASE_DIR / "metadata_watcher.py")],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=str(BASE_DIR),
            env=env,
        )
        return proc, log_file, log_path

    @staticmethod
    def _terminate_process(proc: subprocess.Popen, name: str, timeout: float = 5.0) -> None:
        if proc.poll() is not None:
            return

        print(f"[INFO] Stopping {name}...")
        try:
            proc.send_signal(signal.SIGINT)
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            print(f"[WARN] {name} did not stop in time, killing...")
            proc.kill()
            proc.wait()

    # ------------------------------------------------------------------
    # 對外控制方法
    # ------------------------------------------------------------------

    def start_streaming(self) -> None:
        """啟動常駐 SRT 串流。"""

        print("[INFO] Starting base pipeline: streaming only")
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("GStreamer pipeline 進入 PLAYING 失敗")

        print("[INFO] Streaming started")
        print(
            "[INFO] SRT publish: "
            f"srt://{config.MEDIA_SERVER_IP}:{config.SRT_PORT}?streamid=publish:{config.STREAM_PATH}"
        )

    def start_recording(self) -> None:
        """Start recording without interrupting the stream."""

        with self._lock:
            if self._recording is not None:
                print("[WARN] Recording is already running")
                return

            ctx = build_context()
            session_json = write_session_metadata(ctx)
            watcher_proc, watcher_log, watcher_log_path = self._start_metadata_watcher(ctx)
            record_bin = self._create_record_bin(ctx)

            self.pipeline.add(record_bin)

            tee_pad = self.tee.request_pad_simple("src_%u")
            if tee_pad is None:
                # Older GStreamer versions may not have request_pad_simple.
                tee_pad = self.tee.get_request_pad("src_%u")
            if tee_pad is None:
                raise RuntimeError("tee request pad 失敗")

            record_sink_pad = record_bin.get_static_pad("sink")
            if record_sink_pad is None:
                raise RuntimeError("record_bin sink pad 不存在")

            link_ret = tee_pad.link(record_sink_pad)
            if link_ret != Gst.PadLinkReturn.OK:
                raise RuntimeError(f"tee -> record_bin 連接失敗：{link_ret}")

            record_bin.sync_state_with_parent()

            self._recording = RecordingSession(
                ctx=ctx,
                bin=record_bin,
                tee_pad=tee_pad,
                watcher_proc=watcher_proc,
                watcher_log=watcher_log,
                log_path=watcher_log_path,
            )

            print("[INFO] Recording started")
            print(f"[INFO] Session ID       : {ctx.session_id}")
            print(f"[INFO] Segment dir      : {ctx.segment_dir}")
            print(f"[INFO] Session metadata : {session_json}")
            print(f"[INFO] Watcher log      : {watcher_log_path}")

    def stop_recording(self) -> None:
        """Stop the recording branch and finalize files while streaming continues."""

        with self._lock:
            session = self._recording
            if session is None:
                print("[WARN] Recording is not running")
                return

            print("[INFO] Stopping recording branch...")

            # Block new buffers, send EOS, then finalize files after playback checks pass.
            record_sink_pad = session.bin.get_static_pad("sink")
            block_probe_id = None

            def _drop_late_buffers(_pad, info):
                if info.type & Gst.PadProbeType.BUFFER:
                    return Gst.PadProbeReturn.DROP
                return Gst.PadProbeReturn.OK

            try:
                block_probe_id = session.tee_pad.add_probe(
                    Gst.PadProbeType.BUFFER,
                    _drop_late_buffers,
                )
                print("[INFO] Record branch input blocked")
            except Exception as exc:
                print(f"[WARN] Failed to block record branch input: {exc}")

            eos_sent = False
            try:
                if record_sink_pad is not None:
                    eos_sent = bool(record_sink_pad.send_event(Gst.Event.new_eos()))
                    print(f"[INFO] EOS sent to record branch sink pad: {eos_sent}")
            except Exception as exc:
                print(f"[WARN] Failed to send EOS to record branch sink pad: {exc}")

            if not eos_sent:
                try:
                    eos_sent = bool(session.bin.send_event(Gst.Event.new_eos()))
                    print(f"[INFO] EOS sent to record bin: {eos_sent}")
                except Exception as exc:
                    print(f"[WARN] Failed to send EOS to record bin: {exc}")

            wait_seconds = float(getattr(config, "RECORD_STOP_EOS_WAIT_SECONDS", 1.0))
            if wait_seconds > 0:
                print(f"[INFO] Initial EOS wait: {wait_seconds:.1f}s")
                time.sleep(wait_seconds)

            self._terminate_process(session.watcher_proc, "metadata watcher")
            session.watcher_log.close()

            # Wait for the last segment to become playable before finalizing it.
            finalize_session(session.ctx)

            # Remove the recording branch after cleanup; streaming stays PLAYING.
            try:
                session.bin.set_state(Gst.State.NULL)
                if record_sink_pad is not None and session.tee_pad.is_linked():
                    session.tee_pad.unlink(record_sink_pad)
                if block_probe_id is not None:
                    try:
                        session.tee_pad.remove_probe(block_probe_id)
                    except Exception:
                        pass
                self.tee.release_request_pad(session.tee_pad)
                self.pipeline.remove(session.bin)
            except Exception as exc:
                print(f"[WARN] Failed to remove record branch cleanly: {exc}")

            self._recording = None
            print("[INFO] Recording stopped; streaming is still running")

    def shutdown(self) -> None:
        """Stop the whole program."""

        with self._lock:
            self._quit_requested = True

        if self._recording is not None:
            self.stop_recording()

        print("[INFO] Stopping streaming pipeline...")
        self.pipeline.set_state(Gst.State.NULL)
        print("[INFO] Capture controller stopped")

    # Bus messages

    def _on_bus_message(self, _bus: Gst.Bus, message: Gst.Message) -> None:
        msg_type = message.type

        if msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"[ERROR] GStreamer error: {err}")
            if debug:
                print(f"[ERROR] Debug: {debug}")
            self._quit_requested = True

        elif msg_type == Gst.MessageType.WARNING:
            warn, debug = message.parse_warning()
            print(f"[WARN] GStreamer warning: {warn}")
            if debug:
                print(f"[WARN] Debug: {debug}")

        elif msg_type == Gst.MessageType.EOS:
            # Stopping only the recording branch should not EOS the whole pipeline.
            print("[WARN] Pipeline EOS received")
            self._quit_requested = True

        elif msg_type == Gst.MessageType.ELEMENT:
            structure = message.get_structure()
            if structure is not None:
                name = structure.get_name()
                if name.startswith("splitmuxsink"):
                    print(f"[INFO] {name}: {structure.to_string()}")

    # Command interface

    def run_command_loop(self) -> None:
        """Local CLI control for testing; can be replaced with cloud polling later."""

        if config.START_RECORDING_ON_BOOT:
            self.start_recording()

        print()
        print("Command:")
        print("  r = start recording")
        print("  s = stop recording")
        print("  q = quit")
        print()

        while not self._quit_requested:
            try:
                cmd = input("arloupe> ").strip().lower()
            except EOFError:
                cmd = "q"
            except KeyboardInterrupt:
                print()
                cmd = "q"

            if cmd == "r":
                self.start_recording()
            elif cmd == "s":
                self.stop_recording()
            elif cmd == "q":
                break
            elif cmd == "":
                continue
            else:
                print("[WARN] Unknown command. Use r / s / q")

        self.shutdown()
