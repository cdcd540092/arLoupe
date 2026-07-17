from __future__ import annotations

import time

from fastapi import HTTPException

from app.settings import (
    WIFI_IFACE,
    HOTSPOT_NAME,
    HOTSPOT_SSID,
    HOTSPOT_DHCP_SERVICE,
)
from app.services.commands import run_cmd, run_cmd_for_job
from app.services.jobs import write_job
from app.services.network import get_status_data, restore_hotspot_after_failed_wifi


def get_active_connection_names() -> set[str]:
    result = run_cmd(["nmcli", "-t", "-f", "NAME", "connection", "show", "--active"], check_timeout=False)
    if result["returncode"] != 0:
        return set()
    return {line.strip() for line in result["stdout"].splitlines() if line.strip()}


def get_saved_wifi_profiles() -> dict[str, dict]:
    """
    回傳已儲存 Wi-Fi profiles，key 用 SSID。
    部分 netplan 產生的 connection name 不等於 SSID，所以要讀 802-11-wireless.ssid。
    """
    result = run_cmd(["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"], check_timeout=False)
    active_names = get_active_connection_names()
    saved: dict[str, dict] = {}

    if result["returncode"] != 0:
        return saved

    for line in result["stdout"].splitlines():
        parts = line.split(":", 1)
        if len(parts) != 2:
            continue

        conn_name, conn_type = parts[0].strip(), parts[1].strip()
        if conn_type != "802-11-wireless":
            continue
        if conn_name == HOTSPOT_NAME:
            continue

        detail = run_cmd(
            ["nmcli", "-g", "802-11-wireless.ssid", "connection", "show", conn_name],
            check_timeout=False,
        )

        ssid = detail["stdout"].strip() if detail["returncode"] == 0 else ""
        if not ssid:
            # 有些 connection name 本身就是 SSID
            ssid = conn_name

        saved[ssid] = {
            "ssid": ssid,
            "saved": True,
            "active": conn_name in active_names,
            "connection_name": conn_name,
        }

    return saved


def dbm_to_percent(dbm_text: str) -> str:
    """粗略把 dBm 轉成 0~100。-30 dBm 很強，-90 dBm 很弱。"""
    try:
        dbm = float(dbm_text)
        percent = int(max(0, min(100, 2 * (dbm + 90))))
        return str(percent)
    except ValueError:
        return "0"


def build_wifi_scan_result() -> dict:
    """
    掃描附近 Wi-Fi，並合併已儲存 / 目前連線狀態。
    策略：優先 iw ap-force，失敗或沒掃到再 fallback nmcli。
    """
    status = get_status_data()
    mode = status.get("mode", "unknown")
    saved_profiles = get_saved_wifi_profiles()
    networks: list[dict] = []

    def add_network(ssid: str, signal: str, signal_dbm: str, security: str, source: str) -> None:
        ssid = ssid.strip()
        if not ssid or ssid == HOTSPOT_SSID:
            return

        saved_info = saved_profiles.get(ssid, {})
        networks.append({
            "ssid": ssid,
            "signal": signal,
            "signal_dbm": signal_dbm,
            "security": security,
            "scan_source": source,
            "saved": bool(saved_info.get("saved", False)),
            "active": bool(saved_info.get("active", False)),
            "connection_name": saved_info.get("connection_name", ""),
        })

    iw_result = run_cmd_for_job(["sudo", "iw", "dev", WIFI_IFACE, "scan", "ap-force"], timeout=25)
    if iw_result["returncode"] == 0:
        current_signal_dbm = ""
        for line in iw_result["stdout"].splitlines():
            stripped = line.strip()
            if stripped.startswith("signal:"):
                current_signal_dbm = stripped.replace("signal:", "", 1).replace("dBm", "").strip()
            elif stripped.startswith("SSID:"):
                ssid = stripped.replace("SSID:", "", 1).strip()
                if ssid:
                    add_network(
                        ssid=ssid,
                        signal=dbm_to_percent(current_signal_dbm),
                        signal_dbm=current_signal_dbm,
                        security="未知",
                        source="iw-ap-force",
                    )
                current_signal_dbm = ""

    scan_source = "iw-ap-force"

    if len(networks) == 0:
        nmcli_result = run_cmd_for_job(
            ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "yes"],
            timeout=25,
        )
        scan_source = "nmcli-fallback"

        if nmcli_result["returncode"] != 0:
            raise HTTPException(status_code=500, detail={"iw_result": iw_result, "nmcli_result": nmcli_result})

        for line in nmcli_result["stdout"].splitlines():
            parts = line.split(":", 2)
            if len(parts) < 2:
                continue
            add_network(
                ssid=parts[0].strip(),
                signal=parts[1].strip(),
                signal_dbm="",
                security=parts[2].strip() if len(parts) >= 3 else "",
                source="nmcli-fallback",
            )

    # 去除重複 SSID，保留 active > saved > 訊號強者
    # 注意：只顯示本次實際掃描到的 SSID；已儲存但未掃到的不顯示。
    unique: dict[str, dict] = {}
    for net in networks:
        ssid = net["ssid"]
        signal_value = int(net["signal"]) if str(net["signal"]).isdigit() else 0
        score = signal_value + (10000 if net.get("active") else 0) + (1000 if net.get("saved") else 0)

        if ssid not in unique:
            unique[ssid] = {**net, "_score": score}
            continue

        if score > unique[ssid].get("_score", 0):
            unique[ssid] = {**net, "_score": score}

    sorted_networks = sorted(unique.values(), key=lambda item: item.get("_score", 0), reverse=True)
    for item in sorted_networks:
        item.pop("_score", None)

    return {
        "ok": True,
        "mode": mode,
        "scan_strategy": f"{scan_source}-first",
        "networks": sorted_networks,
    }


