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
