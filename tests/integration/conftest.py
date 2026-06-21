import pytest
from httpx import ASGITransport, AsyncClient

from adapters.http.app import create_app
from adapters.http.rate_limit import create_booking_rate_limiter


@pytest.fixture
def base_booking_payload() -> dict[str, str]:
    return {
        "datetime": "2030-06-21T10:00:00",
        "name": "name",
        "service_type": "service_type",
    }


@pytest.fixture
async def client(session):
    create_booking_rate_limiter._requests.clear()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http_client:
        yield http_client
