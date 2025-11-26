from fastapi import APIRouter
from fastapi.params import Depends

from src.equipment.models import EquipmentFilters, EquipmentCreate, EquipmentUpdate, EquipmentInfo
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
) -> PaginationResponse[EquipmentInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True),
        preload=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.post("/", response_model=EquipmentInfo)
async def create_equipment_endpoint(
        model: EquipmentCreate,
        database: DatabaseSession,
) -> EquipmentInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique=["name", "serial_number"],
        foreign_keys=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ],
        preload=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
        ]
    )

@router.put("/", response_model=EquipmentInfo)
async def update_equipment_endpoint(
        model: EquipmentUpdate,
        database: DatabaseSession,
) -> EquipmentInfo:
    return await services.update(
        id=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique=["name", "serial_number"],
        foreign_keys=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ],
        preload=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
        ]
    )

@router.delete("/{id}", response_model=None)
async def delete_equipment_endpoint(id: int, database: DatabaseSession) -> None:
    return await services.delete(id=id, database=database)