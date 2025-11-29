from collections.abc import Callable
from typing import Generic, TypeVar, Type, Sequence, Any

from fastapi import HTTPException, status
from sqlalchemy import select, and_, func, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.pagination import Pagination
from src.utils import build_relation, validate_unique_fields, validate_relationships

from math import ceil

ModelType = TypeVar("ModelType")

OPERATORS = {
    "eq": lambda col, val: col == val,
    "ne": lambda col, val: col != val,
    "lt": lambda col, val: col < val,
    "lte": lambda col, val: col <= val,
    "gt": lambda col, val: col > val,
    "gte": lambda col, val: col >= val,
    "like": lambda col, val: col.like(f"%{val}%"),
    "ilike": lambda col, val: col.ilike(f"%{val}%"),
    "in": lambda col, val: col.in_(val),
    "notin": lambda col, val: ~col.in_(val),
    "isnull": lambda col, val: col.is_(None) if val else col.is_not(None),
}


def apply_filters(stmt, model, filters: dict):
    conditions = []

    for key, value in filters.items():
        if value is None:
            continue

        if "__" in key:
            field_name, op = key.split("__", 1)
        else:
            field_name, op = key, "eq"

        if not hasattr(model, field_name):
            continue

        col = getattr(model, field_name)
        operator_func = OPERATORS.get(op)
        if operator_func:
            conditions.append(operator_func(col, value))

    if conditions:
        stmt = stmt.where(and_(*conditions))

    return stmt

FilterCallback = Callable[[Select[Any], Type[ModelType], dict[str, Any]], Select[Any]]


class CRUDRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], filter_callback: FilterCallback = apply_filters):
        self.model = model
        self.filter_callback = filter_callback

    async def paginate(
            self,
            database: AsyncSession,
            pagination: Pagination,
            filters: dict | None = None,
            preloads: list[str] | None = None,
    ) -> dict:
        preloads = preloads if preloads else []
        filters = filters if filters else {}

        stmt = select(self.model)
        stmt = self.filter_callback(stmt, self.model, filters)

        if preloads:
            options = build_relation(self.model, preloads)
            stmt = stmt.options(*options)

        count_stmt = select(func.count()).select_from(self.model)
        if filters:
            count_stmt = self.filter_callback(count_stmt, self.model, filters)

        total = (await database.execute(count_stmt)).scalar_one()
        stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await database.execute(stmt)
        items = result.unique().scalars().all()

        total_pages = max(1, ceil(total / pagination.limit))
        return {
            "items": items,
            "total": total,
            "page": pagination.page,
            "pages": total_pages,
            "limit": pagination.limit,
            "has_next": pagination.page < total_pages,
            "has_prev": pagination.page > 1,
        }

    async def get(
            self,
            id: int,
            database: AsyncSession,
            preloads: list[str] | None = None,
    ) -> ModelType:
        preloads = preloads if preloads else []

        stmt = select(self.model).options(*build_relation(self.model, preloads)).where(self.model.id == id)
        obj = (await database.execute(stmt)).scalars().first()
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} does not exist"
            )

        return obj

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> ModelType:
        unique_fields = unique_fields if unique_fields else []
        relationship_fields = relationship_fields if relationship_fields else []
        preloads = preloads if preloads else []

        if not await validate_unique_fields(self.model, data, database, unique_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{self.model.__name__} with the same fields already exists"
            )

        if not await validate_relationships(self.model, data, database, relationship_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some foreign keys does not exist"
            )

        many_to_many = []
        data_copy = data.copy()
        for field in relationship_fields:
            if field + "_ids" not in data_copy:
                continue

            del data_copy[field + "_ids"]
            many_to_many.append(field)

        obj = self.model(**data_copy)
        for field in many_to_many:
            rel = self.model.__mapper__.relationships[field]
            rel_model = rel.mapper.class_

            ids = data[field + "_ids"]
            result = await database.execute(select(rel_model).where(rel_model.id.in_(ids)))
            related_objs = result.scalars().all()
            getattr(obj, field).extend(related_objs)

        database.add(obj)
        await database.commit()

        preload_options = build_relation(self.model, preloads)
        stmt = select(self.model).options(*preload_options).where(self.model.id == obj.id)
        result = await database.execute(stmt)
        return result.scalars().first()

    async def update(
        self,
        id: int,
        data: dict,
        database: AsyncSession,
        unique_fields: list[str] | None = None,
        relationship_fields: list[str] | None = None,
        preloads: list[str] | None = None,
    ) -> ModelType:
        unique_fields = unique_fields if unique_fields else []
        relationship_fields = relationship_fields if relationship_fields else []
        preloads = preloads if preloads else []

        if not await validate_unique_fields(self.model, data, database, unique_fields, exclude_ids=[id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{self.model.__name__} with id the same fields already exists"
            )

        options = build_relation(self.model, relationship_fields)
        stmt = select(self.model).options(*options).where(self.model.id == id)
        result = await database.execute(stmt)
        obj = result.scalars().first()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} does not exist"
            )

        if not await validate_relationships(self.model, data, database, relationship_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some foreign keys does not exist"
            )

        for field, value in data.items():
            if not hasattr(obj, field):
                continue

            if not isinstance(getattr(obj, field), list):
                setattr(obj, field, value)
                continue

            rel = self.model.__mapper__.relationships[field]
            rel_model = rel.mapper.class_

            ids = data[field + "_ids"]

            result = await database.execute(
                select(rel_model).where(rel_model.id.in_(ids))
            )
            related_objs = result.scalars().all()
            setattr(obj, field, related_objs)

        database.add(obj)
        await database.commit()

        for relationship_filed in relationship_fields:
            if isinstance(getattr(obj, relationship_filed), list) and relationship_filed not in preloads:
                setattr(obj, relationship_filed, [])

        if not preloads:
            return obj

        options = build_relation(self.model, preloads)
        stmt = select(self.model).options(*options).where(self.model.id == obj.id)
        result = await database.execute(stmt)
        return result.scalars().first()

    async def delete(self, id: int, database: AsyncSession) -> None:
        stmt = select(self.model).where(self.model.id == id)
        result = await database.execute(stmt)
        obj = result.scalars().first()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} does not exist"
            )

        await database.delete(obj)
        await database.commit()