def classify_nmcli_error(stderr: str, stdout: str) -> str:
    text = f"{stderr}\n{stdout}".lower()
    if "secrets were required" in text or "no secrets" in text or "password" in text:
        return "可能是 Wi-Fi 密碼錯誤，或此 Wi-Fi 需要重新輸入密碼。"
    if "no network with ssid" in text or "not found" in text:
        return "找不到這個 SSID。請確認手機熱點/路由器已開啟，或手動輸入的名稱完全正確。"
    if "activation failed" in text:
        return "NetworkManager 啟用連線失敗。可能是密碼錯、訊號弱、舊 profile 衝突，或熱點尚未釋放完成。"
    if "timeout" in text:
        return "連線逾時。可能是訊號弱、手機熱點未回應，或 Wi-Fi 模式切換中。"
    return "請查看 stderr/stdout 取得詳細原因。"


def verify_wifi_connected(target_ssid: str = "", connection_name: str = "") -> dict:
    """確認 wlan0 是否有 IPv4，並盡量判斷 active connection 是否符合目標。"""
    status = get_status_data()
    ipv4 = status.get("ipv4", "")
    active_text = status.get("active_connections", "")

    matched = False
    if connection_name and connection_name in active_text:
        matched = True
    elif target_ssid:
        profiles = get_saved_wifi_profiles()
        info = profiles.get(target_ssid, {})
        if info.get("connection_name") and info.get("connection_name") in active_text:
            matched = True

    return {
        "connected": bool(ipv4 and status.get("mode") == "wifi" and (matched or not connection_name)),
        "ipv4": ipv4,
        "mode": status.get("mode", "unknown"),
        "access_url": status.get("access_url", ""),
        "active_connections": active_text,
    }


