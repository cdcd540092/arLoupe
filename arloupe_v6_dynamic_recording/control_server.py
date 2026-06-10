"""Pi 5 control API for streaming and recording."""

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
controller: Optional[DynamicCaptureController] = None

# Prevent concurrent start/stop operations.
control_lock = threading.Lock()


class StartRecordingRequest(BaseModel):
    # Optional for the demo phase.
    case_id: str | None = None
    operator_id: str | None = None


@app.on_event("startup")
def on_startup():
    """Initialize the controller and start the permanent stream."""
    global controller

    controller = DynamicCaptureController()
    controller.start_streaming()


@app.on_event("shutdown")
def on_shutdown():
    """Stop recording and streaming on shutdown."""
    global controller

    if controller is not None:
        controller.shutdown()


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "arLoupe Pi5 Control API",
        "device_id": config.DEVICE_ID,
    }


@app.get("/api/capture/status")
def get_status():
    """Return the current Pi 5 capture status."""
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not ready")

    recording = controller._recording is not None

    session_id = None
    recording_date = None

    if recording:
        session_id = controller._recording.ctx.session_id
        recording_date = controller._recording.ctx.recording_date

    return {
        "device_id": config.DEVICE_ID,
        "streaming": True,
        "recording": recording,
        "session_id": session_id,
        "recording_date": recording_date,
    }


@app.post("/api/capture/start")
def start_recording(req: StartRecordingRequest):
    """Start recording."""
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not ready")

    with control_lock:
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
            "session_id": session.ctx.session_id,
            "recording_date": session.ctx.recording_date,
            "case_id": req.case_id,
            "operator_id": req.operator_id,
        }


@app.post("/api/capture/stop")
def stop_recording():
    """Stop recording after the MP4 finalize step completes."""
    if controller is None:
        raise HTTPException(status_code=503, detail="Controller not ready")

    with control_lock:
        if controller._recording is None:
            raise HTTPException(
                status_code=409,
                detail="Recording is not running",
            )

        session_id = controller._recording.ctx.session_id
        recording_date = controller._recording.ctx.recording_date

        controller.stop_recording()

        return {
            "status": "recording_stopped",
            "device_id": config.DEVICE_ID,
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