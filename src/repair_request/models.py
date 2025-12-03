from datetime import datetime

from pydantic import BaseModel
from starlette.datastructures import UploadFile

from src.auth.models import UserInfo
from src.equipment.models import EquipmentInfo
from src.failure_type.models import FailureTypeInfo
from src.repair_request.schemas import UrgencyLevel, RepairRequestStatus
from src.spare_part.models import SparePartInfo

class RepairRequestStateInfo(BaseModel):
    id: int
    created_at: datetime
    status: RepairRequestStatus
    responsible_user: UserInfo | None

class RepairRequestFilters(BaseModel):
    pass

class RepairRequestStateCreate(BaseModel):
    status: RepairRequestStatus
    responsible_user_id: int | None

class FileCreate(BaseModel):
    file_path: str
    repair_request_id: int

class FileInfo(BaseModel):
    file_path: str

class RepairRequestInfo(BaseModel):
    id: int
    description: str
    urgency_level: UrgencyLevel
    manager_note: str
    engineer_note: str

    photos: list[FileInfo]
    failure_types: list[FailureTypeInfo]
    used_spare_parts: list[SparePartInfo]
    state_history: list[RepairRequestStateInfo]
    equipment: EquipmentInfo | None

class RepairRequestCreate(BaseModel):
    description: str
    urgency_level: UrgencyLevel
    manager_note: str
    engineer_note: str

    failure_types_ids: list[int]
    used_spare_parts_ids: list[int]
    equipment_id: int

class RepairRequestUpdate(BaseModel):
    id: int
    manager_note: str | None = None
    engineer_note: str | None = None

    failure_types_ids: list[int] | None = None
    used_spare_parts_ids: list[int] | None = None
    new_state: RepairRequestStateCreate | None = None