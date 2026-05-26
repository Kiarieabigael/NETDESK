import subprocess
import platform
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.alert import Alert


def ping_host(ip_address: str) -> bool:
    """Ping a host and return True if reachable."""
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", "-W", "2", ip_address]
        result = subprocess.run(command, capture_output=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def check_device_status(db: Session, device: Device) -> str:
    """Check device status and update in DB."""
    is_online = ping_host(device.ip_address)
    new_status = "online" if is_online else "offline"
    old_status = device.status

    device.status = new_status
    device.last_checked = datetime.utcnow()
    db.commit()

    # Create alert if device just went offline
    if old_status == "online" and new_status == "offline":
        alert = Alert(
            device_id=device.id,
            alert_message=f"Device '{device.device_name}' ({device.ip_address}) went OFFLINE",
            severity="critical",
        )
        db.add(alert)
        db.commit()

    elif old_status == "offline" and new_status == "online":
        alert = Alert(
            device_id=device.id,
            alert_message=f"Device '{device.device_name}' ({device.ip_address}) is back ONLINE",
            severity="info",
        )
        db.add(alert)
        db.commit()

    return new_status


def check_all_devices(db: Session):
    """Check all devices in the database."""
    devices = db.query(Device).all()
    results = []
    for device in devices:
        status = check_device_status(db, device)
        results.append({"device": device.device_name, "ip": device.ip_address, "status": status})
    return results
