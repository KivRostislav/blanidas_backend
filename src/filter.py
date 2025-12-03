from typing import TypeVar

from sqlalchemy import and_

from src.database import BaseDatabaseModel

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

ModelType = TypeVar("ModelType", bound=BaseDatabaseModel)
def apply_filters(stmt, model: ModelType, filters: dict):
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
