import asyncio

import pytest
from celery.result import EagerResult

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.tasks.confirm_booking import confirm_booking_task
from domain.entities.booking import BookingStatus
from domain.ports.booking_confirmed_client import ConfirmError
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
    assert await repository.find_by(id=booking.id) == [make_from(booking, status=BookingStatus.CONFIRMED)]


async def test_confirm_booking_task_completes_when_booking_not_found(session) -> None:
    repository = SQLAlchemyBookingRepository(session)
    result: EagerResult = await asyncio.to_thread(confirm_booking_task.apply, args=[999])

    assert result.get() is None
    assert await repository.find_by() == []


@pytest.mark.parametrize("patch_random", [0], indirect=True)
async def test_confirm_booking_task_retries_on_confirm_error(
    session,
    patch_random,
) -> None:
    from adapters.celery_app import celery_app

    celery_app.conf.task_eager_propagates = False
    booking = make_booking()
    await SQLAlchemyBookingRepository(session).add(booking)

    with pytest.raises(ConfirmError):
        await asyncio.to_thread(lambda: confirm_booking_task.apply(args=[booking.id]).get())


@pytest.mark.parametrize("patch_random", [1], indirect=True)
async def test_confirm_booking_task_completes_when_booking_is_not_pending(
    session,
    patch_random,
) -> None:
    repository = SQLAlchemyBookingRepository(session)
    booking = make_booking(status=BookingStatus.CONFIRMED)
    await repository.add(booking)

    result: EagerResult = await asyncio.to_thread(confirm_booking_task.apply, args=[booking.id])

    assert result.get() is None
    patch_random.assert_not_called()
    assert await repository.find_by(id=booking.id) == [booking]
