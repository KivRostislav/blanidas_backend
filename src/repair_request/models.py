from datetime import datetime

from pydantic import BaseModel
from starlette.datastructures import UploadFile

from src.auth.models import UserInfo
from src.equipment.models import EquipmentInfo
from src.repair_request.schemas import UrgencyLevel, RepairRequestStatus
from src.spare_part.models import SparePartInfo

class RepairRequestStateInfo(BaseModel):
    id: int
    created_at: datetime
    status: RepairRequestStatus
    responsible_user: UserInfo | None

class RepairRequestStateCreate(BaseModel):
    status: RepairRequestStatus
    responsible_user_id: int

class RepairRequestInfo(BaseModel):
    id: int
    description: str
    urgency_level: UrgencyLevel
    manager_note: str
    engineer_note: str

    photos: list[str]
    used_spare_parts: list[SparePartInfo]
    state_history: list[RepairRequestStateInfo]
    equipment: EquipmentInfo | None

class RepairRequestCreate(BaseModel):
    description: str
    urgency_level: UrgencyLevel
    manager_note: str
    engineer_note: str

    photos: list[UploadFile]
    used_spare_parts_ids: list[int]
    state_history: list[RepairRequestStateCreate]
    equipment_id: int