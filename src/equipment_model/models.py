from pydantic import BaseModel


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