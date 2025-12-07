from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated

from .config import get_settings


class BaseDatabaseModel(DeclarativeBase):
    __abstract__ = True

engine = create_async_engine(get_settings().database_url)
session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

async def get_db_session():
    async with session_factory() as session:
        yield session

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]