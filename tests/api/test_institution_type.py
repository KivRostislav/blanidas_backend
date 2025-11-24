from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import pytest

from src.institution_type.schemas import InstitutionType
from src.pagination import Pagination, PaginationResponse
from tests.factories.institution_type import InstitutionTypeCreateFactory, InstitutionTypeUpdateFactory, InstitutionTypeORMFactory

@pytest.mark.asyncio
async def test_get_institution_type_list_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_orm_factory: InstitutionTypeORMFactory,
) -> None:

    pagination = Pagination(page=1, limit=8)
    response = await client.get("/institution-types/", params=pagination.model_dump())

    result = PaginationResponse(
        page=1,
        limit=8,
        total=0,
        items=[],
        pages=0,
        has_next=False,
        has_prev=False,
    )
    assert response.status_code == 200
    assert response.json() == result.model_dump()

    models = [institution_type_orm_factory.build() for x in range(20)]
    session.add_all(models)
    await session.commit()

    pagination = Pagination(page=3, limit=8)
    response = await client.get("/institution-types/", params=pagination.model_dump())

    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["items"]) == 4
    response_data["items"] = []
    result = PaginationResponse(
        page=3,
        limit=8,
        total=20,
        items=[],
        pages=3,
        has_next=False,
        has_prev=True,
    )
    print(response_data, result.model_dump())
    assert response_data == result.model_dump()



@pytest.mark.asyncio
async def test_create_institution_type_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_create_factory: InstitutionTypeCreateFactory,
) -> None:
    mock_create_institution_type = institution_type_create_factory.build()
    payload = mock_create_institution_type.model_dump()
    response = await client.post("/institution-types/", json=payload)

    assert response.status_code == 200

    obj = (await session.execute(select(InstitutionType))).scalars().first()
    assert obj is not None


    response = await client.post("/institution-types/", json=payload)
    assert response.status_code == 400
    assert response.json() == {"detail": f"{InstitutionType.__name__} with the same fields already exists"}

@pytest.mark.asyncio
async def test_update_institution_type_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_orm_factory: InstitutionTypeORMFactory,
        institution_type_update_factory: InstitutionTypeUpdateFactory,
) -> None:
    mock_update_institution_type = institution_type_update_factory.build()
    payload = mock_update_institution_type.model_dump()
    response = await client.put("/institution-types/", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": f"{InstitutionType.__name__} with id {mock_update_institution_type.id} does not exist"}


    mock_institution_type_orm_factory = institution_type_orm_factory.build()
    session.add(mock_institution_type_orm_factory)
    await session.commit()

    payload["id"] = mock_institution_type_orm_factory.id
    response = await client.put("/institution-types/", json=payload)
    assert response.status_code == 200

    stmt = select(InstitutionType).where(InstitutionType.id == mock_institution_type_orm_factory.id)
    obj = (await session.execute(stmt)).scalars().first()

    assert obj is not None
    assert obj.name == mock_update_institution_type.name


    response = await client.put("/institution-types/", json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_institution_type_endpoint(
        client: AsyncClient,
        session: AsyncSession,
        institution_type_orm_factory: InstitutionTypeORMFactory,
) -> None:
    response = await client.delete(f"/institution-types/{0}")

    assert response.status_code == 404

    mock_institution_type_orm_factory = institution_type_orm_factory.build()
    session.add(mock_institution_type_orm_factory)
    await session.commit()
    await session.refresh(mock_institution_type_orm_factory)

    response = await client.delete(f"/institution-types/{mock_institution_type_orm_factory.id}")
    assert response.status_code == 200

    stmt = select(InstitutionType).where(InstitutionType.id == mock_institution_type_orm_factory.id)
    obj = (await session.execute(stmt)).scalars().first()
    assert obj is None


