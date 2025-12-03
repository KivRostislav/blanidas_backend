from typing import Any, NamedTuple

from fastapi import HTTPException, status
from jwt import InvalidTokenError
from pwdlib import PasswordHash
import jwt
from pydantic import ValidationError

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import TokenInfo, UserInfo, UserPaginationResponse, ScopeInfo
from src.auth.schemas import User, Scope, Scopes, Role
from src.auth.utils import generate_jwt_token, TokenType, generate_payload
from src.config import JWTSettings
from src.pagination import Pagination
from src.repository import CRUDRepository
from src.services import GenericServices

password_hash = PasswordHash.recommended()

class IsAllowedReturnType(NamedTuple):
    is_allowed: bool
    user: User | None

class AuthServices(GenericServices[User, UserInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(User), UserInfo)

    async def create(
            self,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> UserInfo:
        data["password_hash"] = password_hash.hash(data["password"])
        del data["password"]

        return await super().create(
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads,
        )

    async def create_if_not_exists(
            self,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> UserInfo | None:
        try:
            return await self.create(
                data=data,
                database=database,
                unique_fields=unique_fields,
                relationship_fields=relationship_fields,
                preloads=preloads,
            )
        except HTTPException:
            return None

    async def update(
            self,
            id: int,
            data: dict,
            database: AsyncSession,
            unique_fields: list[str] | None = None,
            relationship_fields: list[str] | None = None,
            preloads: list[str] | None = None,
    ) -> UserInfo:
        if "password" in data:
            data["password_hash"] = password_hash.hash(data["password"])
            del data["password"]

        return await super().update(
            id=id,
            data=data,
            database=database,
            unique_fields=unique_fields,
            relationship_fields=relationship_fields,
            preloads=preloads,
        )

    async def list_with_current(
            self,
            current_user_id: int,
            database: AsyncSession,
            pagination: Pagination,
            filters: dict[str, Any] | Any = None,
            preloads: list[str] | None = None,
    ) -> UserPaginationResponse:
        filters.update({"id__ne": current_user_id })
        result = await self.repo.paginate(
            database=database,
            pagination=pagination,
            filters=filters,
            preloads=preloads,
        )

        result["items"] = [self.return_type.model_validate(x, from_attributes=True) for x in result["items"]]
        result["current"] = (await self.get(
            filters={"id": current_user_id},
            database=database,
            preloads=["scopes", "workplace"],
        ))[0]
        return UserPaginationResponse.model_validate(result)

    async def get_token(self, data: dict[str, Any], jwt_settings: JWTSettings, database: AsyncSession) -> TokenInfo:
        try:
            user = (await self.repo.paginate(
                pagination=Pagination(page=1, limit=1),
                filters={"email": data["email"]},
                database=database,
                preloads=["scopes"]
            ))["items"][0]
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")

        if not password_hash.verify(data["password"], user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")
        payload = generate_payload(user)

        refresh_token_str = generate_jwt_token(token_type=TokenType.refresh, payload=payload, settings=jwt_settings)
        access_token = generate_jwt_token(token_type=TokenType.access, payload=payload, settings=jwt_settings)
        return TokenInfo(access_token=access_token, refresh_token=refresh_token_str)

    async def refresh_token(self, data: dict[str, Any], jwt_settings: JWTSettings, database: AsyncSession) -> TokenInfo:
        try:
            token_data = jwt.decode(data["refresh_token"], jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")

        try:
            user = await self.repo.get(id=token_data["id"], database=database, preloads=["scopes"])
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or password")

        payload = generate_payload(user)
        access_token = generate_jwt_token(token_type=TokenType.access, payload=payload, settings=jwt_settings)
        return TokenInfo(access_token=access_token, refresh_token=data["refresh_token"])

    async def is_allowed(
            self,
            data: dict[str, Any],
            database: AsyncSession,
            jwt_settings: JWTSettings,
            scopes: list[Scopes] | None = None,
            role: Role | None = None,
    ) -> IsAllowedReturnType:
        try:
            payload = jwt.decode(data["access_token"], jwt_settings.secret_key, algorithms=[jwt_settings.algorithm])
        except (InvalidTokenError, ValidationError):
            return IsAllowedReturnType(is_allowed=False, user=None)

        id_ = payload.get("id")
        payload_scopes = payload.get("scopes").split(" ")
        payload_role = payload.get("role")
        user = (await self.repo.get(filters={"id": id_}, database=database, preloads=["scopes"]))[0]
        if not user:
            return IsAllowedReturnType(is_allowed=False, user=None)
        if scopes:
            for scope in scopes:
                if scope not in payload_scopes:
                    return IsAllowedReturnType(is_allowed=False, user=None)
        if role and payload_role != role:
            return IsAllowedReturnType(is_allowed=False, user=None)
        return IsAllowedReturnType(is_allowed=True, user=user)


class ScopeServices(GenericServices[Scope, ScopeInfo]):
    def __init__(self):
        super().__init__(CRUDRepository(Scope), ScopeInfo)

    async def create_if_not_exist(self, data: list[dict[str, Any]], database: AsyncSession) -> list[ScopeInfo]:
        result = []
        for scope_data in data:
            try:
                scope = await self.create(
                    data=scope_data,
                    database=database,
                    unique_fields=["name"],
                )
                result.append(ScopeInfo.model_validate(scope, from_attributes=True))
            except HTTPException:
                continue

        return result
