import dataclasses
from enum import Enum
from typing import Callable

from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute


class SortOrder(str, Enum):
    ascending = "asc"
    descending = "desc"

class Sorting(BaseModel):
    sort_order: SortOrder = SortOrder.ascending
    sort_by: str = ""

@dataclasses.dataclass
class SortingRelatedField:
    join: InstrumentedAttribute | None
    column: InstrumentedAttribute

SortingRelatedFieldsMap = dict[str, SortingRelatedField]
SortingCallback = Callable[[Select, Sorting], Select]
SortingWrapperCallback = Callable[[Select, Sorting, SortingRelatedFieldsMap], Select]

def apply_sorting_wrapper(callback: SortingWrapperCallback, related_fields: SortingRelatedFieldsMap) -> SortingCallback:
    def wrapper(stmt: Select, sorting: Sorting) -> Select:
        return callback(stmt, sorting, related_fields)
    return wrapper

def apply_sorting(stmt: Select, sorting: Sorting, related_fields: SortingRelatedFieldsMap) -> Select:
    if sorting.sort_by not in related_fields:
        return stmt

    related_field = related_fields[sorting.sort_by]
    if related_field is None:
        return stmt

    if related_field.join is not None:
        stmt = stmt.join(related_field.join)

    return stmt.order_by(related_field.column.desc() if sorting.sort_order == SortOrder.descending else related_field.column.asc())
