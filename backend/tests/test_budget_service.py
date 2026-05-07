import pytest
from services.budget_service import recalculate_budget
from models.schemas import PlanResponse, DailyPlan, ScheduleItem, Accommodation, Transport, BudgetBreakdown


def _make_response(**overrides) -> PlanResponse:
    defaults = dict(
        actual_days=2,
        overview="测试行程",
        daily_plans=[
            DailyPlan(
                day=1,
                city="西安",
                theme="历史",
                schedule=[
                    ScheduleItem(time="09:00", activity="兵马俑", duration="3小时", cost=120),
                    ScheduleItem(time="14:00", activity="华清宫", duration="2小时", cost=110),
                ],
                accommodation=Accommodation(name="酒店", cost=300),
                meals_cost=150,
                day_total=680,
            ),
            DailyPlan(
                day=2,
                city="西安",
                theme="美食",
                schedule=[
                    ScheduleItem(time="10:00", activity="回民街", duration="2小时", cost=0),
                ],
                accommodation=Accommodation(name="酒店", cost=300),
                meals_cost=200,
                day_total=500,
            ),
        ],
        transport=[
            Transport(fr="北京", to="西安", type="高铁", duration="4.5小时", cost=515),
        ],
        budget_breakdown=BudgetBreakdown(
            transport=515, accommodation=600, tickets=230, meals=350, total=1695
        ),
    )
    defaults.update(overrides)
    return PlanResponse(**defaults)


def test_recalculate_budget_corrects_wrong_total():
    resp = _make_response(
        budget_breakdown=BudgetBreakdown(
            transport=515, accommodation=600, tickets=230, meals=350, total=9999
        )
    )
    result = recalculate_budget(resp)
    assert result.budget_breakdown.total == 1695


def test_recalculate_budget_sums_tickets_from_schedules():
    resp = _make_response()
    result = recalculate_budget(resp)
    assert result.budget_breakdown.tickets == 230  # 120 + 110 + 0


def test_recalculate_budget_sums_accommodation():
    resp = _make_response()
    result = recalculate_budget(resp)
    assert result.budget_breakdown.accommodation == 600  # 300 + 300


def test_recalculate_budget_sums_meals():
    resp = _make_response()
    result = recalculate_budget(resp)
    assert result.budget_breakdown.meals == 350  # 150 + 200


def test_recalculate_budget_sums_transport():
    resp = _make_response()
    result = recalculate_budget(resp)
    assert result.budget_breakdown.transport == 515
