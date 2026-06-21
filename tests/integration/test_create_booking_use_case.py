import pytest

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from adapters.tasks.confirm_booking import CeleryTaskManager
from domain.application_services.booking import BookingServiceApp
from domain.use_cases.create_booking import CreateBookingUseCase
from tests.dummy import make_dummy
from tests.factories import make_booking

pytestmark = pytest.mark.integration


# TODO: моки тасок нахывать именами а не delay
async def test_create_booking_use_case_returns_id_for_new_booking(session, mocker) -> None:
    delay = mocker.patch("adapters.tasks.confirm_booking.confirm_booking_task.delay")
    repository = SQLAlchemyBookingRepository(session)
    use_case = CreateBookingUseCase(
        BookingServiceApp(repository, StubBookingConfirmedClient(), CeleryTaskManager()),
        repository,
    )

    result = await use_case.execute(
        datetime_=make_booking().datetime,
        name="name",
        service_type="service_type",
    )

    assert result.created is True
    bookings = await repository.find_by(name="name")
    assert result.id == bookings[0].id
    delay.assert_called_once_with(result.id)


async def test_create_booking_use_case_returns_existing_id_without_enqueue(session, mocker) -> None:
    delay = mocker.patch("adapters.tasks.confirm_booking.confirm_booking_task.delay")
    repository = SQLAlchemyBookingRepository(session)
    existing = make_booking()
    await repository.add(existing)
    use_case = CreateBookingUseCase(
        BookingServiceApp(repository, make_dummy(StubBookingConfirmedClient), CeleryTaskManager()),
        repository,
    )

    result = await use_case.execute(
        datetime_=existing.datetime,
        name=existing.name,
        service_type=existing.service_type,
    )

    assert result.created is False
    assert result.id == existing.id
    delay.assert_not_called()
