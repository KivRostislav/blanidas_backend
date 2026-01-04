from enum import Enum

from pydantic import BaseModel

class ManufacturerFilters(BaseModel):
    name__ilike: str | None = None

class ManufacturerOrderBy(str, Enum):
    name = "name"

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
