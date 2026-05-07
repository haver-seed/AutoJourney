# AutoJourney 旅行路线规划工具 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 构建一个 Web 应用，用户输入出发地、天数范围、目的地，自动生成高铁出行的旅行路线规划，包含景点推荐、每日行程和预算计算。

**架构：** Vue 3 前端通过 REST API 调用 FastAPI 后端，后端组装 prompt 调用 DeepSeek API 获取结构化行程数据，二次计算预算后返回前端展示，前端集成高德地图可视化路线。

**技术栈：** Vue 3, Element Plus, 高德地图 JS API, Vite, Python FastAPI, Pydantic, DeepSeek API, httpx

---

## 文件结构

### 后端

| 文件 | 职责 |
|------|------|
| `backend/main.py` | FastAPI 应用入口，CORS 配置，挂载路由 |
| `backend/config.py` | 环境变量配置（API Key, 模型名等） |
| `backend/models/schemas.py` | Pydantic 数据模型（请求/响应） |
| `backend/prompts/single_city.py` | 单城市模式 prompt 模板 |
| `backend/prompts/multi_city.py` | 多城市模式 prompt 模板 |
| `backend/services/ai_service.py` | DeepSeek API 调用，重试，JSON 解析 |
| `backend/services/budget_service.py` | 预算二次计算，校验 AI 计算结果 |
| `backend/routers/plan.py` | `/api/plan` 和 `/api/health` 路由 |
| `backend/requirements.txt` | Python 依赖 |
| `backend/tests/test_schemas.py` | 数据模型测试 |
| `backend/tests/test_budget_service.py` | 预算计算测试 |
| `backend/tests/test_ai_service.py` | AI 服务测试（mock） |
| `backend/tests/test_plan_router.py` | API 路由测试（mock） |

### 前端

| 文件 | 职责 |
|------|------|
| `frontend/package.json` | 项目依赖配置 |
| `frontend/vite.config.js` | Vite 构建配置，代理后端 API |
| `frontend/index.html` | HTML 入口 |
| `frontend/src/main.js` | Vue 应用入口，注册 Element Plus |
| `frontend/src/App.vue` | 根组件 |
| `frontend/src/views/Home.vue` | 主页面，组合所有子组件 |
| `frontend/src/components/InputForm.vue` | 输入表单（出发地、天数滑块、目的地、模式） |
| `frontend/src/components/DailyCard.vue` | 每日行程卡片展示 |
| `frontend/src/components/RouteMap.vue` | 高德地图路线展示 |
| `frontend/src/components/BudgetChart.vue` | 预算饼图展示 |
| `frontend/src/api/index.js` | 后端 API 调用封装 |

---

## 任务 1：后端项目初始化与数据模型

**文件：**
- 创建：`backend/requirements.txt`
- 创建：`backend/config.py`
- 创建：`backend/models/__init__.py`
- 创建：`backend/models/schemas.py`
- 创建：`backend/tests/__init__.py`
- 创建：`backend/tests/test_schemas.py`

- [ ] **步骤 1：创建 requirements.txt**

```
fastapi==0.115.0
uvicorn==0.30.0
httpx==0.27.0
pydantic==2.9.0
python-dotenv==1.0.1
pytest==8.3.0
pytest-asyncio==0.24.0
```

