from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.spare_part.schemas import SparePart
from tests.factories.equipment_model import EquipmentModelORMFactory
from tests.factories.institution import InstitutionORMFactory
from tests.factories.institution_type import InstitutionTypeORMFactory
from tests.factories.manufacturer import ManufacturerORMFactory
from tests.factories.spare_part import SparePartORMFactory, SparePartCreateFactory
from tests.factories.spare_part_category import SparePartCategoryORMFactory
from tests.factories.supplier import SupplierORMFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint

api_url = "/api/spare-parts/"

@pytest.mark.asyncio
async def test_get_spare_part_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        spare_part_orm_factory: SparePartORMFactory,
        institution_orm_factory: InstitutionORMFactory,
        institution_type_orm_factory: InstitutionTypeORMFactory,
        equipment_model_orm_factory: EquipmentModelORMFactory,
        spare_part_category_orm_factory: SparePartCategoryORMFactory,
        manufacturer_orm_factory: ManufacturerORMFactory,
        supplier_orm_factory: SupplierORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=SparePart,
        relationships={
            "institution": {
                "self": institution_orm_factory.build,
                "institution_type": institution_type_orm_factory.build
            },
            "compatible_models": [equipment_model_orm_factory.build] * 3,
            "spare_part_category": spare_part_category_orm_factory.build,
            "manufacturer": manufacturer_orm_factory.build,
            "supplier": supplier_orm_factory.build,
        },
        preloads=["institution", "compatible_models", "spare_part_category", "manufacturer", "supplier"],
        orm_factory=spare_part_orm_factory,
        url=api_url,
        page=3,
        limit=8,
        total=20,
    )

@pytest.mark.asyncio
async def test_create_spare_part_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        spare_part_create_factory: SparePartCreateFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        model_type=SparePart,
        preloads=["institution", "compatible_models", "spare_part_category", "manufacturer", "supplier"],
        url=api_url,
        create_factory=spare_part_create_factory,
    )
