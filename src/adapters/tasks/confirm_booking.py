import asyncio

from tenacity import retry, retry_if_exception_type, wait_exponential

from adapters.celery_app import celery_app
from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import session_factory
from adapters.stub_booking_confirmed_client import StubBookingConfirmClient
from domain.application_services.booking import BookingServiceApp
from domain.ports.booking_confirmed_client import ConfirmError
from domain.ports.booking_repository import BookingNotFound
from domain.ports.task_manager import TaskManager


async def _run_confirm(booking_id: int) -> None:
    async with session_factory() as session:
        await BookingServiceApp(
            SQLAlchemyBookingRepository(session),
            StubBookingConfirmClient(),
            CeleryTaskManager(),
        ).confirm(booking_id)


# В рамках задачи считаем, что другие ошибки не умеем обрабатывать
@celery_app.task(name="confirm_booking")
@retry(retry=retry_if_exception_type(ConfirmError), wait=wait_exponential(multiplier=1, exp_base=2))
def confirm_booking_task(booking_id: int) -> None:
    try:
        asyncio.run(_run_confirm(booking_id))
    except BookingNotFound:
        # Тут в будущем можно положить отправку в sentry или что-то ещё,
        # но ретраить или падать, смысла нет.
        raise


class CeleryTaskManager(TaskManager):
    def confirm(self, booking_id: int) -> None:
        confirm_booking_task.delay(booking_id)
