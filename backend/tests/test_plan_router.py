import json
import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from main import app


SAMPLE_AI_RESPONSE = {
    "actual_days": 3,
    "overview": "3天西安游",
    "daily_plans": [
        {
            "day": 1,
            "city": "西安",
            "theme": "历史",
            "schedule": [{"time": "09:00", "activity": "兵马俑", "duration": "3小时", "cost": 120}],
            "accommodation": {"name": "酒店", "cost": 300},
            "meals_cost": 150,
            "day_total": 570,
        }
    ],
    "transport": [{"from": "北京", "to": "西安", "type": "高铁", "duration": "4.5小时", "cost": 515}],
    "budget_breakdown": {"transport": 515, "accommodation": 300, "tickets": 120, "meals": 150, "total": 1085},
}


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_plan_endpoint_success():
    with patch("routers.plan.call_deepseek", new_callable=AsyncMock, return_value=SAMPLE_AI_RESPONSE):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/api/plan", json={
                "departure": "北京",
                "min_days": 3,
                "max_days": 5,
                "destinations": ["西安"],
                "mode": "single-city",
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["actual_days"] == 3
            assert len(data["daily_plans"]) == 1


@pytest.mark.asyncio
async def test_plan_endpoint_invalid_input():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/plan", json={
            "departure": "",
            "min_days": 10,
            "max_days": 5,
            "destinations": [],
        })
        assert resp.status_code == 422
