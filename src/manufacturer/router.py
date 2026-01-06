import json

from fastapi import APIRouter
from fastapi.params import Depends, Query

from src.sorting import SortOrder, Sorting
from src.database import DatabaseSession
from src.decorators import domain_errors
from src.manufacturer.errors import error_map
from src.pagination import Pagination
from src.manufacturer.models import ManufacturerInfo, ManufacturerCreate, ManufacturerUpdate
from src.manufacturer.services import ManufacturerServices
from src.pagination import PaginationResponse


router = APIRouter(prefix="/manufacturers", tags=["Manufacturer"])
services = ManufacturerServices()

@router.get("/", response_model=PaginationResponse[ManufacturerInfo])
async def get_manufacturer_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        sorting: Sorting = Depends(),
        filters: str | None = Query(None),
) -> PaginationResponse[ManufacturerInfo]:
    return await services.paginate(
        database=database,
        filters=json.loads(filters) if filters else None,
        pagination=pagination,
        sorting=None if sorting.sort_by == "" else sorting,
    )

@router.post("/", response_model=ManufacturerInfo)
@domain_errors(error_map)
async def create_manufacturer_endpoint(model: ManufacturerCreate, database: DatabaseSession,) -> ManufacturerInfo:
    return await services.create(data=model.model_dump(exclude_none=True), database=database)

@router.put("/", response_model=ManufacturerInfo)
@domain_errors(error_map)
async def update_manufacturer_endpoint(model: ManufacturerUpdate, database: DatabaseSession) -> ManufacturerInfo:
    return await services.update(id_=model.id, data=model.model_dump(exclude_none=True), database=database)

@router.delete("/{id_}", response_model=int)
async def delete_manufacturer_endpoint(id_: int, database: DatabaseSession) -> int:
    return await services.delete(id_=id_, database=database)
