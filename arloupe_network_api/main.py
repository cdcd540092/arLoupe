from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.settings import STATIC_DIR
from app.routers import pages, network, jobs, wifi, videos, ble, capture_config, storage


app = FastAPI(title="arLoupe Network API")

# 前端靜態檔案
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# 路由模組
app.include_router(pages.router)
app.include_router(network.router)
app.include_router(jobs.router)
app.include_router(wifi.router)
app.include_router(videos.router)
app.include_router(ble.router)
app.include_router(capture_config.router)
app.include_router(storage.router)
