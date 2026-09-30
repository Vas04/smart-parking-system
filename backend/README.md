# Backend

## Requirements

- Python 3.11+
- PostgreSQL
- Mosquitto MQTT broker

## Setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust the database/MQTT settings.

## Run

```bash
uvicorn app.main:app --reload
```

API:
- `GET /health`
- `GET /api/slots`
- `WS /ws`

## ESP32 MQTT message

Publish JSON to `parking/slots`:

```json
{"slot":"SLOT-1","occupied":true}
```
