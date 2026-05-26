from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.device import Device
from app.models.alert import ActivityLog
from app.utils.helpers import get_current_user_from_cookie
from app.services.monitor import check_device_status, check_all_devices

router = APIRouter(prefix="/devices", tags=["devices"])
templates = Jinja2Templates(directory="app/templates")


def require_login(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return None
    return user


@router.get("", response_class=HTMLResponse)
def devices_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    devices = db.query(Device).all()
    return templates.TemplateResponse("devices.html", {
        "request": request, "devices": devices, "user": user
    })


@router.post("/add")
def add_device(
    request: Request,
    device_name: str = Form(...),
    ip_address: str = Form(...),
    location: str = Form(...),
    device_type: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    device = Device(
        device_name=device_name,
        ip_address=ip_address,
        location=location,
        device_type=device_type,
        status="unknown"
    )
    db.add(device)
    db.commit()

    log = ActivityLog(user_id=user.id, action=f"Added device '{device_name}' ({ip_address})")
    db.add(log)
    db.commit()

    return RedirectResponse(url="/devices", status_code=302)


@router.post("/delete/{device_id}")
def delete_device(device_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or user.role not in ["admin"]:
        return RedirectResponse(url="/devices", status_code=302)
    device = db.query(Device).filter(Device.id == device_id).first()
    if device:
        log = ActivityLog(user_id=user.id, action=f"Deleted device '{device.device_name}'")
        db.add(log)
        db.delete(device)
        db.commit()
    return RedirectResponse(url="/devices", status_code=302)


@router.get("/ping/{device_id}", response_class=JSONResponse)
def ping_device(device_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        return JSONResponse({"error": "Device not found"}, status_code=404)
    status = check_device_status(db, device)
    return JSONResponse({"status": status, "device": device.device_name})


@router.get("/ping-all", response_class=JSONResponse)
def ping_all_devices(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    results = check_all_devices(db)
    return JSONResponse({"results": results})
