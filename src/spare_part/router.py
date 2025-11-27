from fastapi import APIRouter
from fastapi.params import Depends

from src.database import DatabaseSession
from src.pagination import Pagination
from src.pagination import PaginationResponse
from src.spare_part.models import SparePartInfo, SparePartFilters, SparePartCreate, SparePartUpdate
from src.spare_part.services import SparePartServices

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
        preload=[
            "supplier",
            "spare_part_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
            "compatible_models"
        ]
    )

@router.post("/", response_model=SparePartInfo)
async def create_spare_part_endpoint(
        model: SparePartCreate,
        database: DatabaseSession,
) -> SparePartInfo:
    #filter for  models dsffffffffffffffffffffffffffffffffffffffffffffffffff

    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique=["name"],
        foreign_keys=[
            "institution",
            "manufacturer",
            "spare_part_category",
            "supplier",
        ],
        many_to_many=[
            "compatible_models"
        ],
        preload=[
            "compatible_models",
            "institution",
            "institution.institution_type",
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
        unique=["name"],
        foreign_keys=[
            "institution",
            "manufacturer",
            "spare_part_category",
            "supplier",
        ],
        many_to_many=[
            "compatible_models"
        ],
        preload=[
            "compatible_models",
            "supplier",
            "spare_part_category",
            "manufacturer",
            "institution",
            "institution.institution_type",
        ]
    )

@router.delete("/{id}", response_model=None)
async def delete_spare_part_endpoint(id: int, database: DatabaseSession) -> None:
    return await services.delete(id=id, database=database)
