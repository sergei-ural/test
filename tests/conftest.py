from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from pytest import FixtureRequest
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from adapters.persistence.booking_repository import SQLAlchemyBookingRepository
from adapters.persistence.database import engine
from adapters.persistence.models import Base


@pytest_asyncio.fixture()
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture()
async def session(init_db: None) -> AsyncSession:
    session_ = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)()
    yield session_
    await session_.close()


@pytest.fixture
def booking_repository(session: AsyncSession) -> SQLAlchemyBookingRepository:
    return SQLAlchemyBookingRepository(session)


@pytest.fixture
def patch_random(mocker: MockerFixture, request: FixtureRequest) -> MagicMock:
    return mocker.patch("adapters.stub_booking_confirmed_client.random.random", return_value=request.param)