- [ ] **步骤 2：创建 config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
```

- [ ] **步骤 3：编写数据模型测试**

```python
# backend/tests/test_schemas.py
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
```

- [ ] **步骤 4：运行测试验证失败**

运行：`cd backend && python -m pytest tests/test_schemas.py -v`
预期：FAIL，ModuleNotFoundError

- [ ] **步骤 5：创建数据模型**

```python
# backend/models/__init__.py
```

```python
# backend/models/schemas.py
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
    fr: str = Field(alias="from")  # "from" is reserved in Python
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
```

- [ ] **步骤 6：运行测试验证通过**

运行：`cd backend && python -m pytest tests/test_schemas.py -v`
预期：全部 PASS

- [ ] **步骤 7：Commit**

```bash
git add backend/requirements.txt backend/config.py backend/models/ backend/tests/test_schemas.py
git commit -m "feat: add backend project setup and data models"
```

---

## 任务 2：Prompt 模板

**文件：**
- 创建：`backend/prompts/__init__.py`
- 创建：`backend/prompts/single_city.py`
- 创建：`backend/prompts/multi_city.py`

- [ ] **步骤 1：创建单城市 prompt 模板**

```python
# backend/prompts/__init__.py
```

```python
# backend/prompts/single_city.py
SYSTEM_PROMPT = """你是一位专业的旅行规划师。用户会告诉你出发城市、旅行天数范围和目标城市。
你需要规划一次单城市深度游行程。

要求：
1. 交通只考虑高铁/火车
2. 在用户给定的天数范围内选择最合适的天数
3. 每天安排 2-4 个景点，不要太赶
4. 预算要合理，给出每项明细
5. 必须返回合法的 JSON，不要包含任何额外文字

返回 JSON 格式：
{
  "actual_days": 实际推荐天数,
  "overview": "行程概述一句话",
  "daily_plans": [
    {
      "day": 1,
      "city": "城市名",
      "theme": "当天主题",
      "schedule": [
        {"time": "09:00", "activity": "活动描述", "duration": "2小时", "cost": 100}
      ],
      "accommodation": {"name": "酒店区域和类型", "cost": 300},
      "meals_cost": 150,
      "day_total": 550
    }
  ],
  "transport": [
    {"from": "出发城市", "to": "目标城市", "type": "高铁", "duration": "X小时", "cost": 500}
  ],
  "budget_breakdown": {
    "transport": 总交通费,
    "accommodation": 总住宿费,
    "tickets": 总门票费,
    "meals": 总餐饮费,
    "total": 总计
  }
}"""


def build_user_prompt(departure: str, min_days: int, max_days: int, destination: str, preferences: str | None) -> str:
    prompt = f"""出发城市：{departure}
行程天数：{min_days}-{max_days}天
目标城市：{destination}"""
    if preferences:
        prompt += f"\n个人偏好：{preferences}"
    prompt += "\n\n请规划行程，返回 JSON。"
    return prompt
```

- [ ] **步骤 2：创建多城市 prompt 模板**

```python
# backend/prompts/multi_city.py
SYSTEM_PROMPT = """你是一位专业的旅行规划师。用户会告诉你出发城市、旅行天数范围和多个目标城市。
你需要规划一次多城市串联游行程。

要求：
1. 交通只考虑高铁/火车，规划城市间的交通衔接
2. 在用户给定的天数范围内选择最合适的天数
3. 合理分配每个城市的停留天数，根据景点数量和距离
4. 每天安排 2-4 个景点，不要太赶
5. 城市间移动的日子安排较少景点
6. 预算要合理，给出每项明细
7. 必须返回合法的 JSON，不要包含任何额外文字

返回 JSON 格式：
{
  "actual_days": 实际推荐天数,
  "overview": "行程概述一句话",
  "daily_plans": [
    {
      "day": 1,
      "city": "城市名",
      "theme": "当天主题",
      "schedule": [
        {"time": "09:00", "activity": "活动描述", "duration": "2小时", "cost": 100}
      ],
      "accommodation": {"name": "酒店区域和类型", "cost": 300},
      "meals_cost": 150,
      "day_total": 550
    }
  ],
  "transport": [
    {"from": "出发城市", "to": "第一个目标城市", "type": "高铁", "duration": "X小时", "cost": 500},
    {"from": "第一个目标城市", "to": "第二个目标城市", "type": "高铁", "duration": "X小时", "cost": 300}
  ],
  "budget_breakdown": {
    "transport": 总交通费,
    "accommodation": 总住宿费,
    "tickets": 总门票费,
    "meals": 总餐饮费,
    "total": 总计
  }
}"""


