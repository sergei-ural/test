from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import Pool


def create_db_engine(
    database_url: str,
    *,
    poolclass: type[Pool] | None = None,
) -> AsyncEngine:
    kwargs: dict = {}
    if poolclass is not None:
        kwargs["poolclass"] = poolclass
    return create_async_engine(database_url, **kwargs)


def to_sync_database_url(database_url: str) -> str:
    if database_url.startswith("sqlite+aiosqlite:"):
        return "sqlite:" + database_url.removeprefix("sqlite+aiosqlite:")
    return database_url
