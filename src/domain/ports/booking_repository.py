from abc import ABC, abstractmethod

from domain.entities.booking import Booking, BookingStatus


class BookingAlreadyExist(Exception):
    pass


class BookingNotFound(Exception):
    pass


class BookingRepository(ABC):
    @abstractmethod
    async def add(self, booking: Booking) -> Booking:
        ...

    @abstractmethod
    async def remove(self, booking: Booking) -> None:
        ...

    @abstractmethod
    async def find_by(
        self,
        *,
        id: int | None = None,
        name: str | None = None,
        service_type: str | None = None,
        status: BookingStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Booking]:
        ...