def build_user_prompt(
    departure: str, min_days: int, max_days: int, destinations: list[str], preferences: str | None
) -> str:
    dest_str = "、".join(destinations)
    prompt = f"""出发城市：{departure}
行程天数：{min_days}-{max_days}天
目标城市：{dest_str}"""
    if preferences:
        prompt += f"\n个人偏好：{preferences}"
    prompt += "\n\n请规划行程，返回 JSON。"
    return prompt
```

- [ ] **步骤 3：Commit**

```bash
git add backend/prompts/
git commit -m "feat: add prompt templates for single-city and multi-city modes"
```

---

## 任务 3：预算计算服务

**文件：**
- 创建：`backend/services/__init__.py`
- 创建：`backend/services/budget_service.py`
- 创建：`backend/tests/test_budget_service.py`

- [ ] **步骤 1：编写预算计算测试**

```python
# backend/tests/test_budget_service.py
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd backend && python -m pytest tests/test_budget_service.py -v`
预期：FAIL，ModuleNotFoundError

- [ ] **步骤 3：创建预算计算服务**

```python
# backend/services/__init__.py
```

```python
# backend/services/budget_service.py
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
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd backend && python -m pytest tests/test_budget_service.py -v`
预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add backend/services/ backend/tests/test_budget_service.py
git commit -m "feat: add budget recalculation service with tests"
```

---

## 任务 4：AI 服务（DeepSeek API 调用）

**文件：**
- 创建：`backend/services/ai_service.py`
- 创建：`backend/tests/test_ai_service.py`

- [ ] **步骤 1：编写 AI 服务测试（mock DeepSeek API）**

```python
# backend/tests/test_ai_service.py
import json
import pytest
from unittest.mock import AsyncMock, patch
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
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps(SAMPLE_AI_JSON)}}]
    }
    mock_response.raise_for_status = AsyncMock()

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
    mock_bad = AsyncMock()
    mock_bad.status_code = 200
    mock_bad.json.return_value = {"choices": [{"message": {"content": "not valid json{"}}]}
    mock_bad.raise_for_status = AsyncMock()

    mock_good = AsyncMock()
    mock_good.status_code = 200
    mock_good.json.return_value = {
        "choices": [{"message": {"content": json.dumps(SAMPLE_AI_JSON)}}]
    }
    mock_good.raise_for_status = AsyncMock()

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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd backend && python -m pytest tests/test_ai_service.py -v`
预期：FAIL，ModuleNotFoundError

- [ ] **步骤 3：创建 AI 服务**

```python
# backend/services/ai_service.py
import json
import httpx
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, REQUEST_TIMEOUT
from models.schemas import PlanResponse


async def call_deepseek(system_prompt: str, user_prompt: str) -> dict:
    url = f"{DEEPSEEK_BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
    }

    last_error = None
    for attempt in range(2):
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                last_error = e
                continue

    raise ValueError(f"AI 返回非法 JSON，重试仍失败: {last_error}")


def parse_ai_response(raw_json: str) -> PlanResponse:
    data = json.loads(raw_json)
    return PlanResponse(**data)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd backend && python -m pytest tests/test_ai_service.py -v`
预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add backend/services/ai_service.py backend/tests/test_ai_service.py
git commit -m "feat: add DeepSeek AI service with retry logic"
```

---

## 任务 5：API 路由

**文件：**
- 创建：`backend/routers/__init__.py`
- 创建：`backend/routers/plan.py`
- 创建：`backend/tests/test_plan_router.py`

- [ ] **步骤 1：编写路由测试**

```python
# backend/tests/test_plan_router.py
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
```

- [ ] **步骤 2：运行测试验证失败**

运行：`cd backend && python -m pytest tests/test_plan_router.py -v`
预期：FAIL，ModuleNotFoundError

- [ ] **步骤 3：创建路由和主入口**

```python
# backend/routers/__init__.py
```

```python
# backend/routers/plan.py
from fastapi import APIRouter, HTTPException
from models.schemas import PlanRequest, PlanResponse
from services.ai_service import call_deepseek
from services.budget_service import recalculate_budget
from prompts import single_city, multi_city

