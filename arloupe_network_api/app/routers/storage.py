from fastapi import APIRouter

from app.models import CleanupSettingsUpdateRequest
from app.services.storage import (
    get_cleanup_settings,
    get_storage_status,
    preview_cleanup,
    run_cleanup,
    update_cleanup_settings,
)

router = APIRouter(prefix="/api/storage", tags=["storage"])


@router.get("/status")
def storage_status_get():
    return get_storage_status()


@router.get("/cleanup/settings")
def cleanup_settings_get():
    return get_cleanup_settings()


@router.post("/cleanup/settings")
def cleanup_settings_update(req: CleanupSettingsUpdateRequest):
    if hasattr(req, "model_dump"):
        data = req.model_dump(exclude_none=True)
    else:
        data = req.dict(exclude_none=True)
    return update_cleanup_settings(data)


@router.get("/cleanup/preview")
def cleanup_preview_get():
    return preview_cleanup()


@router.post("/cleanup/run")
def cleanup_run_post():
    return run_cleanup()
