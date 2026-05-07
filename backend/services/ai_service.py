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
