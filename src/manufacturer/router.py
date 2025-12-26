from fastapi import APIRouter
from fastapi.params import Depends

from src.database import DatabaseSession
from src.pagination import Pagination
from src.manufacturer.models import ManufacturerInfo, ManufacturerFilters, ManufacturerCreate, ManufacturerUpdate
from src.manufacturer.services import ManufacturerServices
from src.pagination import PaginationResponse

router = APIRouter(prefix="/manufacturers", tags=["Manufacturer"])
services = ManufacturerServices()

@router.get("/", response_model=PaginationResponse[ManufacturerInfo])
async def get_manufacturer_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: ManufacturerFilters = Depends(),
) -> PaginationResponse[ManufacturerInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True)
    )

@router.post("/", response_model=ManufacturerInfo)
async def create_manufacturer_endpoint(
        model: ManufacturerCreate,
        database: DatabaseSession,
) -> ManufacturerInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.put("/", response_model=ManufacturerInfo)
async def update_manufacturer_endpoint(
        model: ManufacturerUpdate,
        database: DatabaseSession,
) -> ManufacturerInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.delete("/{id_}", response_model=None)
async def delete_manufacturer_endpoint(id_: int, database: DatabaseSession) -> None:
    return await services.delete(id_=id_, database=database)
