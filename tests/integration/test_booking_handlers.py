import pytest

from adapters.http.rate_limit import create_booking_rate_limiter
from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from domain.entities.booking import BookingStatus
from tests.factories import make_booking

pytestmark = pytest.mark.integration


async def test_get_booking_returns_booking(
    client,
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    booking = make_booking()
    await booking_repository.add(booking)

    response = await client.get(f"/bookings/{booking.id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": booking.id,
        "datetime": booking.datetime.isoformat(),
        "name": booking.name,
        "service_type": booking.service_type,
        "status": booking.status,
    }


async def test_get_booking_returns_404_when_not_found(client) -> None:
    response = await client.get("/bookings/999")

    assert response.status_code == 404


async def test_list_bookings_filters_by_status_and_pagination(
    client,
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    pending = make_booking(name="pending", status=BookingStatus.PENDING)
    confirmed = make_booking(name="confirmed", status=BookingStatus.CONFIRMED)
    failed = make_booking(name="failed", status=BookingStatus.FAILED)
    await booking_repository.add(pending)
    await booking_repository.add(confirmed)
    await booking_repository.add(failed)

    response = await client.get("/bookings", params={"status": BookingStatus.CONFIRMED, "offset": 0, "limit": 10})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": confirmed.id,
            "datetime": confirmed.datetime.isoformat(),
            "name": confirmed.name,
            "service_type": confirmed.service_type,
            "status": confirmed.status,
        }
    ]


async def test_list_bookings_supports_pagination(
    client,
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    first = make_booking(name="first")
    second = make_booking(name="second")
    third = make_booking(name="third")
    await booking_repository.add(first)
    await booking_repository.add(second)
    await booking_repository.add(third)

    response = await client.get("/bookings", params={"offset": 1, "limit": 1})

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == second.id


async def test_cancel_booking_deletes_pending_booking(
    client,
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    booking = make_booking()
    await booking_repository.add(booking)

    response = await client.delete(f"/bookings/{booking.id}")

    assert response.status_code == 200
    assert await booking_repository.find_by() == []


async def test_cancel_booking_returns_404_when_not_found(client) -> None:
    response = await client.delete("/bookings/999")

    assert response.status_code == 404


async def test_cancel_booking_returns_409_when_not_pending(
    client,
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    booking = make_booking(status=BookingStatus.CONFIRMED)
    await booking_repository.add(booking)

    response = await client.delete(f"/bookings/{booking.id}")

    assert response.status_code == 409


async def test_create_booking_rate_limit_returns_429(
    client,
    base_booking_payload,
    confirm_booking_task_delay_mock,
    mocker,
) -> None:
    mocker.patch.object(create_booking_rate_limiter, "_max_requests", 0)

    response = await client.post("/bookings", json={**base_booking_payload, "name": "limited-overflow"})

    assert response.status_code == 429
    confirm_booking_task_delay_mock.assert_not_called()
