from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.dependencies import allowed, current_user, AuthServicesDep, ScopeServicesDep
from src.auth.models import UserCreate, TokenInfo, UserUpdate, UserDelete, \
    UserFilters, UserInfo, UserPaginationResponse, ScopeInfo, TokenGet, TokenRefresh
from src.auth.schemas import Role, User, Scopes
from src.database import DatabaseSession
from src.config import SettingsDep
from src.pagination import Pagination, PaginationResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=UserPaginationResponse)
async def get_users_list_endpoint(
        database: DatabaseSession,
        services: AuthServicesDep,
        filters: UserFilters = Depends(),
        pagination: Pagination = Depends(),
        current: User = Depends(
            current_user(
                scopes=[Scopes.create_users],
                role=Role.manager
            )
        )
) -> UserPaginationResponse:
    return await services.list_with_current(
        current_user_id=current.id,
        database=database,
        pagination=pagination,
        filters=filters.model_dump(exclude_none=True),
        preloads=["scopes", "workplace"],
    )

@router.post("/", response_model=UserInfo)
async def create_user_endpoint(
        model: UserCreate,
        services: AuthServicesDep,
        database: DatabaseSession,
        _:  Annotated[None, Depends(
            allowed(
                role=Role.manager,
                scopes=[Scopes.create_users]
            )
        )]
) -> UserInfo:
    return await services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["username", "email"],
        relationship_fields=["scopes", "workplace"],
        preloads=[
            "scopes",
            "workplace",
        ]
    )

@router.put("/", response_model=UserInfo)
async def update_user_endpoint(
        model: UserUpdate,
        services: AuthServicesDep,
        database: DatabaseSession,
        _: Annotated[None, Depends(
            allowed(
                role=Role.manager,
                scopes=[Scopes.create_users]
            )
        )]
) -> UserInfo:
    return await services.update(
        id=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["username", "email"],
        relationship_fields=["scopes"],
        preloads=["scopes", "workplace"]
    )

@router.delete("/", response_model=None)
async def delete_user_endpoint(
        model: UserDelete,
        services: AuthServicesDep,
        database: DatabaseSession,
        _: Annotated[None, Depends(
            allowed(
                role=Role.manager,
                scopes=[Scopes.create_users]
            )
        )]
) -> None:
    return await services.delete(id=model.id, database=database)


@router.post("/tokens", response_model=TokenInfo)
async def get_token_endpoint(
        settings: SettingsDep,
        services: AuthServicesDep,
        database: DatabaseSession,
        user: OAuth2PasswordRequestForm = Depends()
) -> TokenInfo:
    return await services.get_token(
        data = TokenGet.model_validate({
            "email": user.username,
            "password": user.password,
        }).model_dump(),
        jwt_settings=settings.jwt,
        database=database,
    )

@router.post("/tokens/refresh", response_model=TokenInfo)
async def refresh_token_endpoint(
        model: TokenRefresh,
        settings: SettingsDep,
        services: AuthServicesDep,
        database: DatabaseSession,
) -> TokenInfo:
    return await services.refresh_token(
        data=model.model_dump(),
        jwt_settings=settings.jwt,
        database=database
    )

@router.get("/scopes/{role}", response_model=PaginationResponse[ScopeInfo])
async def get_scopes_endpoint(
        role: Role,
        services: ScopeServicesDep,
        database: DatabaseSession,
        pagination: Pagination = Depends(),
) -> PaginationResponse[ScopeInfo]:
    return await services.list(
        database=database,
        filters={"role": role},
        pagination=pagination,
    )

