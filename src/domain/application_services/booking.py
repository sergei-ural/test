from datetime import datetime

from domain.entities.booking import Booking, BookingStatus
from domain.ports.booking_confirmed_client import BookingConfirmClient
from domain.ports.booking_repository import BookingNotPending, BookingRepository
from domain.ports.task_manager import TaskManager


class BookingServiceApp:
    def __init__(
        self,
        booking_repository: BookingRepository,
        booking_confirm_client: BookingConfirmClient,
        task_manager: TaskManager,
    ) -> None:
        self._booking_repository = booking_repository
        self._booking_confirmed_client = booking_confirm_client
        self._booking_task_manager = task_manager

    async def create(self, datetime_: datetime, name: str, service_type: str) -> Booking:
        booking = Booking.new(datetime_=datetime_, name=name, service_type=service_type)
        await self._booking_repository.add(booking)
        self._booking_task_manager.confirm(booking.id)
        return booking

    async def cancel(self, booking_id: int) -> None:
        booking = await self._booking_repository.get_by(id=booking_id)
        if booking.status != BookingStatus.PENDING:
            raise BookingNotPending()
        booking.status = BookingStatus.FAILED
        await self._booking_repository.update(booking)

    async def confirm(self, booking_id: int) -> None:
        booking = await self._booking_repository.get_by(id=booking_id, status=BookingStatus.PENDING)
        await self._booking_confirmed_client.confirm(booking)
        booking.status = BookingStatus.CONFIRMED
        await self._booking_repository.update(booking)
