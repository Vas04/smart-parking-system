# Smart Parking System

An integrated AI + IoT smart parking platform for real-time parking-slot monitoring.

## Architecture

ESP32 → Wi-Fi → MQTT → FastAPI → PostgreSQL → WebSocket → React

The backend is designed to accept live slot-state updates from ESP32 devices while the frontend receives updates instantly through WebSockets.

## Repository

- `backend/` — FastAPI API, MQTT ingestion, database models
- `frontend/` — React/Vite dashboard
- `docs/` — project documentation

## Initial development

The first software milestone provides:
- 4 parking slots
- REST API for slot status
- MQTT ingestion endpoint/service
- WebSocket live updates
- PostgreSQL-ready database layer
- React real-time dashboard

## Run locally

See the README files inside `backend/` and `frontend/`.
