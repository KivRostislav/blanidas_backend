from datetime import datetime

from fastapi import HTTPException, status
from pwdlib import PasswordHash
import jwt

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from src.auth.models import UserCreate, UserShortInfo, TokenInfo, ScopesCreate, ScopesRead, UserUpdate, UserDelete, \
    UserFilters, UserInfo, UserLogin, UsersGet
from src.auth.schemas import User, Scope, Role, Scopes
from src.auth.utils import generate_jwt_token, TokenType
from src.database import DatabaseSession
from src.config import Settings
from src.models import Pagination
from src.repository import CRUDRepository
from src.services import GenericServices

password_hash = PasswordHash.recommended()

class AuthServices(GenericServices[User, UserInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(UserInfo), UserInfo)



async def signin_user(model: UserLogin, settings: Settings, database: DatabaseSession) -> TokenInfo:
    user = (await database.execute(
        select(User).where(User.email == model.email)
        .options(selectinload(User.scopes))
    )).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    if not password_hash.verify(model.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
    payload = {
        "sub": user.email,
        "username": user.username,
        "role": user.role,
        "scopes": " ".join([x.name for x in user.scopes]),
    }

    refresh_token_str = generate_jwt_token(
        TokenType.refresh,
        settings.jwt_refresh_token_expire_minutes,
        payload,
        settings.jwt_secret_key,
        settings.jwt_algorithm
    )

    access_token = generate_jwt_token(
        TokenType.access,
        settings.jwt_access_token_expire_minutes,
        payload,
        settings.jwt_secret_key,
        settings.jwt_algorithm
    )
    return TokenInfo(access_token=access_token, refresh_token=refresh_token_str)

async def refresh_token(refresh_token_str: str, settings: Settings, database: DatabaseSession) -> TokenInfo:
    data = jwt.decode(refresh_token_str, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    if datetime.fromtimestamp(data["exp"]) < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
    user = (await database.execute(
        select(User).where(User.email == data["sub"])
        .options(selectinload(User.scopes))
    )).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")

    payload = {
        "sub": user.email,
        "username": user.username,
        "role": user.role,
        "scope": " ".join([x.name for x in user.scopes]),
    }

    access_token = generate_jwt_token(
        TokenType.access,
        settings.jwt_access_token_expire_minutes,
        payload,
        settings.jwt_secret_key,
        settings.jwt_algorithm
    )
    return TokenInfo(access_token=access_token, refresh_token=refresh_token_str)

async def get_users_list(
        current_user_email: str,
        filters: UserFilters,
        pagination: Pagination,
        database: DatabaseSession
) -> UsersGet:
    stmt = select(User).where(User.email != current_user_email).options(selectinload(User.scopes))
    current_user = (await database.execute(select(User)
                                           .options(selectinload(User.scopes))
                                           .where(User.email == current_user_email))
                    ).scalars().first()
    for key, value in filters.model_dump(exclude_none=True).items():
        stmt = stmt.where(getattr(User, key) == value)

    if pagination.order_by:
        order_attr = getattr(User, pagination.order_by)
        order_attr = order_attr.desc() if pagination.decs else order_attr
        stmt = stmt.order_by(order_attr)
    stmt = stmt.offset(pagination.offset).limit(pagination.limit)
    users = (await database.execute(stmt.options(selectinload(User.scopes)))).scalars().all()
    map_ = lambda x: UserInfo.model_validate(
        {**x.__dict__, "scopes": [Scopes(x.name) for x in x.scopes]},
        from_attributes=True
    )
    return UsersGet.model_validate({
        "current": map_(current_user),
        "users": [map_(user) for user in users]
    })

async def create_user(user_model: UserCreate, database: DatabaseSession) -> UserShortInfo:
    user = (await database.execute(select(User).where(User.email == user_model.email))).scalars().first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    scopes = (await database.execute(select(Scope).where(
        and_(Scope.role == user_model.role, Scope.name.in_(user_model.scopes))
    ))).scalars().all()

    if len(scopes) != len(user_model.scopes):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid scopes used")
    user = User(**user_model.model_dump(exclude={"password", "scopes"}))
    user.password_hash = password_hash.hash(user_model.password)
    user.scopes.extend(scopes)

    database.add(user)
    await database.commit()
    return UserShortInfo.model_validate(user, from_attributes=True)

async def create_user_if_not_exist(user_model: UserCreate, database: DatabaseSession) -> UserShortInfo | None:
    try:
        return await create_user(user_model, database)
    except HTTPException:
        return None
    except BaseException as e:
        raise e

async def update_user(model: UserUpdate, database: DatabaseSession) -> UserShortInfo:
    user = (await database.execute(select(User).where(User.id == model.id).options(selectinload(User.scopes)))).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")
    scopes = (await database.execute(select(Scope).where(
        and_(Scope.role == model.role, Scope.name.in_(model.scopes))
    ))).scalars().all()

    if len(scopes) != len(model.scopes):
        raise HTTPException(status_code=400, detail="Invalid scopes used")
    for key, value in model.model_dump(exclude={"password", "scopes"}).items():
        setattr(user, key, value)
    if model.password:
        user.password_hash = password_hash.hash(model.password)
    user.scopes = list(scopes)

    database.add(user)
    await database.commit()
    return UserShortInfo.model_validate(user, from_attributes=True)

async def delete_user(user_model: UserDelete, database: DatabaseSession) -> UserShortInfo:
    user = (await database.execute(select(User).where(User.id == user_model.id).options(selectinload(User.scopes)))).scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist")

    await database.delete(user)
    await database.commit()
    return UserShortInfo.model_validate(**user.__dict__)

async def get_scopes(role: Role, database: DatabaseSession) -> ScopesRead:
    result = (await database.execute(select(Scope).where(Scope.role == role))).scalars().all()
    scopes = [x.name for x in result]

    return ScopesRead.model_validate({"role":role, "scopes":scopes}, from_attributes=True)

async def create_scopes_if_not_exist(create_scopes_model: ScopesCreate, database: DatabaseSession) -> list[int]:
    scope_names = (await database.execute(
        select(Scope.name).where(
            and_(Scope.role == create_scopes_model.role, Scope.name.in_(create_scopes_model.scopes))
        )
    )).scalars().all()

    missing = {x.name for x in create_scopes_model.scopes} - set(scope_names)
    if not missing:
        return []

    create_scopes_model.scopes = [Scopes(name) for name in missing]
    return await create_scopes(create_scopes_model, database)


async def create_scopes(create_scopes_model: ScopesCreate, databae: DatabaseSession) -> list[int]:
    scopes = [Scope(role=create_scopes_model.role, name=x) for x in create_scopes_model.scopes]

    databae.add_all(scopes)
    await databae.commit()

    return [x.id for x in scopes]