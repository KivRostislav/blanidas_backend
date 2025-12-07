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

async def validate_relationships(
        model_type: Type,
        data: dict,
        database: AsyncSession,
        relationship_fields: list[str],
) -> bool:
    async def check_relation(model: Type, path: list[str], prefix: str = "") -> bool:
        field = path[0]

        relationship = getattr(model, field).property
        related_model: Type = relationship.mapper.class_
        single_fk = prefix + field + "_id"
        list_fk = prefix + field + "_ids"

        if relationship.uselist:
            if list_fk in data:
                raw_values = data[list_fk]
            elif prefix + field in data:
                raw_values = data[prefix + field]
            else:
                return True

            if not raw_values:
                return True
            if isinstance(raw_values, dict) or (isinstance(raw_values, list) and isinstance(raw_values[0], dict)):
                return True
            if not isinstance(raw_values, list):
                return False

            stmt = select(related_model).where(related_model.id.in_(raw_values))
            result = await database.execute(stmt)
            if len(raw_values) != len(result.scalars().all()):
                return False

        else:
            fk_value = data.get(single_fk)
            if fk_value is None:
                return True

            stmt = select(related_model).where(related_model.id == fk_value)
            result = await database.execute(stmt)
            obj = result.scalars().first()
            if not obj:
                return False

        if len(path) == 1:
            return True

        new_prefix = prefix + field + "."
        return await check_relation(related_model, path[1:], new_prefix)

    for relationship_field in relationship_fields:
        path = relationship_field.split(".")
        ok = await check_relation(model_type, path)
        if not ok:
            return False

    return True

async def validate_uniqueness(
        model_type: Type,
        data: dict,
        database: AsyncSession,
        unique: Sequence[str],
        exclude_ids: list[int] | None = None,
) -> bool:
    if not unique:
        return True

    conditions = []
    for field in unique:
        if field in data and hasattr(model_type, field):
            conditions.append(getattr(model_type, field) == data[field])
    stmt = select(model_type)
    if not conditions:
        return True
    stmt = stmt.where(or_(*conditions))
    exclude_conditions = []
    if exclude_ids and hasattr(model_type, "id"):
        for exclude_id in exclude_ids:
            exclude_conditions.append(getattr(model_type, "id") != exclude_id)
        stmt = stmt.where(and_(*exclude_conditions))

    result = await database.execute(stmt)
    obj = result.scalars().first()
    return not bool(obj)