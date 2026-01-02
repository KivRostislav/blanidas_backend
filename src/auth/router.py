from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends, Query
from fastapi.security import OAuth2PasswordRequestForm

from sorting import SortOrder, Sorting
from src.auth.dependencies import allowed, current_user
from src.auth.models import UserCreate, TokenInfo, UserUpdate, UserDelete, \
    UserFilters, UserInfo, UserPaginationResponse, TokenRefresh, LoginResponse, Login, UserSortBy
from src.auth.schemas import Role, User
from src.auth.services import AuthServices
from src.database import DatabaseSession
from src.config import SettingsDep
from src.pagination import Pagination, PaginationResponse

router = APIRouter(prefix="/users", tags=["Users"])
auth_services = AuthServices()

@router.get("/", response_model=PaginationResponse[UserInfo])
async def get_users_list_endpoint(
        database: DatabaseSession,
        filters: UserFilters = Depends(),
        pagination: Pagination = Depends(),
        sort_by: UserSortBy | None = Query(None),
        sort_order: SortOrder = Query(SortOrder.ascending),
        current: User = Depends(current_user(role=Role.manager))
) -> PaginationResponse[UserInfo]:
    filters_data = filters.model_dump(exclude_none=True)
    filters_data["id__ne"] = current.id
    return await auth_services.paginate(
        sorting=Sorting(order=sort_order, order_by=sort_by) if sort_by else None,
        database=database,
        pagination=pagination,
        filters=filters_data,
        preloads=["workplace"],
    )

@router.post("/", response_model=UserInfo)
async def create_user_endpoint(
        model: UserCreate,
        database: DatabaseSession,
) -> UserInfo:
    return await auth_services.create(
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["username", "email"],
        relationship_fields=["workplace"],
        preloads=["workplace"]
    )

@router.put("/", response_model=UserInfo)
async def update_user_endpoint(
        model: UserUpdate,
        database: DatabaseSession,
) -> UserInfo:
    return await auth_services.update(
        id_=model.id,
        data=model.model_dump(exclude_none=True),
        database=database,
        unique_fields=["username", "email"],
        preloads=["workplace"]
    )

@router.delete("/{id_}", response_model=None)
async def delete_user_endpoint(
        id_: int,
        database: DatabaseSession,
        _: Annotated[None, Depends(allowed(role=Role.manager))]
) -> None:
    return await auth_services.delete(id_=id_, database=database)


@router.post("/login", response_model=LoginResponse)
async def login(
        settings: SettingsDep,
        database: DatabaseSession,
        model: Login
) -> LoginResponse:
    return await auth_services.login(
        data = model.model_dump(),
        jwt_settings=settings.jwt,
        database=database,
    )

@router.post("/tokens/refresh", response_model=TokenInfo)
async def refresh_token_endpoint(
        model: TokenRefresh,
        settings: SettingsDep,
        database: DatabaseSession,
) -> TokenInfo:
    return await auth_services.refresh_token(
        data=model.model_dump(),
        jwt_settings=settings.jwt,
        database=database
    )
