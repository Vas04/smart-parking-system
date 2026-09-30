import os
import cv2
import requests
from ultralytics import YOLO

API_URL = os.getenv("PARKING_API_URL", "http://localhost:8000")
MODEL_PATH = os.getenv("YOLO_MODEL", "yolo11n.pt")
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "0")

# Replace these example regions with calibrated regions for the real camera.
SLOT_ROIS = {
    "SLOT-1": (0, 0, 320, 240),
    "SLOT-2": (320, 0, 640, 240),
    "SLOT-3": (0, 240, 320, 480),
    "SLOT-4": (320, 240, 640, 480),
}

VEHICLE_CLASSES = {2, 3, 5, 7}  # car, motorcycle, bus, truck in COCO


def detect_slot(result, roi):
    x1, y1, x2, y2 = roi
    best = 0.0
    for box in result.boxes:
        if int(box.cls[0]) not in VEHICLE_CLASSES:
            continue
        confidence = float(box.conf[0])
        bx1, by1, bx2, by2 = map(int, box.xyxy[0])
        cx, cy = (bx1 + bx2) // 2, (by1 + by2) // 2
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            best = max(best, confidence)
    return best > 0.30, best


def main():
    model = YOLO(MODEL_PATH)
    source = int(CAMERA_SOURCE) if CAMERA_SOURCE.isdigit() else CAMERA_SOURCE
    cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera source: {source}")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        result = model(frame, verbose=False)[0]

        for slot, roi in SLOT_ROIS.items():
            occupied, confidence = detect_slot(result, roi)
            try:
                requests.post(
                    f"{API_URL}/api/vision",
                    json={"slot": slot, "occupied": occupied,
                          "confidence": confidence, "model": MODEL_PATH},
                    timeout=0.5,
                )
            except requests.RequestException:
                pass

        cv2.imshow("Smart Parking Vision", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
