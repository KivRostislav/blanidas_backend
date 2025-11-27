from typing import Type, Callable

from httpx import AsyncClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Relationship

from src.database import BaseDatabaseModel
from src.pagination import Pagination, PaginationResponse


async def general_test_list_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    model_type: Type,
    orm_factory: SQLAlchemyFactory,
    relationships: dict[str, Callable[[], BaseDatabaseModel]] | None = None,
    preloads: list[str] | None = None,
    page: int = 1,
    limit: int = 8,
    total: int = 0,
):
    relationships = {} if relationships is None else relationships
    preloads = [] if preloads is None else preloads

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

    models = [orm_factory.build(id=None) for _ in range(total)]
    relationship_objs = {}
    for field, factory in relationships.items():
        assert hasattr(model_type, field), f"{field} not found in relationships"
        relationship_obj = factory()
        relationship_objs[field] = relationship_obj

    for relationship_obj in relationship_objs.values():
        if type(relationship_obj) is list:
            session.add_all(relationship_obj)
            continue
        session.add(relationship_obj)
    await session.flush()

    for model in models:
        for field, obj in relationship_objs.items():
            if type(obj) is list:
                setattr(model, field, obj)
                continue
            assert hasattr(model, field + "_id"), f"{field + '_id'} not found in relationships"
            setattr(model, field + "_id", obj.id)

    session.add_all(models)
    await session.flush()

    pagination = Pagination(page=page, limit=limit)
    response = await client.get(url, params=pagination.model_dump())
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["items"]) == total - ((page - 1) * limit)

    # Only for the first-level children
    if relationships:
        for item in response_data["items"]:
            for field in preloads:
                assert field in item, f"{field} not returned in response"
                if type(item[field]) is list:
                    assert len(item[field]) == len(relationship_objs[field])
                    continue
                assert "id" in item[field], f"{field} not returned in response"
                assert item[field]["id"] == relationship_objs[field].id, f"{field} not returned in response"


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
    relationships: dict[str, Callable[[], BaseDatabaseModel]] | None = None,
    preloads: list[str] | None = None,
):
    relationships = {} if relationships is None else relationships
    preloads = [] if preloads is None else preloads
    create_obj = create_factory.build()

    relationship_objs = {}
    for field, factory in relationships.items():
        assert hasattr(model_type, field), f"{field} not found in relationships"
        relationship_obj = factory()
        relationship_objs[field] = relationship_obj

    for relationship_obj in relationship_objs.values():
        if type(relationship_obj) is list:
            session.add_all(relationship_obj)
            continue
        session.add(relationship_obj)
    await session.flush()

    for field, obj in relationship_objs.items():
        if type(obj) is list:
            assert hasattr(create_obj, field + "_ids"), f"{field + '_id'} not found in relationships"
            setattr(create_obj, field + "_ids", [x.id for x in obj])
            continue
        assert hasattr(create_obj, field + "_id"), f"{field + '_id'} not found in relationships"
        setattr(create_obj, field + "_id", obj.id)

    obj_data = create_obj.model_dump()
    response = await client.post(url, json=obj_data)
    assert response.status_code == 200

    # Only for the first-level children
    if relationships:
        response_data = response.json()
        for field in preloads:
            assert field in response_data, f"{field} not returned in response"
            if type(response_data[field]) is list:
                assert len(response_data[field]) == len(relationship_objs[field])
                continue
            assert "id" in response_data[field], f"{field} not returned in response"
            assert response_data[field]["id"] == relationship_objs[field].id, f"{field} not returned in response"

    obj = (await session.execute(select(model_type))).scalars().first()
    assert obj is not None

    for attr, obj in relationship_objs.items():
        create_obj_copy = create_obj.model_copy()
        if type(obj) is list:
            setattr(create_obj_copy, attr + "_ids", [99999999])
        else:
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
    relationships: dict[str, Callable[[], BaseDatabaseModel]] | None = None,
    preloads: list[str] | None = None,
):
    relationships = {} if relationships is None else relationships
    preloads = [] if preloads is None else preloads
    update_obj = update_factory.build()

    payload = update_obj.model_dump()
    response = await client.put(url, json=payload)
    assert response.status_code == 404

    relationship_objs = {}
    for field, factory in relationships.items():
        assert hasattr(model_type, field), f"{field} not found in relationships"
        relationship_obj = factory()
        relationship_objs[field] = relationship_obj

    for relationship_obj in relationship_objs.values():
        if type(relationship_obj) is list:
            session.add_all(relationship_obj)
            continue
        session.add(relationship_obj)
    await session.flush()

    for field, obj in relationship_objs.items():
        if type(obj) is list:
            assert hasattr(update_obj, field + "_ids"), f"{field + '_id'} not found in relationships"
            setattr(update_obj, field + "_ids", [x.id for x in obj])
            print([x.id for x in obj])
            continue
        assert hasattr(update_obj, field + "_id"), f"{field + '_id'} not found in relationships"
        setattr(update_obj, field + "_id", obj.id)
        print(obj.id)

    orm_obj = orm_factory.build()
    session.add(orm_obj)
    await session.flush()

    payload = update_obj.model_dump()
    payload["id"] = orm_obj.id

    response = await client.put(url, json=payload)
    print(response.status_code, response.json())
    assert response.status_code == 200

    # Only for the first-level children
    if relationships:
        response_data = response.json()
        for field in preloads:
            assert field in response_data, f"{field} not returned in response"
            if type(response_data[field]) is list:
                assert len(response_data[field]) == len(relationship_objs[field])
                continue
            assert hasattr(response_data[field], "id"), f"{field} not returned in response {response_data}"
            assert response_data[field]["id"] == relationship_objs[field].id, f"{field} not returned in response"

    for attr, obj in relationship_objs.items():
        update_obj_copy = update_obj.model_copy()
        if type(obj) is list:
            setattr(update_obj_copy, attr + "_ids", [99999999])
        else:
            setattr(update_obj_copy, attr + "_id", 99999999)

        response = await client.put(url, json=update_obj_copy.model_dump())
        assert response.status_code == 400

    stmt = select(model_type).where(model_type.id == orm_obj.id)
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