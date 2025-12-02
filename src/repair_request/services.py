import uuid
import os
from datetime import datetime
from pathlib import Path

import magic

from fastapi import UploadFile, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import User
from src.event import emit, EventTypes
from src.mailer.smtp import MailerService
from src.repair_request.models import RepairRequestInfo, RepairRequestStateCreate, FileCreate, RepairRequestStateInfo
from src.repair_request.schemas import RepairRequest, RepairRequestState, RepairRequestStatus, File
from src.repository import CRUDRepository
from src.services import GenericServices

ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "tif"}
ALLOWED_PHOTO_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

def form_url_to_file(static_dir: Path, filename: str) -> str:
    return os.path.join(static_dir, filename)

class RepairRequestServices(GenericServices[RepairRequest, RepairRequestInfo]):
    def __init__(self):
        self.repair_request_state_repo = CRUDRepository(RepairRequestState)
        self.file_repo = CRUDRepository(File)
        self.auth_repo = CRUDRepository(User)

        super().__init__(CRUDRepository(RepairRequest), RepairRequestInfo)

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            static_files_dir: Path = "",
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
                    raise Exception()

                new_files[f"{uuid.uuid4()}.{ext}"] = content
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type"
            )

        if "photos" in data:
            del data["photos"]

        repair_request = await super().create(
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads,
        )

        repair_request_state_date = RepairRequestStateCreate(
            repair_request_id=repair_request.id,
            responsible_user_id=None,
            created_at=datetime.now(),
            status=RepairRequestStatus.not_taken,
        )

        repair_photos_create = [
            FileCreate(
                file_path=x,
                repair_request_id=repair_request.id)
            .model_dump() for x in new_files.keys()
        ]

        saved_files = []
        try:
            for new_filename, photo_content in new_files.items():
                path = os.path.join(static_files_dir, new_filename)
                with open(path, "wb") as file:
                    file.write(photo_content)
                    saved_files.append(path)
        except Exception as e:
            await super().delete(id=repair_request.id, database=database)
            for path in saved_files:
                os.remove(path)
            raise e

        repair_photos = await self.file_repo.create_many(
            data_list=repair_photos_create,
            database=database,
        )

        repair_request_states = await self.repair_request_state_repo.create(
            data=repair_request_state_date.model_dump(),
            database=database,
            preloads=["responsible_user"],
        )

        repair_request.state_history.append(repair_request_states)
        repair_request.photos.append([
            form_url_to_file(static_files_dir, x.file_path) for x in repair_photos
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
                    payload=LowStockMessagePayload(
                        receiver_username=receiver.username,
                        spare_part_name=spare_part.name,
                        spare_part_serial_number=spare_part.serial_number,
                        spare_part_current_quantity=quantity,
                        spare_part_min_quantity=spare_part.min_quantity,
                    )
                )

        return RepairRequestInfo.model_validate(repair_request, from_attributes=True)


