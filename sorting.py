from enum import Enum

from pydantic import BaseModel

class SortOrder(str, Enum):
    ascending = "asc"
    descending = "desc"

class Sorting(BaseModel):
    order: SortOrder
    order_by: str = SortOrder.ascending