def connect_wifi_background(ssid: str, password: str) -> None:
    """連線到新的 Wi-Fi；需要密碼時才呼叫這個。"""
    ssid = ssid.strip()
    was_hotspot = get_status_data().get("mode") == "hotspot"

    write_job({
        "ok": True,
        "type": "wifi_connect",
        "status": "running",
        "step": "prepare",
        "ssid": ssid,
        "message": f"準備連線到 Wi-Fi：{ssid}",
        "error": "",
        "suggestion": "",
        "stdout": "",
        "stderr": "",
    })

    write_job({"ok": True, "type": "wifi_connect", "status": "running", "step": "stop_hotspot_dhcp", "ssid": ssid, "message": "正在停止熱點 DHCP", "error": "", "suggestion": ""})
    run_cmd_for_job(["sudo", "systemctl", "stop", HOTSPOT_DHCP_SERVICE], timeout=15)

    write_job({"ok": True, "type": "wifi_connect", "status": "running", "step": "down_hotspot", "ssid": ssid, "message": "正在關閉 arLoupe-Setup 熱點", "error": "", "suggestion": ""})
    run_cmd_for_job(["sudo", "nmcli", "connection", "down", HOTSPOT_NAME], timeout=20)
    time.sleep(2)

    # 如果存在同 SSID 舊 profile，先更新密碼再 up；這樣避免舊密碼 profile 干擾
    saved_profiles = get_saved_wifi_profiles()
    old_profile = saved_profiles.get(ssid, {})
    if old_profile.get("connection_name") and password:
        conn_name = old_profile["connection_name"]
        write_job({"ok": True, "type": "wifi_connect", "status": "running", "step": "update_saved_password", "ssid": ssid, "connection_name": conn_name, "message": "偵測到已儲存連線，正在更新密碼", "error": "", "suggestion": ""})
        run_cmd_for_job(["sudo", "nmcli", "connection", "modify", conn_name, "wifi-sec.psk", password], timeout=15)

    write_job({"ok": True, "type": "wifi_connect", "status": "running", "step": "connect_wifi", "ssid": ssid, "message": f"正在連線到 {ssid}", "error": "", "suggestion": ""})

    cmd = ["sudo", "nmcli", "device", "wifi", "connect", ssid]
    if password:
        cmd.extend(["password", password])

    result = run_cmd_for_job(cmd, timeout=45)
    if result["returncode"] != 0:
        suggestion = classify_nmcli_error(result["stderr"], result["stdout"])
        write_job({
            "ok": False,
            "type": "wifi_connect",
            "status": "failed",
            "step": "connect_wifi",
            "ssid": ssid,
            "message": "Wi-Fi 連線失敗",
            "error": result["stderr"] or result["stdout"] or "未知錯誤",
            "suggestion": suggestion,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"],
        })
        if was_hotspot:
            from app.services.network import restore_hotspot_after_failed_wifi
            restore_hotspot_after_failed_wifi()
        return

    write_job({"ok": True, "type": "wifi_connect", "status": "running", "step": "verify_ip", "ssid": ssid, "message": "連線指令完成，正在確認 IP", "error": "", "suggestion": "", "stdout": result["stdout"], "stderr": result["stderr"]})
    time.sleep(3)
    verified = verify_wifi_connected(target_ssid=ssid)

    if verified["connected"]:
        write_job({
            "ok": True,
            "type": "wifi_connect",
            "status": "success",
            "step": "done",
            "ssid": ssid,
            "message": f"已成功連線到 {ssid}",
            "error": "",
            "suggestion": "請將手機或 Windows 改連同一個 Wi-Fi，再開啟新的 Pi 5 網址。",
            "ipv4": verified["ipv4"],
            "access_url": verified["access_url"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        })
    else:
        write_job({
            "ok": False,
            "type": "wifi_connect",
            "status": "failed",
            "step": "verify_ip",
            "ssid": ssid,
            "message": "連線指令完成，但沒有確認到有效 Wi-Fi IP",
            "error": verified.get("active_connections", ""),
            "suggestion": "可能 DHCP 沒拿到 IP，或 NetworkManager 連到其他 profile。請查看 active connections。",
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        })
        if was_hotspot:
            from app.services.network import restore_hotspot_after_failed_wifi
            restore_hotspot_after_failed_wifi()


def connect_saved_wifi_background(ssid: str, connection_name: str) -> None:
    """不輸入密碼，直接連已儲存 Wi-Fi profile。"""
    ssid = ssid.strip()
    connection_name = connection_name.strip()
    was_hotspot = get_status_data().get("mode") == "hotspot"

    if not connection_name and ssid:
        profile = get_saved_wifi_profiles().get(ssid, {})
        connection_name = profile.get("connection_name", "")

    write_job({
        "ok": True,
        "type": "wifi_connect_saved",
        "status": "running",
        "step": "prepare",
        "ssid": ssid,
        "connection_name": connection_name,
        "message": f"準備連線到已儲存 Wi-Fi：{ssid or connection_name}",
        "error": "",
        "suggestion": "",
    })

    if not connection_name:
        write_job({
            "ok": False,
            "type": "wifi_connect_saved",
            "status": "failed",
            "step": "find_profile",
            "ssid": ssid,
            "connection_name": connection_name,
            "message": "找不到已儲存的 Wi-Fi profile",
            "error": "connection_name 為空",
            "suggestion": "請重新掃描，或使用密碼連線一次。",
        })
        return

    write_job({"ok": True, "type": "wifi_connect_saved", "status": "running", "step": "stop_hotspot_dhcp", "ssid": ssid, "connection_name": connection_name, "message": "正在停止熱點 DHCP", "error": "", "suggestion": ""})
    run_cmd_for_job(["sudo", "systemctl", "stop", HOTSPOT_DHCP_SERVICE], timeout=15)

    write_job({"ok": True, "type": "wifi_connect_saved", "status": "running", "step": "down_hotspot", "ssid": ssid, "connection_name": connection_name, "message": "正在關閉 arLoupe-Setup 熱點", "error": "", "suggestion": ""})
    run_cmd_for_job(["sudo", "nmcli", "connection", "down", HOTSPOT_NAME], timeout=20)
    time.sleep(2)

    write_job({"ok": True, "type": "wifi_connect_saved", "status": "running", "step": "connection_up", "ssid": ssid, "connection_name": connection_name, "message": f"正在啟用已儲存連線：{connection_name}", "error": "", "suggestion": ""})
    result = run_cmd_for_job(["sudo", "nmcli", "connection", "up", connection_name], timeout=45)

    if result["returncode"] != 0:
        suggestion = classify_nmcli_error(result["stderr"], result["stdout"])
        write_job({
            "ok": False,
            "type": "wifi_connect_saved",
            "status": "failed",
            "step": "connection_up",
            "ssid": ssid,
            "connection_name": connection_name,
            "message": "已儲存 Wi-Fi 連線失敗",
            "error": result["stderr"] or result["stdout"] or "未知錯誤",
            "suggestion": suggestion + " 如密碼已更改，請按『重新輸入密碼』或先刪除此 Wi-Fi。",
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"],
        })
        if was_hotspot:
            from app.services.network import restore_hotspot_after_failed_wifi
            restore_hotspot_after_failed_wifi()
        return

    time.sleep(3)
    verified = verify_wifi_connected(target_ssid=ssid, connection_name=connection_name)
    if verified["connected"]:
        write_job({
            "ok": True,
            "type": "wifi_connect_saved",
            "status": "success",
            "step": "done",
            "ssid": ssid,
            "connection_name": connection_name,
            "message": f"已成功連線到已儲存 Wi-Fi：{ssid or connection_name}",
            "error": "",
            "suggestion": "請將手機或 Windows 改連同一個 Wi-Fi，再開啟新的 Pi 5 網址。",
            "ipv4": verified["ipv4"],
            "access_url": verified["access_url"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        })
    else:
        write_job({
            "ok": False,
            "type": "wifi_connect_saved",
            "status": "failed",
            "step": "verify_ip",
            "ssid": ssid,
            "connection_name": connection_name,
            "message": "已儲存連線啟用完成，但未確認到有效 IP",
            "error": verified.get("active_connections", ""),
            "suggestion": "可能 DHCP 沒拿到 IP，或連到其他 profile。",
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        })
        if was_hotspot:
            from app.services.network import restore_hotspot_after_failed_wifi
            restore_hotspot_after_failed_wifi()


def forget_wifi_background(ssid: str, connection_name: str) -> None:
    ssid = ssid.strip()
    connection_name = connection_name.strip()
    if not connection_name and ssid:
        connection_name = get_saved_wifi_profiles().get(ssid, {}).get("connection_name", "")

    write_job({
        "ok": True,
        "type": "wifi_forget",
        "status": "running",
        "step": "delete_profile",
        "ssid": ssid,
        "connection_name": connection_name,
        "message": f"正在刪除 Wi-Fi：{ssid or connection_name}",
        "error": "",
        "suggestion": "",
    })

    if not connection_name:
        write_job({
            "ok": False,
            "type": "wifi_forget",
            "status": "failed",
            "step": "find_profile",
            "ssid": ssid,
            "connection_name": connection_name,
            "message": "找不到可刪除的 Wi-Fi profile",
            "error": "connection_name 為空",
            "suggestion": "請重新掃描後再試。",
        })
        return

    result = run_cmd_for_job(["sudo", "nmcli", "connection", "delete", connection_name], timeout=20)
    if result["returncode"] == 0:
        write_job({
            "ok": True,
            "type": "wifi_forget",
            "status": "success",
            "step": "done",
            "ssid": ssid,
            "connection_name": connection_name,
            "message": "已刪除此 Wi-Fi，下次連線需要重新輸入密碼。",
            "error": "",
            "suggestion": "請重新掃描 Wi-Fi。",
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        })
    else:
        write_job({
            "ok": False,
            "type": "wifi_forget",
            "status": "failed",
            "step": "delete_profile",
            "ssid": ssid,
            "connection_name": connection_name,
            "message": "刪除 Wi-Fi 失敗",
            "error": result["stderr"] or result["stdout"] or "未知錯誤",
            "suggestion": "請確認此 profile 是否仍存在。",
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        })