router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/plan", response_model=PlanResponse)
async def create_plan(req: PlanRequest):
    if req.mode == "single-city":
        system_prompt = single_city.SYSTEM_PROMPT
        user_prompt = single_city.build_user_prompt(
            req.departure, req.min_days, req.max_days, req.destinations[0], req.preferences
        )
    else:
        system_prompt = multi_city.SYSTEM_PROMPT
        user_prompt = multi_city.build_user_prompt(
            req.departure, req.min_days, req.max_days, req.destinations, req.preferences
        )

    try:
        raw = await call_deepseek(system_prompt, user_prompt)
        response = PlanResponse(**raw)
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 服务异常: {e}")

    response = recalculate_budget(response)
    return response
```

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.plan import router as plan_router

app = FastAPI(title="AutoJourney")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plan_router)
```

- [ ] **步骤 4：运行测试验证通过**

运行：`cd backend && python -m pytest tests/test_plan_router.py -v`
预期：全部 PASS

- [ ] **步骤 5：Commit**

```bash
git add backend/routers/ backend/main.py backend/tests/test_plan_router.py
git commit -m "feat: add API routes with health and plan endpoints"
```

---

## 任务 6：前端项目初始化

**文件：**
- 创建：`frontend/package.json`
- 创建：`frontend/vite.config.js`
- 创建：`frontend/index.html`
- 创建：`frontend/src/main.js`
- 创建：`frontend/src/App.vue`

- [ ] **步骤 1：创建 package.json**

```json
{
  "name": "autojourney-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "element-plus": "^2.8.0",
    "axios": "^1.7.0",
    "echarts": "^5.5.0",
    "vue-echarts": "^7.0.0",
    "@amap/amap-jsapi-loader": "^1.0.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **步骤 2：创建 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **步骤 3：创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoJourney - 自动旅行规划</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **步骤 4：创建 main.js**

```javascript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
```

- [ ] **步骤 5：创建 App.vue**

```vue
<template>
  <Home />
</template>

<script setup>
import Home from './views/Home.vue'
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f5f7fa;
}
</style>
```

- [ ] **步骤 6：安装依赖并验证启动**

运行：`cd frontend && npm install && npm run dev`
预期：Vite dev server 启动在 http://localhost:3000

- [ ] **步骤 7：Commit**

```bash
git add frontend/
git commit -m "feat: initialize Vue 3 frontend project with Element Plus"
```

---

## 任务 7：API 调用封装

**文件：**
- 创建：`frontend/src/api/index.js`

- [ ] **步骤 1：创建 API 封装**

```javascript
// frontend/src/api/index.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 35000,
})

export async function generatePlan(formData) {
  const payload = {
    departure: formData.departure,
    min_days: formData.minDays,
    max_days: formData.maxDays,
    destinations: formData.destinations,
    mode: formData.mode,
    preferences: formData.preferences || null,
  }
  const { data } = await api.post('/plan', payload)
  return data
}

