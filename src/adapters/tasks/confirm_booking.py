import asyncio

from adapters.celery_app import celery_app
from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import session_factory
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from domain.entities.booking import BookingStatus
from domain.ports.booking_confirmed_client import ConfirmError
from domain.ports.booking_repository import BookingNotFound


async def confirm_booking(booking_id: int) -> None:
    # TODO: Сделать, что бы сессия как то DI создавалась и закрывалась?
    async with session_factory() as session:
        repository = SQLAlchemyBookingRepository(session)
        bookings = await repository.find_by(id=booking_id, status=BookingStatus.PENDING)
        if not bookings:
            raise BookingNotFound()
        await StubBookingConfirmedClient().confirm(bookings[0])


@celery_app.task(bind=True, name="confirm_booking")
def confirm_booking_task(self, booking_id: int) -> None:
    try:
        asyncio.run(confirm_booking(booking_id))
    except ConfirmError as exc:
        raise self.retry(exc=exc, countdown=10) from exc
