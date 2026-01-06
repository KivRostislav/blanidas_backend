from pydantic import EmailStr, BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber


class SupplierInfo(BaseModel):
    id: int
    name: str

class SupplierCreate(BaseModel):
    name: str

class SupplierUpdate(BaseModel):
    id: int
    name: str | None = None

class SupplierDelete(BaseModel):
    id: int
