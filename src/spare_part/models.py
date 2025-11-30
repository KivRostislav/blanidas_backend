from pydantic import BaseModel
from enum import Enum

from src.equipment_model.models import EquipmentModelInfo
from src.institution.models import InstitutionInfo
from src.manufacturer.models import ManufacturerInfo
from src.spare_part_category.models import SparePartCategoryInfo
from src.supplier.models import SupplierInfo

class SparePartLocationQuantityInfo(BaseModel):
    id: int
    quantity: int
    institution: InstitutionInfo | None

class SparePartLocationQuantityCreate(BaseModel):
    quantity: int
    institution_id: int

class SparePartInfo(BaseModel):
    id: int
    name: str
    serial_number: str | None
    price: int
    min_quantity: int
    compatible_models: list[EquipmentModelInfo]
    note: str | None

    locations: list[SparePartLocationQuantityInfo]
    supplier: SupplierInfo | None
    spare_part_category: SparePartCategoryInfo | None
    manufacturer: ManufacturerInfo | None

class SparePartState(str, Enum):
    InStock = "in_stock"
    LowStock = "low_stock"
    OutOfStock = "out_of_stock"

class SparePartFilters(BaseModel):
    name__like: str | None = None
    serial_number__like: str | None = None

    institution_type_id: int | None = None
    spare_part_category_id: int | None = None

   # stock_state: SparePartState | None = None


class SparePartCreate(BaseModel):
    name: str
    serial_number: str | None
    price: int
    min_quantity: int
    compatible_models_ids: list[int]
    note: str | None

    locations: list[SparePartLocationQuantityCreate]
    supplier_id: int
    spare_part_category_id: int
    manufacturer_id: int

class SparePartUpdate(BaseModel):
    id: int
    name: str | None = None
    serial_number: str | None = None
    price: int | None = None
    min_quantity: int | None = None
    compatible_models_ids: list[int] | None = None
    note: str | None = None

    institution_id: int | None = None
    supplier_id: int | None = None
    spare_part_category_id: int | None = None
    manufacturer_id: int | None = None

class SparePartDelete(BaseModel):
    id: int
