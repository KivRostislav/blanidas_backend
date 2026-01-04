from fastapi import APIRouter, Query
from fastapi.params import Depends

from sorting import SortOrder, Sorting
from src.equipment.models import EquipmentFilters, EquipmentCreate, EquipmentUpdate, EquipmentInfo, EquipmentSortBy
from src.equipment.services import EquipmentServices
from src.pagination import PaginationResponse, Pagination
from src.database import DatabaseSession

router = APIRouter(prefix="/equipment", tags=["Equipment"])
services = EquipmentServices()

@router.get("/", response_model=PaginationResponse[EquipmentInfo])
async def get_equipment_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: EquipmentFilters = Depends(),
        sort_by: EquipmentSortBy | None = Query(None),
        sort_order: SortOrder = Query(SortOrder.ascending),
) -> PaginationResponse[EquipmentInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        sorting=Sorting(order=sort_order, order_by=sort_by) if sort_by else None,
        filters=filters.model_dump(exclude_none=True),
        preloads=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.get("/{id_}", response_model=EquipmentInfo)
async def get_equipment_endpoint(id_: int, database: DatabaseSession) -> EquipmentInfo:
    return await services.get(
        id_=id_,
        database=database,
        preloads = [
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

# dsfdsfdsdfsfdsdfsdfd
@router.post("/", response_model=EquipmentInfo)
async def create_equipment_endpoint(
        model: EquipmentCreate,
        database: DatabaseSession,
) -> EquipmentInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name", "serial_number"],
        relationship_fields=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ],
        preloads=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.put("/", response_model=EquipmentInfo)
async def update_equipment_endpoint(
        model: EquipmentUpdate,
        database: DatabaseSession,
) -> EquipmentInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name", "serial_number"],
        relationship_fields=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ],
        preloads=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.delete("/{id_}", response_model=None)
async def delete_equipment_endpoint(id_: int, database: DatabaseSession) -> None:
    return await services.delete(id_=id_, database=database)