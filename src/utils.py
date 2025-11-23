from typing import Type, Any

from sqlalchemy import Sequence, or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


def build_relation(model_type: Type, preload: Sequence[str]) -> list[Any]:
    options = []
    for rel in preload:
        parts = rel.split(".")
        loader = joinedload(getattr(model_type, parts[0]))
        current_loader = loader
        current_model = model_type

        for part in parts[1:]:
            next_model = getattr(current_model, part).property.mapper.class_
            current_loader = current_loader.joinedload(part)
            current_model = next_model

        options.append(current_loader)

    return options

async def validate_foreign_keys(
        model_type: Type,
        data: dict,
        database: AsyncSession,
        foreign_keys: Sequence[str],
) -> bool:
    for fk in foreign_keys:
        parts = fk.split(".")
        if not hasattr(model_type, parts[0]) or parts[0] not in data:
            continue

        type_ = getattr(model_type, parts[0]).property.mapper.class_
        if not hasattr(type_, "id"):
            continue

        stmt = select(type_).where(type_.id == data[fk])
        result = await database.execute(stmt)
        obj = result.scalars().first()

        if not obj:
            return False

    return True

async def validate_unique_fields(
        model_type: Type,
        data: dict,
        database: AsyncSession,
        unique: Sequence[str],
        exclude_ids: list[int] | None = None,
) -> bool:
    conditions = []
    for field in unique:
        if field in data and hasattr(model_type, field):
            conditions.append(getattr(model_type, field) == data[field])
    exclude_conditions = []
    if exclude_ids and hasattr(model_type, "id"):
        for exclude_id in exclude_ids:
            exclude_conditions.append(getattr(model_type, "id") != exclude_id)

    stmt = select(model_type).where(or_(*conditions)).where(and_(*exclude_conditions))
    result = await database.execute(stmt)
    obj = result.scalars().first()
    return not bool(obj)