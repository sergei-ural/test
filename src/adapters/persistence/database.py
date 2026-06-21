from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.pool import Pool

from adapters.settings import settings


def create_db_engine(
    database_url: str,
    poolclass: type[Pool] | None = None,
) -> AsyncEngine:
    kwargs: dict = {}
    if poolclass is not None:
        kwargs["poolclass"] = poolclass
    return create_async_engine(database_url, **kwargs)


engine = create_db_engine(settings.database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False)
