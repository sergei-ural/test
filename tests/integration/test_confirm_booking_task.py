import asyncio

import pytest
from celery.result import EagerResult

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.tasks.confirm_booking import confirm_booking_task
from domain.entities.booking import BookingStatus
from domain.ports.booking_repository import BookingNotFound
from tests.factories import make_booking, make_from

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_booking_task_confirms_pending_booking(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking()
    await repository.add(booking)

    result: EagerResult = await asyncio.to_thread(confirm_booking_task.apply, args=[booking.id])

    assert result.get() is None
    assert await repository.find_by() == [make_from(booking, status=BookingStatus.CONFIRMED)]


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_booking_task_raises_when_booking_not_found(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)

    with pytest.raises(BookingNotFound):
        await asyncio.to_thread(lambda: confirm_booking_task.apply(args=[999]).get())

    assert await repository.find_by() == []
    patch_random.assert_not_called()


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_booking_task_raises_when_booking_is_not_pending(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking(status=BookingStatus.CONFIRMED)
    await repository.add(booking)

    with pytest.raises(BookingNotFound):
        await asyncio.to_thread(lambda: confirm_booking_task.apply(args=[booking.id]).get())

    patch_random.assert_not_called()
    assert await repository.find_by() == [booking]
