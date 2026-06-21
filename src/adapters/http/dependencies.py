from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.tasks.confirm_booking import CeleryTaskManager
from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import session_factory
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from domain.application_services.booking import BookingServiceApplication


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


async def get_booking_service(
    session: AsyncSession = Depends(get_session),
) -> BookingServiceApplication:
    return BookingServiceApplication(
        SQLAlchemyBookingRepository(session),
        StubBookingConfirmedClient(),
        CeleryTaskManager(),
    )
