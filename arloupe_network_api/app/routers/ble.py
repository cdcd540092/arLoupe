from fastapi import APIRouter

from app.models import BleCommandRequest
from app.services.ble import run_ble_command, run_ble_query

router = APIRouter(prefix="/api/ble", tags=["ble"])


@router.post("/command")
def ble_command(req: BleCommandRequest):
    return run_ble_command(req.command)


@router.get("/status")
def ble_status():
    return run_ble_query("status")


@router.get("/services")
def ble_services():
    return run_ble_query("services")


@router.get("/help")
def ble_help():
    return run_ble_query("help")
