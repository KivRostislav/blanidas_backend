from datetime import date
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.auth.schemas import Role, Scopes
from src.pagination import PaginationResponse


class ScopeInfo(BaseModel):
    id: int
    name: str
    role: Role

class ScopeCreate(BaseModel):
    role: Role
    name: str

class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    phone_number: PhoneNumber
    role: Role
    scopes: list[ScopeInfo]
    department: str
    workplace: str | None = None
    hire_at: date

    receive_low_stock_notification: bool
    receive_repair_request_creation_notification: bool

class UserPaginationResponse(PaginationResponse[UserInfo]):
    current: UserInfo

class UsersGet(BaseModel):
    current: UserInfo
    users: list[UserInfo]

class UserShortInfo(BaseModel):
    id: int
    email: EmailStr

class UserFilters(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None

class UserCreate(BaseModel):
    password: str = Field(min_length=8, max_length=64)
    username: str = Field(max_length=64)
    email: EmailStr
    phone_number: PhoneNumber
    role: Role
    scopes_ids: List[int]
    department: str
    workplace_id: Optional[int]
    hire_at: date

    receive_low_stock_notification: bool
    receive_repair_request_creation_notification: bool

class UserUpdate(BaseModel):
    id: int
    username: str | None = Field(max_length=64, default=None)
    password: Optional[str] | None = Field(min_length=8, max_length=50, default=None)
    email: EmailStr | None = None
    phone_number: PhoneNumber | None = None
    role: Role | None = None
    scopes: List[Scopes] | None = None
    department: str | None = None
    workplace_id: Optional[int] | None = None
    hire_at: date | None = None

class UserDelete(BaseModel):
    id: int

class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

class TokenGet(BaseModel):
    email: EmailStr
    password: str

class TokenRefresh(BaseModel):
    refresh_token: str