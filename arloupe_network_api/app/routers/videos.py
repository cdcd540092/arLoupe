from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.settings import MAX_VIDEO_LIST_ITEMS
from app.services.videos import list_local_videos, safe_recording_file

router = APIRouter(prefix="/api/videos", tags=["videos"])


@router.get("/list")
def videos_list(date: str = "", limit: int = MAX_VIDEO_LIST_ITEMS):
    return list_local_videos(date=date, limit=limit)


@router.get("/file/{recording_date}/{filename}")
def video_file(recording_date: str, filename: str, download: int = 0):
    path = safe_recording_file(recording_date, filename, allowed_suffixes=(".mp4",))

    if download:
        return FileResponse(
            path,
            media_type="video/mp4",
            filename=path.name,
        )

    return FileResponse(
        path,
        media_type="video/mp4",
    )


@router.get("/metadata/{recording_date}/{filename}")
def video_metadata(recording_date: str, filename: str):
    path = safe_recording_file(recording_date, filename, allowed_suffixes=(".json",))
    return FileResponse(
        path,
        media_type="application/json",
    )
