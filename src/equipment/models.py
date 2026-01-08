from datetime import date
from enum import Enum

from pydantic import BaseModel, field_serializer

from src.equipment.schemas import EquipmentStatus
from src.equipment_category.models import EquipmentCategoryInfo
from src.equipment_model.models import EquipmentModelInfo
from src.institution.models import InstitutionInfo
from src.manufacturer.models import ManufacturerInfo

class EquipmentInfo(BaseModel):
    id: int
    serial_number: str
    installed: date
    location: str
    status: EquipmentStatus
    institution: InstitutionInfo | None = None
    equipment_model: EquipmentModelInfo | None = None
    equipment_category: EquipmentCategoryInfo | None = None
    manufacturer: ManufacturerInfo | None = None

    @field_serializer('installed')
    def serialize_my_date(self, dt: date) -> str:
        return dt.strftime('%Y-%m-%d')

class EquipmentCreate(BaseModel):
    location: str
    serial_number: str
    installed: date
    institution_id: int
    equipment_model_id: int
    equipment_category_id: int
    manufacturer_id: int

    @field_serializer('installed')
    def serialize_my_date(self, dt: date) -> str:
        return dt.isoformat()

class EquipmentUpdate(BaseModel):
    id: int
    location: str | None = None
    serial_number: str | None = None
    institution_id: int | None = None
    installed: date | None = None
    equipment_model_id: int | None = None
    equipment_category_id: int | None = None
    manufacturer_id: int | None = None

    @field_serializer('installed')
    def serialize_my_date(self, dt: date) -> str:
        return dt.strftime('%Y-%m-%d')

class EquipmentDelete(BaseModel):
    id: int

