from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.manufacturer.schemas import Manufacturer
from src.spare_part_category.schemas import SparePartCategory
from tests.factories.manufacturer import ManufacturerORMFactory, ManufacturerCreateFactory, ManufacturerUpdateFactory
from tests.factories.spare_part_category import SparePartCategoryORMFactory, SparePartCategoryCreateFactory, \
    SparePartCategoryUpdateFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint


@pytest.mark.asyncio
async def test_get_spare_part_category_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        spare_part_category_orm_factory: SparePartCategoryORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=SparePartCategory,
        orm_factory=spare_part_category_orm_factory,
        url="/spare-part-categories/",
        page=3,
        limit=8,
        total=20,
    )

@pytest.mark.asyncio
async def test_create_spare_part_category_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        spare_part_category_create_factory: SparePartCategoryCreateFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        create_factory=spare_part_category_create_factory,
        url="/spare-part-categories/",
        model_type=SparePartCategory,
    )

@pytest.mark.asyncio
async def test_update_spare_part_category_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        spare_part_category_orm_factory: SparePartCategoryORMFactory,
        spare_part_category_update_factory: SparePartCategoryUpdateFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        orm_factory=spare_part_category_orm_factory,
        update_factory=spare_part_category_update_factory,
        url="/spare-part-categories/",
        model_type=SparePartCategory,
    )


@pytest.mark.asyncio
async def test_delete_manufacturer_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        spare_part_category_orm_factory: SparePartCategoryORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=spare_part_category_orm_factory,
        url="/spare-part-categories/{0}",
        model=SparePartCategory,
    )


