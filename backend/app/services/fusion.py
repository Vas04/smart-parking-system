def fuse(sensor_occupied: bool, sensor_confidence: float, vision_occupied: bool, vision_confidence: float):
    sensor_weight = max(0.0, min(1.0, sensor_confidence))
    vision_weight = max(0.0, min(1.0, vision_confidence))
    total = sensor_weight + vision_weight

    if total == 0:
        return False, 0.0, "unknown"

    occupied_score = (
        (sensor_weight if sensor_occupied else 0.0)
        + (vision_weight if vision_occupied else 0.0)
    ) / total

    occupied = occupied_score >= 0.5
    confidence = abs(occupied_score - 0.5) * 2
    source = "sensor+vision" if sensor_weight and vision_weight else ("ir" if sensor_weight else "vision")
    return occupied, confidence, source
