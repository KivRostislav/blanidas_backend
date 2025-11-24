from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.equipment_model.schemas import EquipmentModel
from tests.factories.equipment_model import EquipmentModelORMFactory, EquipmentModelUpdateFactory, \
    EquipmentModelCreateFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint


@pytest.mark.asyncio
async def test_get_equipment_model_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_model_orm_factory: EquipmentModelORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        orm_factory=equipment_model_orm_factory,
        url="/equipment-models/",
        page=3,
        limit=8,
        total=20,
    )



@pytest.mark.asyncio
async def test_create_equipment_model_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_model_create_factory: EquipmentModelCreateFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        create_factory=equipment_model_create_factory,
        url="/equipment-models/",
        model=EquipmentModel,
    )

@pytest.mark.asyncio
async def test_update_equipment_model_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_model_orm_factory: EquipmentModelORMFactory,
        equipment_model_update_factory: EquipmentModelUpdateFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        orm_factory=equipment_model_orm_factory,
        update_factory=equipment_model_update_factory,
        url="/equipment-models/",
        model=EquipmentModel,
    )


@pytest.mark.asyncio
async def test_delete_equipment_model_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_model_orm_factory: EquipmentModelORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=equipment_model_orm_factory,
        url="/equipment-models/{0}",
        model=EquipmentModel,
    )


