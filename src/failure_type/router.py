from fastapi import APIRouter
from fastapi.params import Depends

from src.database import DatabaseSession
from src.failure_type.models import FailureTypeInfo, FailureTypeFilters, FailureTypeCreate, FailureTypeUpdate
from src.failure_type.services import FailureTypeServices
from src.pagination import Pagination, PaginationResponse

router = APIRouter(prefix="/failure-types", tags=["Failure Type"])
services = FailureTypeServices()

@router.get("/", response_model=PaginationResponse[FailureTypeInfo])
async def get_failure_type_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: FailureTypeFilters = Depends(),
) -> PaginationResponse[FailureTypeInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True)
    )

@router.post("/", response_model=FailureTypeInfo)
async def create_failure_type_endpoint(
        model: FailureTypeCreate,
        database: DatabaseSession,
) -> FailureTypeInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.put("/", response_model=FailureTypeInfo)
async def update_failure_type_endpoint(
        model: FailureTypeUpdate,
        database: DatabaseSession,
) -> FailureTypeInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.delete("/{id_}", response_model=None)
async def delete_failure_type_endpoint(id_: int, database: DatabaseSession) -> None:
    return await services.delete(id=id_, database=database)
