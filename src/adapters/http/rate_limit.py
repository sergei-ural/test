import time

from fastapi import HTTPException, Request, status

MAX_REQUESTS = 10
WINDOW_SECONDS = 60
_requests: dict[str, list[float]] = {}


async def enforce_create_booking_rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    recent = [t for t in _requests.get(key, []) if now - t < WINDOW_SECONDS]
    if len(recent) >= MAX_REQUESTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
    _requests[key] = [*recent, now]
