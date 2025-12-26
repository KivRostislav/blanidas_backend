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
from src.repair_request.repository import RepairRequestRepository
from src.repair_request.schemas import RepairRequest, RepairRequestState, File, RepairRequestStatus
from src.repository import CRUDRepository
from src.services import GenericServices

ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "tif"}
ALLOWED_PHOTO_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}

def form_url_to_file(static_dir: str, filename: str) -> str:
    return os.path.join(static_dir, filename)

class RepairRequestServices(GenericServices[RepairRequest, RepairRequestInfo]):
    def __init__(self, proxy_url_to_static_files_dir: str, static_files_dir: str):
        super().__init__(CRUDRepository(RepairRequest), RepairRequestInfo)
        self.repo = RepairRequestRepository()
        self.file_repo = CRUDRepository(File)
        self.auth_repo = CRUDRepository(User)

        self.static_files_dir = static_files_dir
        self.proxy_url_to_static_files_dir = proxy_url_to_static_files_dir

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

        def validate_photos() -> list[str]:
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

            saved_files = []
            try:
                for new_filename, photo_content in new_files.items():
                    path = os.path.join(self.static_files_dir, new_filename)
                    with open(path, "wb") as file:
                        file.write(photo_content)
                        saved_files.append(path)
            except Exception as e:
                background_tasks.add_task(lambda: (os.remove(path) for path in saved_files))
                raise e

            return list(new_files.keys())

        repair_request_obj = await self.repo.create(
            data=data,
            database=database,
            preloads=preloads,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            validate_photos_callback=validate_photos,
        )

        repair_request = RepairRequestInfo.model_validate(repair_request_obj.__dict__, from_attributes=True)
        for photo in repair_request.photos:
            photo.file_path = form_url_to_file(self.proxy_url_to_static_files_dir, photo.file_path)

        if background_tasks and mailer:
            receivers = await self.auth_repo.list(
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
                        equipment_name=repair_request.equipment.equipment_model.name,
                    )
                )

        return repair_request

    async def update(
            self,
            id_: int,
            data: dict,
            database: AsyncSession,
            background_tasks: BackgroundTasks | None = None,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            overwrite_relationships: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> RepairRequestInfo:
        repair_request = await self.repo.update(
            id_=id_,
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            overwrite_relationships=overwrite_relationships,
            preloads=preloads,
        )

        for photo in repair_request.photos:
            photo.file_path = form_url_to_file(self.proxy_url_to_static_files_dir, str(photo.file_path))
        return RepairRequestInfo.model_validate(repair_request, from_attributes=True)

    async def delete(
            self,
            id_: int,
            database: AsyncSession,
            relationship_fields: list[str] | None = None,
            background_tasks: BackgroundTasks | None = None,
    ) -> None:
        photos = await self.file_repo.list(filters={"repair_request_id": id_}, database=database)
        for photo in photos:
            path = form_url_to_file(self.static_files_dir, photo.file_path)
            if background_tasks:
                background_tasks.add_task(os.remove, path)
                continue
            os.remove(path)
        await self.repo.delete(id_=id_, database=database, relationship_fields=relationship_fields)


    async def paginate(
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

    async def get(
            self,
            database: AsyncSession,
            filters: dict[str, Any] | Any = None,
            preloads: list[str] | None = None,
    ) -> RepairRequestInfo:
        result = await self.repo.get(
            database=database,
            filters=filters,
            preloads=preloads
        )
        for photo in result.photos:
            photo.file_path = form_url_to_file(self.proxy_url_to_static_files_dir, str(photo.file_path))

        return RepairRequestInfo.model_validate(result, from_attributes=True)
