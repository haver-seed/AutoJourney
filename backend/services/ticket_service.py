"""12306 train ticket query service — using mcp_12306 for station resolution."""

import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from mcp_12306.services.station_service import StationService

logger = logging.getLogger(__name__)

_station_service = StationService()
_station_loaded = False

# 12306 API endpoints
_URLS = {
    "init": "https://kyfw.12306.cn/otn/leftTicket/init",
    "query_left": "https://kyfw.12306.cn/otn/leftTicket/queryG",
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
    "Host": "kyfw.12306.cn",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": "https://kyfw.12306.cn",
}


async def ensure_loaded():
    global _station_loaded
    if not _station_loaded:
        await _station_service.load_stations()
        _station_loaded = True
        logger.info(f"Loaded {len(_station_service.stations)} stations from mcp_12306")


async def get_station_code(station_name: str) -> str | None:
    """Get 12306 telecode from station name using mcp_12306's fuzzy search."""
    await ensure_loaded()
    code = await _station_service.get_station_code(station_name)
    if code:
        return code
    # Try fuzzy search
    result = await _station_service.search_stations(station_name, 3)
    if result.stations:
        return result.stations[0].code
    return None


async def search_stations(query: str, limit: int = 15) -> list[dict]:
    """Search stations by name/pinyin/city, return list of {name, code, city}."""
    await ensure_loaded()
    result = await _station_service.search_stations(query, limit)
    return [{"name": s.name, "code": s.code, "city": s.city or ""} for s in result.stations]


# 12306 seat code mapping
_SEAT_CODE_MAP = {
    "9": "商务座", "P": "商务座",
    "M": "一等座",
    "O": "二等座",
    "A": "高级软卧",
    "6": "软卧", "I": "一等卧",
    "4": "硬卧", "J": "二等卧",
    "3": "硬座",
    "1": "硬座",
    "W": "无座", "0": "无座",
    "D": "动卧",
}


def _parse_yp_info(yp_info: str) -> dict:
    """Parse 12306 yp_info field to extract seat prices.

    Format: (1 char seat code + 5 chars price in 角 + 4 chars code) repeated.
    1角 = 0.1元, so actual price = price_jiao / 10.
    """
    seats = {}
    if not yp_info or len(yp_info) < 10:
        return seats

    groups = [yp_info[i:i+10] for i in range(0, len(yp_info), 10)]
    for group in groups:
        if len(group) < 6:
            continue
        code = group[0]
        price_str = group[1:6]
        try:
            price_jiao = int(price_str)
            price_yuan = price_jiao / 10.0
        except (ValueError, TypeError):
            continue

        seat_name = _SEAT_CODE_MAP.get(code)
        if seat_name and price_yuan > 0:
            if seat_name not in seats:
                seats[seat_name] = str(price_yuan)

    return seats


def _parse_train_from_line(line: str, station_map: dict, from_station: str, to_station: str, train_date: str) -> dict | None:
    """Parse a single 12306 result line into a train info dict."""
    parts = line.split("|")
    if len(parts) < 40:
        return None

    can_buy = parts[11]
    train_no = parts[3]
    start_time = parts[8]
    arrive_time = parts[9]
    duration = parts[10]
    from_code_actual = parts[6]
    to_code_actual = parts[7]

    # Resolve station names
    from_name = station_map.get(from_code_actual, from_station)
    to_name = station_map.get(to_code_actual, to_station)

    # Parse prices from yp_info
    yp_info = parts[39]
    seats = _parse_yp_info(yp_info)

    # Check availability from traditional fields too
    avail_map = {
        32: "商务座", 31: "一等座", 30: "二等座",
        33: "动卧", 28: "硬卧", 23: "软卧",
        29: "硬座", 26: "无座",
    }
    for idx, name in avail_map.items():
        val = parts[idx] if len(parts) > idx else ""
        if name not in seats and val and val != "--" and val != "":
            seats[name] = val

    # Check if this train has real prices (not just "有"/"无" text)
    has_real_price = False
    for name in ["二等座", "一等座", "商务座"]:
        if name in seats:
            try:
                v = float(seats[name])
                if v > 50:  # price > 50 yuan is likely real
                    has_real_price = True
                    break
            except (ValueError, TypeError):
                pass

    return {
        "train_no": train_no,
        "from": from_name,
        "to": to_name,
        "start_time": start_time,
        "arrive_time": arrive_time,
        "duration": duration,
        "seats": seats,
        "has_real_price": has_real_price,
        "can_buy": can_buy == "Y",
        "date": train_date,
    }


