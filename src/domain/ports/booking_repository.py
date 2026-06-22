from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.booking import Booking, BookingStatus


class BookingAlreadyExist(Exception):
    pass


class BookingNotFound(Exception):
    pass


class FindBookingMoreThanOne(Exception):
    pass


class BookingNotPending(Exception):
    pass


class BookingRepository(ABC):
    @abstractmethod
    async def add(self, booking: Booking) -> None:
        ...

    @abstractmethod
    async def update(self, booking: Booking) -> None:
        ...

    @abstractmethod
    async def get_by(
        self,
        id: int | None = None,
        datetime_: datetime | None = None,
        name: str | None = None,
        service_type: str | None = None,
        status: BookingStatus | None = None,
    ) -> Booking:
        ...

    @abstractmethod
    async def find_by(
        self,
        id: int | None = None,
        datetime_: datetime | None = None,
        name: str | None = None,
        service_type: str | None = None,
        status: BookingStatus | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> list[Booking]:
        ...

    @abstractmethod
    async def count_by(
        self,
        id: int | None = None,
        datetime_: datetime | None = None,
        name: str | None = None,
        service_type: str | None = None,
        status: BookingStatus | None = None,
    ) -> int:
        ...
