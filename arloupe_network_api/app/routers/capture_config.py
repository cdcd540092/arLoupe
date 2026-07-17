from fastapi import APIRouter

from app.models import CaptureConfigUpdateRequest
from app.services.capture_config import apply_capture_config, get_capture_config, update_capture_config

router = APIRouter(prefix="/api/config", tags=["capture-config"])


@router.get("/capture")
def capture_config_get():
    return get_capture_config()


@router.post("/capture")
def capture_config_update(req: CaptureConfigUpdateRequest):
    # pydantic v1/v2 compatible conversion
    if hasattr(req, "model_dump"):
        data = req.model_dump(exclude_none=True)
    else:
        data = req.dict(exclude_none=True)
    return update_capture_config(data)


@router.post("/capture/apply")
def capture_config_apply():
    return apply_capture_config()
