from abc import ABC, abstractmethod

from domain.entities.booking import Booking


class ConfirmError(Exception):
    pass


class BookingConfirmClient(ABC):
    @abstractmethod
    async def confirm(self, booking: Booking) -> None:
        ...
