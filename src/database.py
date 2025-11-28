from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapper
from typing import Annotated

from .config import get_settings

class BaseDatabaseModel(DeclarativeBase):
    pass

engine = create_async_engine(get_settings().database_url, echo=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db_session():
    async with session_factory() as session:
        yield session

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]