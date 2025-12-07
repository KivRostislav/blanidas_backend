from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.institution_type.schemas import InstitutionType
from src.supplier.schemas import Supplier
from tests.factories.institution_type import InstitutionTypeCreateFactory, InstitutionTypeUpdateFactory, InstitutionTypeORMFactory
from tests.factories.supplier import SupplierORMFactory, SupplierCreateFactory, SupplierUpdateFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint

api_url = "/api/suppliers/"

@pytest.mark.asyncio
async def test_get_supplier_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        supplier_orm_factory: SupplierORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=Supplier,
        orm_factory=supplier_orm_factory,
        url=api_url,
        page=3,
        limit=8,
        total=20,
    )

@pytest.mark.asyncio
async def test_create_supplier_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        supplier_create_factory: SupplierCreateFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        create_factory=supplier_create_factory,
        url=api_url,
        model_type=Supplier,
    )

@pytest.mark.asyncio
async def test_update_supplier_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        supplier_orm_factory: SupplierORMFactory,
        supplier_update_factory: SupplierUpdateFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        orm_factory=supplier_orm_factory,
        update_factory=supplier_update_factory,
        url=api_url,
        model_type=Supplier,
    )

@pytest.mark.asyncio
async def test_delete_supplier_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        supplier_orm_factory: SupplierORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=supplier_orm_factory,
        url=f"{api_url}{{0}}",
        model=Supplier,
    )


