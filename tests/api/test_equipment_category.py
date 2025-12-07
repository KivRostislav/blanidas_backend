from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.equipment_category.schemas import EquipmentCategory
from tests.factories.equipment_category import EquipmentCategoryORMFactory, EquipmentCategoryUpdateFactory, \
    EquipmentCategoryCreateFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint

api_url = "/api/equipment-categories/"

@pytest.mark.asyncio
async def test_get_equipment_category_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_category_orm_factory: EquipmentCategoryORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=EquipmentCategory,
        orm_factory=equipment_category_orm_factory,
        url=api_url,
        page=3,
        limit=8,
        total=20,
    )

@pytest.mark.asyncio
async def test_create_equipment_category_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_category_create_factory: EquipmentCategoryCreateFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        create_factory=equipment_category_create_factory,
        url=api_url,
        model_type=EquipmentCategory,
    )

@pytest.mark.asyncio
async def test_update_equipment_category_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_category_orm_factory: EquipmentCategoryORMFactory,
        equipment_category_update_factory: EquipmentCategoryUpdateFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        orm_factory=equipment_category_orm_factory,
        update_factory=equipment_category_update_factory,
        url=api_url,
        model_type=EquipmentCategory,
    )


@pytest.mark.asyncio
async def test_delete_equipment_category_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_category_orm_factory: EquipmentCategoryORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=equipment_category_orm_factory,
        url=f"{api_url}{{0}}",
        model=EquipmentCategory,
    )


