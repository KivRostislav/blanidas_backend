from fastapi import APIRouter
from fastapi.params import Depends

from src.institution.models import InstitutionInfo, InstitutionFilters, InstitutionCreate, InstitutionUpdate
from src.institution.services import InstitutionServices
from src.pagination import PaginationResponse, Pagination
from src.database import DatabaseSession


router = APIRouter(prefix="/institutions", tags=["Institution"])
services = InstitutionServices()

@router.get("/", response_model=PaginationResponse[InstitutionInfo])
async def get_institution_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: InstitutionFilters = Depends(),
) -> PaginationResponse[InstitutionInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True),
        preloads=["institution_type"],
    )

@router.post("/", response_model=InstitutionInfo)
async def create_institution_endpoint(
        model: InstitutionCreate,
        database: DatabaseSession,
) -> InstitutionInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"],
        relationship_fields=["institution_type"],
        preloads=["institution_type"],
    )

@router.put("/", response_model=InstitutionInfo)
async def update_institution_endpoint(
        model: InstitutionUpdate,
        database: DatabaseSession,
) -> InstitutionInfo:
    return await services.update(
        id=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"],
        relationship_fields=["institution_type"],
        preloads=["institution_type"]
    )

@router.delete("/{id}", response_model=None)
async def delete_institution_endpoint(id: int, database: DatabaseSession) -> None:
    return await services.delete(id=id, database=database)

