from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenFIGISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="OPENFIGI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str | None = None
