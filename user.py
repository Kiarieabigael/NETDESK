from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="viewer")  # admin, technician, viewer
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets_created = relationship("Ticket", back_populates="creator", foreign_keys="Ticket.created_by")
    tickets_assigned = relationship("Ticket", back_populates="assignee", foreign_keys="Ticket.assigned_to")
    activity_logs = relationship("ActivityLog", back_populates="user")
