"""Pi 5 control API for streaming and recording.

Manual stream version:
- Starting this FastAPI server does NOT start GStreamer.
- POST /api/stream/start starts the base streaming pipeline.
- POST /api/stream/stop stops the streaming pipeline when not recording.
- POST /api/capture/start auto-starts streaming first if needed, then starts recording.
- POST /api/capture/stop stops recording only; streaming remains running.
"""

from __future__ import annotations

import threading
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import config
from capture_controller import DynamicCaptureController


app = FastAPI(title="arLoupe Pi5 Control API")

# Demo mode allows cross-origin requests from the Windows frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton controller instance.
# None means the GStreamer pipeline is not running.
controller: Optional[DynamicCaptureController] = None

# Prevent concurrent start/stop operations.
control_lock = threading.Lock()


class StartRecordingRequest(BaseModel):
    # Optional for the demo phase.
    case_id: str | None = None
    operator_id: str | None = None


def _controller_status() -> dict:
    """Build a safe status response whether the pipeline exists or not."""
    global controller

    streaming = controller is not None
    recording = False
    session_id = None
    recording_date = None

    if controller is not None and controller._recording is not None:
        recording = True
        session_id = controller._recording.ctx.session_id
        recording_date = controller._recording.ctx.recording_date

    return {
        "device_id": config.DEVICE_ID,
        "streaming": streaming,
        "recording": recording,
        "session_id": session_id,
        "recording_date": recording_date,
        "stream_path": config.STREAM_PATH,
        "media_server_ip": config.MEDIA_SERVER_IP,
        "srt_port": config.SRT_PORT,
    }


def _start_streaming_locked() -> dict:
    """Create controller and start base streaming pipeline. Caller must hold lock."""
    global controller

    if controller is not None:
        return {
            "status": "stream_already_running",
            **_controller_status(),
        }

    new_controller = DynamicCaptureController()
    try:
        new_controller.start_streaming()
    except Exception:
        # Avoid keeping a half-created controller if GStreamer startup fails.
        try:
            new_controller.shutdown()
        except Exception:
            pass
        raise

    controller = new_controller

    return {
        "status": "stream_started",
        **_controller_status(),
    }


@app.on_event("startup")
def on_startup():
    """Start the API only. Do not start GStreamer here."""
    print("[INFO] arLoupe Pi5 Control API started")
    print("[INFO] Stream is idle. Use POST /api/stream/start to start streaming.")


@app.on_event("shutdown")
def on_shutdown():
    """Stop recording and streaming on shutdown."""
    global controller

    with control_lock:
        if controller is not None:
            controller.shutdown()
            controller = None


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "arLoupe Pi5 Control API",
        "device_id": config.DEVICE_ID,
        "streaming_auto_start": False,
    }


@app.get("/api/capture/status")
def get_status():
    """Return the current Pi 5 capture status."""
    return _controller_status()


@app.post("/api/stream/start")
def start_stream():
    """Start the base streaming pipeline."""
    with control_lock:
        try:
            return _start_streaming_locked()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start stream: {exc}",
            )


@app.post("/api/stream/stop")
def stop_stream():
    """Stop the base streaming pipeline.

    Recording depends on the base pipeline, so stream cannot be stopped while
    recording is active.
    """
    global controller

    with control_lock:
        if controller is None:
            return {
                "status": "stream_already_stopped",
                **_controller_status(),
            }

        if controller._recording is not None:
            raise HTTPException(
                status_code=409,
                detail="Recording is running. Stop recording before stopping stream.",
            )

        controller.shutdown()
        controller = None

        return {
            "status": "stream_stopped",
            **_controller_status(),
        }


@app.post("/api/capture/start")
def start_recording(req: StartRecordingRequest):
    """Start recording.

    If streaming is not running, this endpoint starts the base streaming pipeline
    first, then attaches the recording branch.
    """
    global controller

    with control_lock:
        try:
            if controller is None:
                _start_streaming_locked()

            if controller is None:
                raise HTTPException(
                    status_code=500,
                    detail="Controller not available after stream startup",
                )

            if controller._recording is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Recording is already running",
                )

            controller.start_recording()

            session = controller._recording
            if session is None:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to start recording",
                )

            return {
                "status": "recording_started",
                "device_id": config.DEVICE_ID,
                "streaming": True,
                "recording": True,
                "session_id": session.ctx.session_id,
                "recording_date": session.ctx.recording_date,
                "case_id": req.case_id,
                "operator_id": req.operator_id,
            }

        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start recording: {exc}",
            )


@app.post("/api/capture/stop")
def stop_recording():
    """Stop recording after the MP4 finalize step completes.

    Streaming remains running after recording stops.
    """
    if controller is None:
        raise HTTPException(status_code=409, detail="Stream is not running")

    with control_lock:
        if controller is None:
            raise HTTPException(status_code=409, detail="Stream is not running")

        if controller._recording is None:
            raise HTTPException(
                status_code=409,
                detail="Recording is not running",
            )

        session_id = controller._recording.ctx.session_id
        recording_date = controller._recording.ctx.recording_date

        try:
            controller.stop_recording()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to stop recording: {exc}",
            )

        return {
            "status": "recording_stopped",
            "device_id": config.DEVICE_ID,
            "streaming": True,
            "recording": False,
            "session_id": session_id,
            "recording_date": recording_date,
        }


if __name__ == "__main__":
    uvicorn.run(
        "control_server:app",
        host="0.0.0.0",
        port=7000,
        reload=False,
    )
