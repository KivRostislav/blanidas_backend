from typing import Type, Callable

from httpx import AsyncClient
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Relationship

from src.database import BaseDatabaseModel
from src.equipment_category.schemas import EquipmentCategory
from src.equipment_model.schemas import EquipmentModel
from src.institution.schemas import Institution
from src.institution_type.schemas import InstitutionType
from src.manufacturer.schemas import Manufacturer
from src.pagination import Pagination, PaginationResponse

FactoryType = Callable[[], BaseDatabaseModel]
RelationshipFactoryValueType = FactoryType | list[FactoryType] | "RelationshipFactoryType"
RelationshipFactoryType = dict[str, RelationshipFactoryValueType]

async def build_related_recursive(session: AsyncSession, rel_def: RelationshipFactoryValueType):
    if isinstance(rel_def, list):
        objs = []
        for item in rel_def:
            objs.append(await build_related_recursive(session, item))
        return objs

    if isinstance(rel_def, dict):
        assert "self" in rel_def, "Nested relationship dict must contain 'self'"
        obj = rel_def["self"]()

        session.add(obj)
        await session.flush()

        for field, sub_rel in rel_def.items():
            if field == "self":
                continue

            child = await build_related_recursive(session, sub_rel)

            if isinstance(child, list):
                setattr(obj, field, child)
                continue
            assert hasattr(obj, field + "_id"), f"{field} not found in relationships"
            setattr(obj, field + "_id", child.id)

        await session.flush()
        return obj

    if callable(rel_def):
        obj = rel_def()
        session.add(obj)
        await session.flush()
        return obj

    raise TypeError(f"Unsupported relationship definition: {rel_def}")

async def general_test_list_endpoint(
    client: AsyncClient,
    session: AsyncSession,
    url: str,
    model_type: Type,
    orm_factory: SQLAlchemyFactory,
    relationships: RelationshipFactoryType | None = None,
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
        relationship_objs[field] = await build_related_recursive(session, factory)

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
    relationships: RelationshipFactoryType | None = None,
    preloads: list[str] | None = None,
):
    relationships = {} if relationships is None else relationships
    preloads = [] if preloads is None else preloads
    create_obj = create_factory.build()

    relationship_objs = {}
    for field, factory in relationships.items():
        assert hasattr(model_type, field), f"{field} not found in relationships"
        relationship_objs[field] = await build_related_recursive(session, factory)

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

    async def check_preloads(response_data, rel_objs):
        for field, value in rel_objs.items():
            if field not in response_data:
                continue
            resp_val = response_data[field]
            if isinstance(value, list):
                assert isinstance(resp_val, list)
                assert len(resp_val) == len(value)
                for r_item, o_item in zip(resp_val, value):
                    if hasattr(o_item, "__dict__"):
                        await check_preloads(r_item, {k: getattr(o_item, k) for k in preloads if hasattr(o_item, k)})
            else:
                assert "id" in resp_val
                assert resp_val["id"] == value.id
                await check_preloads(resp_val, {k: getattr(value, k) for k in preloads if hasattr(value, k)})

    if relationships:
        response_data = response.json()
        await check_preloads(response_data, relationship_objs)

    obj = (await session.execute(select(model_type))).scalars().first()
    assert obj is not None

    async def check_invalid_ids(obj, rel_objs):
        for field, value in rel_objs.items():
            obj_copy = obj.model_copy()
            if isinstance(value, list):
                setattr(obj_copy, field + "_ids", [99999999])
            else:
                setattr(obj_copy, field + "_id", 99999999)
            response = await client.post(url, json=obj_copy.model_dump())
            assert response.status_code == 400
            if isinstance(value, list):
                for v in value:
                    await check_invalid_ids(v, {k: getattr(v, k) for k in preloads if hasattr(v, k)})
            else:
                await check_invalid_ids(value, {k: getattr(value, k) for k in preloads if hasattr(value, k)})

    await check_invalid_ids(create_obj, relationship_objs)


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
        relationship_objs[field] = await build_related_recursive(session, factory)

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
            continue
        assert hasattr(update_obj, field + "_id"), f"{field + '_id'} not found in relationships"
        setattr(update_obj, field + "_id", obj.id)

    orm_obj = orm_factory.build()
    session.add(orm_obj)
    await session.flush()

    payload = update_obj.model_dump()
    payload["id"] = orm_obj.id

    response = await client.put(url, json=payload)
    print(response.status_code, response.json())
    assert response.status_code == 200

    async def check_preloads(response_data, rel_objs):
        for field, value in rel_objs.items():
            if field not in response_data:
                continue
            resp_val = response_data[field]
            if isinstance(value, list):
                assert isinstance(resp_val, list)
                assert len(resp_val) == len(value)
                for r_item, o_item in zip(resp_val, value):
                    if hasattr(o_item, "__dict__"):
                        await check_preloads(r_item, {k: getattr(o_item, k) for k in preloads if hasattr(o_item, k)})
            else:
                assert "id" in resp_val
                assert resp_val["id"] == value.id
                await check_preloads(resp_val, {k: getattr(value, k) for k in preloads if hasattr(value, k)})

    if relationships:
        response_data = response.json()
        await check_preloads(response_data, relationship_objs)

    async def check_invalid_ids(obj, rel_objs):
        for field, value in rel_objs.items():
            obj_copy = obj.model_copy()
            if isinstance(value, list):
                setattr(obj_copy, field + "_ids", [99999999])
            else:
                setattr(obj_copy, field + "_id", 99999999)
            response = await client.put(url, json=obj_copy.model_dump())
            assert response.status_code == 400
            if isinstance(value, list):
                for v in value:
                    await check_invalid_ids(v, {k: getattr(v, k) for k in preloads if hasattr(v, k)})
            else:
                await check_invalid_ids(value, {k: getattr(value, k) for k in preloads if hasattr(value, k)})

    await check_invalid_ids(update_obj, relationship_objs)

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