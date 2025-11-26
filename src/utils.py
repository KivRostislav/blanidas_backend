from typing import Type, Any

from sqlalchemy import Sequence, or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


def build_relation(model_type: Type, preload: Sequence[str]) -> list[Any]:
    options = []
    for rel in preload:
        parts = rel.split(".")
        attr = getattr(model_type, parts[0])
        loader = joinedload(attr)
        current_loader = loader
        current_model = attr.property.mapper.class_

        for part in parts[1:]:
            sub_attr = getattr(current_model, part)
            next_model = sub_attr.property.mapper.class_
            current_loader = current_loader.joinedload(sub_attr)
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
        if not hasattr(model_type, parts[0]) or parts[0] + "_id" not in data:
            continue

        print(model_type, parts)
        type_ = getattr(model_type, parts[0]).property.mapper.class_
        print(type_)
        if not hasattr(type_, "id"):
            continue

        stmt = select(type_).where(type_.id == data[parts[0] + "_id"])
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
    stmt = select(model_type)
    if conditions:
        stmt = stmt.where(or_(*conditions))
    exclude_conditions = []
    if exclude_ids and hasattr(model_type, "id"):
        for exclude_id in exclude_ids:
            exclude_conditions.append(getattr(model_type, "id") != exclude_id)
        stmt = stmt.where(and_(*exclude_conditions))

    result = await database.execute(stmt)
    obj = result.scalars().first()
    return not bool(obj)