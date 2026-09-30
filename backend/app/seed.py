from sqlalchemy import select

from .database import SessionLocal
from .models import ParkingSlot


def seed_slots():
    with SessionLocal() as db:
        if db.scalar(select(ParkingSlot).limit(1)):
            return
        for number in range(1, 5):
            db.add(ParkingSlot(name=f"SLOT-{number}", occupied=False, source="ir"))
        db.commit()
