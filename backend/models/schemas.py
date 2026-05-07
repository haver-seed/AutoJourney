from typing import Optional
from pydantic import BaseModel, Field, field_validator


class PlanRequest(BaseModel):
    departure: str
    min_days: int
    max_days: int
    destinations: list[str]
    mode: str = "multi-city"
    preferences: Optional[str] = None

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in ("single-city", "multi-city"):
            raise ValueError("mode must be 'single-city' or 'multi-city'")
        return v

    @field_validator("destinations")
    @classmethod
    def validate_destinations(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("destinations must not be empty")
        return v

    @field_validator("max_days")
    @classmethod
    def validate_days(cls, v: int, info) -> int:
        min_days = info.data.get("min_days")
        if min_days is not None and v < min_days:
            raise ValueError("max_days must be >= min_days")
        return v


class ScheduleItem(BaseModel):
    time: str
    activity: str
    duration: str
    cost: float


class Accommodation(BaseModel):
    name: str
    cost: float


class DailyPlan(BaseModel):
    day: int
    city: str
    theme: str
    schedule: list[ScheduleItem]
    accommodation: Accommodation
    meals_cost: float
    day_total: float


class Transport(BaseModel):
    fr: str = Field(alias="from")
    to: str
    type: str
    duration: str
    cost: float

    model_config = {"populate_by_name": True}


class BudgetBreakdown(BaseModel):
    transport: float
    accommodation: float
    tickets: float
    meals: float
    total: float


class PlanResponse(BaseModel):
    actual_days: int
    overview: str
    daily_plans: list[DailyPlan]
    transport: list[Transport]
    budget_breakdown: BudgetBreakdown
