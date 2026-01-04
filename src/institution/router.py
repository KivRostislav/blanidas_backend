from fastapi import APIRouter
from fastapi.params import Depends, Query

from sorting import Sorting, SortOrder
from src.institution.models import InstitutionInfo, InstitutionFilters, InstitutionCreate, InstitutionUpdate, \
    InstitutionOrderBy
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
        sort_by: InstitutionOrderBy | None = Query(None),
        sort_order: SortOrder = Query(SortOrder.ascending),
) -> PaginationResponse[InstitutionInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        sorting=Sorting(order=sort_order, order_by=sort_by) if sort_by else None,
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
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"],
        relationship_fields=["institution_type"],
        preloads=["institution_type"]
    )

@router.delete("/{id_}", response_model=int)
async def delete_institution_endpoint(id_: int, database: DatabaseSession) -> int:
    return await services.delete(id_=id_, database=database)

