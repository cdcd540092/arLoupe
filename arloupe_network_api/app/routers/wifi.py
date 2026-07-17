from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.models import WifiConnectRequest, SavedWifiConnectRequest, WifiForgetRequest
from app.services.wifi import (
    get_saved_wifi_profiles,
    build_wifi_scan_result,
    connect_wifi_background,
    connect_saved_wifi_background,
    forget_wifi_background,
)

router = APIRouter(prefix="/api/network/wifi", tags=["wifi"])


@router.get("/saved")
def saved_wifi():
    return {"ok": True, "profiles": list(get_saved_wifi_profiles().values())}


@router.get("/scan")
def scan_wifi():
    return build_wifi_scan_result()


@router.post("/connect")
def connect_wifi(req: WifiConnectRequest, background_tasks: BackgroundTasks):
    ssid = req.ssid.strip()
    password = req.password

    if not ssid:
        raise HTTPException(status_code=400, detail="SSID 不可為空")

    background_tasks.add_task(connect_wifi_background, ssid, password)
    return {
        "ok": True,
        "message": f"已開始連線到 Wi-Fi：{ssid}。請查看下方連線進度。",
    }


@router.post("/connect-saved")
def connect_saved_wifi(req: SavedWifiConnectRequest, background_tasks: BackgroundTasks):
    ssid = req.ssid.strip()
    connection_name = req.connection_name.strip()

    if not ssid and not connection_name:
        raise HTTPException(status_code=400, detail="SSID 或 connection_name 至少要有一個")

    background_tasks.add_task(connect_saved_wifi_background, ssid, connection_name)
    return {
        "ok": True,
        "message": f"已開始連線到已儲存 Wi-Fi：{ssid or connection_name}。請查看下方連線進度。",
    }


@router.post("/forget")
def forget_wifi(req: WifiForgetRequest, background_tasks: BackgroundTasks):
    ssid = req.ssid.strip()
    connection_name = req.connection_name.strip()

    if not ssid and not connection_name:
        raise HTTPException(status_code=400, detail="SSID 或 connection_name 至少要有一個")

    background_tasks.add_task(forget_wifi_background, ssid, connection_name)
    return {
        "ok": True,
        "message": f"已開始刪除 Wi-Fi：{ssid or connection_name}",
    }
