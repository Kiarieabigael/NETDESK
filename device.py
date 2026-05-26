from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    location = Column(String)
    device_type = Column(String)  # router, switch, printer, access_point, pc, server
    status = Column(String, default="unknown")  # online, offline, unknown
    last_checked = Column(DateTime, default=datetime.utcnow)

    tickets = relationship("Ticket", back_populates="device")
    alerts = relationship("Alert", back_populates="device")
