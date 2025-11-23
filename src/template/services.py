from typing import TypeVar, Type

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from src.equipment.schemas import Equipment
from src.template.models import TemplateBaseUpdate, TemplateBaseInfo, TemplateBaseDelete, TemplateBaseCreate, \
    TemplateBaseFilter
from src.models import Pagination
from src.database import DatabaseSession

from sqlalchemy import select, and_

from src.template.utils import validate_unique_fields, validate_foreign_keys, build_loader, get_nested_relation_paths, \
    build_missing_none_map, deep_merge

TemplateInfoType = TypeVar("TemplateInfoType", bound=TemplateBaseInfo)


TemplateFiltersType = TypeVar("TemplateFiltersType", bound=TemplateBaseFilter)
async def get_template_list(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        filters: TemplateFiltersType,
        pagination: Pagination,
        database: DatabaseSession,
        preload_relations: list[str] | None = None
) -> list[TemplateInfoType]:
    stmt = select(database_model_type)
    conditions = []

    if preload_relations:
        stmt = stmt.options(*build_loader(database_model_type, preload_relations))
    for field, value in filters.model_dump(exclude_none=True).items():
        if field.endswith("_like"):
            real_field = field[:-5]
            if hasattr(database_model_type, real_field):
                conditions.append(getattr(database_model_type, real_field).ilike(f"%{value}%"))
            continue
        if isinstance(value, list):
            if hasattr(database_model_type, field):
                conditions.append(getattr(database_model_type, field).in_(value))
            continue
        if hasattr(database_model_type, field):
            conditions.append(getattr(database_model_type, field) == value)

    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.offset(pagination.offset).limit(pagination.limit)
    templates = (await database.execute(stmt)).scalars().all()
    map_ = lambda x: return_type.model_validate({**x.__dict__}, from_attributes=True)
    return [map_(template) for template in templates]

TemplateCreateType = TypeVar("TemplateCreateType", bound=TemplateBaseCreate)
async def create_template(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        model: TemplateCreateType,
        database: DatabaseSession,
        foreign_key_map: dict[str, type] | None = None,
        unique_fields: list[str] | None = None,
        preload_relations: list[str] | None = None
) -> TemplateInfoType:
    data = model.model_dump(exclude_none=True)
    if unique_fields:
        await validate_unique_fields(unique_fields, database_model_type, data, database)
    if foreign_key_map:
        await validate_foreign_keys(foreign_key_map, data, database)

    template = database_model_type(**model.model_dump())
    database.add(template)
    await database.commit()
    await database.refresh(template)
    if preload_relations:
        stmt = select(database_model_type)
        stmt = stmt.options(*build_loader(database_model_type, preload_relations))
        template = (await database.execute(stmt.where(database_model_type.id == template.id))).scalars().first()

    return return_type.model_validate(template, from_attributes=True)

TemplateUpdateType = TypeVar("TemplateUpdateType", bound=TemplateBaseUpdate)
async def update_template(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        model: TemplateUpdateType,
        database: DatabaseSession,
        foreign_key_map: dict[str, type] | None = None,
        unique_fields: list[str] | None = None,
        preload_relations: list[str] | None = None
) -> TemplateInfoType:
    template = (await database.execute(select(database_model_type).where(database_model_type.id == model.id))).scalars().first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{database_model_type.__name__} with id {model.id} does not exist"
        )

    data = model.model_dump(exclude_none=True)
    if unique_fields:
        await validate_unique_fields(unique_fields, database_model_type, data, database, current_model_id=template.id)
    if foreign_key_map:
        await validate_foreign_keys(foreign_key_map, data, database)

    for key, value in data.items():
        setattr(template, key, value)

    database.add(template)
    await database.commit()
    await database.refresh(template)

    stmt = select(Equipment).where(Equipment.id == template.id)
    if preload_relations:
        stmt = stmt.options(*build_loader(database_model_type, preload_relations))
    template = (await database.execute(stmt)).scalars().first()

    return return_type.model_validate(template, from_attributes=True)

TemplateDeleteType = TypeVar("TemplateDeleteType", bound=TemplateBaseDelete)
async def delete_template(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        model: TemplateDeleteType,
        database: DatabaseSession
) -> TemplateInfoType:
    template = (await database.execute(select(database_model_type).where(database_model_type.id == model.id))).scalars().first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{database_model_type.__name__} with id {model.id} does not exist"
        )

    await database.delete(template)
    await database.commit()
    return return_type.model_validate(template, from_attributes=True)