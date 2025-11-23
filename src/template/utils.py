from typing import Any, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload, RelationshipProperty, class_mapper

from src.database import DatabaseSession

from sqlalchemy import select, or_

def deep_merge(a, b):
    for key, value in b.items():
        if isinstance(value, dict) and isinstance(a.get(key), dict):
            a = deep_merge(a[key], value)
        else:
            a[key] = value
    return a

def build_missing_none_map(missing_paths: set[str]):
    result = {}

    for path in missing_paths:
        parts = path.split(".")
        current = result

        for part in parts[:-1]:
            current = current.setdefault(part, {})

        current[parts[-1]] = None

    return result


def get_nested_relation_paths(model, prefix=None, visited=None):
    if visited is None:
        visited = set()

    mapper = class_mapper(model)
    paths = []

    for prop in mapper.relationships:
        if prop.direction.name != "MANYTOONE":
            continue

        rel_name = prop.key
        rel_model = prop.mapper.class_
        full_path = f"{prefix}.{rel_name}" if prefix else rel_name
        paths.append(full_path)

        if rel_model not in visited:
            visited.add(rel_model)
            paths.extend(
                get_nested_relation_paths(rel_model, prefix=full_path, visited=visited)
            )

    return paths

def build_loader(model, relations: list[str]):
    options = []

    for rel in relations:
        parts = rel.split(".")
        current_model = model

        loader = selectinload(getattr(current_model, parts[0]))
        current = loader

        for part in parts[1:]:
            rel_prop: RelationshipProperty = getattr(current_model, parts[0]).property
            current_model = rel_prop.mapper.class_
            current = current.subqueryload(getattr(current_model, part))
            parts = parts[1:]

        options.append(current)

    return options

async def validate_unique_fields(
        unique_fields: list[str],
        model_type: Type,
        data: dict[str, Any],
        database: DatabaseSession,
        current_model_id: int | None = None,
) -> None:
    conditions = [getattr(model_type, field) == data[field] for field in unique_fields if field in data]
    if conditions:
        stmt = select(model_type).where(or_(*conditions))
        if current_model_id:
            stmt = stmt.where(model_type.id != current_model_id)
        result = (await database.execute(stmt)).scalars().first()
        if result:
            for field in unique_fields:
                if hasattr(result, field) and getattr(result, field) == data.get(field):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{model_type.__name__} with {field}={data[field]} already exists"
                    )

async def validate_foreign_keys(
        database: DatabaseSession,
        data: dict[str, Any],
        foreign_key_map: dict[str, type],
) -> None:
    fk_by_model = {}
    for field, value in data.items():
        if field in foreign_key_map:
            fk_by_model.setdefault(foreign_key_map[field], []).append((field, value))

    for fk_model, field_values in fk_by_model.items():
        fk_ids = {fk_value for _, fk_value in field_values}
        stmt = select(fk_model).where(fk_model.id.in_(fk_ids))
        existing_objs = (await database.execute(stmt)).scalars().all()
        existing_ids = {obj.id for obj in existing_objs}

        for field, fk_value in field_values:
            if fk_value not in existing_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{fk_model.__name__} for {field} with id {fk_value} does not exist"
                )