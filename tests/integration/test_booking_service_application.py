import pytest

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from domain.application_services.booking import BookingServiceApp
from domain.entities.booking import BookingStatus
from domain.ports.booking_confirmed_client import ConfirmError, BookingConfirmedClient
from domain.ports.booking_repository import BookingNotFound
from domain.ports.task_manager import TaskManager
from tests.dummy import make_dummy
from tests.factories import make_booking, make_from

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_calls_client_for_pending_booking(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking()
    await repository.add(booking)
    sut = BookingServiceApp(repository, StubBookingConfirmedClient(), make_dummy(TaskManager))

    got = await sut.confirm(booking.id)

    assert got is None
    assert await repository.find_by() == [make_from(booking, status=BookingStatus.CONFIRMED)]


async def test_confirm_raises_when_pending_booking_not_found(
    session,
) -> None:
    with pytest.raises(BookingNotFound):
        await BookingServiceApp(
            SQLAlchemyBookingRepository(session),
            make_dummy(BookingConfirmedClient),
            make_dummy(TaskManager),
        ).confirm(999)


@pytest.mark.parametrize("patch_random", [0], indirect=True)
async def test_confirm_propagates_confirm_error(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking()
    await repository.add(booking)

    with pytest.raises(ConfirmError):
        await BookingServiceApp(
            repository,
            StubBookingConfirmedClient(),
            make_dummy(TaskManager),
        ).confirm(booking.id)

    assert await repository.find_by() == [booking]
