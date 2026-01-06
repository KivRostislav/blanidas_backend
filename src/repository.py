from typing import Generic, TypeVar, Type

from sqlalchemy import select, func, inspect, insert, delete, update, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from src.sorting import Sorting, apply_sorting_wrapper, apply_sorting
from src.decorators import integrity_errors
from src.exceptions import DomainError, ErrorCode
from src.filters import apply_filters, apply_filters_wrapper
from src.sorting import SortingCallback
from src.utils import build_relation
from src.filters import FilterCallback, Filters


ModelType = TypeVar("ModelType")

class CRUDRepository(Generic[ModelType]):
    def __init__(
            self,
            model: Type[ModelType],
            filter_callback: FilterCallback = apply_filters_wrapper(apply_filters, {}),
            sorting_callback: SortingCallback = apply_sorting_wrapper(apply_sorting, {}),
    ):
        self.model = model
        self.filter_callback = filter_callback
        self.sorting_callback = sorting_callback

    async def fetch(
            self,
            database: AsyncSession,
            filters: Filters | None = None,
            preloads: list[str] | None = None,
            sorting: Sorting | None = None,
            offset: int | None = None,
            limit: int | None = None,
    ) -> tuple[list[ModelType], int]:
        filters = filters or {}
        preloads = preloads or []

        stmt = select(self.model)
        stmt = self.filter_callback(stmt, filters)

        if sorting:
            stmt = self.sorting_callback(stmt, sorting)

        if preloads:
            options = build_relation(self.model, preloads)
            stmt = stmt.options(*options)

        count_stmt = select(func.count(distinct(self.model.id))).select_from(self.model)
        if filters:
            count_stmt = self.filter_callback(count_stmt, filters)

        total = (await database.execute(count_stmt)).scalar() or 0

        if limit is not None and limit != -1:
            stmt = stmt.offset(offset or 0).limit(limit)

        result = await database.execute(stmt)
        items = result.unique().scalars().all()

        return list(items), total

    async def get(self, id_: int, database: AsyncSession, preloads: list[str] | None = None) -> ModelType | None:
        options = build_relation(self.model, preloads or [])
        stmt = select(self.model).options(*options).where(self.model.id == id_)
        return (await database.execute(stmt)).unique().scalars().first()

    @integrity_errors()
    async def create(self, data: dict, database: AsyncSession, preloads: list[str] | None = None) -> ModelType:
        preloads = preloads or []

        obj = self.model(**data)
        database.add(obj)
        await database.flush()

        association_inserts = []
        for field in inspect(self.model).relationships:
            if field.secondary is None:
                continue

            if field.key not in data:
                continue

            ids = data[field.key]
            left_col, right_col = list(field.secondary.c)

            association_inserts.extend([
                {left_col.name: obj.id, right_col.name: related_id} for related_id in ids
            ])

            if association_inserts:
                stmt = insert(field.secondary).values(association_inserts)
                await database.execute(stmt)

        await database.commit()

        preload_options = build_relation(self.model, preloads)
        stmt = (
            select(self.model)
            .options(*preload_options)
            .where(self.model.id == obj.id)
        )

        result = await database.execute(stmt)
        return result.scalars().first()

    @integrity_errors()
    async def update(self, id_: int, data: dict, database: AsyncSession, preloads: list[str] | None = None) -> ModelType:
        preloads = preloads or []

        rows = await database.execute(update(self.model).where(self.model.id == id_).values(data))
        if rows.rowcount == 0:
            raise DomainError(code=ErrorCode.not_entity, field="")

        association_inserts = []
        for field in inspect(self.model).relationships:
            if field.secondary is not None:
                continue

            if field.key not in data:
                continue

            ids = data[field.key]
            left_col, right_col = list(field.secondary.c)
            delete_stmt = (delete(field.secondary).where(left_col == id_))
            await database.execute(delete_stmt)

            association_inserts.extend([{left_col.name: id_, right_col.name: related_id} for related_id in ids])

            if association_inserts:
                stmt = insert(field.secondary).values(association_inserts)
                await database.execute(stmt)

        await database.commit()

        stmt = select(self.model)
        if preloads:
            options = build_relation(self.model, preloads)
            stmt = stmt.options(*options)

        stmt = stmt.where(self.model.id == id_).execution_options(populate_existing=True)
        result = await database.execute(stmt)
        return result.scalars().first()


    async def delete(self, id_: int, database: AsyncSession) -> int:
        stmt = delete(self.model).where(self.model.id == id_)
        result = await database.execute(stmt)
        if result.rowcount == 0:
            raise DomainError(code=ErrorCode.not_entity, field="")

        await database.commit()
        return id_

