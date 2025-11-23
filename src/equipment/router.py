from fastapi import APIRouter
from fastapi.params import Depends

from src.equipment.models import EquipmentFilters, EquipmentCreate, EquipmentUpdate, EquipmentDelete, EquipmentInfo
from src.equipment.schemas import Equipment
from src.equipment.services import EquipmentServices
from src.equipment_category.schemas import EquipmentCategory
from src.equipment_model.schemas import EquipmentModel
from src.institution.schemas import Institution
from src.manufacturer.schemas import Manufacturer
from src.pagination import PaginationResponse, Pagination
from src.database import DatabaseSession
from src.template.dependencies import get_template_list_service, create_template_service, update_template_service, \
    delete_template_service

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
            "equipment_model_id",
            "equipment_category_id",
            "manufacturer_id",
            "institution_id",
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
        service: EquipmentInfo =
            Depends(
                update_template_service(
                    Equipment,
                    EquipmentInfo,
                    EquipmentUpdate,
                    unique_fields=["name", "serial_number"],
                    foreign_key_map={
                            "equipment_model_id": EquipmentModel,
                            "equipment_category_id": EquipmentCategory,
                            "manufacturer_id": Manufacturer,
                            "institution_id": Institution,
                    },
                    preload_relations=[
                            "equipment_model",
                            "equipment_category",
                            "manufacturer",
                            "institution.institution_type",
                    ]
                )
            )
) -> EquipmentInfo:
    return service

@router.delete("/", response_model=EquipmentInfo)
async def delete_equipment_endpoint(
        service: EquipmentInfo =
            Depends(
                delete_template_service(
                    Equipment,
                    EquipmentInfo,
                    EquipmentDelete
                )
            )
) -> EquipmentInfo:
    return service