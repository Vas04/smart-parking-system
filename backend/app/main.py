import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .api.reservations import router as reservations_router
from .api.routes import router as parking_router
from .database import Base, SessionLocal, engine
from .models import ParkingEvent, ParkingSlot
from .seed import seed_slots
from .services.mqtt import MQTTService
from .services.websocket import WebSocketManager

manager = WebSocketManager()
main_loop: asyncio.AbstractEventLoop | None = None


def process_mqtt_message(payload: dict):
    if not isinstance(payload, dict):
        return

    slot_name = payload.get("slot")
    if not slot_name or "occupied" not in payload:
        return

    with SessionLocal() as db:
        slot = db.scalar(select(ParkingSlot).where(ParkingSlot.name == str(slot_name)))
        if slot is None:
            return

        occupied = bool(payload["occupied"])
        changed = slot.occupied != occupied
        slot.occupied = occupied
        slot.confidence = payload.get("confidence")
        slot.source = payload.get("source", "ir")

        if changed:
            db.add(ParkingEvent(
                slot_id=slot.id,
                occupied=occupied,
                source=slot.source,
                confidence=slot.confidence,
                device_id=payload.get("device_id"),
            ))

        db.commit()

        event = {
            "type": "slot_update",
            "slot": slot.name,
            "occupied": slot.occupied,
            "confidence": slot.confidence,
            "source": slot.source,
            "updated_at": slot.updated_at.isoformat(),
        }

    if main_loop and not main_loop.is_closed():
        asyncio.run_coroutine_threadsafe(manager.broadcast(event), main_loop)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()

    Base.metadata.create_all(bind=engine)
    seed_slots()

    mqtt = MQTTService(process_mqtt_message)
    mqtt.start()

    app.state.mqtt = mqtt
    yield

    mqtt.stop()


app = FastAPI(title="AI + IoT Smart Parking API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parking_router)
app.include_router(reservations_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
