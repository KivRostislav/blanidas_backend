from pydantic import BaseModel


class EquipmentCategoryInfo(BaseModel):
    id: int
    name: str

class EquipmentCategoryCreate(BaseModel):
    name: str

class EquipmentCategoryUpdate(BaseModel):
    id: int
    name: str

class EquipmentCategoryDelete(BaseModel):
    id: int