export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/api/
git commit -m "feat: add API client for backend communication"
```

---

## 任务 8：InputForm 组件

**文件：**
- 创建：`frontend/src/components/InputForm.vue`

- [ ] **步骤 1：创建输入表单组件**

```vue
<template>
  <el-card class="input-form">
    <el-form :model="form" label-width="100px" @submit.prevent="handleSubmit">
      <el-form-item label="出发城市">
        <el-input v-model="form.departure" placeholder="如：北京" clearable />
        <div class="hot-tags">
          <el-tag
            v-for="city in hotCities"
            :key="city"
            size="small"
            class="hot-tag"
            @click="form.departure = city"
          >
            {{ city }}
          </el-tag>
        </div>
      </el-form-item>

      <el-form-item label="行程天数">
        <el-slider
          v-model="dayRange"
          range
          :min="3"
          :max="14"
          :marks="dayMarks"
          show-stops
        />
        <span class="day-label">{{ dayRange[0] }} - {{ dayRange[1] }} 天</span>
      </el-form-item>

      <el-form-item label="目的地">
        <div class="dest-input">
          <el-input
            v-model="newDest"
            placeholder="输入城市名，回车添加"
            @keyup.enter="addDestination"
            clearable
          >
            <template #append>
              <el-button @click="addDestination">添加</el-button>
            </template>
          </el-input>
        </div>
        <div class="hot-tags">
          <el-tag
            v-for="city in hotCities"
            :key="city"
            size="small"
            class="hot-tag"
            @click="addDestDirectly(city)"
          >
            {{ city }}
          </el-tag>
        </div>
        <div class="dest-tags" v-if="form.destinations.length">
          <el-tag
            v-for="(dest, idx) in form.destinations"
            :key="idx"
            closable
            @close="removeDestination(idx)"
          >
            {{ dest }}
          </el-tag>
        </div>
      </el-form-item>

      <el-form-item label="旅行模式">
        <el-radio-group v-model="form.mode">
          <el-radio value="multi-city">多城市串联游</el-radio>
          <el-radio value="single-city">单城市深度游</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="个人偏好">
        <el-input
          v-model="form.preferences"
          type="textarea"
          :rows="2"
          placeholder="可选，如：喜欢历史古迹、预算紧张、不吃辣"
        />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
          生成行程
        </el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue'

const emit = defineEmits(['submit'])
defineProps({ loading: Boolean })

const hotCities = ['北京', '上海', '西安', '成都', '杭州', '南京', '重庆', '广州', '武汉', '长沙']

const dayMarks = { 3: '3天', 5: '5天', 7: '7天', 10: '10天', 14: '14天' }

const dayRange = ref([5, 7])
const newDest = ref('')

const form = reactive({
  departure: '',
  destinations: [],
  mode: 'multi-city',
  preferences: '',
})

function addDestination() {
  const dest = newDest.value.trim()
  if (dest && !form.destinations.includes(dest)) {
    form.destinations.push(dest)
    newDest.value = ''
  }
}

function addDestDirectly(city) {
  if (!form.destinations.includes(city)) {
    form.destinations.push(city)
  }
}

function removeDestination(idx) {
  form.destinations.splice(idx, 1)
}

function handleSubmit() {
  if (!form.departure) return
  if (!form.destinations.length) return
  emit('submit', {
    departure: form.departure,
    minDays: dayRange.value[0],
    maxDays: dayRange.value[1],
    destinations: [...form.destinations],
    mode: form.mode,
    preferences: form.preferences,
  })
}
</script>

