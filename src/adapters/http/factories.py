from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.tasks.confirm_booking import CeleryTaskManager
from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import session_factory
from adapters.stub_booking_confirmed_client import StubBookingConfirmedClient
from domain.application_services.booking import BookingServiceApp
from domain.ports.booking_repository import BookingRepository
from domain.use_cases.create_booking import CreateBookingUseCase


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


async def get_booking_repository(
    session: AsyncSession = Depends(get_session),
) -> BookingRepository:
    return SQLAlchemyBookingRepository(session)


async def get_booking_service(
    session: AsyncSession = Depends(get_session),
) -> BookingServiceApp:
    return BookingServiceApp(
        SQLAlchemyBookingRepository(session),
        StubBookingConfirmedClient(),
        CeleryTaskManager(),
    )


async def get_create_booking_use_case(
    session: AsyncSession = Depends(get_session),
) -> CreateBookingUseCase:
    repository = SQLAlchemyBookingRepository(session)
    return CreateBookingUseCase(
        booking_service=BookingServiceApp(
            repository,
            StubBookingConfirmedClient(),
            CeleryTaskManager(),
        ),
        repository=repository,
    )
