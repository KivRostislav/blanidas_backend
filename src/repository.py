import logging
from collections.abc import Callable
from typing import Generic, TypeVar, Type, Any

from fastapi import HTTPException, status
from fastapi.logger import logger
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import UniqueConstraintError, ForeignKeyNotFoundError, NotFoundError
from src.filter import apply_filters
from src.pagination import Pagination
from src.utils import build_relation, validate_uniqueness, validate_relationships

from math import ceil

ModelType = TypeVar("ModelType")
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

        count_stmt = select(func.count(self.model.id)).select_from(self.model)
        if filters:
            count_stmt = self.filter_callback(count_stmt, self.model, filters)

        total = (await database.execute(count_stmt)).scalar() or 0
        if pagination.limit >= 0:
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
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> ModelType:
        unique_fields = unique_fields or []
        relationship_fields = relationship_fields or []
        preloads = preloads or []

        if not await validate_uniqueness(self.model, data, database, unique_fields):
            raise UniqueConstraintError()

        if not await validate_relationships(self.model, data, database, relationship_fields):
            raise ForeignKeyNotFoundError()

        many_to_many: list[str] = []
        data_copy = data.copy()

        for field in relationship_fields:
            ids_key = f"{field}_ids"
            if ids_key in data_copy:
                del data_copy[ids_key]
                many_to_many.append(field)

        obj = self.model(**data_copy)

        for field in many_to_many:
            rel = self.model.__mapper__.relationships[field]
            rel_model = rel.mapper.class_

            ids = data[f"{field}_ids"]
            result = await database.execute(
                select(rel_model).where(rel_model.id.in_(ids))
            )
            related_objs = result.scalars().all()

            getattr(obj, field).extend(related_objs)

        database.add(obj)
        await database.commit()

        preload_options = build_relation(self.model, preloads)
        stmt = (
            select(self.model)
            .options(*preload_options)
            .where(self.model.id == obj.id)
        )

        result = await database.execute(stmt)
        return result.scalars().first()

    async def create_many(
            self,
            data_list: list[dict],
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> list[ModelType]:
        unique_fields = unique_fields or []
        relationship_fields = relationship_fields or []
        preloads = preloads or []

        created_objects = []
        for data in data_list:
            if not await validate_uniqueness(self.model, data, database, unique_fields):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{self.model.__name__} with the same fields already exists"
                )

            if not await validate_relationships(self.model, data, database, relationship_fields):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Some foreign keys do not exist"
                )

            many_to_many = []
            data_copy = data.copy()

            for field in relationship_fields:
                if field + "_ids" in data_copy:
                    many_to_many.append(field)
                    del data_copy[field + "_ids"]

            obj = self.model(**data_copy)
            database.add(obj)
            created_objects.append((obj, many_to_many, data))

        await database.commit()
        for obj, many_to_many, original_data in created_objects:
            for field in many_to_many:
                rel = self.model.__mapper__.relationships[field]
                rel_model = rel.mapper.class_

                ids = original_data[field + "_ids"]
                result = await database.execute(
                    select(rel_model).where(rel_model.id.in_(ids))
                )
                related_objs = result.scalars().all()
                getattr(obj, field).extend(related_objs)

        await database.commit()
        preload_options = build_relation(self.model, preloads)

        ids = [obj.id for obj, _, _ in created_objects]

        stmt = (
            select(self.model)
            .options(*preload_options)
            .where(self.model.id.in_(ids))
        )

        result = await database.execute(stmt)
        return list(result.scalars().all())

    async def update(
            self,
            id_: int,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            overwrite_relationships: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> ModelType:
        unique_fields = unique_fields or []
        relationship_fields = relationship_fields or []
        overwrite_relationships = overwrite_relationships or []
        preloads = preloads or []

        if not await validate_uniqueness(self.model, data, database, unique_fields, exclude_ids=[id_]):
            raise UniqueConstraintError()

        options = build_relation(self.model, relationship_fields)
        stmt = select(self.model).options(*options).where(self.model.id == id_)
        result = await database.execute(stmt)
        obj = result.scalars().first()

        if not obj:
            raise NotFoundError(self.model.__name__, id_)

        if not await validate_relationships(self.model, data, database, relationship_fields):
            raise ForeignKeyNotFoundError()

        for field, raw_value in data.items():
            if field.endswith("_ids"):
                rel_field = field[:-4]
                if rel_field not in self.model.__mapper__.relationships:
                    continue

                rel = self.model.__mapper__.relationships[rel_field]
                rel_model = rel.mapper.class_

                ids = raw_value if isinstance(raw_value, list) else [raw_value]
                result = await database.execute(select(rel_model).where(rel_model.id.in_(ids)))
                related_objs = result.scalars().all()

                rel_list = getattr(obj, rel_field)
                if rel_field in overwrite_relationships:
                    rel_list.clear()
                    await database.flush()

                existing_ids = {o.id for o in rel_list}
                for o in related_objs:
                    if o.id not in existing_ids:
                        rel_list.append(o)
                continue

            if hasattr(obj, field):
                setattr(obj, field, raw_value)

        database.add(obj)
        await database.commit()
        await database.refresh(obj)

        if preloads:
            options = build_relation(self.model, preloads)
            stmt = select(self.model).options(*options).where(self.model.id == obj.id)
            result = await database.execute(stmt)
            return result.scalars().first()

        return obj


    async def delete(
            self,
            id_: int,
            database: AsyncSession,
            relationship_fields: list[str] | None = None,
    ) -> None:
        relationship_fields = relationship_fields or []

        options = build_relation(self.model, relationship_fields)
        stmt = select(self.model).options(*options).where(self.model.id == id_)
        result = await database.execute(stmt)
        obj = result.scalars().first()

        if not obj:
            raise NotFoundError(self.model.__name__, id_)

        await database.delete(obj)
        await database.commit()

    async def delete_many(self, ids: list[int], database: AsyncSession) -> None:
        stmt = select(self.model).where(self.model.id.in_(ids))
        result = await database.execute(stmt)
        objs = result.scalars().all()
        for obj in objs:
            await database.delete(obj)
        await database.commit()

    async def get(
            self,
            filters: dict[str, Any],
            database: AsyncSession,
            preloads: list[str] | None = None,
    ) -> ModelType:
        preloads = preloads or []
        stmt = select(self.model).options(*build_relation(self.model, preloads))
        if filters:
            stmt = self.filter_callback(stmt, self.model, filters)

        return (await database.execute(stmt)).unique().scalars().first()

    async def list(
            self,
            filters: dict[str, Any],
            database: AsyncSession,
            preloads: list[str] | None = None,
    ) -> list[ModelType]:
        preloads = preloads or []
        stmt = select(self.model).options(*build_relation(self.model, preloads))
        if filters:
            stmt = self.filter_callback(stmt, self.model, filters)

        objs = (await database.execute(stmt)).unique().scalars().all() or []
        return list(objs)

