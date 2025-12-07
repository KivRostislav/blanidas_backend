from fastapi import APIRouter
from fastapi.params import Depends

from src.database import DatabaseSession
from src.pagination import Pagination
from src.pagination import PaginationResponse
from src.spare_part_category.models import SparePartCategoryFilters, SparePartCategoryInfo, SparePartCategoryCreate, \
    SparePartCategoryUpdate
from src.spare_part_category.services import SparePartCategoryServices

router = APIRouter(prefix="/spare-part-categories", tags=["Spare Part Category"])
services = SparePartCategoryServices()

@router.get("/", response_model=PaginationResponse[SparePartCategoryInfo])
async def get_spare_part_category_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: SparePartCategoryFilters = Depends(),
) -> PaginationResponse[SparePartCategoryInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True)
    )

@router.post("/", response_model=SparePartCategoryInfo)
async def create_spare_part_category_endpoint(
        model: SparePartCategoryCreate,
        database: DatabaseSession,
) -> SparePartCategoryInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.put("/", response_model=SparePartCategoryInfo)
async def update_spare_part_category_endpoint(
        model: SparePartCategoryUpdate,
        database: DatabaseSession,
) -> SparePartCategoryInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.delete("/{id_}", response_model=None)
async def delete_spare_part_category_endpoint(id_: int, database: DatabaseSession) -> None:
    return await services.delete(id_=id_, database=database)
