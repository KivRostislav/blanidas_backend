from typing import Generic, TypeVar, Type, Sequence

from fastapi import HTTPException, status
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.pagination import Pagination
from src.utils import build_relation, validate_unique_fields, validate_foreign_keys

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

class CRUDRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def paginate(
            self,
            database: AsyncSession,
            pagination: Pagination,
            filters: dict | None = None,
            preload: Sequence[str] | None = None,
    ) -> dict:
        stmt = select(self.model)
        if filters:
            stmt = apply_filters(stmt, self.model, filters)

        if preload:
            options = build_relation(self.model, preload)
            stmt = stmt.options(*options)

        count_stmt = select(func.count()).select_from(self.model)
        if filters:
            count_stmt = apply_filters(stmt, self.model, filters)

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

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            unique: Sequence[str] | None = None,
            foreign_keys: Sequence[str] | None = None,
            many_to_many: Sequence[str] | None = None,
            preload: Sequence[str] | None = None,
    ) -> ModelType:
        if unique and not (await validate_unique_fields(self.model, data, database, unique)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{self.model.__name__} with the same fields already exists"
            )

        if foreign_keys and not (await validate_foreign_keys(self.model, data, database, foreign_keys)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some foreign keys does not exist"
            )
        if not many_to_many:
            many_to_many = []

        data_copy = data.copy()
        for x in many_to_many:
            del data_copy[x + "_ids"]

        obj = self.model(**data_copy)
        for field in many_to_many:
            rel = self.model.__mapper__.relationships[field]
            rel_model = rel.mapper.class_

            ids = data[field + "_ids"]

            result = await database.execute(
                select(rel_model).where(rel_model.id.in_(ids))
            )
            related_objs = result.scalars().all()
            getattr(obj, field).extend(related_objs)

        database.add(obj)
        await database.commit()
        if not preload:
            return obj

        preload_options = build_relation(self.model, preload)
        stmt = select(self.model).options(*preload_options).where(self.model.id == obj.id)
        result = await database.execute(stmt)
        return result.scalars().first()

    async def update(
        self,
        id: int,
        data: dict,
        database: AsyncSession,
        unique: Sequence[str] | None = None,
        foreign_keys: Sequence[str] | None = None,
        many_to_many: Sequence[str] | None = None,
        preload: Sequence[str] = (),
    ) -> ModelType:
        if unique and not await validate_unique_fields(self.model, data, database, unique, exclude_ids=[id]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{self.model.__name__} with id the same fields already exists"
            )
        if not many_to_many:
            many_to_many = []
        options = build_relation(self.model, many_to_many)
        stmt = select(self.model).options(*options).where(self.model.id == id)
        result = await database.execute(stmt)
        obj = result.scalars().first()

        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} does not exist"
            )

        if foreign_keys and not (await validate_foreign_keys(self.model, data, database, foreign_keys)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some foreign keys does not exist"
            )

        for field, value in data.items():
            if hasattr(obj, field) and field not in many_to_many:
                setattr(obj, field, value)

        for field in many_to_many:
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

        for field in many_to_many:
            if field not in preload:
                setattr(obj, field, [])
        if not preload:
            return obj

        options = build_relation(self.model, preload)
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
