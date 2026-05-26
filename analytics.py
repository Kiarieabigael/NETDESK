from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.device import Device
from app.models.ticket import Ticket
from app.models.alert import Alert


def get_dashboard_stats(db: Session) -> dict:
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == "online").count()
    offline_devices = db.query(Device).filter(Device.status == "offline").count()

    total_tickets = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == "open").count()
    in_progress_tickets = db.query(Ticket).filter(Ticket.status == "in_progress").count()
    resolved_tickets = db.query(Ticket).filter(Ticket.status == "resolved").count()

    unread_alerts = db.query(Alert).filter(Alert.is_read == "false").count()
    critical_alerts = db.query(Alert).filter(
        Alert.severity == "critical", Alert.is_read == "false"
    ).count()

    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "unread_alerts": unread_alerts,
        "critical_alerts": critical_alerts,
    }


def get_device_type_breakdown(db: Session) -> dict:
    results = (
        db.query(Device.device_type, func.count(Device.id))
        .group_by(Device.device_type)
        .all()
    )
    return {dtype: count for dtype, count in results}


def get_ticket_priority_breakdown(db: Session) -> dict:
    results = (
        db.query(Ticket.priority, func.count(Ticket.id))
        .group_by(Ticket.priority)
        .all()
    )
    return {priority: count for priority, count in results}


def get_most_problematic_devices(db: Session, limit: int = 5) -> list:
    results = (
        db.query(Device.device_name, func.count(Ticket.id).label("ticket_count"))
        .join(Ticket, Device.id == Ticket.device_id, isouter=True)
        .group_by(Device.id)
        .order_by(func.count(Ticket.id).desc())
        .limit(limit)
        .all()
    )
    return [{"device": name, "tickets": count} for name, count in results]
