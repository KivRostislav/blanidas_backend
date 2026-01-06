import json

from fastapi import APIRouter, Query
from fastapi.params import Depends

from src.decorators import domain_errors
from src.equipment.errors import errors_map
from src.sorting import SortOrder, Sorting
from src.equipment.models import EquipmentCreate, EquipmentUpdate, EquipmentInfo
from src.equipment.services import EquipmentServices
from src.pagination import PaginationResponse, Pagination
from src.database import DatabaseSession

router = APIRouter(prefix="/equipment", tags=["Equipment"])
services = EquipmentServices()

@router.get("/", response_model=PaginationResponse[EquipmentInfo])
async def get_equipment_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        sorting: Sorting = Depends(),
        filters: str | None = Query(None),
) -> PaginationResponse[EquipmentInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        filters=json.loads(filters) if filters else None,
        sorting=None if sorting.sort_by == "" else sorting,
        preloads=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.get("/{id_}", response_model=EquipmentInfo)
@domain_errors(errors_map)
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

@router.post("/", response_model=EquipmentInfo)
@domain_errors(errors_map)
async def create_equipment_endpoint(model: EquipmentCreate, database: DatabaseSession) -> EquipmentInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        preloads=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.put("/", response_model=EquipmentInfo)
@domain_errors(errors_map)
async def update_equipment_endpoint(model: EquipmentUpdate, database: DatabaseSession) -> EquipmentInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        preloads=[
            "equipment_model",
            "equipment_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.delete("/{id_}", response_model=int)
@domain_errors(errors_map)
async def delete_equipment_endpoint(id_: int, database: DatabaseSession) -> int:
    return await services.delete(id_=id_, database=database)