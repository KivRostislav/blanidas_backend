from datetime import date
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.auth.schemas import Role
from src.institution.models import InstitutionInfo
from src.models import UkrainianPhoneNumber
from src.pagination import PaginationResponse


class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: UkrainianPhoneNumber
    role: Role
    department: str
    workplace: InstitutionInfo | None = None
    hire_at: date

    receive_low_stock_notification: bool
    receive_repair_request_created_notification: bool

class UserPaginationResponse(PaginationResponse[UserInfo]):
    current: UserInfo

class UsersGet(BaseModel):
    current: UserInfo
    users: list[UserInfo]

class UserShortInfo(BaseModel):
    id: int
    email: EmailStr

class UserCreate(BaseModel):
    password: str = Field(min_length=8, max_length=64)
    username: str = Field(max_length=64)
    email: EmailStr
    phone_number: UkrainianPhoneNumber
    role: Role
    department: str
    workplace_id: Optional[int]
    hire_at: date

    receive_low_stock_notification: bool
    receive_repair_request_created_notification: bool


class UserUpdate(BaseModel):
    id: int
    username: str | None = Field(max_length=64, default=None)
    password: Optional[str] | None = Field(min_length=8, max_length=50, default=None)
    email: EmailStr | None = None
    phone_number: PhoneNumber | None = None
    role: Role | None = None
    department: str | None = None
    workplace_id: Optional[int] | None = None
    hire_at: date | None = None

    receive_low_stock_notification: bool
    receive_repair_request_created_notification: bool

class UserDelete(BaseModel):
    id: int

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class LoginResponse(BaseModel):
    token: TokenInfo
    current_user: UserInfo

class Login(BaseModel):
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str