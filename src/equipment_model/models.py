from pydantic import BaseModel

class EquipmentModelFilters(BaseModel):
    name__like: str | None = None

class EquipmentModelInfo(BaseModel):
    id: int
    name: str

class EquipmentModelCreate(BaseModel):
    name: str

class EquipmentModelUpdate(BaseModel):
    id: int
    name: str

class EquipmentModelDelete(BaseModel):
    id: int