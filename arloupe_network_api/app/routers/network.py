from fastapi import APIRouter, BackgroundTasks

from app.settings import ENTER_HOTSPOT_SCRIPT, ENTER_WIFI_SCRIPT
from app.services.network import get_status_data, run_script_background

router = APIRouter(prefix="/api/network", tags=["network"])


@router.get("/status")
def network_status():
    return get_status_data()


@router.post("/hotspot")
def enter_hotspot(background_tasks: BackgroundTasks):
    background_tasks.add_task(
        run_script_background,
        ENTER_HOTSPOT_SCRIPT,
        "enter_hotspot",
        "正在切換到熱點模式",
    )
    return {
        "ok": True,
        "message": "即將切換到熱點模式。請稍後連線 Wi-Fi：arLoupe-Setup，然後打開 http://10.42.0.1:7001",
    }


@router.post("/wifi")
def enter_default_wifi(background_tasks: BackgroundTasks):
    background_tasks.add_task(
        run_script_background,
        ENTER_WIFI_SCRIPT,
        "enter_default_wifi",
        "正在切回預設 Wi-Fi",
    )
    return {
        "ok": True,
        "message": "即將切回預設 Wi-Fi。此頁面可能會斷線，請改連外部 Wi-Fi 後重新開啟 Pi 5 網頁。",
    }
