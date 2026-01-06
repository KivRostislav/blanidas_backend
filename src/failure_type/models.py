from pydantic import BaseModel


class FailureTypeInfo(BaseModel):
    id: int
    name: str

class FailureTypeCreate(BaseModel):
    name: str

class FailureTypeUpdate(BaseModel):
    id: int
    name: str | None = None
