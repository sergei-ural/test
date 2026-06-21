import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.models import BookingModel
from domain.entities.booking import Booking, BookingStatus
from domain.ports.booking_repository import BookingAlreadyExist, BookingNotFound, FindBookingMoreThanOne
from tests.factories import make_booking


async def get_all_bookings(session: AsyncSession) -> list[Booking]:
    return [
        Booking(id=m.id, datetime=m.datetime, name=m.name, service_type=m.service_type, status=m.status)
        for m in await session.scalars(select(BookingModel).order_by(BookingModel.id))
    ]


async def test_add(booking_repository: SQLAlchemyBookingRepository, session: AsyncSession) -> None:
    booking = make_booking(id=None)

    await booking_repository.add(booking)

    assert isinstance(booking.id, int)
    assert await get_all_bookings(session) == [make_booking(id=booking.id)]


async def test_add_duplicate_raises(booking_repository: SQLAlchemyBookingRepository, session: AsyncSession) -> None:
    booking = make_booking()
    await booking_repository.add(booking)

    with pytest.raises(BookingAlreadyExist):
        await booking_repository.add(make_booking())

    assert isinstance(booking.id, int)
    assert await get_all_bookings(session) == [make_booking(id=booking.id)]


async def test_remove_existing(booking_repository: SQLAlchemyBookingRepository, session: AsyncSession) -> None:
    booking = make_booking()
    await booking_repository.add(booking)

    await booking_repository.remove(booking)

    assert await get_all_bookings(session) == []


async def test_remove_not_found_raises(booking_repository: SQLAlchemyBookingRepository, session: AsyncSession) -> None:
    with pytest.raises(BookingNotFound):
        await booking_repository.remove(make_booking(id=999))

    assert await get_all_bookings(session) == []


async def test_get_by_existing(booking_repository: SQLAlchemyBookingRepository) -> None:
    booking = make_booking()
    await booking_repository.add(booking)

    got = await booking_repository.get_by(id=booking.id)

    assert got == booking


async def test_get_by_not_found_raises(booking_repository: SQLAlchemyBookingRepository) -> None:
    with pytest.raises(BookingNotFound):
        await booking_repository.get_by(id=999)


async def test_get_by_more_than_one_raises(booking_repository: SQLAlchemyBookingRepository) -> None:
    booking1 = make_booking(name="same", service_type="service_type1")
    booking2 = make_booking(name="same", service_type="service_type2")
    await booking_repository.add(booking1)
    await booking_repository.add(booking2)

    with pytest.raises(FindBookingMoreThanOne):
        await booking_repository.get_by(name="same")


async def test_find_all(booking_repository: SQLAlchemyBookingRepository) -> None:
    booking1 = make_booking(name="name1", status=BookingStatus.PENDING)
    booking2 = make_booking(name="name2", status=BookingStatus.CONFIRMED)
    booking3 = make_booking(name="name3", status=BookingStatus.FAILED)
    await booking_repository.add(booking1)
    await booking_repository.add(booking2)
    await booking_repository.add(booking3)

    got = await booking_repository.find_by()

    assert got == [booking1, booking2, booking3]


async def test_find_by_status(booking_repository: SQLAlchemyBookingRepository) -> None:
    booking1 = make_booking(name="name1", status=BookingStatus.PENDING)
    booking2 = make_booking(name="name2", status=BookingStatus.CONFIRMED)
    await booking_repository.add(booking1)
    await booking_repository.add(booking2)

    got = await booking_repository.find_by(status=BookingStatus.CONFIRMED)

    assert got == [booking2]


async def test_find_by_name(booking_repository: SQLAlchemyBookingRepository) -> None:
    booking1 = make_booking(name="name1", status=BookingStatus.PENDING)
    booking2 = make_booking(name="name2", status=BookingStatus.CONFIRMED)
    await booking_repository.add(booking1)
    await booking_repository.add(booking2)

    got = await booking_repository.find_by(name="name1")

    assert got == [booking1]


async def test_find_by_service_type(booking_repository: SQLAlchemyBookingRepository) -> None:
    booking1 = make_booking(name="name1", service_type="service_type1")
    booking2 = make_booking(name="name2", service_type="service_type2")
    await booking_repository.add(booking1)
    await booking_repository.add(booking2)

    got = await booking_repository.find_by(service_type="service_type1")

    assert got == [booking1]


async def test_find_by_pagination(booking_repository: SQLAlchemyBookingRepository) -> None:
    booking1 = make_booking(name="name1")
    booking2 = make_booking(name="name2")
    booking3 = make_booking(name="name3")
    await booking_repository.add(booking1)
    await booking_repository.add(booking2)
    await booking_repository.add(booking3)

    assert await booking_repository.find_by(offset=1, limit=1) == [booking2]
