from pydantic import BaseModel

class InstitutionTypeFilters(BaseModel):
    name__like: str | None = None

class InstitutionTypeInfo(BaseModel):
    id: int
    name: str

class InstitutionTypeCreate(BaseModel):
    name: str

class InstitutionTypeUpdate(BaseModel):
    id: int
    name: str

class InstitutionTypeDelete(BaseModel):
    id: int


