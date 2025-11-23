from pydantic import BaseModel

class ManufacturerFilters(BaseModel):
    name__like: str | None = None

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
