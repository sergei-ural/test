import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from adapters.persistence.booking_repository import SqlAlchemyBookingRepository
from adapters.persistence.database import create_db_engine
from adapters.persistence.models import Base


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_db_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db_session:
        yield db_session
    await engine.dispose()


@pytest.fixture
def booking_repository(session: AsyncSession) -> SqlAlchemyBookingRepository:
    return SqlAlchemyBookingRepository(session)
