from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.institution_type.schemas import InstitutionType
from tests.factories.institution_type import InstitutionTypeCreateFactory, InstitutionTypeUpdateFactory, InstitutionTypeORMFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint

api_url = "/api/institution-types/"

@pytest.mark.asyncio
async def test_get_institution_type_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_orm_factory: InstitutionTypeORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=InstitutionType,
        orm_factory=institution_type_orm_factory,
        url=api_url,
        page=3,
        limit=8,
        total=20,
    )

@pytest.mark.asyncio
async def test_create_institution_type_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_create_factory: InstitutionTypeCreateFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        create_factory=institution_type_create_factory,
        url=api_url,
        model_type=InstitutionType,
    )

@pytest.mark.asyncio
async def test_update_institution_type_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_orm_factory: InstitutionTypeORMFactory,
        institution_type_update_factory: InstitutionTypeUpdateFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        orm_factory=institution_type_orm_factory,
        update_factory=institution_type_update_factory,
        url=api_url,
        model_type=InstitutionType,
    )


@pytest.mark.asyncio
async def test_delete_institution_type_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_orm_factory: InstitutionTypeORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=institution_type_orm_factory,
        url=f"{api_url}{{0}}",
        model=InstitutionType,
    )


