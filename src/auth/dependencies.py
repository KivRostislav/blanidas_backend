from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import status, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select, exists

import jwt

from src.auth.schemas import User, Scopes, Role
from src.database import DatabaseSession
from src.config import Settings

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/users/signin",
    auto_error=False,
    scopes={scope.value: f"Allows to {scope.value.replace('_', ' ')}" for scope in Scopes}
)


def get_current_user(scopes: List[Scopes], role: Optional[Role]):
    async def wrapper(access_token: Annotated[str, Depends(oauth2_scheme)], settings: Settings, db: DatabaseSession):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            username = payload.get("sub")
            exp = payload.get("exp")
            payload_scopes = payload.get("scopes")
            payload_role = payload.get("role")
            if username is None:
                raise credentials_exception
        except (InvalidTokenError, ValidationError):
            raise credentials_exception

        if datetime.fromtimestamp(exp) < datetime.now():
            raise credentials_exception

        user = (await db.execute(select(User).where(User.email == username))).scalars().first()
        if not user:
            raise credentials_exception
        permissions_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions")
        for scope in scopes:
            if scope not in payload_scopes:
                raise permissions_exception
        if role and payload_role != role:
            raise permissions_exception

        return user
    return wrapper

def auth_user(scopes: List[Scopes] | None = None, role: Role | None = None):
    async def wrapper(access_token: Annotated[str, Depends(oauth2_scheme)], settings: Settings, database: DatabaseSession):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
        try:
            payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            username = payload.get("sub")
            payload_scopes = payload.get("scopes")
            payload_role = payload.get("role")
            if username is None:
                raise credentials_exception
        except (InvalidTokenError, ValidationError):
            raise credentials_exception

        if not (await database.execute(select(exists().where(User.email == username)))):
            raise credentials_exception
        permissions_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough permissions")
        if scopes:
            for scope in scopes:
                if scope not in payload_scopes:
                    raise permissions_exception
        if role and payload_role != role:
            raise permissions_exception
    return wrapper
