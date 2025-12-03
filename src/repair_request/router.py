from fastapi import APIRouter, UploadFile, BackgroundTasks
from fastapi.params import Depends, Form, File
from sqlalchemy.sql.annotation import Annotated

from src.mailer.dependencies import MailerServiceDep
from src.pagination import PaginationResponse, Pagination
from src.repair_request.models import RepairRequestInfo, RepairRequestFilters, RepairRequestCreate, RepairRequestUpdate
from src.database import DatabaseSession
from src.repair_request.schemas import UrgencyLevel
from src.repair_request.services import RepairRequestServices

from src.config import SettingsDep, get_settings

router = APIRouter(prefix="/repair-request", tags=["Repair request"])

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
) -> PaginationResponse[RepairRequestInfo]:
    return await services.list(
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True),
        preloads=[
            "equipment",
            "equipment.institution",
            "failure_types",
            "used_spare_parts",
            "photos",
            "state_history",
        ]
    )

@router.post("/", response_model=RepairRequestInfo)
async def create_repair_request_endpoint(
        database: DatabaseSession,
        background_tasks: BackgroundTasks,
        mailer: MailerServiceDep,
        description: str = Form(...),
        urgency_level: UrgencyLevel = Form(...),
        manager_note: str = Form(...),
        engineer_note: str = Form(...),
        failure_types_ids: list[int] = Form(...),
        used_spare_parts_ids: list[int] = Form(...),
        equipment_id: int = Form(...),
        photos: list[UploadFile] = File(default=[]),
) -> RepairRequestInfo:
    model = RepairRequestCreate(
        description=description,
        urgency_level=urgency_level,
        manager_note=manager_note,
        failure_types_ids=failure_types_ids,
        engineer_note=engineer_note,
        used_spare_parts_ids=used_spare_parts_ids,
        equipment_id=equipment_id,
    )

    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        background_tasks=background_tasks,
        mailer=mailer,
        photos=photos,
        relationship_fields=[
            "equipment",
            "failure_types",
            "used_spare_parts"
        ],
        preloads=[
            "equipment",
            "equipment.institution",
            "failure_types",
            "used_spare_parts",
            "photos",
            "state_history",
        ]
    )


@router.put("/", response_model=RepairRequestInfo)
async def update_repair_request_endpoint(
        model: RepairRequestUpdate,
        database: DatabaseSession,
) -> RepairRequestInfo:
    return await services.update(
        id=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        relationship_fields=[
            "failure_types",
            "used_spare_parts",
            "state_history",
            "state_history.responsible_user",
        ],
        preloads=[
            "equipment",
            "equipment.institution",
            "failure_types",
            "used_spare_parts",
            "photos",
            "state_history",
        ]
    )

@router.delete("/{id}", response_model=None)
async def delete_repair_request_endpoint(id: int, database: DatabaseSession) -> None:
    return await services.delete(id=id, database=database)

