from pydantic import BaseModel


class FailureTypeInfo(BaseModel):
    id: int
    name: str

class FailureTypeFilters(BaseModel):
    name__like: str | None = None

class FailureTypeCreate(BaseModel):
    name: str

class FailureTypeUpdate(BaseModel):
    id: int
    name: str | None = None
