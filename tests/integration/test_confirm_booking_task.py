import asyncio

import pytest
from celery.result import EagerResult

from adapters.tasks.confirm_booking import confirm_booking_task
from domain.entities.booking import BookingStatus
from domain.ports.booking_repository import BookingNotFound
from tests.factories import make_booking, make_from

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_booking_task_confirms_pending_booking(
    booking_repository,
    patch_random,
) -> None:
    booking = make_booking()
    await booking_repository.add(booking)

    result: EagerResult = await asyncio.to_thread(confirm_booking_task.apply, args=[booking.id])

    assert result.get() is None
    assert await booking_repository.find_by() == [make_from(booking, status=BookingStatus.CONFIRMED)]


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_booking_task_raises_when_booking_not_found(
    booking_repository,
    patch_random,
) -> None:
    with pytest.raises(BookingNotFound):
        await asyncio.to_thread(lambda: confirm_booking_task.apply(args=[999]).get())

    assert await booking_repository.find_by() == []
    patch_random.assert_not_called()


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_booking_task_raises_when_booking_is_not_pending(
    booking_repository,
    patch_random,
) -> None:
    booking = make_booking(status=BookingStatus.CONFIRMED)
    await booking_repository.add(booking)

    with pytest.raises(BookingNotFound):
        await asyncio.to_thread(lambda: confirm_booking_task.apply(args=[booking.id]).get())

    patch_random.assert_not_called()
    assert await booking_repository.find_by() == [booking]
