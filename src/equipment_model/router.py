from fastapi import APIRouter
from fastapi.params import Depends

from src.database import DatabaseSession
from src.equipment_model.models import EquipmentModelInfo, EquipmentModelFilters, EquipmentModelCreate, EquipmentModelUpdate
from src.equipment_model.services import EquipmentModelServices
from src.pagination import PaginationResponse, Pagination


router = APIRouter(prefix="/equipment-models", tags=["Equipment Model"])
services = EquipmentModelServices()

@router.get("/", response_model=PaginationResponse[EquipmentModelInfo])
async def get_equipment_model_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: EquipmentModelFilters = Depends(),
) -> PaginationResponse[EquipmentModelInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True)
    )

@router.post("/", response_model=EquipmentModelInfo)
async def create_equipment_model_endpoint(
        model: EquipmentModelCreate,
        database: DatabaseSession,
) -> EquipmentModelInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.put("/", response_model=EquipmentModelInfo)
async def update_equipment_model_endpoint(
        model: EquipmentModelUpdate,
        database: DatabaseSession,
) -> EquipmentModelInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"]
    )

@router.delete("/{id_}", response_model=None)
async def delete_equipment_model_endpoint(id_: int, database: DatabaseSession) -> None:
    return await services.delete(id_=id_, database=database)