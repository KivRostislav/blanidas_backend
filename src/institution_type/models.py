from pydantic import BaseModel


class InstitutionTypeInfo(BaseModel):
    id: int
    name: str

class InstitutionTypeCreate(BaseModel):
    name: str

class InstitutionTypeUpdate(BaseModel):
    id: int
    name: str

