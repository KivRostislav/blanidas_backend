from datetime import datetime

from pydantic import BaseModel, validator, field_validator

from src.auth.models import UserInfo
from src.equipment.models import EquipmentInfo
from src.failure_type.models import FailureTypeInfo
from src.institution.models import InstitutionInfo
from src.repair_request.schemas import UrgencyLevel, RepairRequestStatus
from src.spare_part.models import SparePartInfo

class RepairRequestStateInfo(BaseModel):
    id: int
    created_at: datetime
    status: RepairRequestStatus
    responsible_user: UserInfo | None

class RepairRequestStateCreate(BaseModel):
    status: RepairRequestStatus
    responsible_user_id: int | None

class RepairRequestFilters(BaseModel):
    pass

class FileCreate(BaseModel):
    file_path: str
    repair_request_id: int

class FileInfo(BaseModel):
    file_path: str

class CreateRepairRequestUsedSpareParts(BaseModel):
    quantity: int
    note: str
    spare_part_id: int
    institution_id: int

class RepairRequestUsedSparePartsInfo(BaseModel):
    quantity: int
    note: str
    spare_part: SparePartInfo | None
    institution: InstitutionInfo | None

class RepairRequestInfo(BaseModel):
    id: int
    description: str
    urgency_level: UrgencyLevel
    manager_note: str | None
    engineer_note: str | None
    created_at: datetime
    completed_at: datetime | None

    photos: list[FileInfo]
    failure_types: list[FailureTypeInfo]
    used_spare_parts: list[RepairRequestUsedSparePartsInfo]
    state_history: list[RepairRequestStateInfo]
    equipment: EquipmentInfo | None

class RepairRequestCreate(BaseModel):
    description: str
    urgency_level: UrgencyLevel
    equipment_id: int

class RepairRequestUpdate(BaseModel):
    id: int
    manager_note: str | None = None
    engineer_note: str | None = None

    failure_types_ids: list[int] | None = None
    used_spare_parts: list[CreateRepairRequestUsedSpareParts] | None = None
    state_history: RepairRequestStateCreate | None = None
