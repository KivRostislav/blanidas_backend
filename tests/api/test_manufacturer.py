from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.manufacturer.schemas import Manufacturer
from tests.factories.manufacturer import ManufacturerORMFactory, ManufacturerCreateFactory, ManufacturerUpdateFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint

api_url = "/api/manufacturers/"

@pytest.mark.asyncio
async def test_get_manufacturer_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        manufacturer_orm_factory: ManufacturerORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=Manufacturer,
        orm_factory=manufacturer_orm_factory,
        url=api_url,
        page=3,
        limit=8,
        total=20,
    )

@pytest.mark.asyncio
async def test_create_manufacturer_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        manufacturer_create_factory: ManufacturerCreateFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        create_factory=manufacturer_create_factory,
        url=api_url,
        model_type=Manufacturer,
    )

@pytest.mark.asyncio
async def test_update_manufacturer_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        manufacturer_orm_factory: ManufacturerORMFactory,
        manufacturer_update_factory: ManufacturerUpdateFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        orm_factory=manufacturer_orm_factory,
        update_factory=manufacturer_update_factory,
        url=api_url,
        model_type=Manufacturer,
    )


@pytest.mark.asyncio
async def test_delete_manufacturer_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        manufacturer_orm_factory: ManufacturerORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=manufacturer_orm_factory,
        url=f"{api_url}{{0}}",
        model=Manufacturer,
    )