<style scoped>
.input-form {
  max-width: 800px;
  margin: 0 auto;
}
.hot-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.hot-tag {
  cursor: pointer;
}
.hot-tag:hover {
  opacity: 0.8;
}
.dest-tags {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.day-label {
  margin-left: 16px;
  color: #409eff;
  font-weight: bold;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/components/InputForm.vue
git commit -m "feat: add InputForm component with city tags and day slider"
```

---

## 任务 9：DailyCard 组件

**文件：**
- 创建：`frontend/src/components/DailyCard.vue`

- [ ] **步骤 1：创建每日行程卡片组件**

```vue
<template>
  <el-card class="daily-card" :class="{ active: isActive }" @click="$emit('click')">
    <template #header>
      <div class="card-header">
        <span class="day-badge">Day {{ plan.day }}</span>
        <span class="city">{{ plan.city }}</span>
        <el-tag size="small" type="info">{{ plan.theme }}</el-tag>
      </div>
    </template>

    <div class="timeline">
      <div v-for="item in plan.schedule" :key="item.time" class="timeline-item">
        <div class="time">{{ item.time }}</div>
        <div class="dot" />
        <div class="content">
          <div class="activity">{{ item.activity }}</div>
          <div class="meta">
            <span>{{ item.duration }}</span>
            <span v-if="item.cost > 0" class="cost">¥{{ item.cost }}</span>
            <span v-else class="cost free">免费</span>
          </div>
        </div>
      </div>
    </div>

    <el-divider />
    <div class="summary">
      <span>住宿：{{ plan.accommodation.name }} ¥{{ plan.accommodation.cost }}</span>
      <span>餐饮：¥{{ plan.meals_cost }}</span>
      <span class="day-total">当日合计：¥{{ plan.day_total }}</span>
    </div>
  </el-card>
</template>

<script setup>
defineProps({
  plan: { type: Object, required: true },
  isActive: { type: Boolean, default: false },
})
defineEmits(['click'])
</script>

<style scoped>
.daily-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
  margin-bottom: 16px;
}
.daily-card:hover,
.daily-card.active {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.day-badge {
  background: #409eff;
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: bold;
  font-size: 14px;
}
.city {
  font-weight: bold;
  font-size: 16px;
}
.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}
.time {
  min-width: 50px;
  color: #909399;
  font-size: 13px;
}
.dot {
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}
.activity {
  font-weight: 500;
}
.meta {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
  display: flex;
  gap: 12px;
}
.cost {
  color: #e6a23c;
}
.cost.free {
  color: #67c23a;
}
.summary {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #606266;
  flex-wrap: wrap;
}
.day-total {
  color: #409eff;
  font-weight: bold;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/components/DailyCard.vue
git commit -m "feat: add DailyCard component with timeline layout"
```

---

## 任务 10：RouteMap 组件（高德地图）

**文件：**
- 创建：`frontend/src/components/RouteMap.vue`

- [ ] **步骤 1：创建地图组件**

```vue
<template>
  <div class="map-container">
    <div ref="mapRef" class="map" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'

const props = defineProps({
  transport: { type: Array, default: () => [] },
  dailyPlans: { type: Array, default: () => [] },
  activeDay: { type: Number, default: 0 },
})

const mapRef = ref(null)
let map = null
let markers = []
let polylines = []

onMounted(async () => {
  try {
    const AMap = await AMapLoader.load({
      key: 'YOUR_AMAP_KEY',
      version: '2.0',
      plugins: ['AMap.Scale', 'AMap.ToolBar'],
    })
    map = new AMap.Map(mapRef.value, {
      zoom: 6,
      center: [110, 35],
    })
    map.addControl(new AMap.Scale())
    map.addControl(new AMap.ToolBar())
    updateMap()
  } catch (e) {
    console.error('高德地图加载失败:', e)
  }
})

onUnmounted(() => {
  if (map) {
    map.destroy()
    map = null
  }
})

watch(() => [props.transport, props.dailyPlans, props.activeDay], updateMap, { deep: true })

function clearOverlays() {
  markers.forEach(m => map.remove(m))
  polylines.forEach(p => map.remove(p))
  markers = []
  polylines = []
}

function updateMap() {
  if (!map || !props.dailyPlans.length) return
  clearOverlays()

  const allPoints = []

  props.dailyPlans.forEach((day, idx) => {
    day.schedule.forEach(item => {
      if (item.activity) {
        const marker = new AMap.Marker({
          position: getApproxPosition(day.city, item.activity),
          title: item.activity,
          label: {
            content: item.activity,
            direction: 'top',
          },
        })
        marker.on('click', () => {
          const info = new AMap.InfoWindow({
            content: `<div style="padding:8px">
              <b>${item.activity}</b><br/>
              ${item.time} | ${item.duration}<br/>
              费用：¥${item.cost}
            </div>`,
            offset: new AMap.Pixel(0, -30),
          })
          info.open(map, marker.getPosition())
        })
        map.add(marker)
        markers.push(marker)
        allPoints.push(marker.getPosition())
      }
    })
  })

  props.transport.forEach(t => {
    const fromPos = getCityCenter(t.fr)
    const toPos = getCityCenter(t.to)
    if (fromPos && toPos) {
      const line = new AMap.Polyline({
        path: [fromPos, toPos],
        strokeColor: '#409eff',
        strokeWeight: 3,
        strokeStyle: 'dashed',
      })
      map.add(line)
      polylines.push(line)
    }
  })

  if (allPoints.length) {
    map.setFitView(markers)
  }
}

function getCityCenter(city) {
  const cityCoords = {
    '北京': [116.40, 39.90], '上海': [121.47, 31.23], '西安': [108.94, 34.26],
    '成都': [104.07, 30.57], '杭州': [120.15, 30.28], '南京': [118.78, 32.06],
    '重庆': [106.55, 29.56], '广州': [113.26, 23.13], '武汉': [114.30, 30.59],
    '长沙': [112.97, 28.23], '昆明': [102.83, 25.02], '大理': [100.23, 25.59],
    '丽江': [100.23, 26.87], '桂林': [110.29, 25.27], '洛阳': [112.45, 34.62],
    '开封': [114.35, 34.79], '苏州': [120.62, 31.30], '无锡': [120.31, 31.57],
    '青岛': [120.38, 36.07], '大连': [121.61, 38.91], '厦门': [118.09, 24.48],
    '深圳': [114.07, 22.55], '天津': [117.20, 39.08], '石家庄': [114.51, 38.04],
    '郑州': [113.65, 34.76], '合肥': [117.28, 31.82], '福州': [119.30, 26.08],
    '贵阳': [106.71, 26.57], '哈尔滨': [126.63, 45.75], '长春': [125.32, 43.88],
    '沈阳': [123.43, 41.80], '济南': [117.00, 36.67], '太原': [112.55, 37.87],
    '南昌': [115.89, 28.68], '兰州': [103.83, 36.06], '西宁': [101.74, 36.62],
    '银川': [106.23, 38.49], '乌鲁木齐': [87.62, 43.83], '拉萨': [91.11, 29.65],
    '呼和浩特': [111.75, 40.84], '南宁': [108.32, 22.82],
  }
  return cityCoords[city] ? new AMap.LngLat(...cityCoords[city]) : null
}

function getApproxPosition(city, activity) {
  const center = getCityCenter(city)
  if (!center) return new AMap.LngLat(110, 35)
  const offset = (Math.random() - 0.5) * 0.05
  return new AMap.LngLat(center.getLng() + offset, center.getLat() + offset)
}
</script>

<style scoped>
.map-container {
  height: 100%;
  min-height: 500px;
}
.map {
  width: 100%;
  height: 100%;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/components/RouteMap.vue
git commit -m "feat: add RouteMap component with AMap integration"
```

---

## 任务 11：BudgetChart 组件

**文件：**
- 创建：`frontend/src/components/BudgetChart.vue`

- [ ] **步骤 1：创建预算饼图组件**

```vue
<template>
  <el-card class="budget-card">
    <template #header>
      <div class="budget-header">
        <span>预算总览</span>
        <span class="total">¥{{ budget.total }}</span>
      </div>
    </template>
    <div class="chart-container">
      <v-chart :option="chartOption" autoresize />
    </div>
    <el-descriptions :column="2" border size="small">
      <el-descriptions-item label="交通费用">¥{{ budget.transport }}</el-descriptions-item>
      <el-descriptions-item label="住宿费用">¥{{ budget.accommodation }}</el-descriptions-item>
      <el-descriptions-item label="门票费用">¥{{ budget.tickets }}</el-descriptions-item>
      <el-descriptions-item label="餐饮费用">¥{{ budget.meals }}</el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([PieChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps({
  budget: {
    type: Object,
    default: () => ({ transport: 0, accommodation: 0, tickets: 0, meals: 0, total: 0 }),
  },
})

const chartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    label: { formatter: '{b}\n¥{c}' },
    data: [
      { value: props.budget.transport, name: '交通', itemStyle: { color: '#409eff' } },
      { value: props.budget.accommodation, name: '住宿', itemStyle: { color: '#67c23a' } },
      { value: props.budget.tickets, name: '门票', itemStyle: { color: '#e6a23c' } },
      { value: props.budget.meals, name: '餐饮', itemStyle: { color: '#f56c6c' } },
    ],
  }],
}))
</script>

