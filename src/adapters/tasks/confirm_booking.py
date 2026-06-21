import asyncio

from adapters.celery_app import celery_app
from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import session_factory
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from domain.application_services.booking import BookingServiceApplication
from domain.ports.booking_confirmed_client import ConfirmError
from domain.ports.booking_repository import BookingNotFound


async def _run_confirm(booking_id: int) -> None:
    # TODO: Сделать, что бы сессия как то DI создавалась и закрывалась?
    async with session_factory() as session:
        await BookingServiceApplication(
            SQLAlchemyBookingRepository(session),
            StubBookingConfirmedClient(),
        ).confirm(booking_id)


@celery_app.task(bind=True, name="confirm_booking")
def confirm_booking_task(self, booking_id: int) -> None:
    try:
        asyncio.run(_run_confirm(booking_id))
    except BookingNotFound:
        # Тут в будущем можно положить отправку в sentry или что-то ещё,
        # но ретраить или падать, смысла нет.
        return None
    except ConfirmError as exc:
        raise self.retry(exc=exc, countdown=10) from exc
