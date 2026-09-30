from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ParkingEvent, ParkingSession, ParkingSlot, VisionDetection
from ..schemas import FusionRequest, FusionResponse, RecommendationResponse, SlotResponse, SlotStateUpdate, VisionUpdate
from ..services.analytics import occupancy_summary, recent_events
from ..services.fusion import fuse

router = APIRouter(prefix="/api", tags=["parking"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "smart-parking-api"}


@router.get("/slots", response_model=list[SlotResponse])
def get_slots(db: Session = Depends(get_db)):
    return db.scalars(select(ParkingSlot).order_by(ParkingSlot.id)).all()


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return occupancy_summary(db)


@router.get("/events")
def get_events(limit: int = 50, db: Session = Depends(get_db)):
    return [
        {
            "id": e.id,
            "slot_id": e.slot_id,
            "occupied": e.occupied,
            "source": e.source,
            "confidence": e.confidence,
            "created_at": e.created_at,
        }
        for e in recent_events(db, min(max(limit, 1), 200))
    ]


@router.post("/slots/state", response_model=SlotResponse)
def update_slot_state(update: SlotStateUpdate, db: Session = Depends(get_db)):
    slot = db.scalar(select(ParkingSlot).where(ParkingSlot.name == update.slot))
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")

    changed = slot.occupied != update.occupied
    slot.occupied = update.occupied
    slot.confidence = update.confidence
    slot.source = update.source
    slot.updated_at = datetime.utcnow()

    if changed:
        db.add(ParkingEvent(
            slot_id=slot.id,
            occupied=update.occupied,
            source=update.source,
            confidence=update.confidence,
            device_id=update.device_id,
        ))
        if update.occupied:
            db.add(ParkingSession(slot_id=slot.id))
        else:
            session = db.scalar(
                select(ParkingSession)
                .where(ParkingSession.slot_id == slot.id, ParkingSession.ended_at.is_(None))
                .order_by(ParkingSession.started_at.desc())
            )
            if session:
                session.ended_at = datetime.utcnow()

    db.commit()
    db.refresh(slot)
    return slot


@router.post("/vision", response_model=SlotResponse)
def vision_update(update: VisionUpdate, db: Session = Depends(get_db)):
    slot = db.scalar(select(ParkingSlot).where(ParkingSlot.name == update.slot))
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    db.add(VisionDetection(
        slot_id=slot.id,
        occupied=update.occupied,
        confidence=update.confidence,
        model=update.model,
    ))
    db.commit()
    return slot


@router.post("/fusion", response_model=FusionResponse)
def fusion(update: FusionRequest):
    occupied, confidence, source = fuse(
        update.sensor_occupied,
        update.sensor_confidence,
        update.vision_occupied,
        update.vision_confidence,
    )
    return {"occupied": occupied, "confidence": confidence, "source": source}


@router.get("/recommendation", response_model=RecommendationResponse | None)
def recommendation(db: Session = Depends(get_db)):
    slot = db.scalar(
        select(ParkingSlot)
        .where(ParkingSlot.occupied.is_(False))
        .order_by(ParkingSlot.id)
    )
    if slot is None:
        return None
    return {"slot_id": slot.id, "slot_name": slot.name, "reason": "Currently available"}
