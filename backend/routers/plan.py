import json
from datetime import datetime, timedelta
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import TicketRequest, TicketResponse, TicketSegment, TrainInfo
from services.ticket_service import query_ticket_price, search_stations

router = APIRouter(prefix="/api")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/stations")
async def station_search(q: str = "", limit: int = 15):
    if not q or len(q.strip()) < 1:
        return []
    results = await search_stations(q.strip(), limit)
    return results


def _sse_event(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _calc_segment_dates(departure_date: str, stay_days: list[int]) -> list[str]:
    """Calculate the travel date for each segment based on stay durations."""
    dates = []
    dt = datetime.strptime(departure_date, "%Y-%m-%d")
    dates.append(dt.strftime("%Y-%m-%d"))
    for days in stay_days[:-1]:  # last city has no next segment
        dt += timedelta(days=days)
        dates.append(dt.strftime("%Y-%m-%d"))
    return dates


@router.post("/tickets")
async def query_tickets(req: TicketRequest):
    cities = [req.departure] + req.destinations
    total_segments = len(cities) - 1
    segment_dates = _calc_segment_dates(req.departure_date, req.stay_days)

    async def generate():
        segments = []
        total_cost = 0.0

        for i in range(total_segments):
            from_city = cities[i]
            to_city = cities[i + 1]
            travel_date = segment_dates[i]

            percent = int(10 + 80 * i / total_segments)
            yield _sse_event("progress", {
                "stage": "ticket",
                "percent": percent,
                "message": f"正在查询第 {i + 1}/{total_segments} 段车票：{from_city} → {to_city}...",
            })

            result = await query_ticket_price(from_city, to_city, travel_date)

            if result:
                actual_date = result.get("actual_date", travel_date)
                seats = result.get("seats", {})
                price_str = seats.get("二等座") or seats.get("一等座") or seats.get("商务座") or ""
                cost = 0.0
                if price_str:
                    try:
                        cost = float(price_str)
                    except (ValueError, TypeError):
                        pass

                train_info = TrainInfo(
                    train_no=result.get("train_no", ""),
                    seat_types=result.get("seat_types", ""),
                    note=f"{result.get('start_time', '')}出发，{result.get('arrive_time', '')}到达",
                    start_time=result.get("start_time", ""),
                    arrive_time=result.get("arrive_time", ""),
                    duration=result.get("duration", ""),
                    actual_date=actual_date,
                    reason=result.get("reason", ""),
                )
                segment = TicketSegment(
                    **{"from": from_city, "to": to_city},
                    travel_date=actual_date,
                    train_info=train_info,
                    cost=cost,
                    stay_days=req.stay_days[i] if i < len(req.stay_days) else 0,
                )
            else:
                segment = TicketSegment(
                    **{"from": from_city, "to": to_city},
                    travel_date=travel_date,
                    cost=0,
                    stay_days=req.stay_days[i] if i < len(req.stay_days) else 0,
                )

            total_cost += segment.cost
            segments.append(segment)

        total_days = sum(req.stay_days) + total_segments  # stay days + travel days
        response = TicketResponse(
            segments=segments,
            total_cost=total_cost,
            total_days=total_days,
        )

        yield _sse_event("progress", {"stage": "done", "percent": 100, "message": "查询完毕！"})
        yield _sse_event("result", response.model_dump(by_alias=True))

    return StreamingResponse(generate(), media_type="text/event-stream")
