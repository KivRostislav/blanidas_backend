from pydantic import EmailStr, BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.institution_type.models import InstitutionTypeInfo
from src.models import UkrainianPhoneNumber


class InstitutionInfo(BaseModel):
    id: int
    name: str
    address: str
    institution_type: InstitutionTypeInfo | None = None
    contact_phone: UkrainianPhoneNumber
    contact_email: EmailStr

class InstitutionCreate(BaseModel):
    name: str
    address: str
    institution_type_id: int
    contact_phone: UkrainianPhoneNumber
    contact_email: EmailStr

class InstitutionUpdate(BaseModel):
    id: int
    name: str | None = None
    address: str | None = None
    institution_type_id: int = None
    contact_phone: UkrainianPhoneNumber | None = None
    contact_email: EmailStr | None = None

class InstitutionDelete(BaseModel):
    id: int
