from typing import Generic, TypeVar, Type, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.pagination import PaginationResponse, Pagination
from src.repository import CRUDRepository

ModelType = TypeVar("ModelType")
InfoType = TypeVar("InfoType")
class GenericServices(Generic[ModelType, InfoType]):
    def __init__(self, repository: CRUDRepository[ModelType], return_type: Type[InfoType]):
        self.repo = repository
        self.return_type = return_type

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> InfoType:
        obj = await self.repo.create(
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads,
        )
        return self.return_type.model_validate(obj, from_attributes=True)

    async def update(
            self,
            id: int,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> InfoType:
        obj = await self.repo.update(
            id=id,
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads,
        )
        return self.return_type.model_validate(obj, from_attributes=True)

    async def delete(self, id: int, database) -> None:
        await self.repo.delete(id, database)

    async def get(self, id: int, database: AsyncSession, preloads: list[str] | None = None) -> InfoType:
        obj = await self.repo.get(
            id=id,
            database=database,
            preloads=preloads
        )
        return self.return_type.model_validate(obj, from_attributes=True)

    async def list(
            self,
            database: AsyncSession,
            pagination: Pagination,
            filters: dict[str, Any] | Any = None,
            preloads: list[str] | None = None,
    ) -> PaginationResponse[InfoType]:
        result = await self.repo.paginate(
            database=database,
            pagination=pagination,
            filters=filters,
            preloads=preloads
        )
        result["items"] = [self.return_type.model_validate(x, from_attributes=True) for x in result["items"]]
        return PaginationResponse.model_validate(result, from_attributes=True)
