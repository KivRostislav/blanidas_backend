from typing import TypeVar, Generic, Sequence

from pydantic import BaseModel


class Pagination(BaseModel):
    page: int = 1
    limit: int = 8

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


ItemModelType = TypeVar("ItemModelType", bound=BaseModel)
class PaginationResponse(BaseModel, Generic[ItemModelType]):
    page: int
    limit: int
    total: int
    pages: int
    items: list[ItemModelType]
    has_next: bool
    has_prev: bool
