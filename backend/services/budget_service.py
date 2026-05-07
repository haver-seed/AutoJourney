from models.schemas import PlanResponse


def recalculate_budget(response: PlanResponse) -> PlanResponse:
    tickets = sum(item.cost for day in response.daily_plans for item in day.schedule)
    accommodation = sum(day.accommodation.cost for day in response.daily_plans)
    meals = sum(day.meals_cost for day in response.daily_plans)
    transport = sum(t.cost for t in response.transport)
    total = transport + accommodation + tickets + meals

    response.budget_breakdown.transport = transport
    response.budget_breakdown.accommodation = accommodation
    response.budget_breakdown.tickets = tickets
    response.budget_breakdown.meals = meals
    response.budget_breakdown.total = total

    return response
