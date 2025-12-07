from typing import Generic, TypeVar, Type, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotFoundError
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
        return self.return_type.model_validate(obj.__dict__, from_attributes=True)

    async def update(
            self,
            id: int,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            overwrite_relationships: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> InfoType:
        obj = await self.repo.update(
            id=id,
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            overwrite_relationships=overwrite_relationships,
            preloads=preloads,
        )
        return self.return_type.model_validate(obj.__dict__, from_attributes=True)

    async def delete(
            self,
            id_: int,
            database: AsyncSession,
            relationship_fields: list[str] | None = None,
    ) -> None:
        await self.repo.delete(
            id_=id_,
            database=database,
            relationship_fields=relationship_fields
        )

    async def get(self, filters: dict[str, Any], database: AsyncSession, preloads: list[str] | None = None) -> InfoType:
        objs = await self.repo.get(
            filters=filters,
            database=database,
            preloads=preloads
        )
        return [self.return_type.model_validate(x.__dict__, from_attributes=True) for x in objs]

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
        result["items"] = [self.return_type.model_validate(x.__dict__, from_attributes=True) for x in result["items"]]
        return PaginationResponse.model_validate(result)
