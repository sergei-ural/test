import datetime
from dataclasses import dataclass
from enum import StrEnum


class BookingStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class Booking:
    datetime: datetime.datetime
    name: str
    service_type: str
    status: BookingStatus
    id: int | None = None

    @staticmethod
    def new(datetime_: datetime.datetime, name: str, service_type: str) -> "Booking":
        return Booking(
            datetime=datetime_,
            name=name,
            service_type=service_type,
            status=BookingStatus.PENDING,
        )
