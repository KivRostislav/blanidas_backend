from typing import TypeVar
from sqlalchemy import and_
from sqlalchemy.orm import InstrumentedAttribute

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
    joins = {}

    for raw_key, value in filters.items():
        if value is None:
            continue

        parts = raw_key.split("__")

        if parts[-1] in OPERATORS:
            op = parts.pop()
        else:
            op = "eq"

        operator_func = OPERATORS.get(op)
        if not operator_func:
            continue

        current_model = model
        attr = None

        for part in parts:
            if not hasattr(current_model, part):
                attr = None
                break

            attr = getattr(current_model, part)

            if isinstance(attr, InstrumentedAttribute) and hasattr(attr.property, "mapper"):
                if attr not in joins:
                    stmt = stmt.join(attr)
                    joins[attr] = True
                current_model = attr.property.mapper.class_
            else:
                current_model = None

        if attr is not None and current_model is None:
            conditions.append(operator_func(attr, value))

    if conditions:
        stmt = stmt.where(and_(*conditions))

    return stmt
