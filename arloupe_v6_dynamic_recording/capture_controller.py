#!/usr/bin/env python3
"""arLoupe V6 動態錄影控制器。

這支程式使用 Python GStreamer 建立一條常駐 pipeline：

    v4l2src -> source caps/decode -> videoconvert -> x264enc -> h264parse -> tee
                                                                  ├─ SRT 串流分支，永遠開啟
                                                                  └─ 錄影分支，執行中動態新增 / 移除

支援兩種影像來源：

1. TC358743 / CSI HDMI 輸入：
   INPUT_PIXEL_FORMAT = "UYVY"
   pipeline source:
       video/x-raw,format=UYVY,...

2. USB HDMI 擷取卡：
   INPUT_PIXEL_FORMAT = "MJPG" 或 "MJPEG"
   pipeline source:
       image/jpeg,... ! jpegdec

操作目標：
1. 開機先只串流，不產生 mp4。
2. 按 r 後中途開始錄影。
3. 按 s 後停止錄影並收尾 mp4/json，串流不中斷。
4. 按 q 後結束程式。
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
except Exception as exc:  # pragma: no cover - 只在缺少系統套件時顯示友善錯誤
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
    """目前正在錄影的 session 狀態。"""

    ctx: CaptureContext
    bin: Gst.Bin
    tee_pad: Gst.Pad
    watcher_proc: subprocess.Popen
    watcher_log: TextIO
    log_path: Path


class DynamicCaptureController:
    """管理常駐串流與動態錄影分支。"""

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

    # ------------------------------------------------------------------
    # Pipeline 建立
    # ------------------------------------------------------------------

    def _build_source_desc(self, input_fps: int) -> str:
        """依照 config.INPUT_PIXEL_FORMAT 建立影像來源段。

        USB HDMI 擷取卡通常是 MJPG：
            image/jpeg ! jpegdec

        TC358743 / CSI 通常是 UYVY：
            video/x-raw,format=UYVY
        """

        input_pixel_format = str(getattr(config, "INPUT_PIXEL_FORMAT", "UYVY")).upper()

        # USB HDMI capture card：MJPEG/MJPG
        if input_pixel_format in ("MJPG", "MJPEG"):
            return f"""
                v4l2src name=source device={config.VIDEO_DEVICE} io-mode=mmap do-timestamp=true !
                image/jpeg,width={config.WIDTH},height={config.HEIGHT},framerate={input_fps}/1 !
                jpegdec !
                videorate drop-only=true !
                video/x-raw,width={config.WIDTH},height={config.HEIGHT},framerate={config.FPS}/1 !
            """

        # 原本 TC358743 / CSI：UYVY 或其他 raw 格式
        return f"""
            v4l2src name=source device={config.VIDEO_DEVICE} io-mode=mmap do-timestamp=true !
            video/x-raw,format={input_pixel_format},width={config.WIDTH},height={config.HEIGHT},framerate={input_fps}/1 !
            videorate drop-only=true !
            video/x-raw,format={input_pixel_format},width={config.WIDTH},height={config.HEIGHT},framerate={config.FPS}/1 !
        """

    def _build_base_pipeline(self) -> Gst.Pipeline:
        """建立只包含串流分支的基礎 pipeline。

        注意：這裡沒有錄影分支。
        錄影分支會在 start_recording() 時動態掛到 tee。
        """

        leaky_arg = "leaky=downstream" if config.PRE_ENCODE_QUEUE_LEAKY else ""

        # INPUT_FPS 代表來源輸入幀率，FPS 代表後續串流與錄影輸出幀率。
        # 例如：
        #   USB 擷取卡 1080p30：INPUT_FPS=30, FPS=30
        #   CSI 1080p60 但輸出 30：INPUT_FPS=60, FPS=30
        input_fps = int(getattr(config, "INPUT_FPS", config.FPS))

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

        source_desc = self._build_source_desc(input_fps)

        pipeline_desc = f"""
            {source_desc}
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

        print("[INFO] GStreamer source mode:")
        print(f"[INFO]   VIDEO_DEVICE       = {config.VIDEO_DEVICE}")
        print(f"[INFO]   INPUT_PIXEL_FORMAT = {getattr(config, 'INPUT_PIXEL_FORMAT', 'UYVY')}")
        print(f"[INFO]   INPUT_FPS          = {input_fps}")
        print(f"[INFO]   OUTPUT FPS         = {config.FPS}")
        print(f"[INFO]   SIZE               = {config.WIDTH}x{config.HEIGHT}")

        pipeline = Gst.parse_launch(pipeline_desc)
        if not isinstance(pipeline, Gst.Pipeline):
            raise RuntimeError("GStreamer pipeline 建立失敗")

        return pipeline

    def _create_record_bin(self, ctx: CaptureContext) -> Gst.Bin:
        """建立錄影分支：queue -> h264parse -> splitmuxsink。"""

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

        # splitmuxsink 依 keyframe 與時間門檻切段，實測可能會比設定少約 1 秒。
        # 使用者看到的 SEGMENT_SECONDS 不變，只在 GStreamer 內部多給一點補償時間。
        segment_padding = float(getattr(config, "SEGMENT_TIME_PADDING_SECONDS", 0.0))
        effective_segment_seconds = float(config.SEGMENT_SECONDS) + segment_padding

        sink.set_property("max-size-time", int(effective_segment_seconds * 1_000_000_000))
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
        if sink_pad is None:
            raise RuntimeError("record queue sink pad 不存在")

        ghost_pad = Gst.GhostPad.new("sink", sink_pad)
        if ghost_pad is None:
            raise RuntimeError("record_bin ghost pad 建立失敗")

        record_bin.add_pad(ghost_pad)

        return record_bin

    # ------------------------------------------------------------------
    # Metadata watcher
    # ------------------------------------------------------------------

    def _start_metadata_watcher(self, ctx: CaptureContext) -> tuple[subprocess.Popen, TextIO, Path]:
        """每個錄影 session 啟動自己的 metadata watcher。"""

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
        """安全停止子程序。"""

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
        """在不中斷串流的情況下開始錄影。"""

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
                # 舊版 GStreamer 可能沒有 request_pad_simple。
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
        """停止錄影分支並收尾檔案；SRT 串流維持 PLAYING。"""

        with self._lock:
            session = self._recording

            if session is None:
                print("[WARN] Recording is not running")
                return

            print("[INFO] Stopping recording branch...")

            # 停止錄影的關鍵：
            # 1. 先阻擋後續 buffer 進入錄影分支，避免 EOS 後又繼續寫入。
            # 2. 再把 EOS 送進 record_bin 的 sink ghost pad，讓 splitmuxsink/mp4mux 正常寫完 moov atom。
            # 3. 不要立刻把 .mp4.tmp 改名，finalize_session() 會用 ffprobe 確認可播放才改名。
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

            # 等最後一段真正可播放後，才把 .mp4.tmp 改名為 .mp4 並產生 metadata。
            finalize_session(session.ctx)

            # 收尾完成後再移除錄影分支。串流分支仍然保持 PLAYING。
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
        """結束整個程式。"""

        with self._lock:
            self._quit_requested = True

        if self._recording is not None:
            self.stop_recording()

        print("[INFO] Stopping streaming pipeline...")
        self.pipeline.set_state(Gst.State.NULL)
        print("[INFO] Capture controller stopped")

    # ------------------------------------------------------------------
    # Bus 訊息
    # ------------------------------------------------------------------

    def _on_bus_message(self, _bus: Gst.Bus, message: Gst.Message) -> None:
        """處理 GStreamer bus 訊息。"""

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
            # 正常情況下，單獨停止錄影分支不應該讓整條 pipeline EOS。
            print("[WARN] Pipeline EOS received")
            self._quit_requested = True

        elif msg_type == Gst.MessageType.ELEMENT:
            structure = message.get_structure()
            if structure is not None:
                name = structure.get_name()
                if name.startswith("splitmuxsink"):
                    print(f"[INFO] {name}: {structure.to_string()}")

    # ------------------------------------------------------------------
    # 指令介面
    # ------------------------------------------------------------------

    def run_command_loop(self) -> None:
        """本機測試用命令列控制。之後可替換成 API 或雲端 config polling。"""

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