async def _query_single_day(
    client: httpx.AsyncClient, from_code: str, to_code: str, train_date: str,
    from_station: str, to_station: str
) -> list[dict]:
    """Query 12306 for all trains on a single day."""
    headers = _HEADERS.copy()

    # Init to get cookies
    await client.get(_URLS["init"], headers=headers)

    params = {
        "leftTicketDTO.train_date": train_date,
        "leftTicketDTO.from_station": from_code,
        "leftTicketDTO.to_station": to_code,
        "purpose_codes": "ADULT",
    }
    resp = await client.get(_URLS["query_left"], headers=headers, params=params)

    if resp.status_code != 200:
        logger.warning(f"12306 returned {resp.status_code} for {train_date}")
        return []

    data = resp.json().get("data", {})
    results = data.get("result", [])
    station_map = data.get("map", {})

    trains = []
    for line in results:
        train = _parse_train_from_line(line, station_map, from_station, to_station, train_date)
        if train:
            trains.append(train)
    return trains


def _get_target_price(train: dict) -> float:
    """Extract the target price (prefer 二等座) from a train."""
    seats = train.get("seats", {})
    for name in ["二等座", "一等座", "商务座"]:
        if name in seats:
            try:
                v = float(seats[name])
                if v > 50:
                    return v
            except (ValueError, TypeError):
                pass
    return float("inf")


