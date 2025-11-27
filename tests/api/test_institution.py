from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest

from src.institution.schemas import Institution
from tests.factories.institution import InstitutionORMFactory, InstitutionCreateFactory, InstitutionUpdateFactory
from tests.factories.institution_type import InstitutionTypeORMFactory
from tests.general import general_test_list_endpoint, general_test_create_endpoint, general_test_delete_endpoint, \
    general_test_update_endpoint


@pytest.mark.asyncio
async def test_get_institution_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_orm_factory: InstitutionORMFactory,
        institution_type_orm_factory: InstitutionTypeORMFactory,
) -> None:
    await general_test_list_endpoint(
        client=client,
        session=session,
        model_type=Institution,
        relationships={
            "institution_type": institution_type_orm_factory.build,
        },
        preloads=["institution_type"],
        orm_factory=institution_orm_factory,
        url="/institutions/",
        page=3,
        limit=8,
        total=20,
    )

@pytest.mark.asyncio
async def test_create_institution_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_create_factory: InstitutionCreateFactory,
        institution_type_orm_factory: InstitutionTypeORMFactory,
) -> None:
    await general_test_create_endpoint(
        client=client,
        session=session,
        relationships={"institution_type": institution_type_orm_factory.build},
        preloads=["institution_type"],
        create_factory=institution_create_factory,
        url="/institutions/",
        model_type=Institution,
    )


@pytest.mark.asyncio
async def test_update_institution_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_orm_factory: InstitutionTypeORMFactory,
        institution_orm_factory: InstitutionORMFactory,
        institution_update_factory: InstitutionUpdateFactory,
) -> None:
    await general_test_update_endpoint(
        client=client,
        session=session,
        orm_factory=institution_orm_factory,
        update_factory=institution_update_factory,
        relationships={"institution_type": institution_type_orm_factory.build},
        preloads=["institution_type"],
        url="/institutions/",
        model_type=Institution,
    )

@pytest.mark.asyncio
async def test_delete_institution_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_orm_factory: InstitutionORMFactory,
) -> None:
    await general_test_delete_endpoint(
        client=client,
        session=session,
        orm_factory=institution_orm_factory,
        url="/institutions/{0}",
        model=Institution,
    )
