from fastapi import APIRouter
from fastapi.params import Depends

from src.database import DatabaseSession

from src.institution_type.models import InstitutionTypeInfo, InstitutionTypeCreate, InstitutionTypeFilters, InstitutionTypeUpdate
from src.institution_type.services import InstitutionTypeServices
from src.pagination import Pagination, PaginationResponse

router = APIRouter(prefix="/institution-types", tags=["Institution Type"])
services = InstitutionTypeServices()

@router.get("/", response_model=PaginationResponse[InstitutionTypeInfo])
async def get_institution_type_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: InstitutionTypeFilters = Depends(),
) -> PaginationResponse[InstitutionTypeInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True)
    )

@router.post("/", response_model=InstitutionTypeInfo)
async def create_institution_type_endpoint(
        model: InstitutionTypeCreate,
        database: DatabaseSession,
) -> InstitutionTypeInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique=["name"]
    )

@router.put("/", response_model=InstitutionTypeInfo)
async def update_institution_type_endpoint(
        model: InstitutionTypeUpdate,
        database: DatabaseSession,
) -> InstitutionTypeInfo:
    return await services.update(
        id=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique=["name"]
    )

@router.delete("/{id}", response_model=None)
async def delete_institution_type_endpoint(id: int, database: DatabaseSession) -> None:
    return await services.delete(id=id, database=database)
