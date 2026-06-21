import pytest

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.stub_booking_confirmed_client import StubBookingConfirmClient
from domain.application_services.booking import BookingServiceApp
from domain.entities.booking import BookingStatus
from domain.ports.booking_repository import BookingNotFound, BookingNotPending
from domain.ports.task_manager import TaskManager
from tests.dummy import make_dummy
from tests.factories import make_booking, make_from

pytestmark = pytest.mark.integration


async def test_cancel_marks_pending_booking_as_failed(
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    booking = make_booking()
    await booking_repository.add(booking)
    sut = BookingServiceApp(booking_repository, make_dummy(StubBookingConfirmClient), make_dummy(TaskManager))

    await sut.cancel(booking.id)

    assert await booking_repository.find_by() == [make_from(booking, status=BookingStatus.FAILED)]


async def test_cancel_raises_when_booking_not_found(
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    sut = BookingServiceApp(
        booking_repository,
        make_dummy(StubBookingConfirmClient),
        make_dummy(TaskManager),
    )

    with pytest.raises(BookingNotFound):
        await sut.cancel(999)


async def test_cancel_raises_when_booking_not_pending(
    booking_repository: SQLAlchemyBookingRepository,
) -> None:
    booking = make_booking(status=BookingStatus.CONFIRMED)
    await booking_repository.add(booking)
    sut = BookingServiceApp(booking_repository, make_dummy(StubBookingConfirmClient), make_dummy(TaskManager))

    with pytest.raises(BookingNotPending):
        await sut.cancel(booking.id)
