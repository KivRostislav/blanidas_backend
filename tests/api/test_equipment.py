from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.equipment.schemas import Equipment
from tests.factories.equipment import EquipmentORMFactory, EquipmentCreateFactory, EquipmentUpdateFactory
from tests.factories.equipment_category import EquipmentCategoryORMFactory
from tests.factories.equipment_model import EquipmentModelORMFactory
from tests.factories.institution import InstitutionORMFactory
from tests.factories.manufacturer import ManufacturerORMFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint


@pytest.mark.asyncio
async def test_get_equipment_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_orm_factory: EquipmentORMFactory,
        institution_orm_factory: InstitutionORMFactory,
        equipment_model_orm_factory: EquipmentModelORMFactory,
        equipment_category_orm_factory: EquipmentCategoryORMFactory,
        manufacturer_orm_factory: ManufacturerORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=Equipment,
        preload={
            "institution": institution_orm_factory,
            "equipment_model": equipment_model_orm_factory,
            "equipment_category": equipment_category_orm_factory,
            "manufacturer": manufacturer_orm_factory,
        },
        orm_factory=equipment_orm_factory,
        url="/equipment/",
        page=3,
        limit=8,
        total=20,
    )


@pytest.mark.asyncio
async def test_create_equipment_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_create_factory: EquipmentCreateFactory,
        institution_orm_factory: InstitutionORMFactory,
        equipment_model_orm_factory: EquipmentModelORMFactory,
        equipment_category_orm_factory: EquipmentCategoryORMFactory,
        manufacturer_orm_factory: ManufacturerORMFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        model_type=Equipment,
        preload={
            "institution": institution_orm_factory,
            "equipment_model": equipment_model_orm_factory,
            "equipment_category": equipment_category_orm_factory,
            "manufacturer": manufacturer_orm_factory,
        },
        url="/equipment/",
        create_factory=equipment_create_factory,
    )

@pytest.mark.asyncio
async def test_update_equipment_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_update_factory: EquipmentUpdateFactory,
        equipment_orm_factory: EquipmentORMFactory,
        institution_orm_factory: InstitutionORMFactory,
        equipment_model_orm_factory: EquipmentModelORMFactory,
        equipment_category_orm_factory: EquipmentCategoryORMFactory,
        manufacturer_orm_factory: ManufacturerORMFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        model_type=Equipment,
        preload={
            "institution": institution_orm_factory,
            "equipment_model": equipment_model_orm_factory,
            "equipment_category": equipment_category_orm_factory,
            "manufacturer": manufacturer_orm_factory,
        },
        url="/equipment/",
        orm_factory=equipment_orm_factory,
        update_factory=equipment_update_factory,
    )

@pytest.mark.asyncio
async def test_delete_equipment_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        equipment_orm_factory: EquipmentORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=equipment_orm_factory,
        url="/equipment/{0}",
        model=Equipment,
    )
