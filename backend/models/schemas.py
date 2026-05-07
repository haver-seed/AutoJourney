from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TicketRequest(BaseModel):
    departure: str
    departure_date: str
    destinations: list[str]
    stay_days: list[int]

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("destinations must not be empty")
        return v

    @field_validator("stay_days")
    @classmethod
    def validate_stay_days(cls, v: list[int], info) -> list[int]:
        destinations = info.data.get("destinations", [])
        if len(v) != len(destinations):
            raise ValueError("stay_days length must match destinations length")
        return v


class TrainInfo(BaseModel):
    train_no: str = ""
    seat_types: str = ""
    note: str = ""
    start_time: str = ""
    arrive_time: str = ""
    duration: str = ""
    actual_date: str = ""
    reason: str = ""


class TicketSegment(BaseModel):
    fr: str = Field(alias="from")
    to: str
    travel_date: str
    train_info: Optional[TrainInfo] = None
    cost: float = 0
    stay_days: int = 0

    model_config = {"populate_by_name": True}


class TicketResponse(BaseModel):
    segments: list[TicketSegment]
    total_cost: float
    total_days: int
