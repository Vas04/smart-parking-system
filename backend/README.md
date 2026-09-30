# Smart Parking Backend

## Stack

FastAPI + PostgreSQL + MQTT + WebSocket.

## Start infrastructure

From the repository root:

```bash
docker compose up -d postgres mosquitto
```

## Python setup

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API starts at http://localhost:8000.

Interactive API documentation:
- /docs
- /redoc

## MQTT payload

Publish to topic `parking/slots`:

```json
{
  "slot": "SLOT-1",
  "occupied": true,
  "source": "ir",
  "confidence": 0.98,
  "device_id": "ESP32-01"
}
```

## Main endpoints

- GET /health
- GET /api/slots
- GET /api/summary
- GET /api/events
- POST /api/slots/state
- POST /api/vision
- POST /api/fusion
- GET /api/recommendation
- GET/POST /api/reservations
- WS /ws
