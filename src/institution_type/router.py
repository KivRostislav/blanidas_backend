import json

from fastapi import APIRouter
from fastapi.params import Depends, Query

from src.database import DatabaseSession
from src.decorators import domain_errors
from src.institution_type.errors import errors_map

from src.institution_type.models import InstitutionTypeInfo, InstitutionTypeCreate, InstitutionTypeUpdate
from src.institution_type.services import InstitutionTypeServices
from src.pagination import Pagination, PaginationResponse
from src.sorting import Sorting

router = APIRouter(prefix="/institution-types", tags=["Institution Type"])
services = InstitutionTypeServices()

@router.get("/", response_model=PaginationResponse[InstitutionTypeInfo])
async def get_institution_type_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        sorting: Sorting = Depends(),
        filters: str | None = Query(None),
) -> PaginationResponse[InstitutionTypeInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        filters=json.loads(filters) if filters else None,
        sorting=None if sorting.sort_by == "" else sorting,
    )

@router.post("/", response_model=InstitutionTypeInfo)
@domain_errors(errors_map)
async def create_institution_type_endpoint(model: InstitutionTypeCreate, database: DatabaseSession) -> InstitutionTypeInfo:
    return await services.create(data=model.model_dump(exclude_none=True), database=database)

@router.put("/", response_model=InstitutionTypeInfo)
@domain_errors(errors_map)
async def update_institution_type_endpoint(model: InstitutionTypeUpdate, database: DatabaseSession) -> InstitutionTypeInfo:
    return await services.update(id_=model.id, data=model.model_dump(exclude_none=True), database=database)

@router.delete("/{id_}", response_model=int)
@domain_errors(errors_map)
async def delete_institution_type_endpoint(id_: int, database: DatabaseSession) -> int:
    return await services.delete(id_=id_, database=database)
