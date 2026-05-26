from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import Base, engine
from app.models import user, device, ticket, alert
from app.routes import auth, devices, tickets, dashboard

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NetDesk", description="Network Monitoring & IT Ticketing System")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(tickets.router)


# Seed demo data on startup
@app.on_event("startup")
def seed_demo_data():
    from app.database import SessionLocal
    from app.models.user import User
    from app.models.device import Device
    from app.utils.helpers import hash_password

    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                email="admin@netdesk.local",
                password_hash=hash_password("admin123"),
                role="admin"
            )
            tech = User(
                username="tech1",
                email="tech1@netdesk.local",
                password_hash=hash_password("tech123"),
                role="technician"
            )
            db.add_all([admin, tech])
            db.commit()

        if db.query(Device).count() == 0:
            sample_devices = [
                Device(device_name="Main Router", ip_address="192.168.1.1", location="Server Room", device_type="router", status="unknown"),
                Device(device_name="Core Switch", ip_address="192.168.1.2", location="Server Room", device_type="switch", status="unknown"),
                Device(device_name="Web Server", ip_address="192.168.1.10", location="Server Room", device_type="server", status="unknown"),
                Device(device_name="Admin PC", ip_address="192.168.1.50", location="Admin Office", device_type="pc", status="unknown"),
                Device(device_name="Lab Printer", ip_address="192.168.1.100", location="Computer Lab", device_type="printer", status="unknown"),
                Device(device_name="WiFi AP Lab", ip_address="192.168.1.150", location="Computer Lab", device_type="access_point", status="unknown"),
            ]
            db.add_all(sample_devices)
            db.commit()
    finally:
        db.close()
