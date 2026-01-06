import json

from fastapi import APIRouter
from fastapi.params import Depends, Query

from src.decorators import domain_errors
from src.institution.errors import errors_map
from src.sorting import Sorting, SortOrder
from src.institution.models import InstitutionInfo, InstitutionCreate, InstitutionUpdate
from src.institution.services import InstitutionServices
from src.pagination import PaginationResponse, Pagination
from src.database import DatabaseSession


router = APIRouter(prefix="/institutions", tags=["Institution"])
services = InstitutionServices()

@router.get("/", response_model=PaginationResponse[InstitutionInfo])
async def get_institution_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        sorting: Sorting = Depends(),
        filters: str | None = Query(None),
) -> PaginationResponse[InstitutionInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        filters=json.loads(filters) if filters else None,
        sorting=None if sorting.sort_by == "" else sorting,
        preloads=["institution_type"],
    )

@router.post("/", response_model=InstitutionInfo)
@domain_errors(errors_map)
async def create_institution_endpoint(model: InstitutionCreate, database: DatabaseSession) -> InstitutionInfo:
    return await services.create(data=model.model_dump(exclude_none=True), database=database, preloads=["institution_type"])

@router.put("/", response_model=InstitutionInfo)
@domain_errors(errors_map)
async def update_institution_endpoint(model: InstitutionUpdate, database: DatabaseSession) -> InstitutionInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        preloads=["institution_type"]
    )

@router.delete("/{id_}", response_model=int)
@domain_errors(errors_map)
async def delete_institution_endpoint(id_: int, database: DatabaseSession) -> int:
    return await services.delete(id_=id_, database=database)

