from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import jwt

from src.auth.schemas import User
from src.config import JWTSettings


class TokenType(str, Enum):
    access = "access-token"
    refresh = "refresh-token"

def generate_payload(model: User) -> dict[str, Any]:
     return {
        "sub": model.email,
        "username": model.username,
        "role": model.role,
        "id": model.id,
    }

def generate_jwt_token(
        token_type: TokenType,
        payload: dict[str, Any],
        settings: JWTSettings
) -> str:
    expire_in_minutes = (
        settings.access_token_expire_minutes
        if token_type == TokenType.access
        else settings.refresh_token_expire_minutes
    )
    payload.update({
        "exp": datetime.now() + timedelta(minutes=expire_in_minutes),
        "token_type": token_type.value,
    })

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

