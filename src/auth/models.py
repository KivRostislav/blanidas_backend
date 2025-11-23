from datetime import date
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.auth.schemas import Role, Scopes


class UserInfo(BaseModel):
    username: str
    email: EmailStr
    phone_number: PhoneNumber
    role: Role
    scopes: list[Scopes]
    department: str
    workplace: str | None = None
    hire_at: date


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


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    id: int
    username: str = Field(max_length=64)
    password: Optional[str] = Field(min_length=8, max_length=50, default=None)
    email: EmailStr
    phone_number: PhoneNumber
    role: Role
    scopes: List[Scopes]
    department: str
    workplace_id: Optional[int]
    hire_at: date


class UserDelete(BaseModel):
    id: int


class UserCreate(BaseModel):
    password: str = Field(min_length=8, max_length=64)
    username: str = Field(max_length=64)
    email: EmailStr
    phone_number: PhoneNumber
    role: Role
    scopes: List[Scopes]
    department: str
    workplace_id: Optional[int]
    hire_at: date


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class ScopesRead(BaseModel):
    scopes: List[str]
    role: Role


class ScopesCreate(BaseModel):
    role: Role
    scopes: List[Scopes]