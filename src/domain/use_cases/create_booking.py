from dataclasses import dataclass
from datetime import datetime

from domain.application_services.booking import BookingServiceApp
from domain.ports.booking_repository import BookingAlreadyExist, BookingNotFound, BookingRepository


@dataclass(frozen=True)
class CreateBookingResult:
    id: int
    created: bool


class CreateBookingUseCase:
    def __init__(self, booking_service: BookingServiceApp, repository: BookingRepository) -> None:
        self._booking_service = booking_service
        self._booking_repository = repository

    async def execute(self, datetime_: datetime, name: str, service_type: str) -> CreateBookingResult:
        try:
            booking = await self._booking_service.create(datetime_=datetime_, name=name, service_type=service_type)
        except BookingAlreadyExist:
            booking = await self._booking_repository.get_by(datetime_=datetime_, name=name, service_type=service_type)
            return CreateBookingResult(id=booking.id, created=False)
        return CreateBookingResult(id=booking.id, created=True)

