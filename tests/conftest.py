import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import create_db_engine
from adapters.persistence.models import Base, BookingModel
from adapters.settings import settings


# TODO: Разделить на фикстуру с движком и сессию.
@pytest.fixture
async def session(mocker) -> AsyncSession:
    engine = create_db_engine(settings.database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    mocker.patch("adapters.persistence.database.session_factory", session_factory)
    async with session_factory() as db_session:
        await db_session.execute(delete(BookingModel))
        await db_session.commit()
        yield db_session
    await engine.dispose()


@pytest.fixture
def booking_repository(session: AsyncSession) -> SQLAlchemyBookingRepository:
    return SQLAlchemyBookingRepository(session)


@pytest.fixture
def patch_random(mocker, request):
    return mocker.patch("adapters.stub_booking_confirmed_client.random.random", return_value=request.param)
