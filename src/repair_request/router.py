from fastapi import APIRouter, UploadFile, BackgroundTasks, Query
from fastapi.params import Depends, Form, File

from sorting import SortOrder, Sorting
from src.mailer.dependencies import MailerServiceDep
from src.pagination import PaginationResponse, Pagination
from src.repair_request.models import RepairRequestInfo, RepairRequestFilters, RepairRequestCreate, RepairRequestUpdate, RepairRequestSortBy
from src.database import DatabaseSession
from src.repair_request.schemas import Urgency
from src.repair_request.services import RepairRequestServices

from src.config import get_settings

router = APIRouter(prefix="/repair-requests", tags=["Repair requests"])

settings = get_settings()
services = RepairRequestServices(
    proxy_url_to_static_files_dir=settings.proxy_url_to_static_files_dir,
    static_files_dir=settings.static_files_dir,
)

@router.get("/", response_model=PaginationResponse[RepairRequestInfo])
async def get_repair_request_list_endpoint(
        database: DatabaseSession,
        pagination: Pagination = Depends(),
        filters: RepairRequestFilters = Depends(),
        sort_by: RepairRequestSortBy | None = Query(None),
        sort_order: SortOrder = Query(SortOrder.ascending),
) -> PaginationResponse[RepairRequestInfo]:
    return await services.paginate(
        database=database,
        pagination=pagination,
        sorting=Sorting(order=sort_order, order_by=sort_by) if sort_by else None,
        filters=filters.model_dump(exclude_none=True),
        preloads=[
            "equipment",
            "equipment.institution",
            "equipment.equipment_model",
            "equipment.equipment_category",
            "failure_types",
            "used_spare_parts",
            "used_spare_parts.institution",
            "used_spare_parts.spare_part",
            "photos",
            "status_history",
            "status_history.assigned_engineer",
        ],
    )

@router.get("/{id_}", response_model=RepairRequestInfo)
async def get_repair_request_endpoint(id_: int, database: DatabaseSession) -> RepairRequestInfo:
    return await services.get(
        database=database,
        filters={"id": id_},
        preloads=[
            "equipment",
            "equipment.institution",
            "equipment.equipment_model",
            "equipment.equipment_category",
            "failure_types",
            "used_spare_parts",
            "used_spare_parts.institution",
            "used_spare_parts.spare_part",
            "photos",
            "status_history",
            "status_history.assigned_engineer",
        ]
    )

@router.post("/", response_model=RepairRequestInfo)
async def create_repair_request_endpoint(
        database: DatabaseSession,
        background_tasks: BackgroundTasks,
        mailer: MailerServiceDep,
        issue: str = Form(...),
        urgency: Urgency = Form(...),
        equipment_id: int = Form(...),
        photos: list[UploadFile] | None = File(None),
) -> RepairRequestInfo:
    photos = photos or []

    model = RepairRequestCreate(
        issue=issue,
        urgency=urgency,
        equipment_id=equipment_id,
    )

    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        background_tasks=background_tasks,
        mailer=mailer,
        photos=photos,
        preloads=[
            "equipment.institution",
            "equipment.equipment_model",
            "failure_types",
            "used_spare_parts",
            "photos",
            "status_history",
            "status_history.assigned_engineer",
        ]
    )


@router.put("/", response_model=RepairRequestInfo)
async def update_repair_request_endpoint(
        model: RepairRequestUpdate,
        database: DatabaseSession,
) -> RepairRequestInfo:
    return await services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        relationship_fields=[
            "failure_types",
            "used_spare_parts",
            "status_history",
        ],
        overwrite_relationships=["failure_types", "used_spare_parts"],
        preloads=[
            "failure_types",
            "used_spare_parts",
            "used_spare_parts.institution",
            "used_spare_parts.spare_part",
            "photos",
            "status_history",
            "status_history.assigned_engineer",
            "equipment",
            "equipment.institution",
        ]
    )

@router.delete("/{id_}", response_model=None)
async def delete_repair_request_endpoint(
        id_: int,
        database: DatabaseSession,
        background_tasks: BackgroundTasks
) -> None:
    return await services.delete(
        id_=id_,
        database=database,
        relationship_fields=[
            "failure_types",
            "used_spare_parts",
            "status_history",
        ],
        background_tasks=background_tasks,
    )

