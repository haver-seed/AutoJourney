import pytest
from pydantic import ValidationError
from models.schemas import PlanRequest, PlanResponse, DailyPlan, ScheduleItem


def test_plan_request_valid():
    req = PlanRequest(
        departure="北京",
        min_days=5,
        max_days=7,
        destinations=["西安", "成都"],
        mode="multi-city",
    )
    assert req.departure == "北京"
    assert req.min_days == 5
    assert req.max_days == 7


def test_plan_request_defaults():
    req = PlanRequest(
        departure="北京",
        min_days=5,
        max_days=7,
        destinations=["西安"],
    )
    assert req.mode == "multi-city"
    assert req.preferences is None


def test_plan_request_invalid_mode():
    with pytest.raises(ValidationError):
        PlanRequest(
            departure="北京",
            min_days=5,
            max_days=7,
            destinations=["西安"],
            mode="invalid",
        )


def test_plan_request_min_greater_than_max():
    with pytest.raises(ValidationError):
        PlanRequest(
            departure="北京",
            min_days=10,
            max_days=5,
            destinations=["西安"],
        )


def test_plan_request_empty_destinations():
    with pytest.raises(ValidationError):
        PlanRequest(
            departure="北京",
            min_days=5,
            max_days=7,
            destinations=[],
        )


def test_schedule_item():
    item = ScheduleItem(time="09:00", activity="参观兵马俑", duration="3小时", cost=120)
    assert item.cost == 120


def test_daily_plan():
    plan = DailyPlan(
        day=1,
        city="西安",
        theme="历史探索",
        schedule=[
            ScheduleItem(time="09:00", activity="参观兵马俑", duration="3小时", cost=120)
        ],
        accommodation={"name": "酒店", "cost": 300},
        meals_cost=150,
        day_total=570,
    )
    assert plan.day == 1
    assert len(plan.schedule) == 1
