from datetime import datetime

from sqlalchemy import func, select, update
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
        async with self._session as session:
            session.add(model)
            try:
                await session.commit()
            except IntegrityError as exc:
                raise BookingAlreadyExist from exc
            booking.id = model.id

    async def update(self, booking: Booking) -> None:
        async with self._session as session:
            result = await session.execute(
                update(BookingModel)
                .where(BookingModel.id == booking.id)
                .values(
                    datetime=booking.datetime,
                    name=booking.name,
                    service_type=booking.service_type,
                    status=booking.status,
                )
            )
            if result.rowcount == 0:
                raise BookingNotFound()
            await session.commit()

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
            raise FindBookingMoreThanOne()
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
        query = self._apply_filters(
            select(BookingModel),
            id=id,
            datetime_=datetime_,
            name=name,
            service_type=service_type,
            status=status,
        )
        query = query.order_by(BookingModel.id).offset(offset).limit(limit)
        async with self._session as session:
            return [
                Booking(
                    id=model.id,
                    datetime=model.datetime,
                    name=model.name,
                    service_type=model.service_type,
                    status=model.status,
                )
                for model in (await session.scalars(query)).all()
            ]

    async def count_by(
        self,
        id: int | None = None,
        datetime_: datetime | None = None,
        name: str | None = None,
        service_type: str | None = None,
        status: BookingStatus | None = None,
    ) -> int:
        query = self._apply_filters(
            select(func.count()).select_from(BookingModel),
            id=id,
            datetime_=datetime_,
            name=name,
            service_type=service_type,
            status=status,
        )
        return await self._session.scalar(query) or 0

    def _apply_filters(
        self,
        query,
        id: int | None = None,
        datetime_: datetime | None = None,
        name: str | None = None,
        service_type: str | None = None,
        status: BookingStatus | None = None,
    ):
        for column, value in (
            (BookingModel.id, id),
            (BookingModel.datetime, datetime_),
            (BookingModel.name, name),
            (BookingModel.service_type, service_type),
            (BookingModel.status, status),
        ):
            if value is not None:
                query = query.where(column == value)
        return query
