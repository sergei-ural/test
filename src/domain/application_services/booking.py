from datetime import datetime

from domain.entities.booking import Booking, BookingStatus
from domain.ports.booking_confirmed_client import BookingConfirmedClient
from domain.ports.booking_repository import BookingNotFound, BookingRepository
from domain.ports.task_manager import TaskManager


class BookingServiceApplication:
    def __init__(
        self,
        repository: BookingRepository,
        client: BookingConfirmedClient,
        task_manager: TaskManager,
    ) -> None:
        self._booking_repository = repository
        self._booking_confirmed_client = client
        self._task_manager = task_manager

    async def create(
        self,
        datetime_: datetime,
        name: str,
        service_type: str,
    ) -> Booking:
        booking = Booking.new(
            datetime_=datetime_,
            name=name,
            service_type=service_type,
        )
        await self._booking_repository.add(booking)
        self._task_manager.confirm(booking.id)
        return booking

    async def confirm(self, booking_id: int) -> None:
        # TODO: Сделать get?
        bookings = await self._booking_repository.find_by(id=booking_id, status=BookingStatus.PENDING)
        if not bookings:
            raise BookingNotFound
        booking = bookings[0]
        await self._booking_confirmed_client.confirm(booking)
        booking.status = BookingStatus.CONFIRMED
        await self._booking_repository.save(booking)
