import dataclasses
from enum import Enum
from typing import Callable, Any
from sqlalchemy import and_, Select, exists, select, ColumnElement
from sqlalchemy.orm import InstrumentedAttribute

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

@dataclasses.dataclass
class FilterRelatedField:
    column: InstrumentedAttribute

    use_exists: bool = False
    exists_from: Any | None = None
    join: InstrumentedAttribute | None = None
    exists_condition: Callable[[Any], InstrumentedAttribute] | None = None

FilterRelatedFieldsMap = dict[str, FilterRelatedField | None]
Filters =  dict[str, str | dict[str, str]]

FilterCallback = Callable[[Select, Filters], Select]
FilterWrapperCallback = Callable[[Select, Filters, FilterRelatedFieldsMap], Select]

def apply_filters_wrapper(filter_callback: FilterWrapperCallback, related_fields: FilterRelatedFieldsMap) -> FilterCallback:
    def wrapper(stmt: Select, filters: Filters) -> Select:
        return filter_callback(stmt, filters, related_fields)
    return wrapper

def apply_filters(stmt: Select, filters: Filters, related_fields: FilterRelatedFieldsMap) -> Select:
    conditions = []
    joins = set()

    for field, value in filters.items():
        related_field = related_fields.get(field)
        if not related_field or value is None:
            continue

        column = related_field.column
        if related_field.join is not None and not related_field.use_exists:
            if related_field.join not in joins:
                stmt = stmt.join(related_field.join)
                joins.add(related_field.join)

        if related_field.use_exists:
            subq = (
                select(1)
                .select_from(related_field.exists_from)
                .where(related_field.exists_condition)
                .correlate(None)
            )

            stmt = stmt.where(exists(subq))
            continue

        if isinstance(value, dict):
            condition = build_operator(column, value)
        else:
            condition = column == cast_filter_value(column, value)

        conditions.append(condition)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    return stmt

def get_filter_value(
    value: str | dict[str, str] | None,
    *,
    column: InstrumentedAttribute | None = None,
    enum: type[Enum] | None = None,
):
    if value is None:
        return None

    if isinstance(value, dict):
        operator, raw_value = next(iter(value.items()))
    else:
        operator, raw_value = "eq", value

    if operator == "isnull":
        return str(raw_value).lower() in ("1", "true", "yes")

    if enum is not None:
        try:
            return enum(raw_value).value
        except ValueError:
            raise ValueError(f"Invalid enum value '{raw_value}'")

    if column is not None:
        return cast_filter_value(column, raw_value)

    return raw_value


def build_operator(column, value_dict):
    operators = list(value_dict.keys())
    if not operators:
        return column

    op = operators[0]
    if op not in OPERATORS:
        return column

    raw_value = value_dict.get(op)

    value = cast_filter_value(column, raw_value)

    return OPERATORS[op](column, value)

def cast_filter_value(column: InstrumentedAttribute, value):
    if value is None:
        return None

    try:
        python_type = column.type.python_type
    except NotImplementedError:
        return value

    if isinstance(value, str) and "," in value:
        return [python_type(v) for v in value.split(",")]

    try:
        return python_type(value)
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid value '{value}' for column '{column.key}'"
        )
