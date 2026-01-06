from pydantic import BaseModel


class ManufacturerInfo(BaseModel):
    id: int
    name: str

class ManufacturerCreate(BaseModel):
    name: str

class ManufacturerUpdate(BaseModel):
    id: int
    name: str

class ManufacturerDelete(BaseModel):
    id: int
