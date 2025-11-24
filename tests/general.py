from typing import Callable, Any, Type

from httpx import AsyncClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.pagination import Pagination, PaginationResponse


async def general_test_list_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    orm_factory: SQLAlchemyFactory,
    page: int = 1,
    limit: int = 8,
    total: int = 0
):
    pagination = Pagination(page=page, limit=limit)
    response = await client.get(url, params=pagination.model_dump())
    assert response.status_code == 200
    assert response.json() == PaginationResponse(
        page=page,
        limit=limit,
        total=0,
        items=[],
        pages=1,
        has_next=False,
        has_prev=True,
    ).model_dump()

    models = [orm_factory.build() for _ in range(total)]
    session.add_all(models)
    await session.commit()

    pagination = Pagination(page=page, limit=limit)
    response = await client.get(url, params=pagination.model_dump())
    assert response.status_code == 200
    response_data = response.json()
    response_data["items"] = []
    expected_pages = (total + limit - 1) // limit
    assert response_data["page"] == expected_pages
    assert response_data == PaginationResponse(
        page=page,
        limit=limit,
        total=total,
        items=[],
        pages=expected_pages,
        has_next=page < expected_pages,
        has_prev=page > 1
    ).model_dump()

async def general_test_create_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    create_factory: ModelFactory,
    model: Type
):
    obj_data = create_factory.build().model_dump()
    response = await client.post(url, json=obj_data)
    assert response.status_code == 200

    obj = (await session.execute(select(model))).scalars().first()
    assert obj is not None

    response = await client.post(url, json=obj_data)
    assert response.status_code == 400


async def general_test_update_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    model: Type,
    orm_factory: SQLAlchemyFactory,
    update_factory: ModelFactory,
):
    payload = update_factory.build().model_dump()
    response = await client.put(url, json=payload)
    assert response.status_code == 404

    obj = orm_factory.build()
    session.add(obj)
    await session.commit()
    payload["id"] = obj.id
    response = await client.put(url, json=payload)
    assert response.status_code == 200

    stmt = select(model).where(model.id == obj.id)
    db_obj = (await session.execute(stmt)).scalars().first()
    assert db_obj is not None


async def general_test_delete_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    model: Type,
    orm_factory: SQLAlchemyFactory
):
    response = await client.delete(url.format(0))
    assert response.status_code == 404

    obj = orm_factory.build()
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    response = await client.delete(url.format(obj.id))
    assert response.status_code == 200

    stmt = select(model).where(model.id == obj.id)
    db_obj = (await session.execute(stmt)).scalars().first()
    assert db_obj is None