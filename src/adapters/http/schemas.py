from datetime import datetime

from pydantic import BaseModel, field_validator

from domain.entities.booking import Booking, BookingStatus


class CreateBookingRequest(BaseModel):
    datetime: datetime
    name: str
    service_type: str

    @field_validator("datetime")
    @classmethod
    def datetime_must_not_be_in_past(cls, value: datetime) -> datetime:
        if value < datetime.now(value.tzinfo):
            raise ValueError("must not be in the past")
        return value


class CreateBookingResponse(BaseModel):
    id: int


class BookingResponse(BaseModel):
    id: int
    datetime: datetime
    name: str
    service_type: str
    status: BookingStatus

    @classmethod
    def from_booking(cls, booking: Booking) -> "BookingResponse":
        return cls(
            id=booking.id,
            datetime=booking.datetime,
            name=booking.name,
            service_type=booking.service_type,
            status=booking.status,
        )


class BookingListResponse(BaseModel):
    items: list[BookingResponse]
    total: int
    offset: int
    limit: int
