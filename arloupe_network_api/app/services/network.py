from __future__ import annotations

import re

from app.settings import (
    WIFI_IFACE,
    HOTSPOT_DHCP_SERVICE,
    ENTER_HOTSPOT_SCRIPT,
)
from app.services.commands import run_cmd, run_cmd_for_job
from app.services.jobs import write_job


def parse_ipv4_from_ip_output(text: str) -> str:
    """從 ip -4 addr show wlan0 輸出抓出 IPv4，不含 /24。"""
    match = re.search(r"inet\s+([0-9.]+)/", text)
    if not match:
        return ""
    return match.group(1)


def get_status_data() -> dict:
    active = run_cmd(["nmcli", "connection", "show", "--active"])
    ip = run_cmd(["ip", "-4", "addr", "show", WIFI_IFACE])
    dhcp = run_cmd(["systemctl", "is-active", HOTSPOT_DHCP_SERVICE], check_timeout=False)

    wlan0_text = ip["stdout"]
    ipv4 = parse_ipv4_from_ip_output(wlan0_text)

    if "10.42.0.1/24" in wlan0_text:
        mode = "hotspot"
    elif ipv4:
        mode = "wifi"
    else:
        mode = "unknown"

    return {
        "ok": True,
        "mode": mode,
        "ipv4": ipv4,
        "access_url": f"http://{ipv4}:7001" if ipv4 else "",
        "active_connections": active["stdout"],
        "wlan0_ip": wlan0_text,
        "hotspot_dhcp": dhcp["stdout"].strip(),
    }


def run_script_background(script_path: str, job_type: str, start_message: str) -> None:
    """背景執行切換網路的腳本，並記錄最基本任務狀態。"""
    write_job({
        "ok": True,
        "type": job_type,
        "status": "running",
        "step": "start_script",
        "message": start_message,
        "error": "",
        "stdout": "",
        "stderr": "",
    })

    result = run_cmd_for_job(["sudo", script_path], timeout=90)

    if result["returncode"] == 0:
        status = get_status_data()
        write_job({
            "ok": True,
            "type": job_type,
            "status": "success",
            "step": "done",
            "message": "網路模式切換完成",
            "error": "",
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "mode": status.get("mode", "unknown"),
            "ipv4": status.get("ipv4", ""),
            "access_url": status.get("access_url", ""),
        })
    else:
        write_job({
            "ok": False,
            "type": job_type,
            "status": "failed",
            "step": "run_script",
            "message": "網路模式切換失敗",
            "error": result["stderr"] or result["stdout"] or "未知錯誤",
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"],
        })


def restore_hotspot_after_failed_wifi() -> None:
    """如果從熱點模式切 Wi-Fi 失敗，嘗試恢復熱點，避免設備失聯。"""
    run_cmd_for_job(["sudo", ENTER_HOTSPOT_SCRIPT], timeout=90)
