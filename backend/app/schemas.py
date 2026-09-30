from datetime import datetime

from pydantic import BaseModel, Field


class SlotStateUpdate(BaseModel):
    slot: str = Field(min_length=1, max_length=50)
    occupied: bool
    source: str = "ir"
    confidence: float | None = Field(default=None, ge=0, le=1)
    device_id: str | None = None


class VisionUpdate(BaseModel):
    slot: str
    occupied: bool
    confidence: float | None = Field(default=None, ge=0, le=1)
    model: str = "vision"


class SlotResponse(BaseModel):
    id: int
    name: str
    occupied: bool
    confidence: float | None
    source: str
    updated_at: datetime


class ReservationCreate(BaseModel):
    slot_id: int
    vehicle_number: str = Field(min_length=1, max_length=30)
    start_time: datetime
    end_time: datetime


class ReservationResponse(ReservationCreate):
    id: int
    status: str


class RecommendationResponse(BaseModel):
    slot_id: int
    slot_name: str
    reason: str


class FusionRequest(BaseModel):
    slot: str
    sensor_occupied: bool
    sensor_confidence: float = Field(default=1.0, ge=0, le=1)
    vision_occupied: bool
    vision_confidence: float = Field(default=1.0, ge=0, le=1)


class FusionResponse(BaseModel):
    occupied: bool
    confidence: float
    source: str
