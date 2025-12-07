import uuid
import os
from datetime import datetime
from typing import Any

import magic

from fastapi import UploadFile, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import User
from src.event import emit, EventTypes
from src.mailer.smtp import MailerService
from src.mailer.models import RepairRequestCreatedMessagePayload
from src.pagination import Pagination, PaginationResponse
from src.repair_request.models import RepairRequestInfo, FileCreate, FileInfo, RepairRequestStateCreate
from src.repair_request.schemas import RepairRequest, RepairRequestState, File, RepairRequestStatus
from src.repository import CRUDRepository
from src.services import GenericServices

ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "tif"}
ALLOWED_PHOTO_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}

def form_url_to_file(static_dir: str, filename: str) -> str:
    return os.path.join(static_dir, filename)

class RepairRequestServices(GenericServices[RepairRequest, RepairRequestInfo]):
    def __init__(self, proxy_url_to_static_files_dir: str, static_files_dir: str):
        self.repair_request_state_repo = CRUDRepository(RepairRequestState)
        self.file_repo = CRUDRepository(File)
        self.auth_repo = CRUDRepository(User)

        self.static_files_dir = static_files_dir
        self.proxy_url_to_static_files_dir = proxy_url_to_static_files_dir

        super().__init__(CRUDRepository(RepairRequest), RepairRequestInfo)

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            mailer: MailerService | None = None,
            background_tasks: BackgroundTasks | None = None,
            photos: list[UploadFile] | None = None,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> RepairRequestInfo:
        photos = photos if photos else []

        new_files = {}
        try:
            for photo in photos:
                ext = photo.filename.split(".")[-1].lower()
                content = photo.file.read()
                real_ext = magic.from_buffer(content, mime=True)
                if (
                        ext not in ALLOWED_PHOTO_EXTENSIONS
                        or photo.content_type not in ALLOWED_PHOTO_MIME
                        or real_ext not in ALLOWED_PHOTO_MIME
                ):
                    raise
                new_files[f"{uuid.uuid4()}.{ext}"] = content
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type"
            )
        data["state_history"] = RepairRequestStateCreate(
            status=RepairRequestStatus.not_taken,
            responsible_user_id=None,
        ).model_dump()
        data["state_history"].update({"created_at": datetime.now()})

        repair_request = await super().create(
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads,
        )

        repair_photos_create = [
            FileCreate(
                file_path=new_file,
                repair_request_id=repair_request.id
            ).model_dump() for new_file in new_files.keys()
        ]

        saved_files = []
        try:
            for new_filename, photo_content in new_files.items():
                path = os.path.join(self.static_files_dir, new_filename)
                with open(path, "wb") as file:
                    file.write(photo_content)
                    saved_files.append(path)
        except Exception as e:
            await super().delete(id=repair_request.id, database=database)
            background_tasks.add_task(lambda: (os.remove(path) for path in saved_files))
            raise e

        repair_photos = await self.file_repo.create_many(
            data_list=repair_photos_create,
            database=database,
        )
        repair_request.photos.extend([
            FileInfo(
                file_path=form_url_to_file(
                    self.proxy_url_to_static_files_dir,
                    repair_photo.file_path
                )
            ) for repair_photo in repair_photos
        ])

        if background_tasks and mailer:
            receivers = await self.auth_repo.get(
                database=database,
                filters={"receive_repair_request_created_notification": True}
            )
            for receiver in receivers:
                await emit(
                    event_name=EventTypes.repair_request_created.name,
                    background_tasks=background_tasks,
                    to=receiver.email,
                    mailer=mailer,
                    payload=RepairRequestCreatedMessagePayload(
                        receiver_username=receiver.username,
                        repair_request_description=repair_request.description,
                        repair_request_urgency_level=repair_request.urgency_level.value,
                        repair_request_photos=[photo.file_path for photo in repair_request.photos],
                        equipment_name=repair_request.equipment.name,
                    )
                )

        return repair_request

    async def update(
            self,
            id: int,
            data: dict,
            database: AsyncSession,
            background_tasks: BackgroundTasks | None = None,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            overwrite_relationships: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> RepairRequestInfo:
        if "state_history" in data:
            data["state_history"].update({"created_at": datetime.now()})
        repair_request = await super().update(
            id=id,
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            overwrite_relationships=overwrite_relationships,
            preloads=preloads,
        )

        for photo in repair_request.photos:
            photo.file_path = form_url_to_file(self.proxy_url_to_static_files_dir, photo.file_path)
        return repair_request

    async def delete(
            self,
            id_: int,
            database: AsyncSession,
            relationship_fields: list[str] | None = None,
            background_tasks: BackgroundTasks | None = None,
    ) -> None:
        photos = await self.file_repo.get(filters={"repair_request_id": id_}, database=database)
        for photo in photos:
            path = form_url_to_file(self.static_files_dir, photo.file_path)
            if background_tasks:
                background_tasks.add_task(os.remove, path)
                continue
            os.remove(path)
        await self.repo.delete(id_=id_, database=database, relationship_fields=relationship_fields)


    async def list(
            self,
            database: AsyncSession,
            pagination: Pagination,
            filters: dict[str, Any] | Any = None,
            preloads: list[str] | None = None,
    ) -> PaginationResponse[RepairRequestInfo]:
        result = await self.repo.paginate(
            database=database,
            pagination=pagination,
            filters=filters,
            preloads=preloads
        )
        result["items"] = [self.return_type.model_validate(x.__dict__, from_attributes=True) for x in result["items"]]
        for item in result["items"]:
            for photo in item.photos:
                photo.file_path = form_url_to_file(self.proxy_url_to_static_files_dir, photo.file_path)

        return PaginationResponse.model_validate(result)
