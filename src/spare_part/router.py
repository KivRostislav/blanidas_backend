from fastapi import APIRouter
from fastapi.params import Depends
from fastapi_cloud_cli.config import Settings

from src.database import DatabaseSession
from src.pagination import Pagination
from src.pagination import PaginationResponse
from src.smtp import send_low_stock_message
from src.spare_part.models import SparePartInfo, SparePartFilters, SparePartCreate, SparePartUpdate
from src.spare_part.services import SparePartServices

from src.config import SMTPSettingsDep
import src.smtp

router = APIRouter(prefix="/spare-parts", tags=["Spare Parts"])
services = SparePartServices()

@router.get("/", response_model=PaginationResponse[SparePartInfo])
async def get_spare_part_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: SparePartFilters = Depends(),
) -> PaginationResponse[SparePartInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True),
        preloads=[
            "supplier",
            "spare_part_category",
            "manufacturer",
            "locations.institution",
            "locations.institution.institution_type",
            "compatible_models"
        ]
    )

@router.post("/", response_model=SparePartInfo)
async def create_spare_part_endpoint(
        model: SparePartCreate,
        database: DatabaseSession,
        settings: SMTPSettingsDep,
) -> SparePartInfo:
    #filter for  models dsffffffffffffffffffffffffffffffffffffffffffffffffff

    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        send_low_stock_message_callback=lambda to, payload: send_low_stock_message(to, payload, settings),
        unique_fields=["name"],
        relationship_fields=[
            "manufacturer",
            "spare_part_category",
            "supplier",
            "compatible_models",
        ],
        preloads=[
            "compatible_models",
            "locations",
            "locations.institution",
            "locations.institution.institution_type",
            "manufacturer",
            "spare_part_category",
            "supplier",
        ]
    )

@router.put("/", response_model=SparePartInfo)
async def update_spare_part_endpoint(
        model: SparePartUpdate,
        database: DatabaseSession,
) -> SparePartInfo:
    return await services.update(
        id=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"],
        relationship_fields=[
            "locations",
            "manufacturer",
            "spare_part_category",
            "supplier",
            "compatible_models",
        ],
        preloads=[
            "compatible_models",
            "supplier",
            "spare_part_category",
            "manufacturer",
            "locations.institution",
            "locations.institution.institution_type",
        ]
    )

@router.delete("/{id}", response_model=None)
async def delete_spare_part_endpoint(id: int, database: DatabaseSession) -> None:
    return await services.delete(id=id, database=database)
