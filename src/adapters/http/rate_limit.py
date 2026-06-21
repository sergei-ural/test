import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


# TODO: Разобрать нормально ли сделан лимитер
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = time.monotonic()
        window = self._requests[key]
        while window and now - window[0] >= self._window_seconds:
            window.popleft()
        if len(window) >= self._max_requests:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded")
        window.append(now)


create_booking_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


async def enforce_create_booking_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    create_booking_rate_limiter.check(client_host)
