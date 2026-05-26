from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.ticket import Ticket
from app.models.device import Device
from app.models.user import User
from app.models.alert import ActivityLog
from app.utils.helpers import get_current_user_from_cookie

router = APIRouter(prefix="/tickets", tags=["tickets"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def tickets_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    devices = db.query(Device).all()
    technicians = db.query(User).filter(User.role.in_(["admin", "technician"])).all()
    return templates.TemplateResponse("tickets.html", {
        "request": request, "tickets": tickets,
        "devices": devices, "technicians": technicians, "user": user
    })


@router.post("/create")
def create_ticket(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    priority: str = Form(default="medium"),
    device_id: int = Form(default=None),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    ticket = Ticket(
        title=title,
        description=description,
        priority=priority,
        device_id=device_id if device_id else None,
        created_by=user.id,
        status="open"
    )
    db.add(ticket)
    db.commit()

    log = ActivityLog(user_id=user.id, action=f"Created ticket: '{title}'")
    db.add(log)
    db.commit()

    return RedirectResponse(url="/tickets", status_code=302)


@router.post("/update/{ticket_id}")
def update_ticket(
    ticket_id: int,
    request: Request,
    status: str = Form(None),
    assigned_to: int = Form(None),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        if status:
            ticket.status = status
        if assigned_to:
            ticket.assigned_to = assigned_to
        db.commit()

        log = ActivityLog(user_id=user.id, action=f"Updated ticket #{ticket_id} — status: {status}")
        db.add(log)
        db.commit()

    return RedirectResponse(url="/tickets", status_code=302)


@router.post("/delete/{ticket_id}")
def delete_ticket(ticket_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or user.role != "admin":
        return RedirectResponse(url="/tickets", status_code=302)
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if ticket:
        log = ActivityLog(user_id=user.id, action=f"Deleted ticket #{ticket_id}: '{ticket.title}'")
        db.add(log)
        db.delete(ticket)
        db.commit()
    return RedirectResponse(url="/tickets", status_code=302)
