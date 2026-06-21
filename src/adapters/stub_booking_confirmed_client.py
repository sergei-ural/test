import random

from domain.entities.booking import Booking
from domain.ports.booking_confirmed_client import BookingConfirmedClient, ConfirmError


class StubBookingConfirmedClient(BookingConfirmedClient):
    async def confirm(self, booking: Booking) -> None:
        if random.random() < 0.15:
            raise ConfirmError()
        return None
