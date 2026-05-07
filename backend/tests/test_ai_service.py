import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.ai_service import call_deepseek, parse_ai_response


SAMPLE_AI_JSON = {
    "actual_days": 3,
    "overview": "3天西安深度游",
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
async def test_call_deepseek_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps(SAMPLE_AI_JSON)}}]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("services.ai_service.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.post.return_value = mock_response
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await call_deepseek("system", "user")
        assert result["actual_days"] == 3


@pytest.mark.asyncio
async def test_call_deepseek_invalid_json_retries():
    mock_bad = MagicMock()
    mock_bad.status_code = 200
    mock_bad.json.return_value = {"choices": [{"message": {"content": "not valid json{"}}]}
    mock_bad.raise_for_status = MagicMock()

    mock_good = MagicMock()
    mock_good.status_code = 200
    mock_good.json.return_value = {
        "choices": [{"message": {"content": json.dumps(SAMPLE_AI_JSON)}}]
    }
    mock_good.raise_for_status = MagicMock()

    with patch("services.ai_service.httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.post.side_effect = [mock_bad, mock_good]
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await call_deepseek("system", "user")
        assert result["actual_days"] == 3


def test_parse_ai_response_valid():
    result = parse_ai_response(json.dumps(SAMPLE_AI_JSON))
    assert result.actual_days == 3


def test_parse_ai_response_invalid():
    with pytest.raises(ValueError):
        parse_ai_response("not json")
