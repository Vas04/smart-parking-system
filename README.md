# AI + IoT Intelligent Smart Parking System

Integrated parking management platform combining ESP32 IoT sensing, MQTT, PostgreSQL, FastAPI, WebSocket, React and camera-based vehicle detection.

## Software architecture
ESP32/IR -> MQTT -> FastAPI -> PostgreSQL -> WebSocket -> React
Camera -> YOLO -> Vision API -> FastAPI

## Modules
- backend/ — FastAPI, database, MQTT, fusion, analytics and reservations
- frontend/ — React/Vite real-time dashboard
- firmware/ — ESP32 firmware
- vision/ — YOLO/OpenCV pipeline
- docker-compose.yml — PostgreSQL and Mosquitto

## Start
1. docker compose up -d postgres mosquitto
2. cd backend && python -m venv .venv
3. Activate the environment and run: pip install -r requirements.txt
4. Run: uvicorn app.main:app --reload
5. In frontend: npm install && npm run dev

Backend: http://localhost:8000
Frontend: http://localhost:5173
API docs: http://localhost:8000/docs

The camera ROI coordinates in vision/detect.py must be calibrated for the actual camera view. YOLO inference should run on a PC/laptop or suitable compute host, not on the ESP32-CAM.