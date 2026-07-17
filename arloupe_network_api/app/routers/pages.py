from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.settings import STATIC_DIR

router = APIRouter()


@router.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))
