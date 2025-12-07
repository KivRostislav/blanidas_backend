from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends

from src.database import DatabaseSession
from src.pagination import Pagination
from src.pagination import PaginationResponse
from src.mailer.dependencies import MailerServiceDep
from src.spare_part.filters import spare_part_filter
from src.spare_part.models import SparePartInfo, SparePartFilters, SparePartCreate, SparePartUpdate
from src.spare_part.services import SparePartServices

router = APIRouter(prefix="/spare-parts", tags=["Spare Parts"])
services = SparePartServices(filter_callback=spare_part_filter)

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
            "locations",
            "locations.institution",
            "locations.institution.institution_type",
            "compatible_models"
        ]
    )

@router.post("/", response_model=SparePartInfo)
async def create_spare_part_endpoint(
        model: SparePartCreate,
        database: DatabaseSession,
) -> SparePartInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["name"],
        relationship_fields=[
            "manufacturer",
            "spare_part_category",
            "supplier",
            "compatible_models",
            "locations"
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
        mailer: MailerServiceDep,
        background_task: BackgroundTasks,
        database: DatabaseSession,
) -> SparePartInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        mailer=mailer,
        background_tasks=background_task,
        unique_fields=["name"],
        relationship_fields=[
            "locations",
            "manufacturer",
            "spare_part_category",
            "supplier",
            "compatible_models",
        ],
        overwrite_relationships=[
            "locations",
            "compatible_models",
        ],
        preloads=[
            "compatible_models",
            "supplier",
            "spare_part_category",
            "manufacturer",
            "locations",
            "locations.institution",
            "locations.institution.institution_type",
        ]
    )

@router.delete("/{id_}", response_model=None)
async def delete_spare_part_endpoint(id_: int, database: DatabaseSession) -> None:
    return await services.delete(
        id_=id_,
        database=database,
        relationship_fields=[
            "locations",
            "manufacturer",
            "spare_part_category",
            "supplier",
            "compatible_models",
        ],
    )