def _parse_time_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes since midnight."""
    try:
        h, m = time_str.split(":")
        return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return 0


def _parse_duration_minutes(duration_str: str) -> int:
    """Convert HH:MM duration to minutes."""
    try:
        parts = duration_str.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return 0


def _score_time_convenience(train: dict) -> float:
    """Score time convenience. Higher is better.

    Best scenarios:
    - Overnight train: depart 18:00-23:00, arrive 06:00-10:00 (saves hotel, full day)
    - Early morning depart + reasonable arrival (maximizes sightseeing)
    - Avoid: arrive too late (22:00+), depart too early (before 05:00)
    """
    dep = _parse_time_minutes(train.get("start_time", "12:00"))
    arr = _parse_time_minutes(train.get("arrive_time", "12:00"))
    dur = _parse_duration_minutes(train.get("duration", "05:00"))

    score = 0.0

    # Overnight train bonus: depart evening, arrive next morning
    # If duration > 6 hours and depart after 17:00, likely overnight
    if dur > 360 and dep >= 17 * 60:
        score += 30  # Big bonus: saves hotel cost
        # Extra bonus for arriving at a good time (06:00-10:00)
        if 6 * 60 <= arr <= 10 * 60:
            score += 20  # Perfect: arrive morning, full day ahead
        elif arr < 6 * 60:
            score += 10  # OK: arrive very early

    # Early departure bonus (06:00-08:00): maximize sightseeing time
    if 6 * 60 <= dep <= 8 * 60:
        score += 15

    # Reasonable arrival time bonus (08:00-18:00)
    if 8 * 60 <= arr <= 18 * 60:
        score += 10
    elif 18 * 60 < arr <= 21 * 60:
        score += 0  # Acceptable
    elif arr > 21 * 60:
        score -= 15  # Arrive too late, waste a day

    # Penalty for very early departure (before 05:00)
    if dep < 5 * 60:
        score -= 10

    # Shorter duration bonus (prefer faster trains when price is similar)
    score -= dur / 60  # -1 per hour of travel

    return score


def _build_reason(chosen: dict, all_candidates: list[dict], target_date: str) -> str:
    """Build a detailed reason for why this ticket was chosen."""
    chosen_price = _get_target_price(chosen)
    chosen_date = chosen["date"]
    dep_time = chosen.get("start_time", "")
    arr_time = chosen.get("arrive_time", "")
    dur = chosen.get("duration", "")
    dur_min = _parse_duration_minutes(dur)

    reasons = []

    # Price analysis
    if len(all_candidates) > 1:
        prices = [_get_target_price(t) for t in all_candidates if _get_target_price(t) < float("inf")]
        min_price = min(prices) if prices else chosen_price
        max_price = max(prices) if prices else chosen_price
        price_range = max_price - min_price

        if chosen_price <= min_price + 1:
            reasons.append("价格最低")
        elif price_range > 0 and (chosen_price - min_price) / price_range < 0.2:
            reasons.append(f"价格接近最低（仅贵 ¥{chosen_price - min_price:.0f}）")
    else:
        reasons.append("唯一可选班次")

    # Time convenience analysis
    dep_min = _parse_time_minutes(dep_time)
    arr_min = _parse_time_minutes(arr_time)

    if dur_min > 360 and dep_min >= 17 * 60:
        reasons.append("夜间出发的长途车，节省一晚住宿费")
        if 6 * 60 <= arr_min <= 10 * 60:
            reasons.append(f"{arr_time}到达，时间充裕可直接游玩")
    elif 6 * 60 <= dep_min <= 8 * 60:
        reasons.append("早间出发，最大化游玩时间")
    elif arr_min > 21 * 60:
        reasons.append("注意：到达时间较晚")

    # Date adjustment note
    if chosen_date != target_date:
        delta = (datetime.strptime(chosen_date, "%Y-%m-%d") - datetime.strptime(target_date, "%Y-%m-%d")).days
        if delta < 0:
            reasons.append(f"推荐提前{abs(delta)}天出发")
        else:
            reasons.append(f"推荐推迟{delta}天出发")

    return "；".join(reasons) if reasons else "综合性价比最优"


def _format_seat_info(seats: dict) -> list[str]:
    """Format seat info strings with prices."""
    seat_info = []
    for name in ["二等座", "一等座", "商务座"]:
        if name in seats:
            price = seats[name]
            try:
                price_val = float(price)
                if price_val > 100:
                    seat_info.append(f"{name} ¥{price_val:.0f}")
                else:
                    seat_info.append(f"{name}有票")
            except (ValueError, TypeError):
                seat_info.append(f"{name}有票")
    return seat_info


async def query_ticket_price(
    from_station: str, to_station: str, train_date: str
) -> dict | None:
    """Query 12306 for the best available train, comparing prices across 3 days.

    Compares train_date-1, train_date, train_date+1.
    Skips trains with no available tickets.
    Picks the cheapest 二等座 ticket and includes a reason comment.
    """
    await ensure_loaded()

    from_code = await get_station_code(from_station)
    to_code = await get_station_code(to_station)
    if not from_code or not to_code:
        logger.warning(f"Station code not found: {from_station}({from_code}) -> {to_station}({to_code})")
        return None

    # Generate 3 dates: day before, target day, day after
    target_dt = datetime.strptime(train_date, "%Y-%m-%d")
    dates = [
        (target_dt - timedelta(days=1)).strftime("%Y-%m-%d"),
        train_date,
        (target_dt + timedelta(days=1)).strftime("%Y-%m-%d"),
    ]

    max_retries = 2
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(follow_redirects=False, timeout=10, verify=False) as client:
                # Query all 3 days
                day_results = await asyncio.gather(
                    *[_query_single_day(client, from_code, to_code, d, from_station, to_station) for d in dates],
                    return_exceptions=True,
                )

                # Collect all valid trains
                all_trains = []
                for result in day_results:
                    if isinstance(result, Exception):
                        logger.warning(f"Query failed: {result}")
                        continue
                    all_trains.extend(result)

                if not all_trains:
                    return None

                # Prefer: buyable trains with real prices
                buyable_priced = [t for t in all_trains if t["has_real_price"] and t["can_buy"]]
                if buyable_priced:
                    priced_trains = buyable_priced
                else:
                    # Fallback: any train with real prices (even if not buyable)
                    priced_trains = [t for t in all_trains if t["has_real_price"]]
                    if not priced_trains:
                        # Last resort: any buyable train
                        priced_trains = [t for t in all_trains if t["can_buy"]]
                    if not priced_trains:
                        # Absolute last resort: any train at all
                        priced_trains = all_trains

                if not priced_trains:
                    return None

                # Score each train: lower price + better time convenience
                # Normalize time score to be comparable with price
                prices = [_get_target_price(t) for t in priced_trains]
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price if max_price > min_price else 1

                def sort_key(t):
                    price = _get_target_price(t)
                    time_score = _score_time_convenience(t)
                    # Normalize: price difference as fraction of range, time score scaled
                    # Lower total = better
                    price_norm = (price - min_price) / price_range * 100  # 0-100
                    time_norm = -time_score  # Negative because lower is better
                    date_penalty = 0 if t["date"] == train_date else 5
                    return (price_norm + time_norm + date_penalty,)

                priced_trains.sort(key=sort_key)
                chosen = priced_trains[0]

                # Build result
                seats = chosen["seats"]
                seat_info = _format_seat_info(seats)
                reason = _build_reason(chosen, priced_trains, train_date)

                if not chosen.get("can_buy", True):
                    reason = "暂不可购，" + reason

                return {
                    "train_no": chosen["train_no"],
                    "from": chosen["from"],
                    "to": chosen["to"],
                    "start_time": chosen["start_time"],
                    "arrive_time": chosen["arrive_time"],
                    "duration": chosen["duration"],
                    "seat_types": "、".join(seat_info) if seat_info else "暂无余票",
                    "seats": seats,
                    "actual_date": chosen["date"],
                    "reason": reason,
                }

        except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError) as e:
            if attempt < max_retries - 1:
                logger.warning(f"12306 query retry {attempt + 1}/{max_retries}: {e}")
                await asyncio.sleep(1)
            else:
                logger.error(f"12306 query failed after {max_retries} retries: {e}")

    return None
