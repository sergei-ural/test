from unittest.mock import MagicMock

import pytest

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.stub_booking_confirmed_client import StubBookingConfirmClient
from adapters.tasks.confirm_booking import CeleryTaskManager
from domain.application_services.booking import BookingServiceApp
from domain.use_cases.create_booking import CreateBookingUseCase
from tests.dummy import make_dummy
from tests.factories import make_booking

pytestmark = pytest.mark.integration


async def test_create_booking_use_case_returns_id_for_new_booking(
    booking_repository: SQLAlchemyBookingRepository,
    stub_booking_confirmed_client: StubBookingConfirmClient,
    confirm_booking_task_delay_mock: MagicMock,
) -> None:
    use_case = CreateBookingUseCase(
        BookingServiceApp(booking_repository, stub_booking_confirmed_client, CeleryTaskManager()),
        booking_repository,
    )

    result = await use_case.execute(
        datetime_=make_booking().datetime,
        name="name",
        service_type="service_type",
    )

    assert result.created is True
    bookings = await booking_repository.find_by(name="name")
    assert result.id == bookings[0].id
    confirm_booking_task_delay_mock.assert_called_once_with(result.id)


async def test_create_booking_use_case_returns_existing_id_without_enqueue(
    booking_repository: SQLAlchemyBookingRepository,
    confirm_booking_task_delay_mock: MagicMock,
) -> None:
    existing = make_booking()
    await booking_repository.add(existing)
    use_case = CreateBookingUseCase(
        BookingServiceApp(booking_repository, make_dummy(StubBookingConfirmClient), CeleryTaskManager()),
        booking_repository,
    )

    result = await use_case.execute(
        datetime_=existing.datetime,
        name=existing.name,
        service_type=existing.service_type,
    )

    assert result.created is False
    assert result.id == existing.id
    confirm_booking_task_delay_mock.assert_not_called()
