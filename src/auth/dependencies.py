from typing import Annotated, List, Optional

from fastapi import status, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from src.auth.schemas import User, Scopes, Role
from src.auth.services import AuthServices
from src.database import DatabaseSession
from src.config import JWTSettingsDep


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/tokens",
    auto_error=False,
    scopes={scope.value: f"Allows to {scope.value.replace('_', ' ')}" for scope in Scopes}
)

auth_services = AuthServices()

def current_user(scopes: List[Scopes], role: Optional[Role]):
    async def wrapper(
            access_token: Annotated[str, Depends(oauth2_scheme)],
            jwt_settings: JWTSettingsDep,
            database: DatabaseSession
    ) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication or authorization failed"
        )
        result = await auth_services.is_allowed(
            data={"access_token": access_token},
            database=database,
            jwt_settings=jwt_settings,
            role=role,
            scopes=scopes
        )
        if not result.is_allowed:
            raise exception

        return result.user

    return wrapper

def allowed(scopes: list[Scopes] | None = None, role: Role | None = None):
    async def wrapper(
            access_token: Annotated[str, Depends(oauth2_scheme)],
            jwt_settings: JWTSettingsDep,
            database: DatabaseSession
    ) -> None:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication or authorization failed"
        )
        result = await auth_services.is_allowed(
            data={"access_token": access_token},
            database=database,
            jwt_settings=jwt_settings,
            role=role,
            scopes=scopes
        )
        if not result.is_allowed:
            raise exception
    return wrapper
