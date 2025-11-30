from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class SMTPSettings(BaseSettings):
    server: str
    port: int

    username: str
    password: str

    from_address: str

    low_stock_template_file: Path
    repair_request_creation_template_file: Path

class JWTSettings(BaseModel):
    secret_key: str = Field(min_length=64)
    algorithm: str = "HS256"
    refresh_token_expire_minutes: int
    access_token_expire_minutes: int

class AppSettings(BaseSettings):
    database_url: str
    jwt: JWTSettings
    smtp: SMTPSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__"
    )

@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()

SettingsDep = Annotated[AppSettings, Depends(get_settings)]

def get_jwt_settings(settings: SettingsDep) -> JWTSettings:
    return settings.jwt

JWTSettingsDep = Annotated[JWTSettings, Depends(get_jwt_settings)]

def get_smtp_settings(settings: SettingsDep) -> SMTPSettings:
    return settings.smtp

SMTPSettingsDep = Annotated[SMTPSettings, Depends(get_smtp_settings)]
