from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.dependencies import get_current_user, auth_user
from src.auth.models import UserLogin, UserCreate, ScopesRead, TokenInfo, UserUpdate, UserDelete, \
    UserShortInfo, UserFilters, UsersGet
from src.auth.schemas import Role, User, Scopes
from src.database import DatabaseSession
from src.config import Settings
from src.models import Pagination
import src.auth.services as services

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=UsersGet)
async def get_users_list_endpoint(
        database: DatabaseSession,
        _: Annotated[None, Depends(auth_user(role=Role.manager))],
        filters: UserFilters = Depends(),
        pagination: Pagination = Depends(),
        current_user: User = Depends(get_current_user(scopes=[Scopes.create_users], role=Role.manager))
) -> UsersGet:
    return await services.get_users_list(current_user.email, filters, pagination, database)

@router.post("/", response_model=UserShortInfo)
async def create_user_endpoint(
        user: UserCreate,
        database: DatabaseSession,
        _:  Annotated[None, Depends(auth_user(role=Role.manager, scopes=[Scopes.create_users]))]
) -> UserShortInfo:
    return await services.create_user(user, database)

@router.put("/", response_model=UserShortInfo)
async def update_user_endpoint(
        user: UserUpdate,
        database: DatabaseSession,
        _: Annotated[User, Depends(get_current_user([Scopes.create_users], Role.manager))]
) -> UserShortInfo:
    return await services.update_user(user, database)

@router.delete("/", response_model=UserShortInfo)
async def delete_user_endpoint(
        user: UserDelete,
        database: DatabaseSession,
        _: Annotated[User, Depends(get_current_user([Scopes.create_users], Role.manager))]
) -> UserShortInfo:
    return await services.delete_user(user, database)


@router.post("/signin", response_model=TokenInfo)
async def signin_user_endpoint(
        settings: Settings,
        database: DatabaseSession,
        user: OAuth2PasswordRequestForm = Depends()
) -> TokenInfo:
    return await services.signin_user(UserLogin.model_validate({
        "email": user.username,
        "password": user.password,
    }), settings, database)

@router.post("/tokens/refresh", response_model=TokenInfo)
async def refresh_token_endpoint(refresh_token: str, settings: Settings, database: DatabaseSession) -> TokenInfo:
    return await services.refresh_token(refresh_token, settings, database)

@router.get("/scopes/{role}", response_model=ScopesRead)
async def get_scopes_endpoint(role: Role, database: DatabaseSession) -> ScopesRead:
    return await services.get_scopes(role, database)


