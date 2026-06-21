import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import engine, session_factory
from adapters.persistence.models import Base


@pytest.fixture
async def session() -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    async with session_factory() as db_session:
        yield db_session
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
def booking_repository(session: AsyncSession) -> SQLAlchemyBookingRepository:
    return SQLAlchemyBookingRepository(session)


@pytest.fixture
def patch_random(mocker, request):
    return mocker.patch("adapters.stub_booking_confirmed_client.random.random", return_value=request.param)
