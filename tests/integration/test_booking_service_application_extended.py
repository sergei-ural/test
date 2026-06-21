import pytest

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from domain.application_services.booking import BookingServiceApp
from domain.entities.booking import BookingStatus
from domain.ports.booking_repository import BookingNotFound, BookingNotPending
from tests.dummy import make_dummy
from tests.factories import make_booking, make_from
from domain.ports.task_manager import TaskManager

pytestmark = pytest.mark.integration


async def test_cancel_removes_pending_booking(session) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking()
    await repository.add(booking)
    sut = BookingServiceApp(repository, make_dummy(StubBookingConfirmedClient), make_dummy(TaskManager))

    await sut.cancel(booking.id)

    assert await repository.find_by() == []


async def test_cancel_raises_when_booking_not_found(session) -> None:
    sut = BookingServiceApp(
        SQLAlchemyBookingRepository(session),
        make_dummy(StubBookingConfirmedClient),
        make_dummy(TaskManager),
    )

    with pytest.raises(BookingNotFound):
        await sut.cancel(999)


async def test_cancel_raises_when_booking_not_pending(session) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking(status=BookingStatus.CONFIRMED)
    await repository.add(booking)
    sut = BookingServiceApp(repository, make_dummy(StubBookingConfirmedClient), make_dummy(TaskManager))

    with pytest.raises(BookingNotPending):
        await sut.cancel(booking.id)


# TODO: репозитории и клиенты вынести в фикстуры
@pytest.mark.parametrize("patch_random", [0], indirect=True)
async def test_fail_marks_pending_booking_as_failed(session, patch_random) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking(status=BookingStatus.PENDING)
    await repository.add(booking)
    sut = BookingServiceApp(repository, StubBookingConfirmedClient(), make_dummy(TaskManager))

    await sut.fail(booking.id)

    assert await repository.find_by() == [make_from(booking, status=BookingStatus.FAILED)]


async def test_fail_is_idempotent_for_non_pending_booking(session) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking(status=BookingStatus.CONFIRMED)
    await repository.add(booking)
    sut = BookingServiceApp(repository, make_dummy(StubBookingConfirmedClient), make_dummy(TaskManager))

    with pytest.raises(BookingNotFound):
        await sut.fail(booking.id)

    assert await repository.find_by() == [booking]
