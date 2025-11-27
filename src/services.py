from typing import Generic, TypeVar, Type

from sqlalchemy.ext.asyncio import AsyncSession

from src.pagination import PaginationResponse
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
            unique: list[str] | None = None,
            foreign_keys: list[str] | None = None,
            many_to_many: list[str] | None = None,
            preload: list[str] | None = None,
    ) -> InfoType:
        obj = await self.repo.create(data, database, unique, foreign_keys, many_to_many, preload)
        print(obj)
        return self.return_type.model_validate(obj, from_attributes=True)

    async def update(
            self,
            id: int,
            data: dict,
            database: AsyncSession,
            unique: list[str] | None = None,
            foreign_keys: list[str] | None = None,
            many_to_many: list[str] | None = None,
            preload: list[str] | None = None,
    ) -> InfoType:
        obj = await self.repo.update(id, data, database, unique, foreign_keys, many_to_many, preload)
        return self.return_type.model_validate(obj, from_attributes=True)

    async def delete(self, id: int, database) -> None:
        await self.repo.delete(id, database)

    async def get(self, id: int, database, preload=None) -> InfoType:
        obj = await self.repo.get(database, id, preload)
        return self.return_type.model_validate(obj, from_attributes=True)

    async def list(self, database, pagination, filters=None, preload=None) -> PaginationResponse[InfoType]:
        result = await self.repo.paginate(database, pagination, filters=filters, preload=preload)
        result["items"] = [self.return_type.model_validate(x, from_attributes=True) for x in result["items"]]
        return PaginationResponse.model_validate(result, from_attributes=True)
