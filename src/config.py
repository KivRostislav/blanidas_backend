from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    database_url: str = "sqlite:///db.sqlite3"

    jwt_secret_key: str = Field(min_length=50)
    jwt_algorithm: str = "HS256"
    jwt_refresh_token_expire_minutes: int
    jwt_access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()

Settings = Annotated[AppSettings, Depends(get_settings)]