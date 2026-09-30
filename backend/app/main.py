import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime

import paho.mqtt.client as mqtt
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import ParkingSlot

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "parking/slots")


class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()
main_loop: asyncio.AbstractEventLoop | None = None


def seed_slots():
    with SessionLocal() as db:
        existing = db.scalar(select(ParkingSlot).limit(1))
        if existing is not None:
            return
        for number in range(1, 5):
            db.add(ParkingSlot(name=f"SLOT-{number}", occupied=False))
        db.commit()


def process_mqtt_message(payload: bytes):
    try:
        data = json.loads(payload.decode())
        slot_name = str(data["slot"])
        occupied = bool(data["occupied"])
    except (ValueError, KeyError, TypeError):
        return

    with SessionLocal() as db:
        slot = db.scalar(select(ParkingSlot).where(ParkingSlot.name == slot_name))
        if slot is None:
            return
        slot.occupied = occupied
        slot.updated_at = datetime.utcnow()
        db.commit()
        event = {
            "type": "slot_update",
            "slot": slot.name,
            "occupied": slot.occupied,
            "updated_at": slot.updated_at.isoformat(),
        }

    if main_loop and not main_loop.is_closed():
        asyncio.run_coroutine_threadsafe(manager.broadcast(event), main_loop)


def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, message):
    process_mqtt_message(message.payload)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()

    Base.metadata.create_all(bind=engine)
    seed_slots()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
    except Exception:
        client = None

    yield

    if client:
        client.loop_stop()
        client.disconnect()


app = FastAPI(title="Smart Parking API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/slots")
def get_slots():
    with SessionLocal() as db:
        slots = db.scalars(select(ParkingSlot).order_by(ParkingSlot.id)).all()
        return [
            {
                "id": slot.id,
                "name": slot.name,
                "occupied": slot.occupied,
                "updated_at": slot.updated_at.isoformat(),
            }
            for slot in slots
        ]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
