from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.booking import Booking, BookingStatus
from domain.ports.booking_repository import (
    BookingAlreadyExist,
    BookingNotFound,
    BookingRepository,
    FindBookingMoreThanOne,
)
from adapters.persistence.models import BookingModel


class SQLAlchemyBookingRepository(BookingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, booking: Booking) -> None:
        model = BookingModel(
            datetime=booking.datetime,
            name=booking.name,
            service_type=booking.service_type,
            status=booking.status,
        )
        self._session.add(model)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            # TODO: Точно ли нужно явно делать rollback?
            await self._session.rollback()
            raise BookingAlreadyExist from exc
        booking.id = model.id

    async def remove(self, booking: Booking) -> None:
        result = await self._session.execute(delete(BookingModel).where(BookingModel.id == booking.id))
        if result.rowcount == 0:
            raise BookingNotFound
        await self._session.commit()

    async def save(self, booking: Booking) -> None:
        if booking.id is None:
            raise BookingNotFound

        model = await self._session.get(BookingModel, booking.id)
        if model is None:
            raise BookingNotFound

        model.datetime = booking.datetime
        model.name = booking.name
        model.service_type = booking.service_type
        model.status = booking.status
        await self._session.commit()

    async def get_by(
        self,
        id: int | None = None,
        datetime_: datetime | None = None,
        name: str | None = None,
        service_type: str | None = None,
        status: BookingStatus | None = None,
    ) -> Booking:
        bookings = await self.find_by(
            id=id,
            datetime_=datetime_,
            name=name,
            service_type=service_type,
            status=status,
            limit=2,
        )
        if not bookings:
            raise BookingNotFound()
        if len(bookings) > 1:
            raise FindBookingMoreThanOne
        return bookings[0]

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
        query = select(BookingModel)
        for column, value in (
            (BookingModel.id, id),
            (BookingModel.datetime, datetime_),
            (BookingModel.name, name),
            (BookingModel.service_type, service_type),
            (BookingModel.status, status),
        ):
            if value is not None:
                query = query.where(column == value)

        query = query.order_by(BookingModel.id).offset(offset).limit(limit)
        return [
            Booking(
                id=model.id,
                datetime=model.datetime,
                name=model.name,
                service_type=model.service_type,
                status=model.status,
            )
            for model in (await self._session.scalars(query)).all()
        ]
