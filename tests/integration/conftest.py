import pytest
from httpx import ASGITransport, AsyncClient

from adapters.http.app import create_app
from adapters.http.rate_limit import create_booking_rate_limiter
from adapters.stub_booking_confirmed_client import StubBookingConfirmClient


@pytest.fixture
def base_booking_payload() -> dict[str, str]:
    return {
        "datetime": "2030-06-21T10:00:00",
        "name": "name",
        "service_type": "service_type",
    }


@pytest.fixture
def stub_booking_confirmed_client() -> StubBookingConfirmClient:
    return StubBookingConfirmClient()


@pytest.fixture
def confirm_booking_task_delay_mock(mocker):
    return mocker.patch("adapters.tasks.confirm_booking.confirm_booking_task.delay")


@pytest.fixture
async def client(session):
    create_booking_rate_limiter._requests.clear()
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http_client:
        yield http_client
