from fastapi import APIRouter

from app.services.jobs import read_job, clear_job

router = APIRouter(prefix="/api/network/job", tags=["jobs"])


@router.get("/status")
def job_status():
    return read_job()


@router.post("/clear")
def job_clear():
    clear_job()
    return {"ok": True, "message": "已清除任務狀態"}
