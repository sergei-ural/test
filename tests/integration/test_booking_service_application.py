import pytest

from domain.application_services.booking import BookingServiceApp
from domain.entities.booking import BookingStatus
from domain.ports.booking_confirmed_client import ConfirmError, BookingConfirmClient
from domain.ports.booking_repository import BookingNotFound
from domain.ports.task_manager import TaskManager
from tests.dummy import make_dummy
from tests.factories import make_booking, make_from

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_calls_client_for_pending_booking(
    booking_repository,
    stub_booking_confirmed_client,
    patch_random,
) -> None:
    booking = make_booking()
    await booking_repository.add(booking)
    sut = BookingServiceApp(booking_repository, stub_booking_confirmed_client, make_dummy(TaskManager))

    got = await sut.confirm(booking.id)

    assert got is None
    assert await booking_repository.find_by() == [make_from(booking, status=BookingStatus.CONFIRMED)]


async def test_confirm_raises_when_pending_booking_not_found(
    booking_repository,
) -> None:
    with pytest.raises(BookingNotFound):
        await BookingServiceApp(
            booking_repository=booking_repository,
            booking_confirm_client=make_dummy(BookingConfirmClient),
            task_manager=make_dummy(TaskManager),
        ).confirm(999)


# TODO: Аннотаций много где не хватает
@pytest.mark.parametrize("patch_random", [0], indirect=True)
async def test_confirm_propagates_confirm_error(
    booking_repository,
    stub_booking_confirmed_client,
    patch_random,
) -> None:
    booking = make_booking()
    await booking_repository.add(booking)

    with pytest.raises(ConfirmError):
        await BookingServiceApp(
            booking_repository=booking_repository,
            booking_confirm_client=stub_booking_confirmed_client,
            task_manager=make_dummy(TaskManager),
        ).confirm(booking.id)

    assert await booking_repository.find_by() == [booking]
