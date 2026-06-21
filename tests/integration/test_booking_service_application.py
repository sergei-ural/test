import pytest

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from domain.application_services.booking import BookingServiceApplication
from domain.entities.booking import BookingStatus
from domain.ports.booking_confirmed_client import ConfirmError, BookingConfirmedClient
from domain.ports.booking_repository import BookingNotFound
from tests.dummy import make_dummy
from tests.factories import make_booking, make_from

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_calls_client_for_pending_booking(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = await repository.add(make_booking())
    sut = BookingServiceApplication(repository, StubBookingConfirmedClient())

    got = await sut.confirm(booking.id)

    assert got is None
    assert await repository.find_by(id=booking.id) == [make_from(booking, status=BookingStatus.CONFIRMED)]


async def test_confirm_raises_when_pending_booking_not_found(
    session,
) -> None:
    with pytest.raises(BookingNotFound):
        await BookingServiceApplication(
            SQLAlchemyBookingRepository(session),
            make_dummy(BookingConfirmedClient),
        ).confirm(999)


@pytest.mark.parametrize("patch_random", [0], indirect=True)
async def test_confirm_propagates_confirm_error(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = await repository.add(make_booking())

    with pytest.raises(ConfirmError):
        await BookingServiceApplication(repository, StubBookingConfirmedClient()).confirm(booking.id)

    assert await repository.find_by(id=booking.id, status=BookingStatus.PENDING) == [booking]
