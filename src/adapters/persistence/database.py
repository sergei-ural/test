from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import Pool

from adapters.settings import settings


def create_db_engine(
    database_url: str,
    *,
    poolclass: type[Pool] | None = None,
) -> AsyncEngine:
    kwargs: dict = {}
    if poolclass is not None:
        kwargs["poolclass"] = poolclass
    return create_async_engine(database_url, **kwargs)


engine = create_db_engine(settings.database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


# TODO:А разве нельзя всё делать на одном драйвере асинхронном с алхимией?
def to_sync_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite:"):
        return "sqlite:" + database_url.removeprefix("sqlite+aiosqlite:")
    if database_url.startswith("postgresql+asyncpg:"):
        return database_url.replace("postgresql+asyncpg:", "postgresql+psycopg2:", 1)
    return database_url
