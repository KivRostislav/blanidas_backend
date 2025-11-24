
import pytest
import pytest_asyncio

from typing import Generator

from httpx import AsyncClient, ASGITransport
from polyfactory.pytest_plugin import register_fixture

from src.main import app

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import BaseDatabaseModel, get_db_session

import tests.factories
from tests.factories.institution_type import InstitutionTypeUpdateFactory, InstitutionTypeCreateFactory, InstitutionTypeORMFactory

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

register_fixture(InstitutionTypeCreateFactory)
register_fixture(InstitutionTypeUpdateFactory)
register_fixture(InstitutionTypeORMFactory)

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(BaseDatabaseModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(BaseDatabaseModel.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def session(engine):
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session

@pytest_asyncio.fixture(scope="module")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.fixture(autouse=True)
def overwrite_dependencies(session):
    app.dependency_overrides[get_db_session] = lambda: session
    yield
    app.dependency_overrides.clear()
