from pydantic import EmailStr, BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber


class SupplierInfo(BaseModel):
    id: int
    name: str
    contact_phone: PhoneNumber
    contact_email: EmailStr

class SupplierFilters(BaseModel):
    name__like: str | None = None

class SupplierCreate(BaseModel):
    name: str
    contact_phone: PhoneNumber
    contact_email: EmailStr

class SupplierUpdate(BaseModel):
    id: int
    name: str | None = None
    contact_phone: PhoneNumber | None = None
    contact_email: EmailStr | None = None

class SupplierDelete(BaseModel):
    id: int