<style scoped>
.budget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.total {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}
.chart-container {
  height: 300px;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/components/BudgetChart.vue
git commit -m "feat: add BudgetChart component with ECharts pie chart"
```

---

## 任务 12：Home 页面（组装所有组件）

**文件：**
- 创建：`frontend/src/views/Home.vue`

- [ ] **步骤 1：创建主页面**

```vue
<template>
  <div class="home">
    <div class="header">
      <h1>AutoJourney</h1>
      <p>输入你的旅行信息，AI 为你规划完美行程</p>
    </div>

    <InputForm :loading="loading" @submit="handleGenerate" />

    <div v-if="result" class="result-section">
      <el-alert :title="result.overview" type="success" show-icon :closable="false" />

      <el-row :gutter="20" class="content-row">
        <el-col :span="12">
          <div class="cards-area">
            <DailyCard
              v-for="plan in result.daily_plans"
              :key="plan.day"
              :plan="plan"
              :is-active="activeDay === plan.day"
              @click="activeDay = plan.day"
            />
          </div>
        </el-col>
        <el-col :span="12">
          <RouteMap
            :transport="result.transport"
            :daily-plans="result.daily_plans"
            :active-day="activeDay"
          />
        </el-col>
      </el-row>

      <BudgetChart :budget="result.budget_breakdown" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import InputForm from '../components/InputForm.vue'
import DailyCard from '../components/DailyCard.vue'
import RouteMap from '../components/RouteMap.vue'
import BudgetChart from '../components/BudgetChart.vue'
import { generatePlan } from '../api/index.js'

const loading = ref(false)
const result = ref(null)
const activeDay = ref(1)

async function handleGenerate(formData) {
  loading.value = true
  result.value = null
  try {
    result.value = await generatePlan(formData)
    activeDay.value = 1
  } catch (err) {
    const msg = err.response?.data?.detail || '生成失败，请稍后重试'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}
.header {
  text-align: center;
  margin-bottom: 32px;
}
.header h1 {
  font-size: 36px;
  color: #303133;
  margin-bottom: 8px;
}
.header p {
  color: #909399;
  font-size: 16px;
}
.result-section {
  margin-top: 32px;
}
.content-row {
  margin-top: 20px;
}
.cards-area {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 8px;
}
</style>
```

- [ ] **步骤 2：Commit**

```bash
git add frontend/src/views/Home.vue
git commit -m "feat: add Home view integrating all components"
```

---

## 任务 13：端到端验证

- [ ] **步骤 1：创建 .env 文件**

```bash
# backend/.env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

- [ ] **步骤 2：启动后端**

运行：`cd backend && uvicorn main:app --reload --port 8000`
预期：服务启动在 http://127.0.0.1:8000

- [ ] **步骤 3：测试健康检查**

运行：`curl http://127.0.0.1:8000/api/health`
预期：`{"status":"ok"}`

- [ ] **步骤 4：启动前端**

运行：`cd frontend && npm run dev`
预期：Vite 启动在 http://localhost:3000

- [ ] **步骤 5：浏览器测试**

打开 http://localhost:3000，填写表单，点击生成行程，验证：
- 表单输入正常
- 行程卡片展示
- 地图标注显示
- 预算饼图展示

- [ ] **步骤 6：Commit**

```bash
git add .
git commit -m "feat: complete AutoJourney MVP with end-to-end functionality"
```
