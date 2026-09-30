from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import ParkingEvent, ParkingSession, ParkingSlot


def occupancy_summary(db: Session):
    total = db.scalar(select(func.count(ParkingSlot.id))) or 0
    occupied = db.scalar(
        select(func.count(ParkingSlot.id)).where(ParkingSlot.occupied.is_(True))
    ) or 0
    return {
        "total": total,
        "occupied": occupied,
        "available": total - occupied,
        "occupancy_rate": round((occupied / total) * 100, 2) if total else 0,
    }


def recent_events(db: Session, limit: int = 50):
    return db.scalars(
        select(ParkingEvent).order_by(ParkingEvent.created_at.desc()).limit(limit)
    ).all()


def active_sessions(db: Session):
    return db.scalars(
        select(ParkingSession).where(ParkingSession.ended_at.is_(None))
    ).all()
