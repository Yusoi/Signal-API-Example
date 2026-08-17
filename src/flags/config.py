from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")

    file_path: str
    driver: str = "sqlite+aiosqlite"


class AllSettings(BaseSettings):
    db: DBSettings = Field(default_factory=DBSettings)


settings = AllSettings()
