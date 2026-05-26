from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import ActivityLog
from app.utils.helpers import (
    hash_password, verify_password, create_access_token,
    get_current_user_from_cookie
)

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid username or password"
        })

    token = create_access_token(data={"sub": user.username})

    # Log activity
    log = ActivityLog(user_id=user.id, action=f"User '{user.username}' logged in")
    db.add(log)
    db.commit()

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(default="viewer"),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Username or email already exists"
        })

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()

    log = ActivityLog(user_id=user.id, action=f"New user '{username}' registered")
    db.add(log)
    db.commit()

    return RedirectResponse(url="/auth/login", status_code=302)


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response
