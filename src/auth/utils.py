from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import jwt

class TokenType(str, Enum):
    access = "access-token"
    refresh = "refresh-token"

def generate_jwt_token(token_type: TokenType, expire_minutes: int,
                       payload: dict[str, Any], secret_key: str, algorithm: str) -> str:
    payload.update({
        "exp": datetime.now() + timedelta(minutes=expire_minutes),
        "token_type": token_type.value,
    })

    return jwt.encode(payload, secret_key, algorithm=algorithm)

