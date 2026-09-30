from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Reservation
from ..schemas import ReservationCreate, ReservationResponse

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationResponse])
def list_reservations(db: Session = Depends(get_db)):
    return db.scalars(select(Reservation).order_by(Reservation.start_time.desc())).all()


@router.post("", response_model=ReservationResponse)
def create_reservation(data: ReservationCreate, db: Session = Depends(get_db)):
    reservation = Reservation(**data.model_dump(), status="confirmed")
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation
