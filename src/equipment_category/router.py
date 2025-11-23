from fastapi import APIRouter
from fastapi.params import Depends

from src.equipment_category.models import EquipmentCategoryInfo, EquipmentCategoryFilters, EquipmentCategoryCreate, \
    EquipmentCategoryUpdate, EquipmentCategoryDelete
from src.equipment_category.services import EquipmentCategoryServices
from src.pagination import PaginationResponse, Pagination
from src.database import DatabaseSession


router = APIRouter(prefix="/equipment-category", tags=["Equipment Category"])
services = EquipmentCategoryServices()

@router.get("/", response_model=PaginationResponse[EquipmentCategoryInfo])
async def get_equipment_category_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: EquipmentCategoryFilters = Depends(),
) -> PaginationResponse[EquipmentCategoryInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True),
    )

@router.post("/", response_model=EquipmentCategoryInfo)
async def create_equipment_category_endpoint(
        model: EquipmentCategoryCreate,
        database: DatabaseSession,
) -> EquipmentCategoryInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique=["name"]
    )

@router.put("/", response_model=EquipmentCategoryInfo)
async def update_equipment_category_endpoint(
        model: EquipmentCategoryUpdate,
        database: DatabaseSession,
) -> EquipmentCategoryInfo:
    return await services.update(
        id=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique=["name"]
    )

@router.delete("/", response_model=None)
async def delete_equipment_category_endpoint(
        model: EquipmentCategoryDelete,
        database: DatabaseSession,
) -> None:
    return await services.delete(
        id=model.id,
        database=database
    )