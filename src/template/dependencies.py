from typing import Annotated, Type, Any

from fastapi.params import Depends

from src.auth.schemas import User, Role
from src.auth.dependencies import auth_user

from src.models import Pagination
from src.database import DatabaseSession
from src.template.services import get_template_list, create_template, update_template, delete_template,\
    TemplateCreateType, TemplateFiltersType, TemplateUpdateType, TemplateDeleteType, TemplateInfoType

def get_template_list_service(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        filter_type: Type[TemplateFiltersType],
        preload_relations: list[str] | None = None
) -> Any:
    async def wrapper(
            database: DatabaseSession,
            _: Annotated[User, Depends(auth_user([], Role.manager))],
            filters: filter_type = Depends(),
            pagination: Pagination = Depends(),
    ) -> list[return_type]:
        return await get_template_list(database_model_type, return_type, filters, pagination, database, preload_relations)

    return wrapper

def create_template_service(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        model_type: Type[TemplateCreateType],
        foreign_key_map: dict[str, type] | None = None,
        unique_fields: list[str] | None = None,
        preload_relations: list[str] | None = None
) -> Any:
    async def wrapper(
            model: model_type,
            database: DatabaseSession,
            _: Annotated[User, Depends(auth_user([], Role.manager))],
    ) -> return_type:
        return await create_template(database_model_type, return_type, model, database, foreign_key_map, unique_fields, preload_relations)

    return wrapper

def update_template_service(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        model_type: Type[TemplateUpdateType],
        foreign_key_map: dict[str, type] | None = None,
        unique_fields: list[str] | None = None,
        preload_relations: list[str] | None = None
) -> Any:
    async def wrapper(
            model: model_type,
            database: DatabaseSession,
            _: Annotated[User, Depends(auth_user([], Role.manager))]
    ) -> return_type:
        return await update_template(database_model_type, return_type, model, database, foreign_key_map, unique_fields, preload_relations)

    return wrapper

def update_template_service_async(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        model_type: Type[TemplateUpdateType],
        foreign_key_map: dict[str, type] | None = None,
        unique_fields: list[str] | None = None,
) -> Any:
    async def wrapper(
            model: model_type,
            database: DatabaseSession,
            _: Annotated[User, Depends(auth_user([], Role.manager))]
    ) :
        return lambda: update_template(database_model_type, return_type, model, database, foreign_key_map, unique_fields)

    return wrapper

def delete_template_service(
        database_model_type: Type,
        return_type: Type[TemplateInfoType],
        model_type: Type[TemplateDeleteType],
) -> Any:
    async def wrapper(
            model: model_type,
            database: DatabaseSession,
            _: Annotated[User, Depends(auth_user([], Role.manager))]
    ) -> return_type:
        return lambda: delete_template(database_model_type, return_type, model, database)

    return wrapper