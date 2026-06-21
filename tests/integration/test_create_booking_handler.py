from datetime import datetime
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from tests.factories import make_booking

pytestmark = pytest.mark.integration


async def test_create_booking_returns_201_and_enqueues_confirm(
    client: AsyncClient,
    booking_repository: SQLAlchemyBookingRepository,
    base_booking_payload: dict[str, str],
    confirm_booking_task_delay_mock: MagicMock,
) -> None:
    response = await client.post("/bookings", json=base_booking_payload)

    assert response.status_code == 201
    bookings = await booking_repository.find_by(name=base_booking_payload["name"])
    assert len(bookings) == 1
    assert response.json() == {"id": bookings[0].id}
    confirm_booking_task_delay_mock.assert_called_once_with(bookings[0].id)


async def test_create_booking_succeeds_when_booking_already_exists(
    client: AsyncClient,
    booking_repository: SQLAlchemyBookingRepository,
    base_booking_payload: dict[str, str],
    confirm_booking_task_delay_mock: MagicMock,
) -> None:
    existing = make_booking(
        datetime_=datetime.fromisoformat(base_booking_payload["datetime"]),
        name=base_booking_payload["name"],
        service_type=base_booking_payload["service_type"],
    )
    await booking_repository.add(existing)

    response = await client.post("/bookings", json=base_booking_payload)

    assert response.status_code == 200
    assert response.json() == {"id": existing.id}
    confirm_booking_task_delay_mock.assert_not_called()


async def test_create_booking_rejects_past_datetime(client: AsyncClient) -> None:
    response = await client.post(
        "/bookings",
        json={
            "datetime": "2020-01-01T10:00:00",
            "name": "name",
            "service_type": "service_type",
        },
    )

    assert response.status_code == 422
