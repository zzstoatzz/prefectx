from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="PREFECTX_", env_file=".env", extra="ignore"
    )

    github_token: str = Field("", description="GitHub token.")
    github_username: str = Field("", description="GitHub username.")

settings = Settings()