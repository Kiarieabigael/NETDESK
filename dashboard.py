from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.alert import Alert, ActivityLog
from app.utils.helpers import get_current_user_from_cookie
from app.services.analytics import (
    get_dashboard_stats, get_device_type_breakdown,
    get_ticket_priority_breakdown, get_most_problematic_devices
)

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return RedirectResponse(url="/dashboard")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    stats = get_dashboard_stats(db)
    recent_alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(8).all()
    recent_activity = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc()).limit(10).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "recent_alerts": recent_alerts,
        "recent_activity": recent_activity,
    })


@router.get("/api/chart-data", response_class=JSONResponse)
def chart_data(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    device_types = get_device_type_breakdown(db)
    ticket_priorities = get_ticket_priority_breakdown(db)
    problematic_devices = get_most_problematic_devices(db)

    stats = get_dashboard_stats(db)

    return JSONResponse({
        "device_types": device_types,
        "ticket_priorities": ticket_priorities,
        "problematic_devices": problematic_devices,
        "device_status": {
            "Online": stats["online_devices"],
            "Offline": stats["offline_devices"],
            "Unknown": stats["total_devices"] - stats["online_devices"] - stats["offline_devices"]
        }
    })


@router.get("/alerts", response_class=HTMLResponse)
def alerts_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).all()
    return templates.TemplateResponse("alerts.html", {
        "request": request, "alerts": alerts, "user": user
    })


@router.post("/alerts/mark-read/{alert_id}")
def mark_alert_read(alert_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_read = "true"
        db.commit()
    return RedirectResponse(url="/alerts", status_code=302)
