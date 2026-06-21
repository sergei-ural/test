from domain.entities.booking import BookingStatus
from domain.ports.booking_confirmed_client import BookingConfirmedClient
from domain.ports.booking_repository import BookingNotFound, BookingRepository


class BookingServiceApplication:
    def __init__(
        self,
        repository: BookingRepository,
        client: BookingConfirmedClient,
    ) -> None:
        self._booking_repository = repository
        self._booking_confirmed_client = client

    async def confirm(self, booking_id: int) -> None:
        # TODO: Сделать get?
        bookings = await self._booking_repository.find_by(id=booking_id, status=BookingStatus.PENDING)
        if not bookings:
            raise BookingNotFound
        booking = bookings[0]
        await self._booking_confirmed_client.confirm(booking)
        booking.status = BookingStatus.CONFIRMED
        await self._booking_repository.save(booking)
