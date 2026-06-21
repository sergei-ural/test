from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

from adapters.http.app import create_app
from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from tests.factories import make_booking

pytestmark = pytest.mark.integration

BOOKING_PAYLOAD = {
    "datetime": "2030-06-21T10:00:00",
    "name": "name",
    "service_type": "service_type",
}


@pytest.fixture
async def client(session):
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http_client:
        yield http_client


async def test_create_booking_returns_201_and_enqueues_confirm(
    client,
    booking_repository: SQLAlchemyBookingRepository,
    mocker,
) -> None:
    delay = mocker.patch("adapters.tasks.confirm_booking.confirm_booking_task.delay")

    response = await client.post("/bookings", json=BOOKING_PAYLOAD)

    assert response.status_code == 201
    assert response.content == b""
    bookings = await booking_repository.find_by(name=BOOKING_PAYLOAD["name"])
    assert len(bookings) == 1
    delay.assert_called_once_with(bookings[0].id)


async def test_create_booking_succeeds_when_booking_already_exists(
    client,
    booking_repository: SQLAlchemyBookingRepository,
    mocker,
) -> None:
    delay = mocker.patch("adapters.tasks.confirm_booking.confirm_booking_task.delay")
    await booking_repository.add(
        make_booking(
            datetime_=datetime.fromisoformat(BOOKING_PAYLOAD["datetime"]),
            name=BOOKING_PAYLOAD["name"],
            service_type=BOOKING_PAYLOAD["service_type"],
        )
    )

    response = await client.post("/bookings", json=BOOKING_PAYLOAD)

    assert response.status_code == 204
    assert response.content == b""
    delay.assert_not_called()


async def test_create_booking_rejects_past_datetime(client) -> None:
    response = await client.post(
        "/bookings",
        json={
            "datetime": "2020-01-01T10:00:00",
            "name": "name",
            "service_type": "service_type",
        },
    )

    assert response.status_code == 422
