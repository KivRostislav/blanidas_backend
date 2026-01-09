from math import ceil
from typing import Generic, TypeVar, Type

from sqlalchemy.ext.asyncio import AsyncSession

from src.sorting import Sorting
from src.pagination import PaginationResponse, Pagination
from src.repository import CRUDRepository

ModelType = TypeVar("ModelType")
InfoType = TypeVar("InfoType")
class GenericServices(Generic[ModelType, InfoType]):
    def __init__(self, repository: CRUDRepository[ModelType], return_type: Type[InfoType]):
        self.repo = repository
        self.return_type = return_type

    async def paginate(
            self,
            database: AsyncSession,
            pagination: Pagination,
            filters: str | None = None,
            preloads: list[str] | None = None,
            sorting: Sorting | None = None,
    ) -> PaginationResponse[InfoType]:
        result = await self.repo.fetch(
            database=database,
            limit=pagination.limit,
            offset=pagination.offset,
            filters=filters,
            preloads=preloads,
            sorting=sorting,
        )

        models = [self.return_type.model_validate(x.__dict__, from_attributes=True) for x in result[0]]
        total_pages = max(1, ceil(result[1] / pagination.limit))
        return PaginationResponse.model_validate({
            "items": models,
            "total": result[1],
            "page": pagination.page,
            "pages": total_pages,
            "limit": pagination.limit,
            "has_next": pagination.page < total_pages,
            "has_prev": pagination.page > 1,
        })

    async def create(self, data: dict, database: AsyncSession, preloads: list[str] | None = None) -> InfoType:
        obj = await self.repo.create(data=data, database=database, preloads=preloads)
        return self.return_type.model_validate(obj.__dict__, from_attributes=True)

    async def update(self, id_: int, data: dict, database: AsyncSession, preloads: list[str] | None = None) -> InfoType:
        obj = await self.repo.update(id_=id_, data=data, database=database, preloads=preloads)
        return self.return_type.model_validate(obj.__dict__, from_attributes=True)

    async def delete(self, id_: int, database: AsyncSession) -> int:
        return await self.repo.delete(id_=id_, database=database)

    async def get(self, id_: int, database: AsyncSession, preloads: list[str] | None = None) -> InfoType:
        result = await self.repo.get(id_=id_, database=database, preloads=preloads)
        return self.return_type.model_validate(result.__dict__, from_attributes=True)