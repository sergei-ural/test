from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncEngine

from adapters.settings import settings


def make_async_engine() -> AsyncEngine:
    return create_async_engine(settings.database_url, echo=False, poolclass=NullPool)

engine = make_async_engine()
session_factory = async_sessionmaker(engine, expire_on_commit=False)
