from typing import Type

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
    model_type: Type,
    orm_factory: SQLAlchemyFactory,
    preload: dict[str, SQLAlchemyFactory] | None = None,
    page: int = 1,
    limit: int = 8,
    total: int = 0,
):
    pagination = Pagination(page=page, limit=limit)
    response = await client.get(url, params=pagination.model_dump())
    assert response.status_code == 200
    print(response.json())
    assert response.json() == PaginationResponse(
        page=page,
        limit=limit,
        total=0,
        items=[],
        pages=1,
        has_next=False,
        #dsaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        has_prev=True,
    ).model_dump()

    models = [orm_factory.build(id=None) for _ in range(total)]
    fk = {}
    if preload:
        for attr, factory in preload.items():
            if not hasattr(model_type, attr):
                continue
            fk[attr] = factory.build()
        for model in models:
            for attr, factory in fk.items():
                if not hasattr(model, attr + "_id") or not hasattr(factory, "id"):
                    continue
                setattr(model, attr + "_id", factory.id)

    for fk_obj in fk.values():
        session.add(fk_obj)

    await session.flush()

    for model in models:
        for attr, fk_obj in fk.items():
            setattr(model, f"{attr}_id", fk_obj.id)

    session.add_all(models)
    await session.flush()

    pagination = Pagination(page=page, limit=limit)
    response = await client.get(url, params=pagination.model_dump())
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["items"]) == total - ((page - 1) * limit)

    if preload:
        for item in response_data["items"]:
            for attr, fk_model in fk.items():
                assert attr in item, f"{attr} not returned in response"
                assert item[attr]["id"] == fk_model.id

    response_data["items"] = []
    expected_pages = (total + limit - 1) // limit

    assert response_data["pages"] == expected_pages
    assert response_data == PaginationResponse(
        page=page,
        limit=limit,
        total=total,
        items=[],
        pages=expected_pages,
        has_next=page < expected_pages,
        has_prev=page > 1
    ).model_dump()

    await session.rollback()

async def general_test_create_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    create_factory: ModelFactory,
    model_type: Type,
    preload: dict[str, SQLAlchemyFactory] | None = None,
):
    create_obj = create_factory.build()

    fk = {}
    if preload:
        for attr, factory in preload.items():
            if not hasattr(model_type, attr):
                continue
            fk_obj = factory.build()
            session.add(fk_obj)
            await session.flush()
            fk[attr] = fk_obj

    for attr, fk_obj in fk.items():
        if not hasattr(create_obj, attr + "_id") or not hasattr(fk_obj, "id"):
            continue
        setattr(create_obj, f"{attr}_id", fk_obj.id)

    obj_data = create_obj.model_dump()
    response = await client.post(url, json=obj_data)
    assert response.status_code == 200

    obj = (await session.execute(select(model_type))).scalars().first()
    assert obj is not None

    if preload:
        for attr in preload.keys():
            create_obj_copy = create_obj.model_copy()
            setattr(create_obj_copy, attr + "_id", 99999999)

            response = await client.post(url, json=create_obj_copy.model_dump())
            assert response.status_code == 400

    response = await client.post(url, json=obj_data)
    assert response.status_code == 400
    await session.rollback()


async def general_test_update_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    model_type: Type,
    orm_factory: SQLAlchemyFactory,
    update_factory: ModelFactory,
    preload: dict[str, SQLAlchemyFactory] | None = None,
):
    update_obj = update_factory.build()
    payload = update_obj.model_dump()
    response = await client.put(url, json=payload)
    assert response.status_code == 404

    fk = {}
    if preload:
        for attr, factory in preload.items():
            if not hasattr(model_type, attr):
                continue
            fk[attr] = factory.build()

    obj = orm_factory.build()
    for attr, factory in fk.items():
        if not hasattr(update_obj, attr + "_id") or not hasattr(factory, "id"):
            continue
        setattr(update_obj, attr + "_id", factory.id)

    for preload_obj in fk.values():
        session.add(preload_obj)

    session.add(obj)
    await session.flush()
    payload = update_obj.model_dump()
    payload["id"] = obj.id
    response = await client.put(url, json=payload)
    print(response.status_code, payload)
    assert response.status_code == 200

    if preload:
        for attr in preload.keys():
            old_value = getattr(update_obj, attr + "_id")
            setattr(update_obj, attr + "_id", old_value + 1)
            obj_data = update_obj.model_dump()
            response = await client.put(url, json=obj_data)
            assert response.status_code == 400
            setattr(update_obj, attr + "_id", old_value)

    stmt = select(model_type).where(model_type.id == obj.id)
    db_obj = (await session.execute(stmt)).scalars().first()
    assert db_obj is not None

    await session.rollback()


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
    await session.flush()

    response = await client.delete(url.format(obj.id))
    print(response.status_code)
    assert response.status_code == 200

    stmt = select(model).where(model.id == obj.id)
    db_obj = (await session.execute(stmt)).scalars().first()
    assert db_obj is None

    await session.rollback()