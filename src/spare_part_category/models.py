from pydantic import BaseModel


class SparePartCategoryInfo(BaseModel):
    id: int
    name: str

class SparePartCategoryCreate(BaseModel):
    name: str

class SparePartCategoryUpdate(BaseModel):
    id: int
    name: str

class SparePartCategoryDelete(BaseModel):
    id: int
