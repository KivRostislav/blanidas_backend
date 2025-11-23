from datetime import date

from pydantic import BaseModel

from src.equipment_category.models import EquipmentCategoryInfo
from src.equipment_model.models import EquipmentModelInfo
from src.institution.models import InstitutionInfo
from src.manufacturer.models import ManufacturerInfo


class EquipmentInfo(BaseModel):
    id: int
    name: str
    serial_number: str
    installed: date
    institution: InstitutionInfo | None = None
    equipment_model: EquipmentModelInfo | None = None
    equipment_category: EquipmentCategoryInfo | None = None
    manufacturer: ManufacturerInfo | None = None

class EquipmentFilters(BaseModel):
    name__like: str | None = None
    serial_number__like: str | None = None
    institution_id: int | None = None
    equipment_model_id: int | None = None
    equipment_category_id: int | None = None
    manufacturer_id: int | None = None

class EquipmentCreate(BaseModel):
    name: str
    serial_number: str
    installed: date
    institution_id: int
    equipment_model_id: int
    equipment_category_id: int
    manufacturer_id: int

class EquipmentUpdate(BaseModel):
    name: str | None = None
    serial_number: str | None = None
    institution_id: int | None = None
    installed: date | None = None
    equipment_model_id: int | None = None
    equipment_category_id: int | None = None
    manufacturer_id: int | None = None

class EquipmentDelete(BaseModel):
    id: int

